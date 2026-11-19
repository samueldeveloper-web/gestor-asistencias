r"""
Inspección de solo lectura de la base de datos en Neon (PostgreSQL).

Uso (PowerShell, dentro de la carpeta proyecto_cul):
    pip install psycopg2-binary
    $env:DATABASE_URL = "postgresql://usuario:clave@host.neon.tech/neondb?sslmode=require"
    python herramientas\inspeccionar_bd.py

Genera herramientas\reporte_bd.md con: tablas, columnas, llaves, UNIQUE,
FKs, triggers, funciones, conteo de filas y 3 filas de ejemplo por tabla.
No modifica nada (la sesión se abre en modo READ ONLY).
Las columnas que parecen contraseñas se ocultan en los ejemplos.
"""
import os
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("Falta la variable de entorno DATABASE_URL (cadena de conexión de Neon).")

conn = psycopg2.connect(url)
conn.set_session(readonly=True, autocommit=True)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
out = []
w = out.append

def q(sql, params=None):
    cur.execute(sql, params)
    return cur.fetchall()

w("# Reporte de la base de datos\n")
w(f"Servidor: {q('select version()')[0]['version']}\n")

tablas = [r["table_name"] for r in q("""
    select table_name from information_schema.tables
    where table_schema='public' and table_type='BASE TABLE' order by table_name""")]
w(f"Tablas ({len(tablas)}): " + ", ".join(tablas) + "\n")

for t in tablas:
    w(f"\n## {t}\n")
    cols = q("""select column_name, data_type, is_nullable, column_default
                from information_schema.columns
                where table_schema='public' and table_name=%s order by ordinal_position""", (t,))
    w("| columna | tipo | nulo | default |\n|---|---|---|---|")
    for c in cols:
        w(f"| {c['column_name']} | {c['data_type']} | {c['is_nullable']} | {c['column_default'] or ''} |")
    cons = q("""select conname, pg_get_constraintdef(c.oid) as def
                from pg_constraint c join pg_class r on r.oid=c.conrelid
                join pg_namespace n on n.oid=r.relnamespace
                where n.nspname='public' and r.relname=%s order by contype, conname""", (t,))
    if cons:
        w("\nRestricciones:")
        for c in cons:
            w(f"- `{c['conname']}`: {c['def']}")
    idx = q("""select indexname, indexdef from pg_indexes
               where schemaname='public' and tablename=%s""", (t,))
    if idx:
        w("\nÍndices:")
        for i in idx:
            w(f"- {i['indexdef']}")
    trg = q("""select tgname, pg_get_triggerdef(t.oid) as def from pg_trigger t
               join pg_class r on r.oid=t.tgrelid where r.relname=%s and not t.tgisinternal""", (t,))
    if trg:
        w("\nTriggers:")
        for g in trg:
            w(f"- {g['def']}")
    n = q(f'select count(*) as n from public."{t}"')[0]["n"]
    w(f"\nFilas: **{n}**")
    if n:
        filas = q(f'select * from public."{t}" limit 3')
        w("\nEjemplo:")
        for f in filas:
            limpio = {k: ("***" if any(s in k.lower() for s in ("pass", "clave", "hash", "token")) else v)
                      for k, v in f.items()}
            w(f"- {limpio}")

w("\n## Funciones (public)\n")
for f in q("""select p.proname, pg_get_functiondef(p.oid) as def from pg_proc p
              join pg_namespace n on n.oid=p.pronamespace
              where n.nspname='public' and p.prokind='f' order by p.proname"""):
    w(f"### {f['proname']}\n```sql\n{f['def']}\n```")

w("\n## Vistas\n")
for v in q("select table_name from information_schema.views where table_schema='public'"):
    w(f"- {v['table_name']}")

destino = Path(__file__).with_name("reporte_bd.md")
destino.write_text("\n".join(out), encoding="utf-8")
print(f"Listo: {destino}")
