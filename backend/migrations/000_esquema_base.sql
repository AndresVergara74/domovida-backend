-- ============================================================
-- DomoVida · Migración 000 · Esquema base (al 06-10-2026)
-- Reconstruye la estructura existente en Supabase/PostgreSQL.
-- En producción ya existía todo, salvo la tabla schema_migrations;
-- por eso cada sentencia usa IF NOT EXISTS / CREATE OR REPLACE.
-- ============================================================
BEGIN;

CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version     varchar(20) PRIMARY KEY,
    descripcion text        NOT NULL,
    aplicada_en timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.schema_migrations ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS public.sensores (
    id          serial PRIMARY KEY,
    sensor_id   varchar UNIQUE,
    tipo        varchar,
    habitacion  varchar,
    activo      boolean DEFAULT true,
    creado_en   timestamp
);

CREATE TABLE IF NOT EXISTS public.eventos (
    id            serial PRIMARY KEY,
    sensor_id     varchar,
    tipo          varchar,
    habitacion    varchar,
    valor         json,
    alerta        boolean DEFAULT false,
    "timestamp"   timestamp,
    sync_status   varchar,
    resuelto      boolean DEFAULT false,
    resuelto_en   timestamptz,
    resuelto_por  varchar(100)
);

CREATE TABLE IF NOT EXISTS public.alertas (
    id                serial PRIMARY KEY,
    evento_id         integer REFERENCES public.eventos(id),
    tipo_alerta       varchar NOT NULL,
    nivel_severidad   varchar NOT NULL,
    payload_fhir      jsonb,
    resuelto          boolean DEFAULT false,
    resuelto_en       timestamptz,
    resuelto_por      varchar,
    notas_resolucion  text,
    creado_en         timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_eventos_alerta     ON public.eventos (alerta) WHERE alerta = true;
CREATE INDEX IF NOT EXISTS idx_eventos_sensor_id  ON public.eventos (sensor_id);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo       ON public.eventos (tipo);
CREATE INDEX IF NOT EXISTS idx_eventos_timestamp  ON public.eventos ("timestamp" DESC);
CREATE INDEX IF NOT EXISTS ix_eventos_timestamp   ON public.eventos ("timestamp");

-- Trigger 1: marca el evento como sincronizado al llegar a la nube (ficha técnica 11)
CREATE OR REPLACE FUNCTION public.marcar_como_sincronizado()
RETURNS trigger LANGUAGE plpgsql SET search_path = public AS $$
BEGIN
    NEW.sync_status := 'synced';
    RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trigger_sync_eventos ON public.eventos;
CREATE TRIGGER trigger_sync_eventos BEFORE INSERT ON public.eventos
    FOR EACH ROW EXECUTE FUNCTION public.marcar_como_sincronizado();

-- Trigger 2: crea la alerta con su severidad (ficha técnica 11, prueba PI-02)
CREATE OR REPLACE FUNCTION public.crear_alerta_automatica()
RETURNS trigger LANGUAGE plpgsql SET search_path = public AS $$
BEGIN
    IF NEW.alerta = TRUE THEN
        INSERT INTO alertas (evento_id, tipo_alerta, nivel_severidad, payload_fhir, resuelto, creado_en)
        VALUES (
            NEW.id, NEW.tipo,
            CASE WHEN NEW.tipo IN ('acelerometro', 'cardiovascular', 'boton_panico', 'gas', 'humo')
                 THEN 'critica' ELSE 'alta' END,
            NEW.valor, FALSE, NOW()
        );
    END IF;
    RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trigger_crear_alerta ON public.eventos;
CREATE TRIGGER trigger_crear_alerta AFTER INSERT ON public.eventos
    FOR EACH ROW EXECUTE FUNCTION public.crear_alerta_automatica();

-- RLS: el rol anónimo no ve ninguna fila (pruebas PI-03 y PI-03b).
-- La API se conecta con el rol dueño de la base, que no pasa por RLS.
ALTER TABLE public.sensores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.eventos  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alertas  ENABLE ROW LEVEL SECURITY;

INSERT INTO public.schema_migrations (version, descripcion)
VALUES ('000', 'Esquema base al 06-10-2026')
ON CONFLICT (version) DO NOTHING;

COMMIT;
