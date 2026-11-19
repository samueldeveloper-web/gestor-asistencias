from typing import Optional

from pydantic import BaseModel, ConfigDict


class Asignatura(BaseModel):
    """Datos para crear un registro de asignaturas.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombre_materia: str
    descripcion: Optional[str] = None


class AsignaturaActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombre_materia: Optional[str] = None
    descripcion: Optional[str] = None
