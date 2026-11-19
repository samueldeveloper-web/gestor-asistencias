from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Matricula(BaseModel):
    """Datos para crear un registro de matriculas.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    estudianteid: int
    cursoid: int
    anio_lectivo: int
    estado: Optional[str] = None  # activo | retirado | graduado | promovido
    fecha_matricula: Optional[date] = None


class MatriculaActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    estudianteid: Optional[int] = None
    cursoid: Optional[int] = None
    anio_lectivo: Optional[int] = None
    estado: Optional[str] = None
    fecha_matricula: Optional[date] = None
