r"""
Ejecuta uno o varios archivos .sql contra la base indicada en DATABASE_URL
(Neon o local) y muestra los avisos y el resultado de la última consulta.

Uso (PowerShell, dentro de la carpeta proyecto_cul):
    pip install psycopg2-binary
    $env:DATABASE_URL = "postgresql://usuario:clave@host.neon.tech/neondb?sslmode=require"
    python bd\ejecutar_sql.py bd\migrations\003_completar_estructura.sql bd\migrations\004_falla_genera_notificacion.sql bd\migrations\005_modulos_y_permisos.sql bd\seed.sql bd\migrations\006_vistas_tablero.sql

Cada archivo trae su propio BEGIN/COMMIT: si algo falla, ese archivo se
revierte completo y el script se detiene sin ejecutar los siguientes.
"""
import os
import sys
from pathlib import Path

import psycopg2

url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("Falta la variable de entorno DATABASE_URL.")
if len(sys.argv) < 2:
    sys.exit("Indica al menos un archivo .sql.")

conn = psycopg2.connect(url)
conn.autocommit = True  # los archivos manejan su propia transacción
cur = conn.cursor()

for nombre in sys.argv[1:]:
    ruta = Path(nombre)
    print(f"\n=== {ruta.name}")
    try:
        cur.execute(ruta.read_text(encoding="utf-8"))
    except psycopg2.Error as e:
        if conn.status != psycopg2.extensions.STATUS_READY:
            conn.rollback()
        cur.execute("ROLLBACK")  # por si la transacción del archivo quedó abierta
        sys.exit(f"ERROR en {ruta.name}: {e.pgerror or e}\nNo se aplicó ningún cambio de este archivo.")
    for aviso in conn.notices:
        if "skipping" not in aviso and "ya existe" not in aviso:
            print("  " + aviso.strip())
    conn.notices.clear()
    if cur.description:
        columnas = [c.name for c in cur.description]
        print("  " + " | ".join(columnas))
        for fila in cur.fetchall():
            print("  " + " | ".join("" if v is None else str(v) for v in fila))
    print("  OK")

conn.close()
