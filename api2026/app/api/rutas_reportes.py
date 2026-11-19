"""
Módulo de reportes (Corte 3): visualizar, exportar a PDF/Excel y enviar por correo.
Filtros: rango de fechas (obligatorio), curso, asignatura, estudiante y estado.
Los datos salen de 3 o más tablas relacionadas y nunca incluyen IDs.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Path
from fastapi.responses import Response

from app.core.correo import correo_configurado, enviar_correo
from app.core.documentos import generar_excel, generar_pdf
from app.core.excepciones import DatosInvalidos, ErrorApi
from app.core.security import usuario_actual
from app.models.reporte import EnvioReporte, FiltrosReporte, TipoReporte
from app.repositories.reporte_repo import ReporteRepository

router = APIRouter(prefix="/reportes", tags=["Reportes"])
repo = ReporteRepository()

# Definición de cada reporte: título, columnas visibles (sin IDs) y consulta
REPORTES = {
    "asistencia": {
        "titulo": "Reporte detallado de asistencia",
        "consulta": repo.detalle_asistencia,
        "columnas": [
            {"titulo": "Fecha", "campo": "fecha", "ancho": 1},
            {"titulo": "Estudiante", "campo": "estudiante", "ancho": 2.2},
            {"titulo": "Documento", "campo": "documento", "ancho": 1.2},
            {"titulo": "Curso", "campo": "curso", "ancho": 0.9},
            {"titulo": "Asignatura", "campo": "asignatura", "ancho": 1.6},
            {"titulo": "Docente", "campo": "docente", "ancho": 2},
            {"titulo": "Estado", "campo": "estado", "ancho": 1},
        ],
    },
    "consolidado": {
        "titulo": "Consolidado de asistencia por estudiante",
        "consulta": repo.consolidado_estudiantes,
        "columnas": [
            {"titulo": "Estudiante", "campo": "estudiante", "ancho": 2.2},
            {"titulo": "Documento", "campo": "documento", "ancho": 1.2},
            {"titulo": "Curso", "campo": "curso", "ancho": 0.8},
            {"titulo": "Acudiente", "campo": "acudiente", "ancho": 2},
            {"titulo": "Teléfono acudiente", "campo": "telefono_acudiente", "ancho": 1.2},
            {"titulo": "Presentes", "campo": "presentes", "ancho": 1},
            {"titulo": "Ausencias", "campo": "ausencias", "ancho": 1},
            {"titulo": "Tardes", "campo": "tardes", "ancho": 1},
            {"titulo": "Excusados", "campo": "excusados", "ancho": 1},
            {"titulo": "Total", "campo": "total", "ancho": 0.6},
            {"titulo": "% Asistencia", "campo": "porcentaje_asistencia", "ancho": 0.9},
        ],
    },
    "notificaciones": {
        "titulo": "Notificaciones enviadas a acudientes",
        "consulta": repo.notificaciones_fallas,
        "columnas": [
            {"titulo": "Enviada", "campo": "fecha_envio", "ancho": 1.2},
            {"titulo": "Acudiente", "campo": "acudiente", "ancho": 1.8},
            {"titulo": "Correo", "campo": "correo_acudiente", "ancho": 2},
            {"titulo": "Estudiante", "campo": "estudiante", "ancho": 1.8},
            {"titulo": "Curso", "campo": "curso", "ancho": 0.7},
            {"titulo": "Fecha falla", "campo": "fecha_falla", "ancho": 1},
            {"titulo": "Tipo", "campo": "tipo", "ancho": 0.9},
            {"titulo": "Título", "campo": "titulo", "ancho": 2.2},
            {"titulo": "Correo enviado", "campo": "correo", "ancho": 1},
            {"titulo": "Lectura", "campo": "lectura", "ancho": 0.9},
        ],
    },
}


def _resumen(tipo: str, filas: list[dict]) -> list[tuple[str, str]]:
    if tipo == "asistencia":
        conteo = {e: sum(1 for f in filas if f["estado"] == e) for e in ("presente", "ausente", "tarde", "excusado")}
        total = len(filas)
        pct = round(100 * (conteo["presente"] + conteo["tarde"]) / total, 1) if total else 0
        return [("Registros", str(total)), ("Presentes", str(conteo["presente"])),
                ("Ausencias", str(conteo["ausente"])), ("Tardes", str(conteo["tarde"])),
                ("Excusados", str(conteo["excusado"])), ("% Asistencia", f"{pct}%".replace(".", ","))]
    if tipo == "consolidado":
        ausencias = sum(f["ausencias"] for f in filas)
        criticos = sum(1 for f in filas if f["porcentaje_asistencia"] < 80)
        return [("Estudiantes", str(len(filas))), ("Ausencias", str(ausencias)),
                ("Con asistencia < 80 %", str(criticos))]
    enviados = sum(1 for f in filas if f["correo"] == "Enviado")
    leidas = sum(1 for f in filas if f["lectura"] == "Leída")
    return [("Notificaciones", str(len(filas))), ("Correos enviados", str(enviados)),
            ("Leídas por el acudiente", str(leidas))]


def _armar(tipo: str, filtros: FiltrosReporte, usuario: dict | None) -> dict:
    if filtros.fecha_fin < filtros.fecha_inicio:
        raise DatosInvalidos("La fecha final no puede ser anterior a la fecha inicial")
    if (filtros.fecha_fin - filtros.fecha_inicio).days > 400:
        raise DatosInvalidos("El rango de fechas no puede superar un año")
    definicion = REPORTES[tipo]
    datos = filtros.model_dump()
    filas = definicion["consulta"](datos, usuario)
    return {
        "tipo": tipo,
        "titulo": definicion["titulo"],
        "columnas": [{"titulo": c["titulo"], "campo": c["campo"]} for c in definicion["columnas"]],
        "filas": filas,
        "filtros": [{"etiqueta": e, "valor": v} for e, v in repo.descripcion_filtros(datos)],
        "resumen": [{"etiqueta": e, "valor": v} for e, v in _resumen(tipo, filas)],
        "_columnas_archivo": definicion["columnas"],
    }


def _respuesta_archivo(contenido: bytes, nombre: str, mime: str) -> Response:
    # Expose-Headers permite que el navegador lea el nombre del archivo (CORS)
    return Response(contenido, media_type=mime, headers={
        "Content-Disposition": f'attachment; filename="{nombre}"',
        "Access-Control-Expose-Headers": "Content-Disposition"})


def _quien(usuario: dict | None) -> str:
    if not usuario:
        return "usuario de prueba"
    perfil = usuario.get("perfil") or {}
    return f"{perfil.get('nombre') or 'Usuario'} ({usuario.get('rol') or 'sin rol'})"


def _archivo(reporte: dict, formato: str, usuario: dict | None) -> tuple[bytes, str, str]:
    args = (reporte["titulo"], reporte["_columnas_archivo"], reporte["filas"],
            [(f["etiqueta"], f["valor"]) for f in reporte["filtros"]],
            [(r["etiqueta"], r["valor"]) for r in reporte["resumen"]], _quien(usuario))
    marca = datetime.now().strftime("%Y%m%d_%H%M")
    if formato == "pdf":
        return generar_pdf(*args), f"reporte_{reporte['tipo']}_{marca}.pdf", "application/pdf"
    return (generar_excel(*args), f"reporte_{reporte['tipo']}_{marca}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/{tipo}")
def ver_reporte(tipo: TipoReporte = Path(description="asistencia | consolidado | notificaciones"),
                filtros: FiltrosReporte = Depends(), usuario: dict | None = Depends(usuario_actual)):
    """Datos del reporte para visualizarlos en pantalla (DataTables)."""
    reporte = _armar(tipo, filtros, usuario)
    reporte.pop("_columnas_archivo")
    return reporte


@router.get("/{tipo}/pdf")
def exportar_pdf(tipo: TipoReporte, filtros: FiltrosReporte = Depends(),
                 usuario: dict | None = Depends(usuario_actual)):
    return _respuesta_archivo(*_archivo(_armar(tipo, filtros, usuario), "pdf", usuario))


@router.get("/{tipo}/excel")
def exportar_excel(tipo: TipoReporte, filtros: FiltrosReporte = Depends(),
                   usuario: dict | None = Depends(usuario_actual)):
    return _respuesta_archivo(*_archivo(_armar(tipo, filtros, usuario), "excel", usuario))


@router.post("/{tipo}/enviar")
def enviar_reporte(tipo: TipoReporte, datos: EnvioReporte, usuario: dict | None = Depends(usuario_actual)):
    """Genera el reporte y lo envía por correo como adjunto (PDF o Excel)."""
    if not correo_configurado():
        raise ErrorApi(503, "El correo no está configurado en la API (SMTP_USER y SMTP_PASSWORD en el .env)")
    filtros = FiltrosReporte(**datos.model_dump(include=set(FiltrosReporte.model_fields)))
    reporte = _armar(tipo, filtros, usuario)
    contenido, nombre, mime = _archivo(reporte, datos.formato, usuario)
    rango = reporte["filtros"][0]["valor"]
    texto = (f"Hola,\n\nAdjuntamos el {reporte['titulo'].lower()} ({rango}), "
             f"con {len(reporte['filas'])} registros.\n\n"
             + (f"{datos.mensaje}\n\n" if datos.mensaje else "")
             + f"Enviado por {_quien(usuario)} desde el gestor de asistencia.")
    try:
        enviar_correo(datos.correo, f"{reporte['titulo']} · {rango}", texto, adjuntos=[(nombre, contenido, mime)])
    except Exception as e:
        raise ErrorApi(502, f"No se pudo enviar el correo: {e}")
    return {"mensaje": f"Reporte enviado a {datos.correo}", "archivo": nombre, "registros": len(reporte["filas"])}
