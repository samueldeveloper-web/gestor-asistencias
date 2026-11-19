from typing import Optional

from pydantic import BaseModel, ConfigDict


class Usuario(BaseModel):
    """Datos para crear un registro de usuarios.
    extra="allow": acepta otras columnas que existan en la tabla de Neon."""
    model_config = ConfigDict(extra="allow")

    username: str
    email: str
    rolid: int
    password: str  # se guarda encriptada en password_hash
    personal_institucionalid: Optional[int] = None
    estudianteid: Optional[int] = None
    acudienteid: Optional[int] = None


class UsuarioActualizar(BaseModel):
    """En PUT todos los campos son opcionales: solo se cambia lo que se envía."""
    model_config = ConfigDict(extra="allow")

    username: Optional[str] = None
    email: Optional[str] = None
    rolid: Optional[int] = None
    password: Optional[str] = None
    personal_institucionalid: Optional[int] = None
    estudianteid: Optional[int] = None
    acudienteid: Optional[int] = None
