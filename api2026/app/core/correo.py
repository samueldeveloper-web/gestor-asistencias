"""Envío de correos.

Dos formas, según lo que haya en el .env:
1. BREVO_API_KEY  -> se envía por la API HTTPS de Brevo (funciona en Render gratis,
   que bloquea los puertos SMTP 25/465/587).
2. SMTP_USER + SMTP_PASSWORD -> se envía por SMTP (por ejemplo Gmail con contraseña
   de aplicación). Funciona en local.
"""
import base64
import json
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage

from app.core.config import Config


def correo_configurado() -> bool:
    return bool(Config.BREVO_API_KEY or (Config.SMTP_USER and Config.SMTP_PASSWORD))


def enviar_correo(destinatario: str, asunto: str, texto: str, html: str | None = None,
                  adjuntos: list[tuple[str, bytes, str]] | None = None) -> None:
    """Envía un correo. adjuntos = [(nombre_archivo, contenido, mime 'application/pdf'), ...].
    Lanza una excepción si falla, para que quien llama decida qué hacer."""
    if Config.BREVO_API_KEY:
        _enviar_brevo(destinatario, asunto, texto, html, adjuntos)
    elif Config.SMTP_USER and Config.SMTP_PASSWORD:
        _enviar_smtp(destinatario, asunto, texto, html, adjuntos)
    else:
        raise RuntimeError("Falta configurar el correo: BREVO_API_KEY o SMTP_USER/SMTP_PASSWORD en el .env")


def _enviar_brevo(destinatario, asunto, texto, html, adjuntos):
    cuerpo = {
        "sender": {"name": Config.NOMBRE_INSTITUCION, "email": Config.SMTP_REMITENTE},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": texto,
        "htmlContent": html or f"<pre style='font-family:Arial'>{texto}</pre>",
    }
    if adjuntos:
        cuerpo["attachment"] = [{"name": n, "content": base64.b64encode(c).decode()} for n, c, _ in adjuntos]
    peticion = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=json.dumps(cuerpo).encode("utf-8"), method="POST",
        headers={"api-key": Config.BREVO_API_KEY, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(peticion, timeout=20):
            pass
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Brevo respondió {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}") from e


def _enviar_smtp(destinatario, asunto, texto, html, adjuntos):
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
