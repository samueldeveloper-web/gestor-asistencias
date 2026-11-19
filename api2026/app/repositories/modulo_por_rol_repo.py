from app.repositories.base_repo import BaseRepository


class ModuloPorRolRepository(BaseRepository):
    TABLA = ('modulo_por_rol', 'rol_modulo')
    PK = "modulo_por_rolid"
    RECURSO = "Permiso de módulo"
