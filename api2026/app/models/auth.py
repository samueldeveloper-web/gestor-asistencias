from typing import Optional

from pydantic import BaseModel


class LoginEntrada(BaseModel):
    identifier: str          # usuario o correo
    password: str
    rolid: Optional[int] = None  # rol elegido en el login (opcional)


class CambioPassword(BaseModel):
    password_actual: str
    password_nueva: str
