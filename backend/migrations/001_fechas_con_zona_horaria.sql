-- ============================================================
-- DomoVida · Migración 001 · Fechas con zona horaria (ficha técnica 19, D4)
-- Cambia eventos."timestamp" y sensores.creado_en a timestamptz (UTC).
--
-- Los datos existentes sin zona se interpretan según su origen:
--   · eventos de los scripts de prueba (valor contiene la clave "prueba"):
--     el navegador envió la hora en UTC.
--   · resto de los eventos (simulador): hora de Chile (America/Santiago).
--   · sensores.creado_en: la generaba el servidor en UTC.
-- Requiere el backend con tiempo.py (commit del 06-10-2026).
-- Respaldo previo: Documents/respaldos_domovida/2026-10-06_1245
-- ============================================================
BEGIN;

ALTER TABLE public.eventos
    ALTER COLUMN "timestamp" TYPE timestamptz
    USING CASE
        WHEN "timestamp" IS NULL THEN NULL
        WHEN (valor::jsonb) ? 'prueba' THEN "timestamp" AT TIME ZONE 'UTC'
        ELSE "timestamp" AT TIME ZONE 'America/Santiago'
    END;

ALTER TABLE public.sensores
    ALTER COLUMN creado_en TYPE timestamptz
    USING creado_en AT TIME ZONE 'UTC';

INSERT INTO public.schema_migrations (version, descripcion)
VALUES ('001', 'Fechas con zona horaria (timestamptz, UTC)')
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Verificación: las dos columnas deben mostrar "timestamp with time zone"
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND ((table_name = 'eventos' AND column_name = 'timestamp')
    OR (table_name = 'sensores' AND column_name = 'creado_en'));
