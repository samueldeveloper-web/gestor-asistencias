-- =============================================================================
-- schema.sql · Gestor de asistencia estudiantil "Aula Presente"
-- Esquema final de la BD en Neon (PostgreSQL) tras las migraciones 001–005.
-- Fuente única para backend, frontend, modelo en Access y versión local.
--
-- 16 tablas. Todas tienen:
--   esta_activo          BOOLEAN     borrado lógico (eliminar = FALSE)
--   fecha_creacion       TIMESTAMPTZ automática (DEFAULT, no cambia nunca)
--   fecha_actualizacion  TIMESTAMPTZ automática (trigger BEFORE UPDATE)
-- Función principal: registrar una falla (asistencia 'ausente') crea una
-- notificación para cada acudiente del estudiante (trigger en asistencia).
--
-- Uso en una BD vacía:  psql -d asistencia_local -f bd/schema.sql
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- Seguridad: roles, módulos del menú, permisos y usuarios
-- -----------------------------------------------------------------------------
CREATE TABLE rol (
    rolid               SERIAL PRIMARY KEY,
    nombre              VARCHAR NOT NULL UNIQUE,
    descripcion         TEXT,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modulo (
    moduloid            SERIAL PRIMARY KEY,
    nombre              VARCHAR NOT NULL,
    ruta                VARCHAR NOT NULL UNIQUE,
    icono               VARCHAR,
    descripcion         TEXT,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modulo_por_rol (
    modulo_por_rolid    SERIAL PRIMARY KEY,
    rolid               INTEGER NOT NULL REFERENCES rol (rolid) ON DELETE CASCADE,
    moduloid            INTEGER NOT NULL REFERENCES modulo (moduloid) ON DELETE CASCADE,
    permiso_crear       BOOLEAN NOT NULL DEFAULT FALSE,
    permiso_leer        BOOLEAN NOT NULL DEFAULT TRUE,
    permiso_actualizar  BOOLEAN NOT NULL DEFAULT FALSE,
    permiso_eliminar    BOOLEAN NOT NULL DEFAULT FALSE,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_rol_modulo UNIQUE (rolid, moduloid)
);

-- -----------------------------------------------------------------------------
-- Personas
-- -----------------------------------------------------------------------------
CREATE TABLE personal_institucional (
    personalid          SERIAL PRIMARY KEY,
    nombres             VARCHAR NOT NULL,
    apellidos           VARCHAR NOT NULL,
    documento_identidad VARCHAR NOT NULL UNIQUE,
    telefono            VARCHAR NOT NULL,
    direccion           TEXT,
    email               VARCHAR NOT NULL,
    cargo               VARCHAR NOT NULL,          -- Docente, Coordinador académico, ...
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE estudiantes (
    estudiante_id       SERIAL PRIMARY KEY,
    nombres             VARCHAR NOT NULL,
    apellidos           VARCHAR NOT NULL,
    documento_identidad VARCHAR NOT NULL UNIQUE,
    fecha_nacimiento    DATE NOT NULL,
    direccion           TEXT,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE acudientes (
    acudiente_id        SERIAL PRIMARY KEY,
    nombres             VARCHAR NOT NULL,
    apellidos           VARCHAR NOT NULL,
    telefono            VARCHAR NOT NULL,
    email               VARCHAR NOT NULL,          -- destino de los correos de fallas
    direccion           TEXT,
    fecha_nacimiento    DATE,
    documento_identidad VARCHAR NOT NULL UNIQUE,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Un estudiante puede tener varios acudientes; solo uno es contacto principal.
CREATE TABLE estudiante_acudiente (
    estudiante_acudienteid SERIAL PRIMARY KEY,
    estudianteid        INTEGER NOT NULL REFERENCES estudiantes (estudiante_id) ON DELETE RESTRICT,
    acudienteid         INTEGER NOT NULL REFERENCES acudientes (acudiente_id) ON DELETE RESTRICT,
    parentesco          VARCHAR NOT NULL,
    contacto_principal  BOOLEAN NOT NULL DEFAULT FALSE,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX uq_estudiante_acudiente_par ON estudiante_acudiente (estudianteid, acudienteid);
CREATE UNIQUE INDEX uq_estudiante_contacto_principal ON estudiante_acudiente (estudianteid)
    WHERE contacto_principal IS TRUE;

-- Cuenta de acceso. Se liga a lo sumo a una persona (personal, estudiante o acudiente).
CREATE TABLE usuario (
    usuarioid           SERIAL PRIMARY KEY,
    username            VARCHAR NOT NULL UNIQUE,
    email               VARCHAR NOT NULL UNIQUE,
    password_hash       VARCHAR NOT NULL,          -- bcrypt ($2a$/$2b$)
    rolid               INTEGER NOT NULL REFERENCES rol (rolid),
    personal_institucionalid INTEGER UNIQUE REFERENCES personal_institucional (personalid) ON DELETE SET NULL,
    estudianteid        INTEGER UNIQUE REFERENCES estudiantes (estudiante_id) ON DELETE SET NULL,
    acudienteid         INTEGER UNIQUE REFERENCES acudientes (acudiente_id) ON DELETE SET NULL,
    ultimo_ingreso      TIMESTAMPTZ,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_usuario_un_vinculo CHECK (
        (personal_institucionalid IS NOT NULL)::int
      + (estudianteid IS NOT NULL)::int
      + (acudienteid IS NOT NULL)::int <= 1)
);
CREATE INDEX idx_usuario_email ON usuario (email);
CREATE INDEX idx_usuario_username ON usuario (username);

-- -----------------------------------------------------------------------------
-- Académico
-- -----------------------------------------------------------------------------
CREATE TABLE cursos (
    cursoid             SERIAL PRIMARY KEY,
    nombre_curso        VARCHAR NOT NULL UNIQUE,   -- p. ej. "10-A"
    nivel_educativo     VARCHAR NOT NULL,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asignaturas (
    materiaid           SERIAL PRIMARY KEY,
    nombre_materia      VARCHAR NOT NULL UNIQUE,
    descripcion         TEXT,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Qué docente dicta qué asignatura en qué curso y año.
CREATE TABLE carga_academica (
    cargaid             SERIAL PRIMARY KEY,
    cursoid             INTEGER NOT NULL REFERENCES cursos (cursoid) ON DELETE RESTRICT,
    materiaid           INTEGER NOT NULL REFERENCES asignaturas (materiaid) ON DELETE RESTRICT,
    personal_institucionalid INTEGER NOT NULL REFERENCES personal_institucional (personalid),
    anio_lectivo        INTEGER NOT NULL,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_curso_materia_anio UNIQUE (cursoid, materiaid, anio_lectivo)
);
CREATE INDEX idx_carga_personal ON carga_academica (personal_institucionalid);

CREATE TABLE matriculas (
    matriculaid         SERIAL PRIMARY KEY,
    estudianteid        INTEGER NOT NULL REFERENCES estudiantes (estudiante_id) ON DELETE RESTRICT,
    cursoid             INTEGER NOT NULL REFERENCES cursos (cursoid) ON DELETE RESTRICT,
    anio_lectivo        INTEGER NOT NULL,
    estado              VARCHAR DEFAULT 'activo'
                        CHECK (estado IN ('activo', 'retirado', 'graduado', 'promovido')),
    fecha_matricula     DATE DEFAULT CURRENT_DATE,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_estudiante_anio UNIQUE (estudianteid, anio_lectivo)
);
CREATE INDEX idx_matriculas_estudiante_curso ON matriculas (estudianteid, cursoid);

-- -----------------------------------------------------------------------------
-- Asistencia, excusas y notificaciones (función principal)
-- -----------------------------------------------------------------------------
CREATE TABLE asistencia (
    asistenciaid        SERIAL PRIMARY KEY,
    estudianteid        INTEGER NOT NULL REFERENCES estudiantes (estudiante_id) ON DELETE RESTRICT,
    cursoid             INTEGER NOT NULL REFERENCES cursos (cursoid) ON DELETE RESTRICT,
    personal_institucionalid INTEGER REFERENCES personal_institucional (personalid) ON DELETE SET NULL,
    materiaid           INTEGER NOT NULL REFERENCES asignaturas (materiaid) ON DELETE RESTRICT,
    estado              VARCHAR NOT NULL
                        CHECK (estado IN ('presente', 'ausente', 'tarde', 'excusado')),
    fecha               DATE NOT NULL,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_estudiante_materia_fecha UNIQUE (estudianteid, cursoid, materiaid, fecha)
);
CREATE INDEX idx_asistencia_estudiante ON asistencia (estudianteid);
CREATE INDEX idx_asistencia_fecha ON asistencia (fecha);
CREATE INDEX idx_asistencia_fecha_estudiante ON asistencia (fecha, estudianteid);

CREATE TABLE excusas (
    excusaid            SERIAL PRIMARY KEY,
    asistenciaid        INTEGER NOT NULL REFERENCES asistencia (asistenciaid) ON DELETE RESTRICT,
    estudianteid        INTEGER NOT NULL REFERENCES estudiantes (estudiante_id) ON DELETE RESTRICT,
    acudienteid         INTEGER REFERENCES acudientes (acudiente_id) ON DELETE RESTRICT,
    motivo              TEXT NOT NULL,
    documento_adjunto   VARCHAR,
    estado              VARCHAR DEFAULT 'pendiente'
                        CHECK (estado IN ('pendiente', 'aprobada', 'rechazada')),
    fecha_presentacion  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (estudianteid IS NOT NULL OR acudienteid IS NOT NULL)
);
CREATE INDEX idx_excusas_asistencia ON excusas (asistenciaid);

CREATE TABLE notificaciones (
    notificacionid      SERIAL PRIMARY KEY,
    estudianteid        INTEGER REFERENCES estudiantes (estudiante_id) ON DELETE RESTRICT,
    acudienteid         INTEGER NOT NULL REFERENCES acudientes (acudiente_id) ON DELETE RESTRICT,
    asistenciaid        INTEGER REFERENCES asistencia (asistenciaid) ON DELETE RESTRICT,
    titulo              VARCHAR NOT NULL,
    mensaje             TEXT NOT NULL,
    tipo                VARCHAR DEFAULT 'asistencia'
                        CHECK (tipo IN ('asistencia', 'excusa', 'general')),
    leido               BOOLEAN DEFAULT FALSE,
    fecha_envio         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    enviado_correo      BOOLEAN NOT NULL DEFAULT FALSE,  -- la API lo pone en TRUE al enviar el correo
    fecha_correo        TIMESTAMPTZ,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_notificaciones_acudiente ON notificaciones (acudienteid);
CREATE UNIQUE INDEX uq_notificacion_asistencia_acudiente_tipo
    ON notificaciones (asistenciaid, acudienteid, tipo) WHERE asistenciaid IS NOT NULL;

-- -----------------------------------------------------------------------------
-- Parámetros
-- -----------------------------------------------------------------------------
CREATE TABLE configuracion_institucional (
    clave               VARCHAR PRIMARY KEY,
    valor               TEXT NOT NULL,
    esta_activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Funciones y triggers
-- =============================================================================

-- fecha_actualizacion automática y fecha_creacion inmutable (todas las tablas).
CREATE OR REPLACE FUNCTION fn_actualizar_fecha()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.fecha_creacion := OLD.fecha_creacion;
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

DO $$
DECLARE t text;
BEGIN
    FOR t IN SELECT table_name FROM information_schema.tables
             WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE ON public.%I
                        FOR EACH ROW EXECUTE FUNCTION fn_actualizar_fecha()',
                       'trg_' || t || '_fecha_actualizacion', t);
    END LOOP;
END;
$$;

-- Falla → notificación a cada acudiente activo del estudiante.
CREATE OR REPLACE FUNCTION fn_notificar_falla()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO notificaciones (estudianteid, acudienteid, asistenciaid, titulo, mensaje, tipo,
                                fecha_envio, fecha_creacion)
    SELECT
        NEW.estudianteid,
        ea.acudienteid,
        NEW.asistenciaid,
        'Inasistencia de ' || e.nombres || ' ' || e.apellidos,
        format('Le informamos que %s %s no asistió a la clase de %s (curso %s) el %s. '
               'Si la falla tiene justificación, puede registrar una excusa en la plataforma.',
               e.nombres, e.apellidos, m.nombre_materia, c.nombre_curso,
               to_char(NEW.fecha, 'DD/MM/YYYY')),
        'asistencia',
        CASE WHEN TG_OP = 'INSERT' THEN NEW.fecha_creacion ELSE CURRENT_TIMESTAMP END,
        CASE WHEN TG_OP = 'INSERT' THEN NEW.fecha_creacion ELSE CURRENT_TIMESTAMP END
    FROM estudiante_acudiente ea
    JOIN acudientes a  ON a.acudiente_id = ea.acudienteid AND a.esta_activo
    JOIN estudiantes e ON e.estudiante_id = NEW.estudianteid
    JOIN asignaturas m ON m.materiaid = NEW.materiaid
    JOIN cursos c      ON c.cursoid = NEW.cursoid
    WHERE ea.estudianteid = NEW.estudianteid
      AND ea.esta_activo
    ON CONFLICT (asistenciaid, acudienteid, tipo) WHERE asistenciaid IS NOT NULL DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_asistencia_notificar_falla_ins
    AFTER INSERT ON asistencia
    FOR EACH ROW
    WHEN (NEW.estado = 'ausente' AND NEW.esta_activo)
    EXECUTE FUNCTION fn_notificar_falla();

CREATE TRIGGER trg_asistencia_notificar_falla_upd
    AFTER UPDATE OF estado ON asistencia
    FOR EACH ROW
    WHEN (NEW.estado = 'ausente' AND OLD.estado IS DISTINCT FROM 'ausente' AND NEW.esta_activo)
    EXECUTE FUNCTION fn_notificar_falla();

-- Excusa aprobada/rechazada → aviso al acudiente; aprobada → asistencia 'excusado'.
CREATE OR REPLACE FUNCTION fn_excusa_revisada()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.estado = 'aprobada' THEN
        UPDATE asistencia SET estado = 'excusado'
        WHERE asistenciaid = NEW.asistenciaid AND estado <> 'excusado';
    END IF;

    INSERT INTO notificaciones (estudianteid, acudienteid, asistenciaid, titulo, mensaje, tipo)
    SELECT
        NEW.estudianteid,
        ea.acudienteid,
        NEW.asistenciaid,
        'Excusa ' || NEW.estado,
        format('La excusa presentada para la falla de %s %s del %s fue %s.',
               e.nombres, e.apellidos, to_char(s.fecha, 'DD/MM/YYYY'), NEW.estado),
        'excusa'
    FROM estudiante_acudiente ea
    JOIN acudientes a  ON a.acudiente_id = ea.acudienteid AND a.esta_activo
    JOIN estudiantes e ON e.estudiante_id = NEW.estudianteid
    JOIN asistencia s  ON s.asistenciaid = NEW.asistenciaid
    WHERE ea.estudianteid = NEW.estudianteid
      AND ea.esta_activo
    ON CONFLICT (asistenciaid, acudienteid, tipo) WHERE asistenciaid IS NOT NULL DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_excusas_revisada
    AFTER UPDATE OF estado ON excusas
    FOR EACH ROW
    WHEN (NEW.estado IN ('aprobada', 'rechazada') AND OLD.estado IS DISTINCT FROM NEW.estado)
    EXECUTE FUNCTION fn_excusa_revisada();
