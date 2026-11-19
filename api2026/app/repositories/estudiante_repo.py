from app.repositories.base_repo import BaseRepository


class EstudianteRepository(BaseRepository):
    TABLA = ('estudiantes', 'estudiante')
    PK = "estudiante_id"
    RECURSO = "Estudiante"
