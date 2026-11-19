from typing import Optional

from pydantic import BaseModel, ConfigDict


class EstudianteAcudiente(BaseModel):
    """Datos para crear un registro de estudiante_acudiente.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    estudianteid: int
    acudienteid: int
    parentesco: str
    contacto_principal: Optional[bool] = None


class EstudianteAcudienteActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    estudianteid: Optional[int] = None
    acudienteid: Optional[int] = None
    parentesco: Optional[str] = None
    contacto_principal: Optional[bool] = None
