from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Asistencia(BaseModel):
    """Datos para crear un registro de asistencia.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    estudianteid: int
    cursoid: int
    personal_institucionalid: Optional[int] = None
    materiaid: int
    estado: str  # presente | ausente | tarde | excusado
    fecha: date


class AsistenciaActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    estudianteid: Optional[int] = None
    cursoid: Optional[int] = None
    personal_institucionalid: Optional[int] = None
    materiaid: Optional[int] = None
    estado: Optional[str] = None
    fecha: Optional[date] = None
