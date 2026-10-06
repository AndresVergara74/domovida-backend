# Ficha 19 · Propuesta de mejora de la base de datos (modelo v2)

**Proyecto:** DomoVida · **Autor:** Andrés Rodrigo Vergara Acevedo · **Fecha:** 6 de octubre de 2026
**Estado:** en ejecución por etapas desde el Sprint 4. Etapas 1 y 3 completadas el 06-10-2026 (ver secciones 4.1 y 4.2); etapas 2, 4, 5 y 6 planificadas.
**Diagramas:** modelo actual en [`diagramas/05_modelo_datos.png`](../../../diagramas/05_modelo_datos.png) · modelo propuesto en [`diagramas/08_modelo_datos_v2_propuesto.png`](../../../diagramas/08_modelo_datos_v2_propuesto.png)

---

## 1. Por qué mejorar la base de datos

El modelo actual (tablas `sensores`, `eventos` y `alertas` en Supabase/PostgreSQL) sirvió para construir y validar el prototipo: las pruebas PI-02, PI-03 y PI-03b están aprobadas. Al documentarlo en el diagrama entidad-relación (06-10-2026) se identificaron limitaciones que impedirán avanzar en tres frentes del proyecto:

- **HU-03 (sincronización del modo borde):** hoy no es posible subir a Supabase los eventos guardados en SQLite sin internet sin riesgo de duplicarlos.
- **HU-17 (proteger las lecturas de la API):** la base no sabe qué cuidador puede ver qué hogar, así que no se pueden escribir políticas RLS por usuario.
- **Crecimiento:** el prototipo representa un solo hogar (el paciente `domovida-p001` está fijo en el código) y la tabla `eventos` crece con cada lectura de los sensores.

## 2. Diagnóstico del modelo actual

| N° | Problema detectado | Consecuencia | Prioridad |
|---|---|---|---|
| D1 | Las columnas de atención (`resuelto`, `resuelto_en`, `resuelto_por`) están duplicadas en `eventos` y `alertas`, y la API solo actualiza las de `eventos` (ajuste 17). | Dos fuentes de verdad; la tabla `alertas` no refleja qué alertas se atendieron. | Alta |
| D2 | Los identificadores son enteros autoincrementales, generados por separado en SQLite (borde) y en PostgreSQL (nube). | Al sincronizar, los `id` del borde chocan con los de la nube; no hay forma de evitar duplicados. Bloquea HU-03. | Alta |
| D3 | `eventos.sync_status` lo marca un trigger como `synced` al insertar en la nube, por lo que siempre vale lo mismo. | El campo no informa nada útil sobre la sincronización. | Alta |
| D4 | Mezcla de fechas con y sin zona horaria: `eventos.timestamp` y `sensores.creado_en` sin zona; `alertas` con zona. | Errores de hora entre UTC y Chile (ya ocurrió: ajuste 1 del registro de pruebas). | Alta |
| D5 | No existen las entidades hogar, paciente ni cuidador; el seudónimo del paciente está fijo en `fhir_router.py`. | No se pueden escribir políticas RLS por cuidador (bloquea HU-17) ni monitorear más de un hogar. | Media |
| D6 | `eventos.sensor_id` no es clave foránea de `sensores`; `tipo` y `habitacion` se repiten en cada evento. | Se pueden guardar lecturas de sensores inexistentes, y los datos repetidos pueden quedar inconsistentes. | Media |
| D7 | `tipo`, `nivel_severidad` y similares son texto libre, sin restricciones. | Un error de tipeo (por ejemplo «critico» en vez de «critica») pasa sin aviso. | Media |
| D8 | `eventos.valor` es `json` y `alertas.payload_fhir` es `jsonb`; además, `payload_fhir` solo copia `valor`, porque el recurso FHIR se genera al consultar. | Inconsistencia de tipos y una columna redundante. | Baja |
| D9 | El consentimiento informado se guarda solo en el navegador (`localStorage`). | No queda constancia en el servidor de quién aceptó, cuándo ni qué versión del texto (responsabilidad proactiva, Ley N° 21.719). | Media |
| D10 | No hay registro de quién consulta los datos. | Falta trazabilidad de accesos a datos de salud. | Baja |
| D11 | No hay política de retención: cada lectura de los sensores se guarda para siempre. | La tabla `eventos` superó las 28.000 filas en pocos días; el plan gratuito de Supabase tiene 500 MB. También contradice el principio de minimización de datos. | Media |
| D12 | Los cambios de estructura se hicieron a mano en el panel de Supabase, sin migraciones versionadas. | No se puede reconstruir la base desde el repositorio ni revisar su historial. | Alta |

## 3. Modelo propuesto (v2)

Ver el diagrama [`08_modelo_datos_v2_propuesto`](../../../diagramas/08_modelo_datos_v2_propuesto.png). Los cambios principales son:

1. **Identificadores UUID generados en el borde (D2, D3).** Cada lectura recibe su `id` (UUID) en el hogar, antes de enviarse. Al sincronizar se usa `INSERT … ON CONFLICT (id) DO NOTHING`, así una lectura reenviada nunca se duplica. Se reemplaza `sync_status` por `origen` (borde o nube), `medido_en` (hora del sensor) y `recibido_en` (hora de llegada a la nube), que además permiten medir el retraso de la sincronización. **Habilita HU-03.**
2. **Una sola fuente de verdad para la atención (D1).** `lecturas` guarda solo mediciones; `alertas` guarda el ciclo de vida completo con `estado` (activa, atendida o falsa alarma), `atendida_por` (clave foránea al cuidador) y `atendida_en`. La API pasa a actualizar `alertas`.
3. **Hogares, pacientes y cuidadores (D5).** `cuidadores.id` es el mismo identificador de Supabase Auth, y la tabla `cuidador_hogar` indica qué hogares puede ver cada cuidador. Con eso las políticas RLS pasan a ser por usuario, por ejemplo: `hogar_id IN (SELECT hogar_id FROM cuidador_hogar WHERE cuidador_id = auth.uid())`. **Habilita HU-17.** El paciente se guarda solo con seudónimo, iniciales y hash del RUT; el hogar, solo con la comuna.
4. **Integridad (D6, D7, D8).** Claves foráneas `lecturas.sensor_id → sensores.id` y `sensores.hogar_id → hogares.id`; restricciones `CHECK` para tipos de sensor, severidad y estado; `jsonb` en todos los campos JSON; se elimina `payload_fhir`.
5. **Fechas siempre con zona horaria (D4).** Todas las columnas de fecha pasan a `timestamptz`, guardadas en UTC y mostradas en hora de Chile.
6. **Consentimiento en el servidor (D9).** Tabla `consentimientos` con versión del texto, fecha de aceptación y fecha de revocación.
7. **Auditoría de accesos (D10).** Tabla `auditoria` con quién consultó, atendió o exportó datos, y cuándo.
8. **Retención (D11).** Las lecturas normales (sin alerta) se resumen por hora y se borran después de 30 días; las lecturas con alerta y las alertas se conservan. El plazo se define junto con la política de privacidad.
9. **Índices pensados para las consultas reales.** Índice parcial para las alertas activas (`WHERE estado = 'activa'`) e índice compuesto `(sensor_id, medido_en DESC)` para el historial.

## 4. Plan de trabajo

| Etapa | Cambios | Sprint | Historias o hallazgos relacionados | Prueba que la valida |
|---|---|---|---|---|
| 1 ✅ | Migraciones versionadas en el repositorio (D12) y fechas `timestamptz` (D4) | Sprint 4 (completada 06-10-2026) | Ajustes 1 y 12 | PU-05 (9/9) y PI-06 (aprobada) |
| 2 | UUID en el borde, `origen`, `medido_en` y `recibido_en`, y reenvío idempotente (D2, D3) | Sprint 4 | HU-03 | PR-03 repetida: 100 % de los eventos del borde llegan a Supabase, sin duplicados |
| 3 ✅ | `alertas` como única fuente de verdad de la atención (D1) | Sprint 4 (completada 06-10-2026) | Ajustes 15 y 17, HU-06 | PU-06 (13/13) y PI-07 (PS-01b repetida, 3/3) |
| 4 | Hogares, pacientes, cuidadores y RLS por cuidador (D5) | Sprint 5 | HU-17 | PS-03: un cuidador no ve los datos de un hogar que no es suyo |
| 5 | Claves foráneas, `CHECK` y `jsonb` (D6, D7, D8) | Sprint 5 | — | PU de restricciones: un tipo inválido se rechaza |
| 6 | Consentimiento en el servidor, auditoría y retención (D9, D10, D11) | Post-prototipo | Ley N° 21.719 | Auditoría SQL |

### 4.1 Etapa 1 completada (06-10-2026, commit a0aadd7)

- **Decisión:** en lugar de Alembic o Supabase CLI se usaron archivos SQL numerados en `backend/migrations/` y una tabla `schema_migrations` que registra cuáles se aplicaron. Es más simple para un equipo de una persona, no agrega dependencias y se ejecuta desde el SQL Editor de Supabase. Alembic queda como opción si el equipo crece.
- **Migración 000:** describe el esquema que ya existía (tablas, índices, triggers con `search_path` fijo y RLS). Usa `IF NOT EXISTS` y `CREATE OR REPLACE`, así que no cambia nada en producción y sirve para crear la base desde cero.
- **Migración 001:** cambia `eventos.timestamp` y `sensores.creado_en` a `timestamptz`. Cada fila existente se convirtió según su origen: el simulador enviaba hora de Chile sin zona y los scripts de prueba enviaban UTC.
- **Código:** `backend/tiempo.py` centraliza las fechas. Todo se guarda y se entrega en UTC con zona, y una lectura de sensor sin zona se interpreta como hora de Chile.
- **Respaldo previo:** `backend/scripts/respaldo_supabase.py` exporta las tablas a JSON fuera del repositorio.
- **Pendiente menor:** comprobar la reconstrucción completa desde cero (migraciones 000 y 001 sobre un PostgreSQL vacío, por ejemplo con Docker) y repetir la prueba en cada etapa siguiente.

### 4.2 Etapa 3 completada (06-10-2026, commit f1de2d5 y migración 002)

- **Código:** `backend/alertas_servicio.py` crea la alerta en la misma transacción que el evento y registra la atención en `alertas`. Si la alerta ya existe, la reutiliza. Eso permitió desplegar el código antes de eliminar el trigger sin crear duplicados.
- **Migración 002:** copió a `alertas` la atención de 1.463 alertas que solo estaba en `eventos`, eliminó el trigger `crear_alerta_automatica` y agregó un índice único por evento y un índice parcial para las alertas activas.
- **Modo borde:** como la alerta la crea el backend, la tabla `alertas` existe también en SQLite (ajuste 15).
- **Pendiente:** eliminar las columnas obsoletas `eventos.resuelto*` cuando el panel lea la atención desde `alertas` (etapa 5), y actualizar los diagramas 05 y 08 y las fichas 05 y 11, que todavía describen el trigger.

## 5. Riesgos y cuidados de la migración

- **Hacer respaldo antes de cada etapa:** exportar las tablas actuales desde Supabase (Database → Backups o `pg_dump`).
- **Migrar sin cortar el servicio:** crear las tablas nuevas, copiar los datos y cambiar la API en un despliegue; las tablas antiguas se borran solo cuando las pruebas pasen.
- **Mantener el modo borde compatible:** SQLite debe usar el mismo esquema (UUID como texto, fechas ISO 8601 con zona).
- **Actualizar la documentación:** diagrama ER, matriz de trazabilidad, registro de pruebas y fichas técnicas 05, 10 y 11.
