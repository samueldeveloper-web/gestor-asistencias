"""Envío de correos por SMTP (por ejemplo Gmail con contraseña de aplicación)."""
import smtplib
from email.message import EmailMessage

from app.core.config import Config


def correo_configurado() -> bool:
    return bool(Config.SMTP_USER and Config.SMTP_PASSWORD)


def enviar_correo(destinatario: str, asunto: str, texto: str, html: str | None = None,
                  adjuntos: list[tuple[str, bytes, str]] | None = None) -> None:
    """Envía un correo. adjuntos = [(nombre_archivo, contenido, mime 'application/pdf'), ...].
    Lanza una excepción si falla, para que quien llama decida qué hacer."""
    if not correo_configurado():
        raise RuntimeError("Falta configurar SMTP_USER y SMTP_PASSWORD en el .env")
    mensaje = EmailMessage()
    mensaje["From"] = f"{Config.NOMBRE_INSTITUCION} <{Config.SMTP_REMITENTE}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(texto)
    if html:
        mensaje.add_alternative(html, subtype="html")
    for nombre, contenido, mime in adjuntos or []:
        principal, _, secundario = mime.partition("/")
        mensaje.add_attachment(contenido, maintype=principal, subtype=secundario or "octet-stream",
                               filename=nombre)
    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=20) as servidor:
        servidor.starttls()
        servidor.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        servidor.send_message(mensaje)
