from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Estudiante(BaseModel):
    """Datos para crear un registro de estudiantes.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombres: str
    apellidos: str
    documento_identidad: str
    fecha_nacimiento: date
    direccion: Optional[str] = None


class EstudianteActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    documento_identidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
