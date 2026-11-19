-- Carga inicial de roles, módulos y permisos aprobados para Aula Presente.
-- Ejecutable más de una vez: actualiza roles/módulos existentes y aplica
-- permisos por pareja rol-módulo sin crear filas duplicadas.
-- Este script NO implementa autenticación ni protege las rutas de la API.
-- Las rutas /excusas, /notificaciones y /carga-academica se definen aquí
-- para la matriz; sus pantallas de frontend se completarán posteriormente.

BEGIN;

INSERT INTO rol (nombre, descripcion, esta_activo)
VALUES
    ('Administrador', 'Administra la operación y configuración institucional.', TRUE),
    ('Estudiante', 'Consulta su información académica y de asistencia.', TRUE),
    ('Acudiente', 'Consulta información de los estudiantes que tiene asociados.', TRUE)
ON CONFLICT (nombre) DO UPDATE
SET descripcion = EXCLUDED.descripcion,
    esta_activo = TRUE,
    fecha_actualizacion = CURRENT_TIMESTAMP;

INSERT INTO modulo (nombre, ruta, descripcion, esta_activo)
VALUES
    ('Inicio', '/dashboard', 'Resumen personalizado según el rol.', TRUE),
    ('Asistencia', '/registros', 'Registro y consulta de asistencia.', TRUE),
    ('Estudiantes y acudientes', '/usuarios', 'Perfiles y vínculos entre estudiantes y acudientes.', TRUE),
    ('Excusas', '/excusas', 'Registro y revisión de excusas.', TRUE),
    ('Notificaciones', '/notificaciones', 'Consulta y gestión de notificaciones.', TRUE),
    ('Reportes', '/reportes', 'Consulta de reportes según el alcance del rol.', TRUE),
    ('Configuración', '/configuracion', 'Parámetros institucionales.', TRUE),
    ('Cursos y carga académica', '/carga-academica', 'Cursos, asignaturas y asignaciones docentes.', TRUE)
ON CONFLICT (ruta) DO UPDATE
SET nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    esta_activo = TRUE,
    fecha_actualizacion = CURRENT_TIMESTAMP;

WITH permisos(nombre_rol, ruta_modulo, puede_crear, puede_leer, puede_actualizar, puede_eliminar) AS (
    VALUES
    -- Administrador: gestiona módulos; los registros históricos no se borran.
    ('Administrador', '/dashboard', FALSE, TRUE, FALSE, FALSE),
    ('Administrador', '/registros', TRUE, TRUE, TRUE, FALSE),
    ('Administrador', '/usuarios', TRUE, TRUE, TRUE, FALSE),
    ('Administrador', '/excusas', FALSE, TRUE, TRUE, FALSE),
    ('Administrador', '/notificaciones', TRUE, TRUE, TRUE, FALSE),
    ('Administrador', '/reportes', FALSE, TRUE, FALSE, FALSE),
    ('Administrador', '/configuracion', FALSE, TRUE, TRUE, FALSE),
    ('Administrador', '/carga-academica', TRUE, TRUE, TRUE, FALSE),

    -- Estudiante: permisos de lectura; la API deberá limitar los datos al propio estudiante.
    ('Estudiante', '/dashboard', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/registros', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/usuarios', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/excusas', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/notificaciones', FALSE, FALSE, FALSE, FALSE),
    ('Estudiante', '/reportes', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/configuracion', FALSE, FALSE, FALSE, FALSE),
    ('Estudiante', '/carga-academica', FALSE, TRUE, FALSE, FALSE),

    -- Acudiente: puede crear excusas y consultar solo los datos de sus estudiantes asociados.
    ('Acudiente', '/dashboard', FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/registros', FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/usuarios', FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/excusas', TRUE, TRUE, FALSE, FALSE),
    ('Acudiente', '/notificaciones', FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/reportes', FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/configuracion', FALSE, FALSE, FALSE, FALSE),
    ('Acudiente', '/carga-academica', FALSE, TRUE, FALSE, FALSE)
)
INSERT INTO modulo_por_rol (
    rolid, moduloid, permiso_crear, permiso_leer,
    permiso_actualizar, permiso_eliminar
)
SELECT
    r.rolid,
    m.moduloid,
    p.puede_crear,
    p.puede_leer,
    p.puede_actualizar,
    p.puede_eliminar
FROM permisos p
JOIN rol r ON r.nombre = p.nombre_rol
JOIN modulo m ON m.ruta = p.ruta_modulo
ON CONFLICT (rolid, moduloid) DO UPDATE
SET permiso_crear = EXCLUDED.permiso_crear,
    permiso_leer = EXCLUDED.permiso_leer,
    permiso_actualizar = EXCLUDED.permiso_actualizar,
    permiso_eliminar = EXCLUDED.permiso_eliminar,
    fecha_actualizacion = CURRENT_TIMESTAMP;

COMMIT;

-- Comprobación posterior: deben aparecer 3 roles, 8 módulos y 24 permisos.
SELECT r.nombre AS rol,
       m.nombre AS modulo,
       m.ruta,
       mr.permiso_crear,
       mr.permiso_leer,
       mr.permiso_actualizar,
       mr.permiso_eliminar
FROM rol r
JOIN modulo_por_rol mr ON mr.rolid = r.rolid
JOIN modulo m ON m.moduloid = mr.moduloid
WHERE r.nombre IN ('Administrador', 'Estudiante', 'Acudiente')
ORDER BY r.nombre, m.nombre;
