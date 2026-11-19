from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonalInstitucion(BaseModel):
    """Datos para crear un registro de personal_institucion.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombres: str
    apellidos: str
    documento_identidad: str
    telefono: str
    email: str
    cargo: str
    direccion: Optional[str] = None


class PersonalInstitucionActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    documento_identidad: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    cargo: Optional[str] = None
    direccion: Optional[str] = None
