from app.repositories.base_repo import BaseRepository


class AsistenciaRepository(BaseRepository):
    TABLA = ('asistencia', 'asistencias')
    PK = "asistenciaid"
    RECURSO = "Asistencia"
