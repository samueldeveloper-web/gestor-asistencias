from app.repositories.base_repo import BaseRepository


class EstudianteAcudienteRepository(BaseRepository):
    TABLA = 'estudiante_acudiente'
    PK = "estudiante_acudienteid"
    RECURSO = "Vínculo estudiante-acudiente"
