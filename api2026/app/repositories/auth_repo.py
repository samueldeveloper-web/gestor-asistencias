"""Datos que necesita el login: usuario, rol, módulos y perfil (estudiante/acudiente/docente)."""
from psycopg2 import sql

from app.repositories.acudiente_repo import AcudienteRepository
from app.repositories.base_repo import BaseRepository
from app.repositories.estudiante_repo import EstudianteRepository
from app.repositories.personal_institucion_repo import PersonalInstitucionRepository
from app.repositories.utilidades import COLUMNAS_CORREO, COLUMNAS_FK_USUARIO, primera

# (tipo de perfil, repositorio, columna en la tabla usuario que apunta al perfil)
PERFILES = (("acudiente", AcudienteRepository, "acudienteid"),
            ("docente", PersonalInstitucionRepository, "personal_institucionalid"),
            ("estudiante", EstudianteRepository, "estudianteid"))


class AuthRepository(BaseRepository):
    TABLA = ("usuarios", "usuario")
    PK = "usuarioid"

    def perfil_de(self, usuario: dict) -> dict | None:
        """Busca la fila de acudiente, docente o estudiante ligada al usuario. Primero por
        usuario.acudienteid / personal_institucionalid / estudianteid; si no, por usuarioid o correo."""
        usuario_pk = self.esquema()["pk"]
        correo = usuario.get(primera(usuario.keys(), COLUMNAS_CORREO) or "")
        for tipo, Repo, col_usuario in PERFILES:
            repo = Repo()
            try:
                e = repo.esquema()
            except Exception:
                continue
            if usuario.get(col_usuario) is not None:
                fila = self._buscar(e, e["pk"], usuario[col_usuario])
                if fila:
                    return self._perfil(tipo, e, fila)
        for tipo, Repo, _ in PERFILES:
            try:
                e = Repo().esquema()
            except Exception:
                continue
            col_fk = primera(e["columnas"], COLUMNAS_FK_USUARIO)
            col_correo = primera(e["columnas"], COLUMNAS_CORREO)
            fila = None
            if col_fk:
                fila = self.ejecutar(sql.SQL("SELECT * FROM {} WHERE {} = %s LIMIT 1").format(
                    sql.Identifier(e["tabla"]), sql.Identifier(col_fk)), (usuario[usuario_pk],), uno=True)
            elif col_correo and correo:
                fila = self.ejecutar(sql.SQL("SELECT * FROM {} WHERE LOWER({}) = LOWER(%s) LIMIT 1").format(
                    sql.Identifier(e["tabla"]), sql.Identifier(col_correo)), (correo,), uno=True)
            if fila:
                return self._perfil(tipo, e, fila)
        return None

    def _buscar(self, e, columna, valor):
        return self.ejecutar(sql.SQL("SELECT * FROM {} WHERE {} = %s LIMIT 1").format(
            sql.Identifier(e["tabla"]), sql.Identifier(columna)), (valor,), uno=True)

    @staticmethod
    def _perfil(tipo, e, fila):
        return {"tipo": tipo, "id": fila[e["pk"]],
                "nombre": f"{fila.get('nombres', '')} {fila.get('apellidos', '')}".strip()}

    def registrar_ingreso(self, usuarioid: int):
        e = self.esquema()
        if "ultimo_ingreso" in e["columnas"]:
            self.ejecutar(sql.SQL("UPDATE {} SET ultimo_ingreso = CURRENT_TIMESTAMP WHERE {} = %s").format(
                sql.Identifier(e["tabla"]), sql.Identifier(e["pk"])), (usuarioid,), escribir=True)
