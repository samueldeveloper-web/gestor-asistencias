-- Normaliza las relaciones entre estudiantes y acudientes en la tabla puente.
-- Basado en la inspección de Neon del 16/10/2026:
-- 13 estudiantes con 13 vínculos antiguos, 9 filas en la tabla puente,
-- 6 vínculos antiguos ausentes y 2 filas idénticas para el mismo par.
-- Ejecutar una sola vez en Neon después de revisar el preflight.
-- No borra estudiantes, acudientes ni historial académico.
-- No se puede deducir el parentesco de los seis vínculos nuevos: se usa
-- 'Por confirmar' para corregirlo luego desde la aplicación.

BEGIN;

LOCK TABLE estudiantes, estudiante_acudiente IN SHARE ROW EXCLUSIVE MODE;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'estudiantes'
          AND column_name = 'acudiente_id'
    ) THEN
        RAISE EXCEPTION 'No se encontró estudiantes.acudiente_id. Verifica si ya se ejecutó la migración.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM estudiante_acudiente
        GROUP BY estudianteid, acudienteid
        HAVING COUNT(DISTINCT parentesco) > 1
    ) THEN
        RAISE EXCEPTION 'Hay pares duplicados con parentescos diferentes. Revisa esos datos antes de continuar.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM estudiantes e
        LEFT JOIN acudientes a ON a.acudiente_id = e.acudiente_id
        WHERE e.acudiente_id IS NOT NULL AND a.acudiente_id IS NULL
    ) THEN
        RAISE EXCEPTION 'Hay estudiantes cuyo acudiente_id no existe en acudientes.';
    END IF;
END;
$$;

-- Conserva una fila por pareja estudiante-acudiente; prioriza TRUE y luego
-- la fila más antigua si una pareja aparece repetida.
WITH duplicadas AS (
    SELECT estudiante_acudienteid,
           ROW_NUMBER() OVER (
               PARTITION BY estudianteid, acudienteid
               ORDER BY contacto_principal DESC NULLS LAST,
                        estudiante_acudienteid ASC
           ) AS posicion
    FROM estudiante_acudiente
)
DELETE FROM estudiante_acudiente ea
USING duplicadas d
WHERE ea.estudiante_acudienteid = d.estudiante_acudienteid
  AND d.posicion > 1;

-- La columna antigua es la referencia oficial para decidir cuál acudiente
-- queda como contacto principal durante esta migración.
UPDATE estudiante_acudiente ea
SET contacto_principal = FALSE,
    fecha_actualizacion = CURRENT_TIMESTAMP
FROM estudiantes e
WHERE ea.estudianteid = e.estudiante_id
  AND e.acudiente_id IS NOT NULL
  AND ea.acudienteid <> e.acudiente_id;

-- Copia los seis vínculos que existían solo en estudiantes.acudiente_id.
INSERT INTO estudiante_acudiente (
    estudianteid, acudienteid, parentesco, contacto_principal,
    fecha_creacion, fecha_actualizacion
)
SELECT
    e.estudiante_id, e.acudiente_id, 'Por confirmar', TRUE,
    COALESCE(e.fecha_creacion, CURRENT_TIMESTAMP),
    COALESCE(e.fecha_actualizacion, CURRENT_TIMESTAMP)
FROM estudiantes e
WHERE e.acudiente_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM estudiante_acudiente ea
      WHERE ea.estudianteid = e.estudiante_id
        AND ea.acudienteid = e.acudiente_id
  );

-- Confirma que el acudiente antiguo de cada estudiante quedó como principal.
UPDATE estudiante_acudiente ea
SET contacto_principal = TRUE,
    fecha_actualizacion = CURRENT_TIMESTAMP
FROM estudiantes e
WHERE e.acudiente_id IS NOT NULL
  AND ea.estudianteid = e.estudiante_id
  AND ea.acudienteid = e.acudiente_id;

-- Si algún vínculo se perdió o quedaron varios principales, aborta y revierte.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM estudiantes e
        WHERE e.acudiente_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM estudiante_acudiente ea
              WHERE ea.estudianteid = e.estudiante_id
                AND ea.acudienteid = e.acudiente_id
          )
    ) THEN
        RAISE EXCEPTION 'La verificación falló: todavía hay vínculos antiguos sin migrar.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM estudiante_acudiente
        WHERE contacto_principal IS TRUE
        GROUP BY estudianteid
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'La verificación falló: hay más de un contacto principal.';
    END IF;
END;
$$;

UPDATE estudiante_acudiente
SET contacto_principal = FALSE
WHERE contacto_principal IS NULL;

ALTER TABLE estudiante_acudiente
    ALTER COLUMN contacto_principal SET DEFAULT FALSE,
    ALTER COLUMN contacto_principal SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_estudiante_acudiente_par
    ON estudiante_acudiente (estudianteid, acudienteid);

CREATE UNIQUE INDEX IF NOT EXISTS uq_estudiante_contacto_principal
    ON estudiante_acudiente (estudianteid)
    WHERE contacto_principal IS TRUE;

-- Quita FKs redundantes y mantiene las restricciones originales de PostgreSQL.
ALTER TABLE estudiante_acudiente
    DROP CONSTRAINT IF EXISTS fk_ea_acudiente,
    DROP CONSTRAINT IF EXISTS fk_ea_estudiante;

-- La columna antigua se retira solo después de copiar y verificar sus vínculos.
ALTER TABLE estudiantes
    DROP CONSTRAINT IF EXISTS estudiantes_acudiente_fk,
    DROP COLUMN acudiente_id;

COMMIT;
