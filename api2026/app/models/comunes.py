from pydantic import BaseModel


class CambioEstado(BaseModel):
    esta_activo: bool


class MarcarLeida(BaseModel):
    leida: bool = True


class RevisionExcusa(BaseModel):
    aprobada: bool
    observacion: str | None = None
