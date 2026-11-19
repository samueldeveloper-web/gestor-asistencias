from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

TipoReporte = Literal["asistencia", "consolidado", "notificaciones"]
EstadoAsistencia = Literal["presente", "ausente", "tarde", "excusado"]


class FiltrosReporte(BaseModel):
    """Criterios de filtro de los reportes. El rango de fechas es obligatorio."""
    fecha_inicio: date
    fecha_fin: date
    cursoid: Optional[int] = None
    materiaid: Optional[int] = None
    estudianteid: Optional[int] = None
    estado: Optional[EstadoAsistencia] = None


class EnvioReporte(FiltrosReporte):
    """Datos para enviar el reporte por correo como archivo adjunto."""
    correo: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=150)
    formato: Literal["pdf", "excel"] = "pdf"
    mensaje: Optional[str] = Field(default=None, max_length=500)
