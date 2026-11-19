from typing import Optional

from pydantic import BaseModel, ConfigDict


class Curso(BaseModel):
    """Datos para crear un registro de cursos.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    nombre_curso: str
    nivel_educativo: str


class CursoActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    nombre_curso: Optional[str] = None
    nivel_educativo: Optional[str] = None
