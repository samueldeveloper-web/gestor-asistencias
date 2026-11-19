-- 005 · Módulos del menú y permisos por rol (el menú se arma solo desde la BD).
-- Rutas acordadas con el frontend. Los 4 roles ya existen:
--   1 Administrador · 2 Estudiante · 3 Acudiente · 4 Docente
-- Nada se borra: los módulos y permisos que ya no aplican quedan con
-- esta_activo = FALSE. La API debe listar solo los que tengan
-- modulo.esta_activo, modulo_por_rol.esta_activo y permiso_leer en TRUE.
-- Ejecutable más de una vez.

BEGIN;

-- Asegura los 4 roles (no cambia sus rolid).
INSERT INTO rol (nombre, descripcion)
VALUES
    ('Administrador', 'Administra la operación y configuración institucional.'),
    ('Estudiante', 'Consulta su información académica y de asistencia.'),
    ('Acudiente', 'Consulta información de los estudiantes que tiene asociados.'),
    ('Docente', 'Registra la asistencia de sus cursos y revisa excusas.')
ON CONFLICT (nombre) DO UPDATE SET esta_activo = TRUE;

-- Módulos (icono = clase de Bootstrap Icons).
WITH datos(nombre, ruta, icono, descripcion) AS (
    VALUES
    ('Inicio',            '/dashboard',       'bi-house-door',      'Resumen personalizado según el rol.'),
    ('Estudiantes',       '/estudiantes',     'bi-mortarboard',     'Registro y consulta de estudiantes.'),
    ('Acudientes',        '/acudientes',      'bi-people',          'Registro de acudientes y sus vínculos con estudiantes.'),
    ('Docentes',          '/docentes',        'bi-person-badge',    'Personal docente y administrativo.'),
    ('Cursos',            '/cursos',          'bi-collection',      'Cursos de la institución.'),
    ('Asignaturas',       '/asignaturas',     'bi-book',            'Asignaturas del plan de estudios.'),
    ('Carga académica',   '/carga-academica', 'bi-diagram-3',       'Asignación de docentes a cursos y asignaturas.'),
    ('Matrículas',        '/matriculas',      'bi-journal-check',   'Matrícula de estudiantes por año lectivo.'),
    ('Mis cursos',        '/mis-cursos',      'bi-easel',           'Cursos y asignaturas a cargo del docente.'),
    ('Mis hijos',         '/mis-hijos',       'bi-person-hearts',   'Estudiantes asociados al acudiente.'),
    ('Asistencia',        '/asistencia',      'bi-calendar-check',  'Registro y consulta de asistencia.'),
    ('Excusas',           '/excusas',         'bi-file-earmark-medical', 'Registro y revisión de excusas.'),
    ('Notificaciones',    '/notificaciones',  'bi-bell',            'Avisos de fallas y excusas a los acudientes.'),
    ('Usuarios',          '/usuarios',        'bi-person-gear',     'Cuentas de acceso y su rol.'),
    ('Roles y módulos',   '/roles-modulos',   'bi-shield-lock',     'Módulos y permisos de cada rol.'),
    ('Reportes',          '/reportes',        'bi-file-earmark-bar-graph', 'Reportes en PDF o Excel con filtros.'),
    ('Tablero',           '/tablero',         'bi-bar-chart',       'Tablero de indicadores en Power BI.')
)
INSERT INTO modulo (nombre, ruta, icono, descripcion, esta_activo)
SELECT nombre, ruta, icono, descripcion, TRUE FROM datos
ON CONFLICT (ruta) DO UPDATE
SET nombre = EXCLUDED.nombre,
    icono = EXCLUDED.icono,
    descripcion = EXCLUDED.descripcion,
    esta_activo = TRUE;

-- Rutas antiguas que el frontend ya no usa.
UPDATE modulo SET esta_activo = FALSE
WHERE ruta IN ('/registros', '/configuracion', '/inicio', '/academico')
  AND esta_activo;

-- Matriz de permisos: C(rear) L(eer) A(ctualizar) E(liminar = borrado lógico).
WITH permisos(rol, ruta, c, l, a, e) AS (
    VALUES
    ('Administrador', '/dashboard',       FALSE, TRUE, FALSE, FALSE),
    ('Administrador', '/estudiantes',     TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/acudientes',      TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/docentes',        TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/cursos',          TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/asignaturas',     TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/carga-academica', TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/matriculas',      TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/asistencia',      TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/excusas',         FALSE, TRUE, TRUE,  TRUE),
    ('Administrador', '/notificaciones',  TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/usuarios',        TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/roles-modulos',   TRUE,  TRUE, TRUE,  TRUE),
    ('Administrador', '/reportes',        FALSE, TRUE, FALSE, FALSE),
    ('Administrador', '/tablero',         FALSE, TRUE, FALSE, FALSE),

    ('Docente', '/dashboard',      FALSE, TRUE, FALSE, FALSE),
    ('Docente', '/mis-cursos',     FALSE, TRUE, FALSE, FALSE),
    ('Docente', '/estudiantes',    FALSE, TRUE, FALSE, FALSE),
    ('Docente', '/asistencia',     TRUE,  TRUE, TRUE,  FALSE),
    ('Docente', '/excusas',        FALSE, TRUE, TRUE,  FALSE),
    ('Docente', '/notificaciones', FALSE, TRUE, FALSE, FALSE),
    ('Docente', '/reportes',       FALSE, TRUE, FALSE, FALSE),
    ('Docente', '/tablero',        FALSE, TRUE, FALSE, FALSE),

    ('Acudiente', '/dashboard',      FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/mis-hijos',      FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/asistencia',     FALSE, TRUE, FALSE, FALSE),
    ('Acudiente', '/excusas',        TRUE,  TRUE, TRUE,  FALSE),
    ('Acudiente', '/notificaciones', FALSE, TRUE, TRUE,  FALSE),
    ('Acudiente', '/reportes',       FALSE, TRUE, FALSE, FALSE),

    ('Estudiante', '/dashboard',  FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/asistencia', FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/excusas',    FALSE, TRUE, FALSE, FALSE),
    ('Estudiante', '/reportes',   FALSE, TRUE, FALSE, FALSE)
),
aplicados AS (
    INSERT INTO modulo_por_rol (rolid, moduloid, permiso_crear, permiso_leer,
                                permiso_actualizar, permiso_eliminar, esta_activo)
    SELECT r.rolid, m.moduloid, p.c, p.l, p.a, p.e, TRUE
    FROM permisos p
    JOIN rol r ON r.nombre = p.rol
    JOIN modulo m ON m.ruta = p.ruta
    ON CONFLICT (rolid, moduloid) DO UPDATE
    SET permiso_crear = EXCLUDED.permiso_crear,
        permiso_leer = EXCLUDED.permiso_leer,
        permiso_actualizar = EXCLUDED.permiso_actualizar,
        permiso_eliminar = EXCLUDED.permiso_eliminar,
        esta_activo = TRUE
    RETURNING modulo_por_rolid
)
-- Todo permiso que no esté en la matriz queda inactivo y sin acceso.
UPDATE modulo_por_rol mr
SET esta_activo = FALSE,
    permiso_crear = FALSE, permiso_leer = FALSE,
    permiso_actualizar = FALSE, permiso_eliminar = FALSE
WHERE mr.modulo_por_rolid NOT IN (SELECT modulo_por_rolid FROM aplicados)
  AND (mr.esta_activo OR mr.permiso_leer);

COMMIT;

-- Comprobación: menú de cada rol.
SELECT r.nombre AS rol, string_agg(m.ruta, ', ' ORDER BY m.moduloid) AS menu
FROM modulo_por_rol mr
JOIN rol r USING (rolid)
JOIN modulo m USING (moduloid)
WHERE mr.esta_activo AND mr.permiso_leer AND m.esta_activo
GROUP BY r.nombre
ORDER BY r.nombre;
