from psycopg2 import sql

from app.core.security import COLUMNAS_PASSWORD, encriptar_password
from app.repositories.base_repo import BaseRepository
from app.repositories.utilidades import COLUMNAS_CORREO, primera


class UsuarioRepository(BaseRepository):
    TABLA = ("usuarios", "usuario")
    PK = "usuarioid"
    RECURSO = "Usuario"

    # ---- la contraseña nunca sale de la API y siempre se guarda encriptada
    def columna_password(self):
        return primera(self.esquema()["columnas"], COLUMNAS_PASSWORD)

    def _limpiar(self, fila):
        if fila is None:
            return None
        return {k: v for k, v in fila.items() if k not in COLUMNAS_PASSWORD}

    def _preparar(self, datos: dict) -> dict:
        datos = dict(datos)
        col = self.columna_password()
        clave = None
        for nombre in ("password", *COLUMNAS_PASSWORD):
            if datos.get(nombre):
                clave = datos.pop(nombre)
        if clave and col:
            datos[col] = encriptar_password(clave)
        return datos

    def obtener_todos(self, solo_activos=True, filtros=None):
        return [self._limpiar(f) for f in super().obtener_todos(solo_activos, filtros)]

    def obtener_por_id(self, id_registro):
        return self._limpiar(super().obtener_por_id(id_registro))

    def crear(self, datos):
        return self._limpiar(super().crear(self._preparar(datos)))

    def actualizar(self, id_registro, datos):
        return self._limpiar(super().actualizar(id_registro, self._preparar(datos)))

    def cambiar_estado(self, id_registro, activo):
        return self._limpiar(super().cambiar_estado(id_registro, activo))

    # ---- login
    def buscar_para_login(self, identificador: str):
        """Busca por usuario o correo (sin distinguir mayúsculas). Incluye la contraseña guardada."""
        e = self.esquema()
        columnas = [c for c in ("username", "usuario", "nombre_usuario", *COLUMNAS_CORREO) if c in e["columnas"]]
        if not columnas:
            return None
        condicion = sql.SQL(" OR ").join(
            sql.SQL("LOWER({}::text) = LOWER(%s)").format(sql.Identifier(c)) for c in columnas)
        consulta = sql.SQL("SELECT * FROM {} WHERE {} LIMIT 1").format(sql.Identifier(e["tabla"]), condicion)
        return self.ejecutar(consulta, [identificador] * len(columnas), uno=True)
