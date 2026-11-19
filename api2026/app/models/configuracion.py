from typing import Optional

from pydantic import BaseModel, ConfigDict


class Configuracion(BaseModel):
    """Parámetro institucional (clave/valor), p. ej. nombre del colegio o año lectivo."""
    model_config = ConfigDict(extra="allow")

    clave: str
    valor: str


class ConfiguracionActualizar(BaseModel):
    model_config = ConfigDict(extra="allow")

    valor: Optional[str] = None
