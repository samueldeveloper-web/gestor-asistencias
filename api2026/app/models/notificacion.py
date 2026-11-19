from typing import Optional

from pydantic import BaseModel, ConfigDict


class Notificacion(BaseModel):
    """Datos para crear un registro de notificaciones.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    acudienteid: int
    estudianteid: Optional[int] = None
    asistenciaid: Optional[int] = None
    tipo: Optional[str] = None
    titulo: str
    mensaje: str
    leido: Optional[bool] = None


class NotificacionActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    acudienteid: Optional[int] = None
    estudianteid: Optional[int] = None
    asistenciaid: Optional[int] = None
    tipo: Optional[str] = None
    titulo: Optional[str] = None
    mensaje: Optional[str] = None
    leido: Optional[bool] = None
