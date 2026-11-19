import os

from dotenv import load_dotenv

load_dotenv()


def _bool(nombre: str, defecto: bool) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes")


class Config:
    """Parámetros de la API leídos del .env (nunca se escriben en el código)."""

    JWT_SECRET = os.getenv("JWT_SECRET", "cambia-esta-clave-en-el-env")
    JWT_ALGORITMO = "HS256"
    JWT_MINUTOS = int(os.getenv("JWT_MINUTOS", "480"))
    # Si es false, las rutas CRUD se pueden probar en /docs sin token
    AUTH_OBLIGATORIA = _bool("AUTH_OBLIGATORIA", True)

    CORS_ORIGENES = [o.strip() for o in os.getenv(
        "CORS_ORIGENES", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_REMITENTE = os.getenv("SMTP_REMITENTE", "") or SMTP_USER
    NOMBRE_INSTITUCION = os.getenv("NOMBRE_INSTITUCION", "Aula Presente")
