from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Acudiente(BaseModel):
    """Datos para crear un registro de acudientes.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombres: str
    apellidos: str
    telefono: str
    email: str
    documento_identidad: str
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None


class AcudienteActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    documento_identidad: Optional[str] = None
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
