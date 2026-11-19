"""Autenticación con JWT y manejo seguro de contraseñas (bcrypt)."""
from datetime import datetime, timedelta, timezone

import base64
import hashlib
import hmac

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Config
from app.core.excepciones import ErrorApi

COLUMNAS_PASSWORD = ("password_hash", "contrasena_hash", "contrasena", "contraseña", "password", "clave", "pass")

_bearer = HTTPBearer(auto_error=False)


def encriptar_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, guardada: str | None) -> bool:
    """Acepta contraseñas en bcrypt y, por compatibilidad con datos de prueba, en texto plano."""
    if not guardada:
        return False
    if guardada.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), guardada.encode("utf-8"))
        except ValueError:
            return False
    if guardada.startswith("scrypt$"):
        return _verificar_scrypt(password, guardada)
    return password == guardada


def _verificar_scrypt(password: str, guardada: str) -> bool:
    """Usuarios antiguos con formato 'scrypt$<sal>$<hash>' (scrypt N=16384, r=8, p=1).
    Prueba la sal como texto o como hex y el hash en hex o base64."""
    partes = guardada.split("$")
    if len(partes) < 3:
        return False
    sal_txt, hash_txt = partes[-2], partes[-1]
    sales = [sal_txt.encode()]
    try:
        sales.append(bytes.fromhex(sal_txt))
    except ValueError:
        pass
    esperados = []
    try:
        esperados.append(bytes.fromhex(hash_txt))
    except ValueError:
        pass
    try:
        esperados.append(base64.b64decode(hash_txt + "=" * (-len(hash_txt) % 4)))
    except ValueError:
        pass
    for sal in sales:
        for esperado in esperados:
            if not esperado:
                continue
            try:
                calculado = hashlib.scrypt(password.encode(), salt=sal, n=16384, r=8, p=1,
                                           dklen=len(esperado), maxmem=64 * 1024 * 1024)
            except ValueError:
                continue
            if hmac.compare_digest(calculado, esperado):
                return True
    return False


def crear_token(datos: dict) -> str:
    carga = dict(datos)
    carga["exp"] = datetime.now(timezone.utc) + timedelta(minutes=Config.JWT_MINUTOS)
    return jwt.encode(carga, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITMO)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise ErrorApi(401, "La sesión expiró, inicia sesión de nuevo")
    except jwt.InvalidTokenError:
        raise ErrorApi(401, "Token inválido")


def usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict | None:
    """Dependencia de las rutas protegidas: exige 'Authorization: Bearer <token>'."""
    if credenciales is None:
        if Config.AUTH_OBLIGATORIA:
            raise ErrorApi(401, "Debes iniciar sesión (falta el token)")
        return None
    return decodificar_token(credenciales.credentials)
