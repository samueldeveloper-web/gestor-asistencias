import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Carga las variables del archivo .env al entorno de Python
load_dotenv()


class Database:
    """Entrega conexiones a PostgreSQL (Neon o local) leyendo el archivo .env."""

    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT", "5432")
        # Neon exige SSL; para la versión local se puede poner DB_SSLMODE=disable
        self.sslmode = os.getenv("DB_SSLMODE", "require")

    def get_connection(self):
        try:
            return psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                sslmode=self.sslmode,
                cursor_factory=RealDictCursor,
                connect_timeout=10,
            )
        except Exception as e:
            print(f"Error de conexión a la BD: {e}")
            return None
