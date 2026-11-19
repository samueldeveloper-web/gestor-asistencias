from app.repositories.base_repo import BaseRepository


class CursoRepository(BaseRepository):
    TABLA = ('cursos', 'curso')
    PK = "cursoid"
    RECURSO = "Curso"
