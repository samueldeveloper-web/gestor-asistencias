from app.core.excepciones import DatosInvalidos
from app.repositories.asistencia_repo import AsistenciaRepository
from app.repositories.base_repo import BaseRepository
from app.repositories.utilidades import primera

COLUMNAS_REVISION = ("estado_revision", "estado_excusa", "revision", "estado")


class ExcusaRepository(BaseRepository):
    TABLA = ("excusas", "excusa")
    PK = "excusaid"
    RECURSO = "Excusa"

    def revisar(self, excusaid: int, aprobada: bool, observacion: str | None = None):
        """Aprueba o rechaza la excusa. Si se aprueba, la asistencia pasa a 'excusado'."""
        excusa = self.obtener_por_id(excusaid)
        e = self.esquema()
        cambios = {}
        col = primera(e["columnas"], ("aprobada",))
        if col:
            cambios[col] = aprobada
        col = primera([c for c in e["columnas"] if c != e["estado"]], COLUMNAS_REVISION)
        if col:
            cambios[col] = "aprobada" if aprobada else "rechazada"
        col = primera(e["columnas"], ("observacion_revision", "respuesta", "observacion"))
        if col and observacion is not None:
            cambios[col] = observacion
        if not cambios:
            raise DatosInvalidos("La tabla excusas no tiene columna para guardar la revisión.")
        actualizada = self.actualizar(excusaid, cambios)
        id_asis = excusa.get("asistenciaid", excusa.get("asistencia_id"))
        if aprobada and id_asis is not None:
            AsistenciaRepository().actualizar(id_asis, {"estado": "excusado"})
        return actualizada

    def crear(self, datos: dict):
        """Si no llega el estudiante, se toma de la asistencia que se está excusando."""
        datos = dict(datos)
        if not datos.get("estudianteid") and datos.get("asistenciaid"):
            asistencia = AsistenciaRepository().obtener_por_id(datos["asistenciaid"])
            datos["estudianteid"] = asistencia.get("estudianteid")
        return super().crear(datos)
