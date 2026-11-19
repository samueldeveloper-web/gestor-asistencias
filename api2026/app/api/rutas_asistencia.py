from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.asistencia import Asistencia, AsistenciaActualizar
from app.models.comunes import CambioEstado
from app.repositories.asistencia_repo import AsistenciaRepository
from app.repositories.notificacion_repo import NotificacionRepository

router = APIRouter(prefix="/asistencia", tags=["Asistencia"], dependencies=[Depends(usuario_actual)])
repo = AsistenciaRepository()
notificaciones = NotificacionRepository()

ESTADOS_FALLA = {"ausente", "falla", "inasistencia"}


@router.get("/")
def listar_asistencia(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_asistencia(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_asistencia(datos: Asistencia, tareas: BackgroundTasks):
    """Registra la asistencia. Si es 'ausente', el trigger de la BD crea la notificación
    y la API envía el correo al acudiente en segundo plano."""
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    id_nuevo = nuevo[repo.esquema()["pk"]]
    falla = str(nuevo.get("estado", "")).lower() in ESTADOS_FALLA
    if falla:
        tareas.add_task(_enviar_correos_falla, id_nuevo)
    return {"mensaje": "Asistencia registrada exitosamente", "id": id_nuevo, "data": nuevo,
            "notificacion": "Se notificará por correo al acudiente" if falla else None}


def _enviar_correos_falla(asistenciaid: int):
    try:
        print("Correo de falla:", notificaciones.enviar_pendientes(asistenciaid))
    except Exception as e:
        print(f"No se pudo enviar el correo de la falla {asistenciaid}: {e}")


@router.put("/{id_registro}")
def actualizar_asistencia(id_registro: int, datos: AsistenciaActualizar, tareas: BackgroundTasks):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    if str(actualizado.get("estado", "")).lower() in ESTADOS_FALLA:
        tareas.add_task(_enviar_correos_falla, id_registro)
    return {"mensaje": "Asistencia actualizada correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_asistencia(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Asistencia desactivada correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_asistencia(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
