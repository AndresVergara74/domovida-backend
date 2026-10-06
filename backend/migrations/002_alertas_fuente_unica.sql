-- ============================================================
-- DomoVida · Migración 002 · `alertas` como fuente única de verdad
-- (ficha técnica 19, etapa 3, D1 · ajuste 17)
--
-- Antes: el trigger crear_alerta_automatica creaba la alerta y la API
-- registraba la atención solo en eventos.resuelto*; alertas.resuelto*
-- quedaba sin uso.
-- Ahora: el backend crea la alerta en la misma transacción que el evento
-- (alertas_servicio.py) y registra la atención en alertas.resuelto*.
-- Las columnas eventos.resuelto* quedan obsoletas (se copian por
-- compatibilidad y se eliminarán en una migración posterior).
--
-- Requiere el backend con alertas_servicio.py ya desplegado: ese código
-- reutiliza la alerta del trigger si existe, así que no hay duplicados
-- ni antes ni después de esta migración.
-- ============================================================
BEGIN;

-- 1. Eventos con alerta que no tienen fila en alertas (si los hubiera)
INSERT INTO public.alertas (evento_id, tipo_alerta, nivel_severidad, payload_fhir, resuelto, resuelto_en, resuelto_por, creado_en)
SELECT e.id, e.tipo,
       CASE WHEN e.tipo IN ('acelerometro', 'cardiovascular', 'boton_panico', 'gas', 'humo')
            THEN 'critica' ELSE 'alta' END,
       e.valor::jsonb, COALESCE(e.resuelto, false), e.resuelto_en, e.resuelto_por, COALESCE(e."timestamp", now())
FROM public.eventos e
WHERE e.alerta = true
  AND NOT EXISTS (SELECT 1 FROM public.alertas a WHERE a.evento_id = e.id);

-- 2. Copiar a alertas la atención registrada hasta hoy en eventos
UPDATE public.alertas a
SET resuelto = true, resuelto_en = e.resuelto_en, resuelto_por = e.resuelto_por
FROM public.eventos e
WHERE a.evento_id = e.id
  AND e.resuelto = true
  AND COALESCE(a.resuelto, false) = false;

-- 3. La alerta la crea el backend: se elimina el trigger para no duplicar
DROP TRIGGER IF EXISTS trigger_crear_alerta ON public.eventos;
DROP FUNCTION IF EXISTS public.crear_alerta_automatica();

-- 4. Una alerta por evento, y búsqueda rápida de las alertas activas
CREATE UNIQUE INDEX IF NOT EXISTS uq_alertas_evento_id ON public.alertas (evento_id);
CREATE INDEX IF NOT EXISTS idx_alertas_activas ON public.alertas (creado_en DESC) WHERE resuelto = false;

INSERT INTO public.schema_migrations (version, descripcion)
VALUES ('002', 'alertas como fuente única de verdad de la atención')
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Verificación: 0 eventos con alerta sin fila en alertas, 0 diferencias de atención
SELECT
  (SELECT count(*) FROM public.eventos e WHERE e.alerta AND NOT EXISTS
     (SELECT 1 FROM public.alertas a WHERE a.evento_id = e.id))                    AS eventos_sin_alerta,
  (SELECT count(*) FROM public.eventos e JOIN public.alertas a ON a.evento_id = e.id
     WHERE COALESCE(e.resuelto, false) <> COALESCE(a.resuelto, false))            AS diferencias_atencion,
  (SELECT count(*) FROM pg_trigger WHERE tgname = 'trigger_crear_alerta')          AS trigger_antiguo,
  (SELECT string_agg(version, ', ' ORDER BY version) FROM public.schema_migrations) AS migraciones;
