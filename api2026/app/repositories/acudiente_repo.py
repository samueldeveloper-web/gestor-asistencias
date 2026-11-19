from psycopg2 import sql

from app.repositories.base_repo import BaseRepository
from app.repositories.estudiante_acudiente_repo import EstudianteAcudienteRepository
from app.repositories.estudiante_repo import EstudianteRepository


class AcudienteRepository(BaseRepository):
    TABLA = ("acudientes", "acudiente")
    PK = "acudiente_id"
    RECURSO = "Acudiente"

    def estudiantes_de(self, acudiente_id: int):
        """Estudiantes vinculados al acudiente (para el módulo 'mis hijos')."""
        self.obtener_por_id(acudiente_id)
        ea = EstudianteAcudienteRepository().esquema()
        es = EstudianteRepository().esquema()
        condiciones = [sql.SQL("ea.acudienteid = %s")]
        if ea["estado"]:
            condiciones.append(sql.SQL("ea.{} IS TRUE").format(sql.Identifier(ea["estado"])))
        consulta = sql.SQL("""SELECT e.*, ea.{} AS estudiante_acudienteid, ea.parentesco, ea.contacto_principal
                              FROM {} ea JOIN {} e ON e.{} = ea.estudianteid
                              WHERE {} ORDER BY e.apellidos, e.nombres""").format(
            sql.Identifier(ea["pk"]), sql.Identifier(ea["tabla"]), sql.Identifier(es["tabla"]),
            sql.Identifier(es["pk"]), sql.SQL(" AND ").join(condiciones))
        return self.ejecutar(consulta, (acudiente_id,), todos=True)
