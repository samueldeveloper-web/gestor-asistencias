-- Vistas para el tablero de Power BI (Corte 3).
-- Power BI se conecta a Neon y lee estas vistas: datos ya unidos y sin IDs visibles.
-- Ejecutable más de una vez (CREATE OR REPLACE). No modifica tablas.

BEGIN;

-- Una fila por registro de asistencia, con nombres de estudiante, curso, asignatura y docente.
CREATE OR REPLACE VIEW vw_tablero_asistencia AS
SELECT a.fecha,
       EXTRACT(YEAR FROM a.fecha)::int  AS anio,
       EXTRACT(MONTH FROM a.fecha)::int AS mes,
       (ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])[EXTRACT(MONTH FROM a.fecha)::int] AS nombre_mes,
       EXTRACT(ISODOW FROM a.fecha)::int AS dia_semana,
       e.nombres || ' ' || e.apellidos  AS estudiante,
       c.nombre_curso                   AS curso,
       c.nivel_educativo,
       m.nombre_materia                 AS asignatura,
       COALESCE(p.nombres || ' ' || p.apellidos, 'Sin asignar') AS docente,
       a.estado,
       CASE WHEN a.estado = 'ausente' THEN 1 ELSE 0 END AS es_falla,
       CASE WHEN a.estado IN ('presente', 'tarde') THEN 1 ELSE 0 END AS asistio
FROM asistencia a
JOIN estudiantes e ON e.estudiante_id = a.estudianteid
JOIN cursos c      ON c.cursoid = a.cursoid
JOIN asignaturas m ON m.materiaid = a.materiaid
LEFT JOIN personal_institucional p ON p.personalid = a.personal_institucionalid
WHERE a.esta_activo IS NOT FALSE;

-- Notificaciones a acudientes: enviadas por correo y leídas.
CREATE OR REPLACE VIEW vw_tablero_notificaciones AS
SELECT n.fecha_envio::date               AS fecha,
       n.tipo,
       ac.nombres || ' ' || ac.apellidos AS acudiente,
       e.nombres || ' ' || e.apellidos   AS estudiante,
       CASE WHEN n.enviado_correo THEN 1 ELSE 0 END AS enviada_correo,
       CASE WHEN n.leido THEN 1 ELSE 0 END          AS leida
FROM notificaciones n
JOIN acudientes ac ON ac.acudiente_id = n.acudienteid
LEFT JOIN estudiantes e ON e.estudiante_id = n.estudianteid
WHERE n.esta_activo IS NOT FALSE;

-- Excusas presentadas por los acudientes y su resultado.
CREATE OR REPLACE VIEW vw_tablero_excusas AS
SELECT COALESCE(x.fecha_presentacion, x.fecha_creacion)::date AS fecha,
       x.estado                                             AS estado_revision,
       e.nombres || ' ' || e.apellidos                      AS estudiante,
       c.nombre_curso                                       AS curso
FROM excusas x
JOIN asistencia a  ON a.asistenciaid = x.asistenciaid
JOIN estudiantes e ON e.estudiante_id = x.estudianteid
JOIN cursos c      ON c.cursoid = a.cursoid;

-- Enlace del tablero publicado (lo cambia el administrador desde /tablero).
INSERT INTO configuracion_institucional (clave, valor)
VALUES ('tablero_powerbi_url', '')
ON CONFLICT (clave) DO NOTHING;

COMMIT;

SELECT 'vw_tablero_asistencia' AS vista, COUNT(*) FROM vw_tablero_asistencia
UNION ALL SELECT 'vw_tablero_notificaciones', COUNT(*) FROM vw_tablero_notificaciones
UNION ALL SELECT 'vw_tablero_excusas', COUNT(*) FROM vw_tablero_excusas;
