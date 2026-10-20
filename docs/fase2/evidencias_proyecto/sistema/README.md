# Evidencias de sistema — DomoVida

## Aplicación
- Backend (FastAPI): [`/backend`](../../../../backend) · publicado en https://domovida-backend.onrender.com (documentación en `/docs`)
- Frontend (React + Vite + TypeScript): [`/frontend`](../../../../frontend) · publicado en https://domovida-backend.vercel.app
- Contenedores: [`docker-compose.yml`](../../../../docker-compose.yml), `backend/Dockerfile`, `frontend/Dockerfile` (réplica ejecutada en AWS Academy EC2)
- Servidor en Chile: Oracle Cloud Chile Central (Santiago), backend + SQLite en la misma máquina, con HTTPS (Caddy + Let's Encrypt): https://domovida.duckdns.org/api/health · configuración en [`infra/oracle`](../../../../infra/oracle) · pruebas PR-01c (latencia 54 ms) y PR-04 (carga, 20 usuarios, p95 < 200 ms)
- Simulador de 8 sensores: [`backend/simulate_sensors.py`](../../../../backend/simulate_sensors.py)

## Base de datos
- Supabase / PostgreSQL (nube) y SQLite3 (Edge local y servidor Oracle).
- Esquema versionado con migraciones en [`backend/migrations`](../../../../backend/migrations): `000_esquema_base.sql`, `001_fechas_con_zona_horaria.sql`, `002_alertas_fuente_unica.sql` y `003_sincronizacion_borde.sql` (pruebas PI-06, PI-07 y PI-08).
- Sincronización del modo borde con la nube (almacenamiento y reenvío): [`backend/sincronizador.py`](../../../../backend/sincronizador.py) · pruebas PU-07 y PR-03b.
- Triggers `sync_status` y `crear_alerta_automatica`, y políticas RLS: ver la ficha técnica [11_triggers_supabase.md](../documentacion/fichas_tecnicas/11_triggers_supabase.md) y [10_conexion_supabase.md](../documentacion/fichas_tecnicas/10_conexion_supabase.md).
- Pruebas sobre la base de datos (PI-02 trigger, PI-03 RLS): [registro_pruebas.md](../documentacion/pruebas/registro_pruebas.md).
