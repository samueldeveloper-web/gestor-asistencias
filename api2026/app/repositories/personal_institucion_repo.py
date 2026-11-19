from app.repositories.base_repo import BaseRepository


class PersonalInstitucionRepository(BaseRepository):
    TABLA = ('personal_institucional', 'personal_institucion')
    PK = "personalid"
    RECURSO = "Personal de la institución"
