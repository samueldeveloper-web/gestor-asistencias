from app.repositories.base_repo import BaseRepository


class CargaAcademicaRepository(BaseRepository):
    TABLA = 'carga_academica'
    PK = "cargaid"
    RECURSO = "Carga académica"
