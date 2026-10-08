# Migraciones de la base de datos (Supabase/PostgreSQL)

Cada cambio de estructura de la base se escribe como un archivo SQL numerado y se versiona en el repositorio (ficha técnica 19, problema D12). Así la base se puede reconstruir desde cero y revisar su historial.

| Archivo | Contenido | Aplicada en producción |
|---|---|---|
| `000_esquema_base.sql` | Esquema existente al 06-10-2026: tablas `sensores`, `eventos` y `alertas`, triggers, RLS, índices y la tabla de control `schema_migrations` | 06-10-2026 (solo la tabla de control; el resto ya existía) |
| `001_fechas_con_zona_horaria.sql` | Fechas `timestamptz` en UTC (problema D4) | 06-10-2026 |
| `002_alertas_fuente_unica.sql` | `alertas` como fuente única de verdad de la atención; el backend crea la alerta y se elimina el trigger `crear_alerta_automatica` (D1, ajuste 17) | 06-10-2026 |
| `003_sincronizacion_borde.sql` | Columnas `uuid`, `origen` y `notificado` en `eventos` para sincronizar el modo borde sin duplicados (HU-03, D2 y D3). Se aplica **antes** de desplegar el código | 08-10-2026 |

## Cómo aplicar una migración

1. **Respaldar** la base: `python scripts/respaldo_supabase.py` (carpeta `backend`).
2. Abrir Supabase → **SQL Editor** → **New query**, pegar el archivo completo y presionar **Run**. Cada archivo corre dentro de una transacción: si algo falla, no se aplica nada.
3. Verificar con la consulta final que trae cada archivo.
4. Comprobar qué migraciones están aplicadas:
   ```sql
   SELECT * FROM public.schema_migrations ORDER BY version;
   ```

## Reglas

- Nunca editar una migración ya aplicada: los cambios nuevos van en un archivo nuevo con el número siguiente.
- Cada archivo registra su versión en `schema_migrations` al final.
- Los cambios hechos a mano en el panel de Supabase deben pasarse a una migración el mismo día.
