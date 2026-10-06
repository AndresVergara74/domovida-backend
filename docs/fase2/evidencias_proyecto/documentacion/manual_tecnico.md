# DomoVida · Manual técnico

**Proyecto APT:** DomoVida: Plataforma IoT de Monitoreo y Asistencia para el Adulto Mayor en el Hogar
**Autor:** Andrés Rodrigo Vergara Acevedo · Capstone PTY4614 · Duoc UC, sede Viña del Mar
**Versión:** 6 de octubre de 2026 (formato según la Guía de apoyo del estudiante, sección 8)

Este manual permite que otra persona instale, configure, ejecute, pruebe y opere DomoVida sin consultar al autor. La versión breve está en el [README](../../../../README.md).

---

## 1. Componentes del sistema

| Componente | Tecnología | Carpeta | Producción |
|---|---|---|---|
| API | Python 3.11, FastAPI, SQLAlchemy, Uvicorn | `backend/` | Render (Oregón, EE. UU.) |
| Panel del cuidador | React 18, TypeScript, Vite | `frontend/` | Vercel |
| Base de datos y autenticación | PostgreSQL + Supabase Auth | — | Supabase (São Paulo, Brasil) |
| Base local (modo borde) | SQLite | `backend/*.db` (no se sube) | Computador del hogar |
| Simulador de sensores | Python | `backend/simulate_sensors.py` | Computador del hogar |
| Notificaciones push | ntfy.sh | `backend/notifier.py` | Servicio público ntfy.sh |

La arquitectura, el despliegue y los flujos están dibujados en [`docs/fase2/diagramas`](../../diagramas/README.md).

## 2. Requisitos

| Herramienta | Versión probada | Uso |
|---|---|---|
| Docker y Docker Compose | Docker 24+, Compose v2 | Ejecutar todo con un comando |
| Python | 3.11 (`backend/runtime.txt`: 3.11.9) | Backend, simulador y pruebas |
| Node.js y npm | Node 18+ (probado con 18 y 22) | Panel |
| Git | cualquiera reciente | Clonar el repositorio |

**Recursos mínimos:** 2 GB de RAM libres, 2 GB de disco y los puertos **80** (panel en Docker), **8000** (API) y **5173** (panel en desarrollo) libres.

**Cuentas necesarias solo para producción:** GitHub, Render, Vercel y Supabase (planes gratuitos), y la app **ntfy** en el celular del cuidador.

## 3. Instalación y configuración

```bash
git clone https://github.com/AndresVergara74/domovida-backend.git
cd domovida-backend
copy .env.example .env        # Windows (PowerShell)
cp .env.example .env          # Linux / macOS
```

Todas las variables están explicadas en [`.env.example`](../../../../.env.example). **Ninguna es obligatoria para ejecutar en local**: sin valores, el sistema usa SQLite y no exige clave ni sesión.

| Variable | Servicio | Para qué sirve | Si está vacía |
|---|---|---|---|
| `DATABASE_URL` / `DOCKER_DATABASE_URL` | API | Conexión a la base (SQLite o PostgreSQL de Supabase por Session Pooler, puerto 6543) | SQLite local |
| `NTFY_TOPIC` | API | Tópico ntfy del cuidador (usar un nombre difícil de adivinar) | Valor por defecto |
| `DOMOVIDA_API_KEY` | API y simulador | Clave que exigen los sensores (cabecera `X-API-Key`) | Se aceptan datos sin clave |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | API | Validar la sesión del cuidador | Atender alertas no exige sesión |
| `CORS_ORIGINS` | API | Orígenes web extra permitidos | Solo localhost y Vercel |
| `PUERTA_HORA_NOCHE_INICIO`, `PUERTA_HORA_NOCHE_FIN`, `PUERTA_MINUTOS_MAX_ABIERTA` | API | Regla de la puerta principal | 22, 7 y 10 |
| `VITE_API_URL`, `VITE_WS_URL` | Panel | Dirección de la API y del WebSocket | `localhost:8000` |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | Panel | Inicio de sesión del cuidador | No aparece el botón «Ingresar» |

**Reglas de seguridad de la configuración:**
- El archivo `.env` real **nunca** se sube a GitHub (está en `.gitignore`).
- `SUPABASE_ANON_KEY` es la clave **pública** (anon o publishable). Nunca usar la `service_role` ni la `secret`.
- Generar la clave de los sensores directamente en un archivo, sin copiarla a chats ni consolas:
  ```powershell
  python -c "import secrets; open(r'C:\ruta\segura\domovida_api_key.txt','w').write(secrets.token_urlsafe(32))"
  ```

## 4. Ejecución

### 4.1 Con Docker (recomendado para revisar el proyecto)

```bash
docker compose up --build      # iniciar
docker compose down            # detener (los datos de SQLite quedan en el volumen backend_data)
```

| Servicio | URL |
|---|---|
| Panel | http://localhost |
| API y documentación interactiva | http://localhost:8000/docs |
| Estado del sistema | http://localhost:8000/api/health |

### 4.2 Sin Docker (desarrollo)

```bash
# Terminal 1 · API (carpeta backend)
python -m venv venv
venv\Scripts\activate                 # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 · Panel (carpeta frontend)
npm install
npm run dev                           # http://localhost:5173

# Terminal 3 · Simulador (carpeta backend)
python simulate_sensors.py
```

Si la API tiene `DOMOVIDA_API_KEY`, el simulador necesita la misma clave:

```powershell
$env:DOMOVIDA_API_KEY = Get-Content C:\ruta\segura\domovida_api_key.txt
$env:DOMOVIDA_API_URL = "http://localhost:8000"     # o la URL de Render
python simulate_sensors.py
```

### 4.3 Modo borde (sin internet)

1. Ejecutar la API con `DATABASE_URL=sqlite:///./domovida_offline.db` y **sin** `SUPABASE_URL` (sin internet, Supabase no es alcanzable).
2. Ejecutar el panel local con `VITE_API_URL=http://localhost:8000`.
3. Las caídas se guardan en SQLite y llegan al panel local por WebSocket; ntfy falla sin internet y la API sigue funcionando (prueba PR-03).
4. **Limitación conocida:** al volver internet, los eventos de SQLite no se suben solos a Supabase (HU-03 reabierta, ficha técnica 19).

### 4.4 Usuarios de prueba

El cuidador se crea en Supabase → **Authentication → Users → Add user → Create new user**, con **Auto Confirm User** marcado. Sus credenciales se guardan fuera del repositorio. Sin `SUPABASE_URL` no se necesita usuario.

## 5. Despliegue en producción

| Servicio | Configuración |
|---|---|
| **Supabase** | Proyecto PostgreSQL con las tablas `sensores`, `eventos` y `alertas`; triggers `crear_alerta_automatica` y `marcar_como_sincronizado` (ficha técnica 11), ambos con `search_path=public`; RLS activo en las tres tablas (pruebas PI-03 y PI-03b); usuario cuidador en Supabase Auth. |
| **Render** (API) | Servicio web Python conectado al repositorio de GitHub, rama `main`, con despliegue automático. Comando de inicio: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` (`backend/Procfile`). Variables: `DATABASE_URL`, `NTFY_TOPIC`, `DOMOVIDA_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `PYTHON_VERSION`. |
| **Vercel** (panel) | Proyecto conectado al repositorio, carpeta `frontend`, compilación `npm run build`, despliegue automático. Variables: `VITE_API_URL`, `VITE_WS_URL`, `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` (marcadas como no sensibles, porque son públicas). Después de cambiar una variable se necesita **Redeploy**. |
| **AWS EC2** (entorno de prueba) | Instancia con Docker; `git clone` y `docker compose up --build`; agregar la IP pública en `CORS_ORIGINS`. Sin https: el consentimiento no puede calcular el hash SHA-256 (ajuste 11). |

**Verificación después de cada despliegue:** abrir `https://domovida-backend.onrender.com/api/health` y comprobar `"estado_general": "healthy"`, `"clave_api_sensores": {"activa": true}` y `"auth_cuidador": {"activa": true}`; luego abrir el panel y verificar «API conectada» y «Tiempo real activo».

## 6. Operación y mantenimiento

| Tarea | Cómo hacerlo | Frecuencia |
|---|---|---|
| Mantener Supabase activo | Abrir el panel publicado (el plan gratuito pausa el proyecto por inactividad) | Semanal |
| Revisar la seguridad | Supabase → Advisors → Security Advisor | Al cierre de cada sprint |
| Cambiar la clave de los sensores | Generar una nueva (sección 3), reemplazarla en Render y en el simulador, y comparar la huella en `/api/health` (largo 43 y los mismos 8 caracteres que la clave local) | Si se expone o cada 6 meses |
| Revisar errores | Render → Logs; Vercel → Deployments; consola del navegador (F12) | Ante cualquier falla |
| Respaldar la base | Supabase → Database → Backups, o `pg_dump` con la cadena de conexión | Antes de cualquier cambio de estructura |

## 7. Pruebas

El plan, los resultados y las evidencias están en [`pruebas/registro_pruebas.md`](pruebas/registro_pruebas.md), con prefijos PU (unitarias), PI (integración), PR (rendimiento) y PS (seguridad). La relación entre requisitos y pruebas está en [`trazabilidad.xlsx`](trazabilidad.xlsx).

```bash
# Pruebas automatizadas (carpeta backend) · requieren: pip install httpx "fhir.resources>=8"
python test_reglas_puerta.py        # PU-04
python test_seguridad.py            # PS-01
python test_auth_cuidador.py        # PS-01b
python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-04_validacion_fhir.py
python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-05_validacion_fhir_patient.py
```

Las pruebas en producción (PR-01, PR-02, PR-03, PS-01 y PS-01b) se ejecutan pegando el script `.js` correspondiente en la consola del navegador (F12) con el panel publicado abierto, porque la API solo acepta peticiones desde los orígenes permitidos por CORS.

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| El puerto 80, 8000 o 5173 está ocupado | Otra aplicación lo usa | Cerrarla o cambiar el puerto en `docker-compose.yml` o en el comando |
| La API en Render tarda hasta 1 minuto | El plan gratuito suspende el servicio sin uso | Esperar y recargar |
| La API no arranca: error de conexión a la base | Supabase pausado por inactividad | Reactivar el proyecto en el panel de Supabase |
| No se conecta a PostgreSQL desde el computador | El proveedor de internet bloquea el puerto 5432 | Usar el Session Pooler (puerto 6543) |
| `401 Clave de API ausente o inválida` | El simulador no tiene la misma clave que Render | Comparar la huella en `/api/health` con la de la clave local |
| `401` al presionar «Atender» | La sesión del cuidador expiró (1 hora) | Presionar «Ingresar» otra vez |
| «blocked by CORS policy» en la consola | El script se ejecutó desde otra página | Ejecutarlo en la pestaña del panel (`domovida-backend.vercel.app`) |
| El panel no muestra «Ingresar» | Faltan las variables `VITE_SUPABASE_*` o no se hizo Redeploy | Agregarlas en Vercel y redesplegar |
| No llegan avisos al celular | La app ntfy no está suscrita o Android limita la batería | Suscribirse al tópico y permitir uso en segundo plano |
| El panel muestra «API desconectada» | El despliegue de Vercel falló | Revisar Vercel → Deployments y corregir el error de compilación |
| `git push` falla con «Connection was reset» | Corte momentáneo de la red | Repetir `git push` |

## 9. Estructura del repositorio

```
domovida-backend/
├── README.md · .env.example · docker-compose.yml · .gitignore
├── backend/            API FastAPI, simulador, pruebas automatizadas, Dockerfile
├── frontend/           Panel React + Vite, Dockerfile
└── docs/
    ├── fase1/          Guía 1.5 y evidencias de la Fase 1
    ├── fase2/
    │   ├── diagramas/              8 diagramas de diseño (Mermaid y PNG)
    │   ├── evidencias_grupales/    Guías 2.4 y 2.6
    │   └── evidencias_proyecto/documentacion/
    │       ├── agil/               Product Vision, Product Backlog, DoD, fichas de sprint
    │       ├── capturas/           Evidencias de las pruebas
    │       ├── fichas_tecnicas/    Fichas técnicas del sistema
    │       ├── pruebas/            Registro de pruebas y scripts
    │       ├── manual_tecnico.md   Este documento
    │       └── trazabilidad.xlsx   Matriz de trazabilidad
    └── fase3/          Evaluación de usabilidad (SUS), pendiente
```
