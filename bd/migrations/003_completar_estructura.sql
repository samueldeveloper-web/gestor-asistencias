-- 003 · Completa la estructura existente sin borrar datos.
--  a) esta_activo (borrado lógico) en todas las tablas y NOT NULL.
--  b) fecha_creacion / fecha_actualizacion como TIMESTAMPTZ en todas.
--  c) Un solo trigger BEFORE UPDATE por tabla (había dos por tabla).
--  d) Quita llaves foráneas duplicadas y deja reglas coherentes.
-- Ejecutable más de una vez. Hecho sobre el esquema real de Neon (19/11/2026).
-- Neon guarda la hora en UTC: las fechas sin zona se interpretan como UTC.

BEGIN;

-- a) + b) -------------------------------------------------------------------
DO $$
DECLARE
    t   text;
    col text;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN IF NOT EXISTS esta_activo BOOLEAN DEFAULT TRUE', t);
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP', t);
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN IF NOT EXISTS fecha_actualizacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP', t);

        -- Columnas de fecha sin zona horaria → TIMESTAMPTZ
        FOR col IN
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = t
              AND column_name IN ('fecha_creacion', 'fecha_actualizacion', 'fecha_envio', 'fecha_presentacion')
              AND data_type = 'timestamp without time zone'
        LOOP
            EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I TYPE TIMESTAMPTZ USING %I AT TIME ZONE ''UTC''', t, col, col);
        END LOOP;

        EXECUTE format('ALTER TABLE public.%I DISABLE TRIGGER USER', t);
        EXECUTE format('UPDATE public.%I SET esta_activo = TRUE WHERE esta_activo IS NULL', t);
        EXECUTE format('UPDATE public.%I SET fecha_creacion = CURRENT_TIMESTAMP WHERE fecha_creacion IS NULL', t);
        EXECUTE format('UPDATE public.%I SET fecha_actualizacion = fecha_creacion WHERE fecha_actualizacion IS NULL', t);
        EXECUTE format('ALTER TABLE public.%I ENABLE TRIGGER USER', t);

        EXECUTE format('ALTER TABLE public.%I
                          ALTER COLUMN esta_activo SET DEFAULT TRUE,
                          ALTER COLUMN esta_activo SET NOT NULL,
                          ALTER COLUMN fecha_creacion SET DEFAULT CURRENT_TIMESTAMP,
                          ALTER COLUMN fecha_creacion SET NOT NULL,
                          ALTER COLUMN fecha_actualizacion SET DEFAULT CURRENT_TIMESTAMP,
                          ALTER COLUMN fecha_actualizacion SET NOT NULL', t);
    END LOOP;
END;
$$;

-- c) Un único trigger BEFORE UPDATE ------------------------------------------
-- Actualiza fecha_actualizacion y protege fecha_creacion de cambios.
CREATE OR REPLACE FUNCTION fn_actualizar_fecha()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    NEW.fecha_creacion := OLD.fecha_creacion;
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I', 'trg_update_' || t, t);
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I', 'trg_' || t || '_fecha_actualizacion', t);
        EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE ON public.%I
                        FOR EACH ROW EXECUTE FUNCTION fn_actualizar_fecha()',
                       'trg_' || t || '_fecha_actualizacion', t);
    END LOOP;
END;
$$;

-- Las dos funciones antiguas hacían lo mismo y ya no las usa ningún trigger.
DROP FUNCTION IF EXISTS update_fecha_actualizacion_column();
DROP FUNCTION IF EXISTS actualizar_fecha_actualizacion();

-- d) Llaves foráneas duplicadas ----------------------------------------------
-- Para cada (tabla, columnas, tabla destino) con más de una FK, conserva una
-- sola: la que tenga ON DELETE RESTRICT/NO ACTION (nunca se borra historial).
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT conname, conrelid::regclass AS tabla
        FROM (
            SELECT c.conname, c.conrelid,
                   ROW_NUMBER() OVER (
                       PARTITION BY c.conrelid, c.conkey, c.confrelid
                       ORDER BY CASE c.confdeltype WHEN 'r' THEN 0 WHEN 'a' THEN 1 ELSE 2 END, c.oid
                   ) AS pos
            FROM pg_constraint c
            JOIN pg_namespace n ON n.oid = c.connamespace
            WHERE c.contype = 'f' AND n.nspname = 'public'
        ) x
        WHERE pos > 1
    LOOP
        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', r.tabla, r.conname);
        RAISE NOTICE 'FK duplicada eliminada: %.%', r.tabla, r.conname;
    END LOOP;
END;
$$;

-- carga_academica.personal_institucionalid es NOT NULL: SET NULL no tiene
-- sentido. Se reemplaza por RESTRICT.
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT c.conname
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
        WHERE c.contype = 'f'
          AND c.conrelid = 'public.carga_academica'::regclass
          AND a.attname = 'personal_institucionalid'
          AND c.confdeltype = 'n'
    LOOP
        EXECUTE format('ALTER TABLE carga_academica DROP CONSTRAINT %I', r.conname);
    END LOOP;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
        WHERE c.contype = 'f' AND c.conrelid = 'public.carga_academica'::regclass
          AND a.attname = 'personal_institucionalid'
    ) THEN
        ALTER TABLE carga_academica
            ADD CONSTRAINT fk_carga_academica_personal
            FOREIGN KEY (personal_institucionalid)
            REFERENCES personal_institucional (personalid) ON DELETE RESTRICT;
    END IF;
END;
$$;

-- Índices únicos de estudiante_acudiente (por si la 001 no los dejó).
CREATE UNIQUE INDEX IF NOT EXISTS uq_estudiante_acudiente_par
    ON estudiante_acudiente (estudianteid, acudienteid);
CREATE UNIQUE INDEX IF NOT EXISTS uq_estudiante_contacto_principal
    ON estudiante_acudiente (estudianteid)
    WHERE contacto_principal IS TRUE;

COMMIT;

-- Verificación: cada tabla debe tener 1 trigger de fecha y las 3 columnas NOT NULL.
SELECT t.table_name,
       (SELECT count(*) FROM pg_trigger g
         WHERE g.tgrelid = format('public.%I', t.table_name)::regclass
           AND NOT g.tgisinternal AND g.tgname LIKE '%fecha_actualizacion') AS triggers_fecha,
       (SELECT string_agg(column_name || ':' || is_nullable, ', ')
          FROM information_schema.columns c
         WHERE c.table_schema = 'public' AND c.table_name = t.table_name
           AND column_name IN ('esta_activo', 'fecha_creacion', 'fecha_actualizacion')) AS columnas
FROM information_schema.tables t
WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
ORDER BY 1;
