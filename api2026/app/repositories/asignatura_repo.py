from app.repositories.base_repo import BaseRepository


class AsignaturaRepository(BaseRepository):
    TABLA = ('asignaturas', 'materias', 'asignatura', 'materia')
    PK = "materiaid"
    RECURSO = "Asignatura"
