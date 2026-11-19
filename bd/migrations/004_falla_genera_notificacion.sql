-- 004 · Función principal: una falla genera notificación al acudiente.
-- Al registrar (o cambiar a) estado 'ausente' en asistencia, se crea una
-- notificación para cada acudiente activo vinculado al estudiante.
-- Al aprobar o rechazar una excusa, se avisa al acudiente; si se aprueba,
-- la asistencia pasa a 'excusado'.
-- La API NO crea estas notificaciones: solo envía el correo de las que tengan
-- enviado_correo = FALSE y luego las marca (enviado_correo, fecha_correo).
-- Ejecutable más de una vez.

BEGIN;

ALTER TABLE notificaciones
    ADD COLUMN IF NOT EXISTS asistenciaid INTEGER,
    ADD COLUMN IF NOT EXISTS enviado_correo BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS fecha_correo TIMESTAMPTZ;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_notificaciones_asistencia') THEN
        ALTER TABLE notificaciones
            ADD CONSTRAINT fk_notificaciones_asistencia
            FOREIGN KEY (asistenciaid) REFERENCES asistencia (asistenciaid) ON DELETE RESTRICT;
    END IF;
END;
$$;

-- Evita notificar dos veces la misma falla al mismo acudiente.
CREATE UNIQUE INDEX IF NOT EXISTS uq_notificacion_asistencia_acudiente_tipo
    ON notificaciones (asistenciaid, acudienteid, tipo)
    WHERE asistenciaid IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Falla → notificación
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_notificar_falla()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
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

DROP TRIGGER IF EXISTS trg_asistencia_notificar_falla_ins ON asistencia;
CREATE TRIGGER trg_asistencia_notificar_falla_ins
    AFTER INSERT ON asistencia
    FOR EACH ROW
    WHEN (NEW.estado = 'ausente' AND NEW.esta_activo)
    EXECUTE FUNCTION fn_notificar_falla();

DROP TRIGGER IF EXISTS trg_asistencia_notificar_falla_upd ON asistencia;
CREATE TRIGGER trg_asistencia_notificar_falla_upd
    AFTER UPDATE OF estado ON asistencia
    FOR EACH ROW
    WHEN (NEW.estado = 'ausente' AND OLD.estado IS DISTINCT FROM 'ausente' AND NEW.esta_activo)
    EXECUTE FUNCTION fn_notificar_falla();

-- ---------------------------------------------------------------------------
-- Excusa revisada → aviso al acudiente (y asistencia 'excusado' si se aprueba)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_excusa_revisada()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
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

DROP TRIGGER IF EXISTS trg_excusas_revisada ON excusas;
CREATE TRIGGER trg_excusas_revisada
    AFTER UPDATE OF estado ON excusas
    FOR EACH ROW
    WHEN (NEW.estado IN ('aprobada', 'rechazada') AND OLD.estado IS DISTINCT FROM NEW.estado)
    EXECUTE FUNCTION fn_excusa_revisada();

COMMIT;

-- Prueba rápida (opcional, dentro de una transacción que se revierte):
-- BEGIN;
-- INSERT INTO asistencia (estudianteid, cursoid, personal_institucionalid, materiaid, estado, fecha)
-- SELECT c.estudianteid, c.cursoid, k.personal_institucionalid, k.materiaid, 'ausente', CURRENT_DATE + 365
-- FROM matriculas c JOIN carga_academica k ON k.cursoid = c.cursoid AND k.anio_lectivo = c.anio_lectivo
-- LIMIT 1;
-- SELECT titulo, mensaje FROM notificaciones ORDER BY notificacionid DESC LIMIT 3;
-- ROLLBACK;
