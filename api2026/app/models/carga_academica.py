from typing import Optional

from pydantic import BaseModel, ConfigDict


class CargaAcademica(BaseModel):
    """Datos para crear un registro de carga_academica.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    cursoid: int
    materiaid: int
    personal_institucionalid: int
    anio_lectivo: int


class CargaAcademicaActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    cursoid: Optional[int] = None
    materiaid: Optional[int] = None
    personal_institucionalid: Optional[int] = None
    anio_lectivo: Optional[int] = None
