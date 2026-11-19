from app.repositories.base_repo import BaseRepository


class ModuloRepository(BaseRepository):
    TABLA = ('modulo', 'modulos')
    PK = "moduloid"
    RECURSO = "Módulo"
