from psycopg2 import sql

from app.repositories.base_repo import BaseRepository
from app.repositories.modulo_por_rol_repo import ModuloPorRolRepository
from app.repositories.modulo_repo import ModuloRepository


class RolRepository(BaseRepository):
    TABLA = ("rol", "roles")
    PK = "rolid"
    RECURSO = "Rol"

    def modulos_de_rol(self, rolid: int):
        """Módulos activos que el rol puede ver, leídos solo de la BD (modulo_por_rol)."""
        self.obtener_por_id(rolid)  # 404 si el rol no existe
        mpr = ModuloPorRolRepository().esquema()
        mod = ModuloRepository().esquema()
        fk_rol = "rolid" if "rolid" in mpr["columnas"] else "rol_id"
        fk_mod = "moduloid" if "moduloid" in mpr["columnas"] else "modulo_id"
        condiciones = [sql.SQL("mr.{} = %s").format(sql.Identifier(fk_rol))]
        if "permiso_leer" in mpr["columnas"]:
            condiciones.append(sql.SQL("mr.permiso_leer IS TRUE"))
        if mpr["estado"]:
            condiciones.append(sql.SQL("mr.{} IS TRUE").format(sql.Identifier(mpr["estado"])))
        if mod["estado"]:
            condiciones.append(sql.SQL("m.{} IS TRUE").format(sql.Identifier(mod["estado"])))
        permisos = [c for c in ("permiso_crear", "permiso_leer", "permiso_actualizar", "permiso_eliminar")
                    if c in mpr["columnas"]]
        columnas_mod = [c for c in ("nombre", "ruta", "descripcion", "icono", "orden") if c in mod["columnas"]]
        seleccion = [sql.SQL("m.{} AS moduloid").format(sql.Identifier(mod["pk"]))]
        seleccion += [sql.SQL("m.{}").format(sql.Identifier(c)) for c in columnas_mod]
        seleccion += [sql.SQL("mr.{}").format(sql.Identifier(c)) for c in permisos]
        consulta = sql.SQL("""SELECT {} FROM {} mr JOIN {} m ON m.{} = mr.{}
                              WHERE {} ORDER BY {}""").format(
            sql.SQL(", ").join(seleccion),
            sql.Identifier(mpr["tabla"]), sql.Identifier(mod["tabla"]),
            sql.Identifier(mod["pk"]), sql.Identifier(fk_mod),
            sql.SQL(" AND ").join(condiciones),
            sql.SQL("m.orden, m.{}").format(sql.Identifier(mod["pk"])) if "orden" in mod["columnas"]
            else sql.SQL("m.{}").format(sql.Identifier(mod["pk"])))
        return self.ejecutar(consulta, (rolid,), todos=True)
