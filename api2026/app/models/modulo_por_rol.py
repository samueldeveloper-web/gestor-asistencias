from typing import Optional

from pydantic import BaseModel, ConfigDict


class ModuloPorRol(BaseModel):
    """Datos para crear un registro de modulo_por_rol.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    rolid: int
    moduloid: int
    permiso_crear: Optional[bool] = None
    permiso_leer: Optional[bool] = None
    permiso_actualizar: Optional[bool] = None
    permiso_eliminar: Optional[bool] = None


class ModuloPorRolActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    rolid: Optional[int] = None
    moduloid: Optional[int] = None
    permiso_crear: Optional[bool] = None
    permiso_leer: Optional[bool] = None
    permiso_actualizar: Optional[bool] = None
    permiso_eliminar: Optional[bool] = None
