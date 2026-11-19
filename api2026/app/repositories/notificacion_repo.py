"""
Notificaciones de fallas. La fila la crea un TRIGGER de la BD cuando se registra
una asistencia 'ausente'; este repositorio busca las pendientes, envía el correo
a cada acudiente y las marca como enviadas.
"""
from psycopg2 import sql

from app.core.config import Config
from app.core.correo import correo_configurado, enviar_correo
from app.repositories.base_repo import BaseRepository
from app.repositories.utilidades import COLUMNAS_CORREO, primera

COLUMNAS_ENVIADA = ("enviado_correo", "enviada_correo", "correo_enviado", "enviada", "enviado")
# fecha_envio en Neon es la fecha de creación de la notificación, por eso no se usa aquí
COLUMNAS_FECHA_ENVIO = ("fecha_correo", "fecha_envio_correo", "fecha_enviado_correo")
COLUMNAS_LEIDA = ("leido", "leida")


class NotificacionRepository(BaseRepository):
    TABLA = ("notificaciones", "notificacion")
    PK = "notificacionid"
    RECURSO = "Notificación"

    def _col(self, candidatas):
        return primera(self.esquema()["columnas"], candidatas)

    def marcar_leida(self, notificacionid: int, leida: bool = True):
        col = self._col(COLUMNAS_LEIDA)
        if not col:
            return self.obtener_por_id(notificacionid)
        return self.actualizar(notificacionid, {col: leida})

    def pendientes(self, asistenciaid: int | None = None):
        e = self.esquema()
        enviada = self._col(COLUMNAS_ENVIADA)
        condiciones, valores = [], []
        if not enviada:
            # Sin columna de "correo enviado" no se sabe qué falta: no se reenvía nada
            return []
        if enviada:
            condiciones.append(sql.SQL("COALESCE({}, FALSE) = FALSE").format(sql.Identifier(enviada)))
        if e["estado"]:
            condiciones.append(sql.SQL("{} IS TRUE").format(sql.Identifier(e["estado"])))
        col_asis = primera(e["columnas"], ("asistenciaid", "asistencia_id"))
        if asistenciaid is not None and col_asis:
            condiciones.append(sql.SQL("{} = %s").format(sql.Identifier(col_asis)))
            valores.append(asistenciaid)
        where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(condiciones) if condiciones else sql.SQL("")
        consulta = sql.SQL("SELECT * FROM {}{} ORDER BY {}").format(
            sql.Identifier(e["tabla"]), where, sql.Identifier(e["pk"]))
        return self.ejecutar(consulta, valores, todos=True)

    # ---------------------------------------------------------------- datos del correo
    def _uno(self, tabla, pk, valor):
        if valor is None:
            return None
        return self.ejecutar(sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
            sql.Identifier(tabla), sql.Identifier(pk)), (valor,), uno=True)

    def _destinatarios(self, notif: dict) -> list[dict]:
        """Acudientes a quienes va la notificación: el de la fila o, si no tiene, los del estudiante."""
        from app.repositories.acudiente_repo import AcudienteRepository
        from app.repositories.estudiante_acudiente_repo import EstudianteAcudienteRepository
        acu = AcudienteRepository().esquema()
        id_acu = notif.get("acudienteid", notif.get("acudiente_id"))
        if id_acu is not None:
            fila = self._uno(acu["tabla"], acu["pk"], id_acu)
            return [fila] if fila else []
        id_est = notif.get("estudianteid", notif.get("estudiante_id"))
        if id_est is None:
            return []
        ea = EstudianteAcudienteRepository().esquema()
        filtro = sql.SQL(" AND ea.{} IS TRUE").format(sql.Identifier(ea["estado"])) if ea["estado"] else sql.SQL("")
        return self.ejecutar(sql.SQL("""SELECT a.* FROM {} ea JOIN {} a ON a.{} = ea.acudienteid
                                        WHERE ea.estudianteid = %s{}""").format(
            sql.Identifier(ea["tabla"]), sql.Identifier(acu["tabla"]), sql.Identifier(acu["pk"]), filtro),
            (id_est,), todos=True)

    def _contexto(self, notif: dict) -> dict:
        from app.repositories.asignatura_repo import AsignaturaRepository
        from app.repositories.asistencia_repo import AsistenciaRepository
        from app.repositories.curso_repo import CursoRepository
        from app.repositories.estudiante_repo import EstudianteRepository
        asis_e = AsistenciaRepository().esquema()
        asistencia = self._uno(asis_e["tabla"], asis_e["pk"], notif.get("asistenciaid", notif.get("asistencia_id"))) or {}
        id_est = notif.get("estudianteid", notif.get("estudiante_id")) or asistencia.get("estudianteid")
        es = EstudianteRepository().esquema()
        estudiante = self._uno(es["tabla"], es["pk"], id_est) or {}
        materia, curso = {}, {}
        if asistencia.get("materiaid") is not None:
            m = AsignaturaRepository().esquema()
            materia = self._uno(m["tabla"], m["pk"], asistencia["materiaid"]) or {}
        if asistencia.get("cursoid") is not None:
            c = CursoRepository().esquema()
            curso = self._uno(c["tabla"], c["pk"], asistencia["cursoid"]) or {}
        return {
            "estudiante": f"{estudiante.get('nombres', '')} {estudiante.get('apellidos', '')}".strip() or "su acudido",
            "fecha": str(asistencia.get("fecha", ""))[:10],
            "materia": materia.get("nombre_materia") or materia.get("nombre") or "",
            "curso": curso.get("nombre_curso") or curso.get("nombre") or "",
            "estado": asistencia.get("estado", "ausente"),
        }

    def _redactar(self, notif: dict, acudiente: dict, ctx: dict) -> tuple[str, str, str]:
        nombre_acu = f"{acudiente.get('nombres', '')} {acudiente.get('apellidos', '')}".strip() or "acudiente"
        asunto = notif.get("titulo") or notif.get("asunto") or f"Inasistencia de {ctx['estudiante']} el {ctx['fecha']}"
        detalle = " · ".join(x for x in (ctx["curso"], ctx["materia"]) if x)
        cuerpo = notif.get("mensaje") or (
            f"Le informamos que {ctx['estudiante']} registró inasistencia el {ctx['fecha']}"
            + (f" en {detalle}" if detalle else "") + ".")
        texto = (f"Estimado(a) {nombre_acu}:\n\n{cuerpo}\n\nSi la falla tiene justificación, puede registrar "
                 f"la excusa en la plataforma.\n\n{Config.NOMBRE_INSTITUCION}")
        html = f"""<div style="font-family:Arial,sans-serif;max-width:560px">
  <h2 style="color:#0d6efd;margin-bottom:4px">{Config.NOMBRE_INSTITUCION}</h2>
  <p>Estimado(a) <b>{nombre_acu}</b>:</p>
  <p>{cuerpo}</p>
  <table style="border-collapse:collapse">
    <tr><td style="padding:4px 12px 4px 0;color:#666">Estudiante</td><td><b>{ctx['estudiante']}</b></td></tr>
    <tr><td style="padding:4px 12px 4px 0;color:#666">Fecha</td><td>{ctx['fecha']}</td></tr>
    {'<tr><td style="padding:4px 12px 4px 0;color:#666">Clase</td><td>' + detalle + '</td></tr>' if detalle else ''}
  </table>
  <p>Si la falla tiene justificación, puede registrar la excusa en la plataforma.</p>
  <p style="color:#999;font-size:12px">Mensaje automático, por favor no responda este correo.</p>
</div>"""
        return asunto, texto, html

    def enviar_pendientes(self, asistenciaid: int | None = None) -> dict:
        """Envía por correo las notificaciones pendientes y las marca como enviadas."""
        resultado = {"pendientes": 0, "enviadas": 0, "fallidas": [], "sin_correo": 0}
        filas = self.pendientes(asistenciaid)
        resultado["pendientes"] = len(filas)
        if not filas:
            return resultado
        if not correo_configurado():
            resultado["fallidas"].append("Correo no configurado: define SMTP_USER y SMTP_PASSWORD en el .env")
            return resultado
        e = self.esquema()
        col_enviada = self._col(COLUMNAS_ENVIADA)
        col_fecha = self._col(COLUMNAS_FECHA_ENVIO)
        for notif in filas:
            ctx = self._contexto(notif)
            enviados = 0
            for acudiente in self._destinatarios(notif):
                correo = acudiente.get(primera(acudiente.keys(), COLUMNAS_CORREO) or "")
                if not correo:
                    resultado["sin_correo"] += 1
                    continue
                asunto, texto, html = self._redactar(notif, acudiente, ctx)
                try:
                    enviar_correo(correo, asunto, texto, html)
                    enviados += 1
                except Exception as ex:  # el error de un correo no detiene los demás
                    resultado["fallidas"].append(f"{correo}: {ex}")
            if enviados:
                cambios = []
                if col_enviada:
                    cambios.append(sql.SQL("{} = TRUE").format(sql.Identifier(col_enviada)))
                if col_fecha:
                    cambios.append(sql.SQL("{} = CURRENT_TIMESTAMP").format(sql.Identifier(col_fecha)))
                if cambios:
                    self.ejecutar(sql.SQL("UPDATE {} SET {} WHERE {} = %s").format(
                        sql.Identifier(e["tabla"]), sql.SQL(", ").join(cambios), sql.Identifier(e["pk"])),
                        (notif[e["pk"]],), escribir=True)
                resultado["enviadas"] += 1
        return resultado
