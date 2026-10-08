-- ============================================================
-- DomoVida · Migración 003 · Sincronización del modo borde (HU-03)
-- (ficha técnica 19, etapa 2 · D2 y D3)
--
-- Agrega a eventos:
--   uuid        identificador generado en el origen (borde o nube); evita
--               duplicados cuando un evento se reenvía tras un corte.
--   origen      'borde' (llegó desde el hogar por el sincronizador) o 'nube'.
--   notificado  el aviso ntfy ya se envió; la nube no lo repite.
-- La columna sync_status ya existía (trigger marcar_como_sincronizado).
--
-- Se aplica ANTES de desplegar el código de HU-03: el código actual
-- ignora estas columnas, y el nuevo las necesita.
-- ============================================================
BEGIN;

ALTER TABLE public.eventos ADD COLUMN IF NOT EXISTS uuid varchar(36);
ALTER TABLE public.eventos ADD COLUMN IF NOT EXISTS origen varchar(10) DEFAULT 'nube';
ALTER TABLE public.eventos ADD COLUMN IF NOT EXISTS notificado boolean DEFAULT false;

-- Eventos existentes: reciben un UUID y quedan con origen 'nube'
UPDATE public.eventos SET uuid = gen_random_uuid()::text WHERE uuid IS NULL;
UPDATE public.eventos SET origen = 'nube' WHERE origen IS NULL;
UPDATE public.eventos SET notificado = false WHERE notificado IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_eventos_uuid ON public.eventos (uuid);

INSERT INTO public.schema_migrations (version, descripcion)
VALUES ('003', 'Sincronización del modo borde: uuid, origen y notificado en eventos')
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Verificación: 0 eventos sin uuid, 0 uuid repetidos, migraciones 000 a 003
SELECT
  (SELECT count(*) FROM public.eventos)                                     AS eventos,
  (SELECT count(*) FROM public.eventos WHERE uuid IS NULL)                  AS sin_uuid,
  (SELECT count(*) - count(DISTINCT uuid) FROM public.eventos)              AS uuid_repetidos,
  (SELECT count(*) FROM public.eventos WHERE origen = 'nube')               AS origen_nube,
  (SELECT string_agg(version, ', ' ORDER BY version) FROM public.schema_migrations) AS migraciones;
