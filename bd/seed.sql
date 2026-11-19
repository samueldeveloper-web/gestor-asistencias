-- seed.sql · Datos de prueba realistas (Colombia, año lectivo 2026).
-- Completa los datos que ya existen en Neon hasta tener al menos
-- 20 filas en tablas principales y 10 en secundarias. No borra ni modifica
-- los datos existentes. Se puede ejecutar más de una vez (no duplica).
-- En Neon, ejecutar después de las migraciones 003, 004 y 005.
-- En una BD vacía basta con schema.sql antes (crea los roles si faltan).
--
-- las notificaciones NO se insertan aquí, las genera el trigger de faltas.
-- Contraseña de todos los usuarios nuevos: Aula2026*  (bcrypt con pgcrypto)

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Roles (por si se parte de una BD vacía creada solo con schema.sql).
-- En Neon ya existen con rolid 1..4 y no se modifican.
INSERT INTO rol (nombre, descripcion) VALUES
    ('Administrador', 'Administra la operación y configuración institucional.'),
    ('Estudiante', 'Consulta su información académica y de asistencia.'),
    ('Acudiente', 'Consulta información de los estudiantes que tiene asociados.'),
    ('Docente', 'Registra la asistencia de sus cursos y revisa excusas.')
ON CONFLICT (nombre) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Secundarias
-- ---------------------------------------------------------------------------
-- Cursos y asignaturas básicas: solo si la BD está casi vacía (instalación
-- local desde schema.sql). En Neon ya existen y no se tocan.
INSERT INTO cursos (nombre_curso, nivel_educativo)
SELECT v.nombre, v.nivel
FROM (VALUES ('6-A','Básica secundaria'),('6-B','Básica secundaria'),('7-A','Básica secundaria'),
             ('7-B','Básica secundaria'),('8-A','Básica secundaria'),('8-B','Básica secundaria'),
             ('9-A','Básica secundaria'),('9-B','Básica secundaria'),('10-A','Media académica'),
             ('11-A','Media académica')) AS v(nombre, nivel)
WHERE (SELECT count(*) FROM cursos) < 10
ON CONFLICT (nombre_curso) DO NOTHING;

INSERT INTO asignaturas (nombre_materia, descripcion)
SELECT v.nombre, v.descripcion
FROM (VALUES ('Matemáticas','Aritmética, álgebra, geometría y estadística.'),
             ('Lengua Castellana','Comprensión lectora y producción textual.'),
             ('Ciencias Naturales','Biología, química y física básicas.'),
             ('Ciencias Sociales','Historia, geografía y constitución política.'),
             ('Inglés','Lengua extranjera.')) AS v(nombre, descripcion)
WHERE (SELECT count(*) FROM asignaturas) < 5
ON CONFLICT (nombre_materia) DO NOTHING;

INSERT INTO asignaturas (nombre_materia, descripcion) VALUES
    ('Educación Física',        'Actividad física, deporte y hábitos saludables.'),
    ('Ética y Valores',         'Formación ciudadana y convivencia escolar.'),
    ('Tecnología e Informática','Uso de herramientas digitales y pensamiento computacional.'),
    ('Educación Artística',     'Expresión plástica, musical y escénica.'),
    ('Filosofía',               'Pensamiento crítico y argumentación.')
ON CONFLICT (nombre_materia) DO NOTHING;

INSERT INTO configuracion_institucional (clave, valor) VALUES
    ('nombre_institucion',        'Institución Educativa Aula Presente'),
    ('anio_lectivo',              '2026'),
    ('jornada',                   'Mañana'),
    ('hora_inicio_clases',        '06:30'),
    ('hora_fin_clases',           '12:30'),
    ('dias_maximos_excusa',       '3'),
    ('umbral_alerta_fallas',      '3'),
    ('correo_remitente',          'notificaciones@aulapresente.edu.co'),
    ('telefono_institucion',      '6053456789'),
    ('ciudad',                    'Barranquilla'),
    ('rector',                    'Mg. Patricia Ospina Restrepo')
ON CONFLICT (clave) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Personas
-- ---------------------------------------------------------------------------
INSERT INTO personal_institucional (nombres, apellidos, documento_identidad, telefono, direccion, email, cargo) VALUES
    ('Andrés Felipe', 'Rojas Castaño',    '1045678901', '3004561230', 'Cra 43 # 72-15',    'andres.rojas@aulapresente.edu.co',    'Docente'),
    ('Luisa Fernanda','Martínez Ochoa',   '1045678902', '3015673421', 'Calle 84 # 51-20',  'luisa.martinez@aulapresente.edu.co',  'Docente'),
    ('Jorge Iván',    'Gutiérrez Pardo',  '1045678903', '3026784512', 'Cra 38 # 70-08',    'jorge.gutierrez@aulapresente.edu.co', 'Docente'),
    ('Diana Marcela', 'Salazar Muñoz',    '1045678904', '3107895623', 'Calle 76 # 45-33',  'diana.salazar@aulapresente.edu.co',   'Docente'),
    ('Ricardo',       'Peña Villalba',    '1045678905', '3118906734', 'Cra 54 # 64-110',   'ricardo.pena@aulapresente.edu.co',    'Docente'),
    ('Paola Andrea',  'Cárdenas Ríos',    '1045678906', '3129017845', 'Calle 90 # 49C-12', 'paola.cardenas@aulapresente.edu.co',  'Docente'),
    ('Hernán Darío',  'Valencia Mejía',   '1045678907', '3150128956', 'Cra 46 # 80-25',    'hernan.valencia@aulapresente.edu.co', 'Docente'),
    ('Natalia',       'Herrera Quintero', '1045678908', '3161239067', 'Calle 79 # 42F-40', 'natalia.herrera@aulapresente.edu.co', 'Docente'),
    ('Camilo Ernesto','Torres Aguilar',   '1045678909', '3172340178', 'Cra 50 # 68-90',    'camilo.torres@aulapresente.edu.co',   'Coordinador académico'),
    ('Mónica',        'Arango Bedoya',    '1045678910', '3183451289', 'Calle 85 # 47-18',  'monica.arango@aulapresente.edu.co',   'Docente')
ON CONFLICT (documento_identidad) DO NOTHING;

INSERT INTO estudiantes (nombres, apellidos, documento_identidad, fecha_nacimiento, direccion) VALUES
    ('Valentina',     'Gómez Rincón',     '1102345601', '2011-03-14', 'Calle 72 # 41-25'),
    ('Santiago',      'López Ariza',      '1102345602', '2010-07-22', 'Cra 44 # 76-12'),
    ('Isabella',      'Moreno Duarte',    '1102345603', '2012-01-09', 'Calle 68 # 53-40'),
    ('Mateo',         'Ramírez Cuello',   '1102345604', '2009-11-30', 'Cra 41 # 82-07'),
    ('Mariana',       'Castro Pineda',    '1102345605', '2011-09-05', 'Calle 93 # 46-15'),
    ('Samuel',        'Navarro Fuentes',  '1102345606', '2010-04-18', 'Cra 52 # 74-33'),
    ('Gabriela',      'Ortiz Barrios',    '1102345607', '2012-06-27', 'Calle 77 # 39-60'),
    ('Juan José',     'Díaz Mendoza',     '1102345608', '2009-02-11', 'Cra 49 # 70-21')
ON CONFLICT (documento_identidad) DO NOTHING;

INSERT INTO acudientes (nombres, apellidos, telefono, email, direccion, fecha_nacimiento, documento_identidad) VALUES
    ('Claudia Patricia','Rincón Vega',     '3001112233', 'claudia.rincon@gmail.com',    'Calle 72 # 41-25', '1982-05-10', '32765401'),
    ('Luis Alberto',    'López Herrera',   '3012223344', 'luis.lopez.h@hotmail.com',    'Cra 44 # 76-12',   '1979-08-02', '72345602'),
    ('Sandra Milena',   'Duarte Cabrera',  '3023334455', 'sandra.duarte@gmail.com',     'Calle 68 # 53-40', '1985-12-19', '32765403'),
    ('Óscar Javier',    'Ramírez Polo',    '3104445566', 'oscar.ramirez.polo@gmail.com','Cra 41 # 82-07',   '1976-03-25', '72345604'),
    ('Adriana',         'Pineda Salcedo',  '3115556677', 'adriana.pineda@yahoo.com',    'Calle 93 # 46-15', '1984-07-07', '32765405'),
    ('Fabián Enrique',  'Navarro Ruiz',    '3126667788', 'fabian.navarro@gmail.com',    'Cra 52 # 74-33',   '1980-10-14', '72345606'),
    ('Yolanda',         'Barrios De Ortiz','3157778899', 'yolanda.barrios@hotmail.com', 'Calle 77 # 39-60', '1974-01-29', '32765407'),
    ('Rafael Antonio',  'Díaz Charris',    '3168889900', 'rafael.diaz.ch@gmail.com',    'Cra 49 # 70-21',   '1978-09-16', '72345608')
ON CONFLICT (documento_identidad) DO NOTHING;

-- Vínculo estudiante ↔ acudiente (los nuevos estudiantes no tenían ninguno).
INSERT INTO estudiante_acudiente (estudianteid, acudienteid, parentesco, contacto_principal)
SELECT e.estudiante_id, a.acudiente_id, v.parentesco, v.principal
FROM (VALUES
    ('1102345601', '32765401', 'Madre',  TRUE),
    ('1102345602', '72345602', 'Padre',  TRUE),
    ('1102345603', '32765403', 'Madre',  TRUE),
    ('1102345604', '72345604', 'Padre',  TRUE),
    ('1102345605', '32765405', 'Madre',  TRUE),
    ('1102345606', '72345606', 'Padre',  TRUE),
    ('1102345607', '32765407', 'Abuela', TRUE),
    ('1102345608', '72345608', 'Padre',  TRUE),
    -- Hermanos o acudientes que también responden por otro estudiante
    ('1102345603', '72345604', 'Tío',    FALSE),
    ('1102345607', '32765405', 'Tía',    FALSE)
) AS v(doc_est, doc_acu, parentesco, principal)
JOIN estudiantes e ON e.documento_identidad = v.doc_est
JOIN acudientes  a ON a.documento_identidad = v.doc_acu
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- Usuarios (uno por persona nueva; máximo un vínculo por usuario)
-- ---------------------------------------------------------------------------
INSERT INTO usuario (username, email, password_hash, rolid, personal_institucionalid)
SELECT lower(translate(split_part(p.nombres, ' ', 1) || '.' || split_part(p.apellidos, ' ', 1),
                       'áéíóúÁÉÍÓÚñÑ', 'aeiouAEIOUnN')),
       p.email, crypt('Aula2026*', gen_salt('bf')),
       (SELECT rolid FROM rol WHERE nombre = CASE WHEN p.cargo ILIKE 'coordinador%' THEN 'Administrador' ELSE 'Docente' END),
       p.personalid
FROM personal_institucional p
WHERE p.documento_identidad BETWEEN '1045678901' AND '1045678910'
ON CONFLICT DO NOTHING;

INSERT INTO usuario (username, email, password_hash, rolid, acudienteid)
SELECT lower(translate(split_part(a.nombres, ' ', 1) || '.' || split_part(a.apellidos, ' ', 1),
                       'áéíóúÁÉÍÓÚñÑ', 'aeiouAEIOUnN')),
       a.email, crypt('Aula2026*', gen_salt('bf')),
       (SELECT rolid FROM rol WHERE nombre = 'Acudiente'),
       a.acudiente_id
FROM acudientes a
WHERE a.documento_identidad IN ('32765401','72345602','32765403','72345604',
                                '32765405','72345606','32765407','72345608')
ON CONFLICT DO NOTHING;

INSERT INTO usuario (username, email, password_hash, rolid, estudianteid)
SELECT lower(translate(split_part(e.nombres, ' ', 1) || '.' || split_part(e.apellidos, ' ', 1),
                       'áéíóúÁÉÍÓÚñÑ', 'aeiouAEIOUnN')) || right(e.documento_identidad, 2),
       lower(translate(split_part(e.nombres, ' ', 1) || '.' || split_part(e.apellidos, ' ', 1),
                       'áéíóúÁÉÍÓÚñÑ', 'aeiouAEIOUnN')) || right(e.documento_identidad, 2)
           || '@estudiantes.aulapresente.edu.co',
       crypt('Aula2026*', gen_salt('bf')),
       (SELECT rolid FROM rol WHERE nombre = 'Estudiante'),
       e.estudiante_id
FROM estudiantes e
WHERE e.documento_identidad IN ('1102345601','1102345602','1102345603','1102345604')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- Carga académica, matrículas, asistencia y excusas (año lectivo vigente)
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    v_anio  integer := COALESCE((SELECT max(anio_lectivo) FROM carga_academica), 2026);
    v_falta integer;
    v_ultima_excusa integer := COALESCE((SELECT max(excusaid) FROM excusas), 0);
BEGIN
    -- Carga académica: completar hasta 20 combinando curso × asignatura
    -- que aún no tengan docente, priorizando cursos con estudiantes.
    v_falta := GREATEST(0, 20 - (SELECT count(*) FROM carga_academica));
    INSERT INTO carga_academica (cursoid, materiaid, personal_institucionalid, anio_lectivo)
    SELECT x.cursoid, x.materiaid, d.personalid, v_anio
    FROM (
        SELECT c.cursoid, m.materiaid,
               ROW_NUMBER() OVER (ORDER BY
                   (SELECT count(*) FROM matriculas mt WHERE mt.cursoid = c.cursoid AND mt.anio_lectivo = v_anio) DESC,
                   c.cursoid, m.materiaid) AS n
        FROM cursos c CROSS JOIN asignaturas m
        WHERE c.esta_activo AND m.esta_activo
          AND NOT EXISTS (SELECT 1 FROM carga_academica k
                          WHERE k.cursoid = c.cursoid AND k.materiaid = m.materiaid AND k.anio_lectivo = v_anio)
    ) x
    JOIN (
        SELECT personalid, ROW_NUMBER() OVER (ORDER BY personalid) - 1 AS n,
               count(*) OVER () AS total
        FROM personal_institucional
        WHERE esta_activo AND cargo ILIKE '%docente%'
    ) d ON d.n = (x.n - 1) % d.total
    WHERE x.n <= v_falta
    ON CONFLICT DO NOTHING;

    -- Matrículas: todo estudiante activo sin matrícula en el año vigente
    -- queda en un curso que tenga carga académica (reparto en orden).
    INSERT INTO matriculas (estudianteid, cursoid, anio_lectivo, estado, fecha_matricula)
    SELECT e.estudiante_id, c.cursoid, v_anio, 'activo', make_date(v_anio, 1, 20)
    FROM (
        SELECT estudiante_id, ROW_NUMBER() OVER (ORDER BY estudiante_id) - 1 AS n
        FROM estudiantes
        WHERE esta_activo
          AND NOT EXISTS (SELECT 1 FROM matriculas m
                          WHERE m.estudianteid = estudiante_id AND m.anio_lectivo = v_anio)
    ) e
    JOIN (
        SELECT cursoid, ROW_NUMBER() OVER (ORDER BY cursoid) - 1 AS n, count(*) OVER () AS total
        FROM (SELECT DISTINCT cursoid FROM carga_academica WHERE anio_lectivo = v_anio AND esta_activo) k
    ) c ON c.n = e.n % c.total
    ON CONFLICT DO NOTHING;

    -- Matrículas de años anteriores para estudiantes antiguos (historial).
    INSERT INTO matriculas (estudianteid, cursoid, anio_lectivo, estado, fecha_matricula)
    SELECT m.estudianteid, m.cursoid, v_anio - 1, 'promovido', make_date(v_anio - 1, 1, 22)
    FROM matriculas m
    WHERE m.anio_lectivo = v_anio
      AND (SELECT count(*) FROM matriculas) < 20
    ON CONFLICT DO NOTHING;

    -- Asistencia: días hábiles del 3 al 18 de noviembre para cada estudiante
    -- y cada asignatura de su curso. Distribución realista: ~82 % presente,
    -- ~11 % ausente, ~7 % tarde. Las ausencias disparan las notificaciones.
    INSERT INTO asistencia (estudianteid, cursoid, personal_institucionalid, materiaid, estado, fecha, fecha_creacion)
    SELECT mt.estudianteid, k.cursoid, k.personal_institucionalid, k.materiaid,
           CASE
               WHEN abs(hashtext(mt.estudianteid || '-' || k.cargaid || '-' || f.dia)) % 100 < 11 THEN 'ausente'
               WHEN abs(hashtext(mt.estudianteid || '-' || k.cargaid || '-' || f.dia)) % 100 < 18 THEN 'tarde'
               ELSE 'presente'
           END,
           f.dia,
           (f.dia + time '07:10') AT TIME ZONE 'America/Bogota'
    FROM matriculas mt
    JOIN carga_academica k ON k.cursoid = mt.cursoid AND k.anio_lectivo = mt.anio_lectivo AND k.esta_activo
    CROSS JOIN LATERAL (
        SELECT d::date AS dia
        FROM generate_series(make_date(v_anio, 11, 3), make_date(v_anio, 11, 18), interval '1 day') d
        WHERE extract(isodow FROM d) < 6
    ) f
    WHERE mt.anio_lectivo = v_anio AND mt.estado = 'activo' AND mt.esta_activo
    ON CONFLICT DO NOTHING;

    -- Excusas: el acudiente principal justifica algunas ausencias (hasta 20 en total).
    v_falta := GREATEST(0, 20 - (SELECT count(*) FROM excusas));
    INSERT INTO excusas (asistenciaid, estudianteid, acudienteid, motivo, documento_adjunto, estado, fecha_presentacion)
    SELECT s.asistenciaid, s.estudianteid, ea.acudienteid,
           (ARRAY['Cita médica programada en la EPS.',
                  'Incapacidad médica por gripa.',
                  'Calamidad doméstica.',
                  'Diligencia familiar fuera de la ciudad.',
                  'Control odontológico.'])[1 + abs(hashtext(s.asistenciaid::text)) % 5],
           CASE WHEN abs(hashtext(s.asistenciaid::text)) % 3 = 0
                THEN 'excusas/incapacidad_' || s.asistenciaid || '.pdf' END,
           'pendiente',
           ((s.fecha + 1) + time '18:30') AT TIME ZONE 'America/Bogota'
    FROM asistencia s
    JOIN estudiante_acudiente ea ON ea.estudianteid = s.estudianteid AND ea.contacto_principal AND ea.esta_activo
    WHERE s.estado = 'ausente'
      AND NOT EXISTS (SELECT 1 FROM excusas x WHERE x.asistenciaid = s.asistenciaid)
    ORDER BY s.fecha, s.asistenciaid
    LIMIT v_falta;

    -- Revisión de las excusas nuevas (dispara el trigger: aprobada → asistencia
    -- 'excusado' + aviso; rechazada → aviso). Un tercio queda pendiente.
    UPDATE excusas SET estado = CASE WHEN excusaid % 3 = 0 THEN 'rechazada' ELSE 'aprobada' END
    WHERE estado = 'pendiente'
      AND excusaid > v_ultima_excusa
      AND excusaid % 3 <> 1
      AND fecha_presentacion < make_date(v_anio, 11, 15);

    -- Parte de las notificaciones antiguas ya fueron leídas y enviadas por correo.
    UPDATE notificaciones
    SET leido = TRUE, enviado_correo = TRUE, fecha_correo = fecha_envio
    WHERE asistenciaid IN (SELECT asistenciaid FROM asistencia WHERE fecha < make_date(v_anio, 11, 12))
      AND NOT leido
      AND notificacionid % 2 = 0;
END;
$$;

COMMIT;

-- Conteo final por tabla.
SELECT t.table_name AS tabla,
       (xpath('/row/n/text()', query_to_xml(format('select count(*) as n from public.%I', t.table_name), false, true, '')))[1]::text::int AS filas
FROM information_schema.tables t
WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
ORDER BY 1;
