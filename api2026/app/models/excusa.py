from typing import Optional

from pydantic import BaseModel, ConfigDict


class Excusa(BaseModel):
    """Datos para crear un registro de excusas.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    asistenciaid: int
    estudianteid: Optional[int] = None  # si no se envía se toma de la asistencia
    acudienteid: Optional[int] = None
    motivo: str
    documento_adjunto: Optional[str] = None


class ExcusaActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    asistenciaid: Optional[int] = None
    acudienteid: Optional[int] = None
    motivo: Optional[str] = None
    documento_adjunto: Optional[str] = None
