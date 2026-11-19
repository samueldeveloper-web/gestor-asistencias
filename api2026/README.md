# api2026 — API del gestor de asistencia

FastAPI + PostgreSQL (Neon) con SQL puro (psycopg2), estructura de clase:
`app/core` (conexión, JWT, correo, errores) · `app/models` (Pydantic) · `app/repositories` (SQL) · `app/api` (rutas) · `main.py`.

## Ejecutar (Windows / PowerShell)
```powershell
cd api2026
python -m venv myvenv
.\myvenv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # y llena DB_*, JWT_SECRET y SMTP_*
uvicorn main:app --reload
```
Abre http://127.0.0.1:8000/docs. Para probar en /docs: haz `POST /auth/login`, copia `access_token` y pégalo en el botón **Authorize**
(o pon `AUTH_OBLIGATORIA=false` en el .env mientras pruebas).

## Base de datos local
Mismo código, solo cambia el .env: `DB_HOST=localhost`, `DB_NAME=...`, `DB_USER=postgres`, `DB_SSLMODE=disable`.

## Correo (Gmail)
Activa la verificación en 2 pasos en la cuenta, crea una *contraseña de aplicación* y ponla en `SMTP_PASSWORD` (con `SMTP_USER` = el correo).

## Contrato para el frontend
Ver [CONTRATO_API.md](CONTRATO_API.md).
