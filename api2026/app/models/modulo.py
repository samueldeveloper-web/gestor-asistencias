from typing import Optional

from pydantic import BaseModel, ConfigDict


class Modulo(BaseModel):
    """Datos para crear un registro de modulo.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombre: str
    ruta: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None


class ModuloActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombre: Optional[str] = None
    ruta: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
