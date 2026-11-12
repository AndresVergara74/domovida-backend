# DomoVida

**Plataforma IoT de monitoreo y asistencia para el adulto mayor en el hogar.**

DomoVida detecta caídas y otros eventos de riesgo en el hogar de una persona mayor que vive sola y alerta al cuidador en tiempo real, en el panel web y en el celular. Es el proyecto APT de la asignatura Capstone (PTY4614) de Ingeniería en Informática, Duoc UC, sede Viña del Mar.

| | |
|---|---|
| **Panel del cuidador** | https://domovida-backend.vercel.app |
| **API en producción (Oracle Cloud Santiago)** | https://domovida.duckdns.org/api/health |
| **API de respaldo (documentación interactiva)** | https://domovida-backend.onrender.com/docs |
| **Tablero Kanban (Scrum)** | https://github.com/users/AndresVergara74/projects/1 |
| **Autor** | Andrés Rodrigo Vergara Acevedo |

> Desde el 31/10/2026 el panel usa el servidor de Oracle Cloud en Santiago (Always Free). Render + Supabase quedan como respaldo en la nube y reciben una copia de los eventos; el servidor gratuito de Render se suspende sin uso, por lo que su primera consulta puede tardar hasta 1 minuto.

---

## 1. Qué hace

- **Simula 8 sensores** del hogar: caídas (acelerómetro), movimiento e inactividad (PIR), gas, humo, apertura de puerta, frecuencia cardíaca y SpO2, y botón de pánico.
- **Detecta eventos de riesgo** en el backend con reglas de umbral (caída sobre 17 m/s², gas sobre 500 ppm, humo sobre 800, inactividad sobre 30 minutos) y la regla de la puerta principal: alerta si se abre de noche (22:00–07:00) o si queda abierta 10 minutos o más.
- **Semáforo del hogar:** verde si todo está en orden, amarillo si un sensor deja de enviar datos por más de 10 minutos y rojo ante una alerta. Colores con contraste según WCAG 2.1.
- **Alerta al cuidador** en el panel por WebSocket y en el celular con notificaciones push (ntfy).
- **Registra la atención** de cada alerta: el cuidador inicia sesión y queda guardado quién la atendió y a qué hora.
- **Funciona sin internet** en modo borde (SQLite local).
- **Interoperabilidad HL7 FHIR R4:** recursos `Observation` y `Patient` seudonimizado.
- **Protección de datos** según los principios de la Ley N° 21.719: seudonimización SHA-256, RLS en Supabase, clave de API para los sensores y sesión para el cuidador.

## 2. Arquitectura

```
 Sensores (simulador)            Panel del cuidador (React + Vite)
        │  HTTPS + X-API-Key              │  HTTPS / WebSocket  (Vercel)
        ▼                                 ▼
 ┌──────────────────────────────────────────────┐        ┌─────────────┐
 │  API FastAPI + SQLite · Oracle Cloud Santiago│──────▶ │   ntfy.sh   │──▶ celular
 │  Docker + Caddy (HTTPS) · Always Free        │        └─────────────┘
 │  reglas · alertas · WebSocket · FHIR · auth  │
 └───────────────┬──────────────────────────────┘
                 │ sincronización (cada 30 s)    ┌──────────────────────────────┐
                 └──────────────────────────────▶│ Respaldo en la nube:          │
                                                 │ API en Render + Supabase      │
                                                 │ PostgreSQL (RLS, triggers)    │
                                                 └──────────────────────────────┘
 Supabase Auth valida la sesión del cuidador en ambos servidores.
```

| Componente | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Uvicorn |
| Frontend | React 18, TypeScript, Vite, Recharts, Leaflet |
| Base de datos | SQLite (servidor de Santiago y modo borde) · Supabase PostgreSQL (respaldo en la nube) |
| Tiempo real y notificaciones | WebSocket · ntfy.sh |
| Autenticación | Clave de API (sensores) · Supabase Auth (cuidador) |
| Interoperabilidad | HL7 FHIR R4 (SNOMED CT, LOINC) |
| Contenedores | Docker y Docker Compose |
| Despliegue | Oracle Cloud Santiago, VM Always Free con Docker y Caddy (API) · Vercel (panel) · Render (API de respaldo) · probado también en AWS EC2 |

## 3. Requisitos

| Herramienta | Versión probada | Para qué |
|---|---|---|
| Docker y Docker Compose | Docker 24+ · Compose v2 | Ejecutar todo con un comando |
| Git | cualquiera reciente | Clonar el repositorio |
| Python | 3.11 | Solo si se ejecuta sin Docker, el simulador o las pruebas |
| Node.js y npm | Node 18+ | Solo si se ejecuta el panel sin Docker |

Recursos mínimos: 2 GB de RAM libres, 2 GB de disco y los puertos **80** y **8000** libres.

## 4. Instalación y ejecución con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/AndresVergara74/domovida-backend.git
cd domovida-backend

# 2. Crear el archivo de configuración a partir de la plantilla
copy .env.example .env        # Windows (PowerShell)
cp .env.example .env          # Linux / macOS

# 3. (Opcional) completar .env. Con los valores por defecto funciona en local con SQLite.

# 4. Construir y levantar los servicios
docker compose up --build
```

| Servicio | URL |
|---|---|
| Panel del cuidador | http://localhost |
| API y documentación | http://localhost:8000/docs |
| Estado del sistema | http://localhost:8000/api/health |

Para detener: `docker compose down` (los datos de SQLite se conservan en el volumen `backend_data`).

## 5. Ejecución sin Docker (desarrollo)

**Backend** (desde la carpeta `backend`):

```bash
python -m venv venv
venv\Scripts\activate          # Windows   ·   source venv/bin/activate en Linux/macOS
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Panel** (desde la carpeta `frontend`, en otra terminal):

```bash
npm install
npm run dev                    # http://localhost:5173
```

**Simulador de sensores** (desde `backend`, en otra terminal):

```bash
python simulate_sensors.py
```

Si el backend tiene definida `DOMOVIDA_API_KEY`, el simulador debe usar la misma clave. En PowerShell, por ejemplo, se puede cargar desde un archivo fuera del repositorio:

```powershell
$env:DOMOVIDA_API_KEY = Get-Content C:\ruta\segura\domovida_api_key.txt
$env:DOMOVIDA_API_URL = "http://localhost:8000"
python simulate_sensors.py
```

**Modo borde (sin internet):** ejecutar el backend con `DATABASE_URL=sqlite:///./domovida_offline.db` y el panel local. Con `NUBE_API_URL` y `NUBE_API_KEY`, los eventos guardados sin conexión se suben solos a la nube al volver internet (HU-03; ver manual técnico, sección 4.3). Sin `SUPABASE_URL`, atender alertas no exige sesión, porque Supabase no es alcanzable sin conexión.

## 6. Variables de entorno

Todas están documentadas en [`.env.example`](.env.example), sin valores reales. Las principales:

| Variable | Dónde | Descripción |
|---|---|---|
| `DATABASE_URL` / `DOCKER_DATABASE_URL` | backend | Base de datos (SQLite o PostgreSQL de Supabase) |
| `NTFY_TOPIC` | backend | Tópico ntfy de las notificaciones del cuidador |
| `DOMOVIDA_API_KEY` | backend y simulador | Clave de los sensores (cabecera `X-API-Key`) |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | backend | Validación de la sesión del cuidador |
| `PROTEGER_LECTURAS` | backend | Con `1`, las consultas de datos exigen la sesión del cuidador (HU-17); vacío = abiertas |
| `NUBE_API_URL`, `NUBE_API_KEY`, `SYNC_INTERVALO_SEG` | backend | Sincronización con la API de respaldo (modo borde y servidor de Santiago) |
| `VITE_API_URL`, `VITE_WS_URL` | panel | Dirección de la API y del WebSocket |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | panel | Inicio de sesión del cuidador (valores públicos) |

**Usuario cuidador:** se crea en Supabase → *Authentication → Users → Add user*. Sus credenciales no se publican en el repositorio.

## 7. Pruebas

Plan, resultados y evidencias en [`registro_pruebas.md`](docs/fase2/evidencias_proyecto/documentacion/pruebas/registro_pruebas.md), con prefijos **PU** (unitarias), **PI** (integración), **PR** (rendimiento) y **PS** (seguridad).

Pruebas automatizadas (desde `backend`, con `pip install httpx "fhir.resources>=8"`):

```bash
python test_reglas_sensores.py    # PU-02 · reglas de detección por umbral
python test_reglas_puerta.py      # PU-04 · regla de la puerta principal
python test_tiempo.py             # PU-05 · fechas en UTC con zona horaria
python test_alertas.py            # PU-06 · alertas como fuente única de verdad
python test_lecturas.py           # PS-01c · consultas de lectura con sesión (HU-17)
python test_sincronizacion.py     # PU-07 · sincronización del modo borde (HU-03)
python test_seguridad.py          # PS-01 · clave de API de los sensores
python test_auth_cuidador.py      # PS-01b · sesión del cuidador
python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-04_validacion_fhir.py          # FHIR Observation
python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-05_validacion_fhir_patient.py  # FHIR Patient
```

Resultados principales del prototipo:

| Prueba | Resultado |
|---|---|
| PR-01 / PR-01c · Latencia de la alerta (30 caídas) | 100 % recibidas; 1.577 ms en Render + Supabase, 216 ms en AWS EC2, **54 ms en Oracle Santiago** |
| PR-02 · Notificaciones ntfy en el celular | 30/30 (100 %) |
| PR-03 · Continuidad sin internet (modo borde) | 10/10 caídas guardadas y mostradas |
| PU-07 / PR-03b · Sincronización del modo borde con la nube | 13/13; 5/5 caídas subidas a Supabase al volver internet, sin duplicados |
| PI-03 / PI-03b · RLS con rol anónimo | 0 filas visibles |
| PI-04 / PI-05 · HL7 FHIR R4 | Observation, Bundle y Patient válidos |
| PS-01 / PS-01b · Autenticación | 3/3 y 3/3 en producción |
| PU-05 / PI-06 · Fechas en UTC y migraciones | 9/9; base migrada a `timestamptz` sin pérdida de datos |
| PU-06 / PI-07 · `alertas` como fuente única de verdad | 13/13; 1.463 diferencias corregidas, 0 duplicados |
| PU-02 · Reglas de detección por umbral | 17/17 |
| PR-04 · Carga con Locust (20 usuarios) | 976 solicitudes, 0 errores; p95 bajo 200 ms |
| PR-05 · Flujo crítico con el panel en Oracle Santiago | Aprobada: alerta al instante, aviso en el celular y atención registrada |
| PI-09 / PU-10 · Semáforo y contraste WCAG 2.1 | Aprobadas |
| Escala SUS con 7 cuidadores | Media 92,1 (meta 70) |

Los cambios en la estructura de la base de datos se hacen con migraciones numeradas en [`backend/migrations/`](backend/migrations/README.md).

## 8. Solución de problemas

| Problema | Solución |
|---|---|
| El puerto 80 u 8000 está ocupado | Cerrar la aplicación que lo usa o cambiar el puerto en `docker-compose.yml` |
| El panel muestra «API desconectada» | Revisar `https://domovida.duckdns.org/api/health`; si el servidor de Santiago no responde, ver el manual técnico (sección 5.1) |
| La API de respaldo en Render tarda al primer intento | El plan gratuito se suspende sin uso; esperar 1 minuto y recargar |
| El backend no arranca con Supabase | El plan gratuito de Supabase pausa el proyecto por inactividad; reactivarlo en el panel de Supabase |
| `401 Clave de API ausente o inválida` | El sensor o simulador no envía la misma `DOMOVIDA_API_KEY` del backend |
| `401` al atender una alerta | La sesión del cuidador expiró (dura 1 hora); volver a presionar «Ingresar» |
| No llegan notificaciones al celular | Suscribirse al tópico de `NTFY_TOPIC` en la app ntfy y quitar el ahorro de batería |

## 9. Documentación del proyecto

| Documento | Ubicación |
|---|---|
| Definición del proyecto (Fase 1, Guía 1.5) | [`docs/fase1/evidencias_grupales`](docs/fase1/evidencias_grupales) |
| Avance e informe final (Fase 2, Guías 2.4 y 2.6) | [`docs/fase2/evidencias_grupales`](docs/fase2/evidencias_grupales) |
| Presentación y guion | [`docs/fase2/evidencias_proyecto/presentacion`](docs/fase2/evidencias_proyecto/presentacion) |
| **Manual técnico** (instalación, despliegue, operación y solución de problemas) | [`manual_tecnico.md`](docs/fase2/evidencias_proyecto/documentacion/manual_tecnico.md) |
| Diagramas de diseño (arquitectura, despliegue, secuencia, casos de uso, datos y seguridad) | [`docs/fase2/diagramas`](docs/fase2/diagramas) |
| Matriz de trazabilidad y Product Backlog | [`trazabilidad.xlsx`](docs/fase2/evidencias_proyecto/documentacion/trazabilidad.xlsx) · [`product_backlog.xlsx`](docs/fase2/evidencias_proyecto/documentacion/agil/product_backlog.xlsx) |
| Fichas técnicas (arquitectura, datos, decisiones) | [`docs/fase2/evidencias_proyecto/documentacion/fichas_tecnicas`](docs/fase2/evidencias_proyecto/documentacion/fichas_tecnicas) |
| Fichas de sprint, retrospectivas y Definition of Done | [`docs/fase2/evidencias_proyecto/documentacion/agil`](docs/fase2/evidencias_proyecto/documentacion/agil) |
| Registro de pruebas y evidencias | [`docs/fase2/evidencias_proyecto/documentacion/pruebas`](docs/fase2/evidencias_proyecto/documentacion/pruebas) |

### Mapa de entregables según la Guía de apoyo del estudiante

La Guía sugiere una estructura de carpetas (sección 11). Para no romper los enlaces y el historial ya entregados en las Fases 1 y 2, el repositorio conserva su estructura por fases; esta tabla indica dónde está cada entregable.

| Etapa / sección de la Guía | Entregable | Ubicación en este repositorio |
|---|---|---|
| 1. Inicio (3) | Documento de inicio | [`docs/fase1/evidencias_grupales`](docs/fase1/evidencias_grupales) (Guía 1.5) |
| 2. Requisitos (5.1, 5.2) | Product Vision y Product Backlog | [`agil/product_vision.md`](docs/fase2/evidencias_proyecto/documentacion/agil/product_vision.md) · [`product_backlog.xlsx`](docs/fase2/evidencias_proyecto/documentacion/agil/product_backlog.xlsx) |
| 3. Planificación (5.3) | Tablero Kanban y cronograma | [GitHub Projects](https://github.com/users/AndresVergara74/projects/1) · [`docs/fase1/evidencias_grupales/planificacion`](docs/fase1/evidencias_grupales/planificacion) |
| 4. Diseño (6) | Arquitectura, modelo de datos, UML, Docker | [`docs/fase2/diagramas`](docs/fase2/diagramas) · [`fichas_tecnicas`](docs/fase2/evidencias_proyecto/documentacion/fichas_tecnicas) · [`docker-compose.yml`](docker-compose.yml) |
| 5. Desarrollo | Código por incrementos | [`backend/`](backend) · [`frontend/`](frontend) · historial de commits |
| 5.4 | Definition of Done | [`definition_of_done.md`](docs/fase2/evidencias_proyecto/documentacion/agil/definition_of_done.md) |
| 5.5, 5.6 | Fichas de sprint y retrospectivas | [`docs/fase2/evidencias_proyecto/documentacion/agil`](docs/fase2/evidencias_proyecto/documentacion/agil) |
| 6. Pruebas (7) | Plan, casos, scripts y evidencias (PU, PI, PR, PS) | [`registro_pruebas.md`](docs/fase2/evidencias_proyecto/documentacion/pruebas/registro_pruebas.md) · [`pruebas/`](docs/fase2/evidencias_proyecto/documentacion/pruebas) · [`capturas/`](docs/fase2/evidencias_proyecto/documentacion/capturas) · pruebas `backend/test_*.py` |
| 6. Pruebas con usuarios | Escala SUS (7 cuidadores) | [`usabilidad/`](docs/fase2/evidencias_proyecto/documentacion/usabilidad) |
| 7. Despliegue (8) | Manual técnico y README | [`manual_tecnico.md`](docs/fase2/evidencias_proyecto/documentacion/manual_tecnico.md) · este README |
| 7. Cierre (9) | Innovación y documento de cierre | Fase 3 (semanas 16 a 18), en `docs/fase3/` |
| 10. Trazabilidad | Matriz Problema → Requisito → HU → Componente → Prueba → Evidencia | [`trazabilidad.xlsx`](docs/fase2/evidencias_proyecto/documentacion/trazabilidad.xlsx) |

## 10. Protección de datos

DomoVida es un prototipo académico y **no usa datos reales de personas**. El paciente se identifica solo con un seudónimo; el RUT se guarda como hash SHA-256 con sal; las tablas de Supabase tienen RLS; las claves y contraseñas viven en variables de entorno y nunca en el repositorio. El sistema no reemplaza la atención médica.

## 11. Declaración de uso de inteligencia artificial

En el desarrollo de este proyecto utilicé Claude (Anthropic) como asistente para proponer y revisar código, explicar conceptos técnicos, redactar borradores de documentación y diseñar diagramas. Todas las decisiones de diseño, alcance y prioridad, la ejecución de los cambios, las pruebas en producción y la validación de los resultados fueron realizadas por mí. Revisé y comprendí cada propuesta antes de incorporarla al proyecto, y soy responsable de su contenido.

Referencia: Anthropic. (2026). *Claude* [Modelo de lenguaje de gran tamaño]. https://claude.ai
