from app.repositories.base_repo import BaseRepository


class MatriculaRepository(BaseRepository):
    TABLA = ('matriculas', 'matricula')
    PK = "matriculaid"
    RECURSO = "Matrícula"
