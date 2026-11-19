"""
Repositorio base con SQL puro (psycopg2). Cada tabla tiene su propio repositorio
(<tabla>_repo.py) que hereda de esta clase y declara:

    TABLA     nombre de la tabla en PostgreSQL (o una tupla de nombres posibles)
    PK        columna llave primaria
    RECURSO   nombre en singular para los mensajes de error

Al primer uso se leen de information_schema las columnas reales de la tabla,
así solo se insertan/actualizan columnas que existen en la BD y el borrado
lógico usa la columna de estado que tenga la tabla.
"""
from psycopg2 import Error as ErrorPostgres
from psycopg2 import sql

from app.core.database import Database
from app.core.excepciones import (BaseDatosNoDisponible, DatosInvalidos,
                                  RecursoNoEncontrado, traducir_error_bd)

COLUMNAS_ESTADO = ("esta_activo", "estado_registro", "activo", "estado")
COLUMNAS_CREADO = ("fecha_creacion", "creado", "created_at")
COLUMNAS_ACTUALIZADO = ("fecha_actualizacion", "actualizado", "updated_at")

_cache_esquema: dict = {}


class BaseRepository:
    TABLA: str | tuple = ""
    PK: str = "id"
    RECURSO: str = "Registro"
    ORDEN: str | None = None  # columna para ORDER BY (por defecto la PK)

    def __init__(self):
        # Composición: el repositorio instancia su propia conexión
        self.db = Database()

    # ------------------------------------------------------------------ conexión
    def _conectar(self):
        conn = self.db.get_connection()
        if conn is None:
            raise BaseDatosNoDisponible()
        return conn

    def ejecutar(self, consulta, parametros=None, uno=False, todos=False, escribir=False):
        """Ejecuta SQL y traduce los errores de PostgreSQL a errores HTTP."""
        conn = self._conectar()
        try:
            with conn.cursor() as cursor:
                cursor.execute(consulta, parametros)
                resultado = None
                if uno:
                    resultado = cursor.fetchone()
                elif todos:
                    resultado = cursor.fetchall()
            if escribir:
                conn.commit()
            return resultado
        except ErrorPostgres as e:
            conn.rollback()
            raise traducir_error_bd(e) from e
        finally:
            conn.close()

    # ------------------------------------------------------------------ esquema
    def esquema(self) -> dict:
        """Devuelve {'tabla', 'pk', 'columnas', 'estado', 'creado', 'actualizado'} de la tabla real."""
        clave = (self.__class__.__name__,)
        if clave in _cache_esquema:
            return _cache_esquema[clave]
        candidatas = self.TABLA if isinstance(self.TABLA, tuple) else (self.TABLA,)
        filas = self.ejecutar(
            """SELECT table_name, column_name FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = ANY(%s)
               ORDER BY ordinal_position""", (list(candidatas),), todos=True)
        por_tabla: dict[str, list[str]] = {}
        for f in filas:
            por_tabla.setdefault(f["table_name"], []).append(f["column_name"])
        tabla = next((t for t in candidatas if t in por_tabla), None)
        if tabla is None:
            raise DatosInvalidos(f"La tabla {candidatas[0]} no existe en la base de datos.")
        columnas = por_tabla[tabla]
        pk_real = self.ejecutar(
            """SELECT a.attname AS columna FROM pg_index i
               JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
               WHERE i.indrelid = %s::regclass AND i.indisprimary""", (f'public."{tabla}"',), uno=True)
        info = {
            "tabla": tabla,
            "pk": pk_real["columna"] if pk_real else self.PK,
            "columnas": columnas,
            "estado": next((c for c in COLUMNAS_ESTADO if c in columnas), None),
            "creado": next((c for c in COLUMNAS_CREADO if c in columnas), None),
            "actualizado": next((c for c in COLUMNAS_ACTUALIZADO if c in columnas), None),
        }
        # Columnas de texto como asistencia.estado o matriculas.estado no son borrado lógico
        if info["estado"] == "estado" and "esta_activo" not in columnas:
            tipo = self.ejecutar(
                """SELECT data_type FROM information_schema.columns
                   WHERE table_schema='public' AND table_name=%s AND column_name='estado'""",
                (tabla,), uno=True)
            if tipo and tipo["data_type"] != "boolean":
                info["estado"] = None
        _cache_esquema[clave] = info
        return info

    def _ident(self, nombre):
        return sql.Identifier(nombre)

    def _datos_validos(self, datos: dict) -> dict:
        """Deja solo columnas que existen y que el usuario puede escribir."""
        e = self.esquema()
        prohibidas = {e["pk"], e["creado"], e["actualizado"]}
        return {k: v for k, v in datos.items() if k in e["columnas"] and k not in prohibidas}

    # ------------------------------------------------------------------ CRUD
    def obtener_todos(self, solo_activos: bool = True, filtros: dict | None = None):
        e = self.esquema()
        condiciones, valores = [], []
        if solo_activos and e["estado"]:
            condiciones.append(sql.SQL("{} IS NOT FALSE").format(self._ident(e["estado"])))  # NULL cuenta como activo
        for columna, valor in (filtros or {}).items():
            if columna in e["columnas"]:
                condiciones.append(sql.SQL("{}::text = %s").format(self._ident(columna)))
                valores.append(str(valor).lower() if isinstance(valor, bool) else str(valor))
        where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(condiciones) if condiciones else sql.SQL("")
        consulta = sql.SQL("SELECT * FROM {} {} ORDER BY {} ASC").format(
            self._ident(e["tabla"]), where, self._ident(self.ORDEN or e["pk"]))
        return self.ejecutar(consulta, valores, todos=True)

    def obtener_por_id(self, id_registro: int):
        e = self.esquema()
        consulta = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
            self._ident(e["tabla"]), self._ident(e["pk"]))
        fila = self.ejecutar(consulta, (id_registro,), uno=True)
        if not fila:
            raise RecursoNoEncontrado(self.RECURSO)
        return fila

    def crear(self, datos: dict):
        e = self.esquema()
        datos = self._datos_validos(datos)
        if not datos:
            raise DatosInvalidos("No se enviaron campos válidos para esta tabla.")
        consulta = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            self._ident(e["tabla"]),
            sql.SQL(", ").join(map(self._ident, datos.keys())),
            sql.SQL(", ").join(sql.Placeholder() * len(datos)))
        return self.ejecutar(consulta, list(datos.values()), uno=True, escribir=True)

    def actualizar(self, id_registro: int, datos: dict):
        e = self.esquema()
        datos = self._datos_validos(datos)
        if not datos:
            raise DatosInvalidos("No se enviaron campos válidos para actualizar.")
        asignaciones = [sql.SQL("{} = %s").format(self._ident(k)) for k in datos]
        if e["actualizado"]:
            # Respaldo por si la tabla aún no tiene el trigger BEFORE UPDATE
            asignaciones.append(sql.SQL("{} = CURRENT_TIMESTAMP").format(self._ident(e["actualizado"])))
        consulta = sql.SQL("UPDATE {} SET {} WHERE {} = %s RETURNING *").format(
            self._ident(e["tabla"]), sql.SQL(", ").join(asignaciones), self._ident(e["pk"]))
        fila = self.ejecutar(consulta, [*datos.values(), id_registro], uno=True, escribir=True)
        if not fila:
            raise RecursoNoEncontrado(self.RECURSO)
        return fila

    def cambiar_estado(self, id_registro: int, activo: bool):
        e = self.esquema()
        if not e["estado"]:
            raise DatosInvalidos(f"La tabla {e['tabla']} no tiene columna de estado para borrado lógico.")
        return self.actualizar_columna_estado(id_registro, activo)

    def actualizar_columna_estado(self, id_registro: int, activo: bool):
        e = self.esquema()
        asignaciones = [sql.SQL("{} = %s").format(self._ident(e["estado"]))]
        if e["actualizado"]:
            asignaciones.append(sql.SQL("{} = CURRENT_TIMESTAMP").format(self._ident(e["actualizado"])))
        consulta = sql.SQL("UPDATE {} SET {} WHERE {} = %s RETURNING *").format(
            self._ident(e["tabla"]), sql.SQL(", ").join(asignaciones), self._ident(e["pk"]))
        fila = self.ejecutar(consulta, (activo, id_registro), uno=True, escribir=True)
        if not fila:
            raise RecursoNoEncontrado(self.RECURSO)
        return fila

    def eliminar(self, id_registro: int):
        """Borrado lógico: no se hace DELETE, se cambia el estado a FALSE."""
        return self.cambiar_estado(id_registro, False)
