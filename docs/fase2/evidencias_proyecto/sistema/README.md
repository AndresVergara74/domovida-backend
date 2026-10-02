# Evidencias de sistema — DomoVida

## Aplicación
- Backend (FastAPI): [`/backend`](../../../../backend) · publicado en https://domovida-backend.onrender.com (documentación en `/docs`)
- Frontend (React + Vite + TypeScript): [`/frontend`](../../../../frontend) · publicado en https://domovida-backend.vercel.app
- Contenedores: [`docker-compose.yml`](../../../../docker-compose.yml), `backend/Dockerfile`, `frontend/Dockerfile` (réplica ejecutada en AWS Academy EC2)
- Simulador de 8 sensores: [`backend/simulate_sensors.py`](../../../../backend/simulate_sensors.py)

## Base de datos
- Supabase / PostgreSQL (nube) y SQLite3 (Edge local).
- Triggers `sync_status` y `crear_alerta_automatica`, y políticas RLS: ver la ficha técnica [11_triggers_supabase.md](../documentacion/fichas_tecnicas/11_triggers_supabase.md) y [10_conexion_supabase.md](../documentacion/fichas_tecnicas/10_conexion_supabase.md).
- Pruebas sobre la base de datos (PI-02 trigger, PI-03 RLS): [registro_pruebas.md](../documentacion/pruebas/registro_pruebas.md).
