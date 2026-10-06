# PI-06 · Migraciones versionadas y conversión de fechas a UTC (Supabase)

Fecha: 06-10-2026 · Ficha técnica 19, etapa 1 (decisiones D4 y D12)

## Procedimiento
1. Respaldo previo con `backend/scripts/respaldo_supabase.py` (alertas 1.647, eventos 28.850, sensores 0 filas), guardado fuera del repositorio.
2. Despliegue del código tolerante (commit a0aadd7) y verificación de `/api/health` en Render: `"timestamp": "2026-10-06T15:57:03…+00:00"`.
3. Simulador detenido. Revisión de los triggers existentes (`trigger_sync_eventos`, `trigger_crear_alerta`): coinciden con los de la migración 000, por lo que no se duplican.
4. Registro de la hora de filas de control antes de migrar.
5. Ejecución de `000_esquema_base.sql` y `001_fechas_con_zona_horaria.sql` en el SQL Editor de Supabase (cada una en una transacción).
6. Comparación de las filas de control y revisión del panel en Vercel.

## Resultado

| Fila | Origen | Antes (sin zona) | Después (timestamptz) | Esperado |
|------|--------|------------------|------------------------|----------|
| 28759 | Simulador (hora de Chile) | 2026-10-02 10:35:59.143177 | 2026-10-02 13:35:59.143177+00 | +3 h (Chile UTC−3) |
| 28851 | Script de prueba (UTC) | 2026-10-06 01:28:50.198 | 2026-10-06 01:28:50.198+00 | sin cambio |

- `eventos.timestamp` y `sensores.creado_en`: `timestamp with time zone`.
- `schema_migrations`: `000, 001`.
- Panel (Vercel): el evento 28851 se muestra como 05-10-2026, 10:28:50 p. m. (hora de Chile). El contador "eventos hoy" deja de contar ese evento como del 6 de octubre.

**Estado: Aprobada.**

## Evidencia (carpeta capturas)
PI-06_triggers_antes_migracion.png, PI-06_migracion_000_ok.png, PI-06_antes_eventos_prueba.png, PI-06_antes_eventos_simulador.png, PI-06_migracion_001_timestamptz.png, PI-06_despues_conversion_utc.png, PI-06_panel_hora_chile.png
