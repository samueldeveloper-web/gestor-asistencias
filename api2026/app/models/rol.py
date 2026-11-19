from typing import Optional

from pydantic import BaseModel, ConfigDict


class Rol(BaseModel):
    """Datos para crear un registro de rol.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombre: str
    descripcion: Optional[str] = None


class RolActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombre: Optional[str] = None
    descripcion: Optional[str] = None
