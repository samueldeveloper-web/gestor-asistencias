"""
Consultas de los reportes (SQL puro). Cada reporte une 3 o más tablas y nunca
devuelve IDs: solo nombres, documentos, fechas y estados.
El alcance depende del rol de quien consulta (datos del token JWT):
  Docente    -> asistencia de sus cargas académicas
  Acudiente  -> sus estudiantes asociados
  Estudiante -> su propia asistencia
  Administrador -> todo
"""
from app.repositories.base_repo import BaseRepository

# Docente de la clase: el que registró la asistencia o, si falta, el de la carga académica
_DOCENTE = """
    LEFT JOIN LATERAL (
        SELECT p.nombres || ' ' || p.apellidos AS nombre
        FROM personal_institucional p
        WHERE p.personalid = COALESCE(a.personal_institucionalid, (
            SELECT ca.personal_institucionalid FROM carga_academica ca
            WHERE ca.cursoid = a.cursoid AND ca.materiaid = a.materiaid
              AND ca.esta_activo IS NOT FALSE
            ORDER BY ca.anio_lectivo DESC LIMIT 1))
    ) doc ON TRUE
"""

_ACUDIENTE_PRINCIPAL = """
    LEFT JOIN LATERAL (
        SELECT ac.nombres || ' ' || ac.apellidos AS nombre, ac.telefono, ac.email
        FROM estudiante_acudiente ea
        JOIN acudientes ac ON ac.acudiente_id = ea.acudienteid
        WHERE ea.estudianteid = e.estudiante_id AND ea.esta_activo IS NOT FALSE
        ORDER BY ea.contacto_principal DESC, ea.estudiante_acudienteid
        LIMIT 1
    ) acu ON TRUE
"""


class ReporteRepository(BaseRepository):
    TABLA = "asistencia"
    PK = "asistenciaid"
    RECURSO = "Reporte"

    # ------------------------------------------------------------- filtros comunes
    @staticmethod
    def _condiciones(filtros: dict, usuario: dict | None, alias_fecha: str = "a.fecha",
                     con_materia: bool = True) -> tuple[list[str], list]:
        condiciones = [f"{alias_fecha} BETWEEN %s AND %s", "a.esta_activo IS NOT FALSE"]
        parametros: list = [filtros["fecha_inicio"], filtros["fecha_fin"]]
        if filtros.get("cursoid"):
            condiciones.append("a.cursoid = %s")
            parametros.append(filtros["cursoid"])
        if con_materia and filtros.get("materiaid"):
            condiciones.append("a.materiaid = %s")
            parametros.append(filtros["materiaid"])
        if filtros.get("estudianteid"):
            condiciones.append("a.estudianteid = %s")
            parametros.append(filtros["estudianteid"])
        if filtros.get("estado"):
            condiciones.append("a.estado = %s")
            parametros.append(filtros["estado"])

        rol = str((usuario or {}).get("rol") or "").lower()
        perfil = (usuario or {}).get("perfil") or {}
        id_perfil = perfil.get("id")
        if rol.startswith("docente"):
            condiciones.append("""(a.personal_institucionalid = %s OR EXISTS (
                SELECT 1 FROM carga_academica ca WHERE ca.cursoid = a.cursoid
                AND ca.materiaid = a.materiaid AND ca.personal_institucionalid = %s
                AND ca.esta_activo IS NOT FALSE))""")
            parametros += [id_perfil, id_perfil]
        elif rol.startswith("acudiente"):
            condiciones.append("""EXISTS (SELECT 1 FROM estudiante_acudiente ea
                WHERE ea.estudianteid = a.estudianteid AND ea.acudienteid = %s
                AND ea.esta_activo IS NOT FALSE)""")
            parametros.append(id_perfil)
        elif rol.startswith("estudiante"):
            condiciones.append("a.estudianteid = %s")
            parametros.append(id_perfil)
        return condiciones, parametros

    # ------------------------------------------------------------- reportes
    def detalle_asistencia(self, filtros: dict, usuario: dict | None) -> list[dict]:
        """Asistencia registro por registro: asistencia + estudiantes + cursos + asignaturas + docente."""
        condiciones, parametros = self._condiciones(filtros, usuario)
        consulta = f"""
            SELECT to_char(a.fecha, 'DD/MM/YYYY') AS fecha,
                   e.nombres || ' ' || e.apellidos AS estudiante,
                   e.documento_identidad AS documento,
                   c.nombre_curso AS curso,
                   m.nombre_materia AS asignatura,
                   COALESCE(doc.nombre, 'Sin asignar') AS docente,
                   a.estado
            FROM asistencia a
            JOIN estudiantes e ON e.estudiante_id = a.estudianteid
            JOIN cursos c ON c.cursoid = a.cursoid
            JOIN asignaturas m ON m.materiaid = a.materiaid
            {_DOCENTE}
            WHERE {' AND '.join(condiciones)}
            ORDER BY a.fecha DESC, c.nombre_curso, e.apellidos, e.nombres, m.nombre_materia
        """
        return self.ejecutar(consulta, parametros, todos=True) or []

    def consolidado_estudiantes(self, filtros: dict, usuario: dict | None) -> list[dict]:
        """Totales por estudiante: asistencia + estudiantes + cursos + acudientes (contacto principal)."""
        condiciones, parametros = self._condiciones(filtros, usuario)
        consulta = f"""
            SELECT e.nombres || ' ' || e.apellidos AS estudiante,
                   e.documento_identidad AS documento,
                   c.nombre_curso AS curso,
                   COALESCE(acu.nombre, 'Sin acudiente') AS acudiente,
                   COALESCE(acu.telefono, '') AS telefono_acudiente,
                   COUNT(*) FILTER (WHERE a.estado = 'presente') AS presentes,
                   COUNT(*) FILTER (WHERE a.estado = 'ausente')  AS ausencias,
                   COUNT(*) FILTER (WHERE a.estado = 'tarde')    AS tardes,
                   COUNT(*) FILTER (WHERE a.estado = 'excusado') AS excusados,
                   COUNT(*) AS total,
                   ROUND(100.0 * COUNT(*) FILTER (WHERE a.estado IN ('presente', 'tarde'))
                         / NULLIF(COUNT(*), 0), 1) AS porcentaje_asistencia
            FROM asistencia a
            JOIN estudiantes e ON e.estudiante_id = a.estudianteid
            JOIN cursos c ON c.cursoid = a.cursoid
            {_ACUDIENTE_PRINCIPAL}
            WHERE {' AND '.join(condiciones)}
            GROUP BY e.estudiante_id, e.nombres, e.apellidos, e.documento_identidad,
                     c.nombre_curso, acu.nombre, acu.telefono
            ORDER BY ausencias DESC, c.nombre_curso, estudiante
        """
        filas = self.ejecutar(consulta, parametros, todos=True) or []
        for f in filas:
            f["porcentaje_asistencia"] = float(f["porcentaje_asistencia"] or 0)
        return filas

    def notificaciones_fallas(self, filtros: dict, usuario: dict | None) -> list[dict]:
        """Notificaciones (fallas y excusas) enviadas a acudientes: notificaciones + acudientes + estudiantes + asistencia + cursos."""
        condiciones, parametros = self._condiciones(filtros, usuario)
        consulta = f"""
            SELECT to_char(n.fecha_envio, 'DD/MM/YYYY HH24:MI') AS fecha_envio,
                   ac.nombres || ' ' || ac.apellidos AS acudiente,
                   ac.email AS correo_acudiente,
                   e.nombres || ' ' || e.apellidos AS estudiante,
                   c.nombre_curso AS curso,
                   to_char(a.fecha, 'DD/MM/YYYY') AS fecha_falla,
                   initcap(n.tipo) AS tipo,
                   n.titulo,
                   CASE WHEN n.enviado_correo THEN 'Enviado' ELSE 'Pendiente' END AS correo,
                   CASE WHEN n.leido THEN 'Leída' ELSE 'No leída' END AS lectura
            FROM notificaciones n
            JOIN acudientes ac ON ac.acudiente_id = n.acudienteid
            JOIN asistencia a ON a.asistenciaid = n.asistenciaid
            JOIN estudiantes e ON e.estudiante_id = a.estudianteid
            JOIN cursos c ON c.cursoid = a.cursoid
            WHERE n.esta_activo IS NOT FALSE AND {' AND '.join(condiciones)}
            ORDER BY n.fecha_envio DESC
        """
        return self.ejecutar(consulta, parametros, todos=True) or []

    # ------------------------------------------------------------- textos de filtros
    def descripcion_filtros(self, filtros: dict) -> list[tuple[str, str]]:
        """Convierte los filtros en texto legible (nombres, no IDs) para el encabezado."""
        texto = [("Rango de fechas",
                  f"{filtros['fecha_inicio']:%d/%m/%Y} a {filtros['fecha_fin']:%d/%m/%Y}")]
        buscar = [
            ("cursoid", "Curso", "SELECT nombre_curso AS n FROM cursos WHERE cursoid = %s"),
            ("materiaid", "Asignatura", "SELECT nombre_materia AS n FROM asignaturas WHERE materiaid = %s"),
            ("estudianteid", "Estudiante",
             "SELECT nombres || ' ' || apellidos AS n FROM estudiantes WHERE estudiante_id = %s"),
        ]
        for campo, etiqueta, consulta in buscar:
            if filtros.get(campo):
                fila = self.ejecutar(consulta, (filtros[campo],), uno=True)
                texto.append((etiqueta, fila["n"] if fila else "—"))
        if filtros.get("estado"):
            texto.append(("Estado", str(filtros["estado"]).capitalize()))
        return texto
