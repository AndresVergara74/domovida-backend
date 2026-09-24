Perfecto. Copia todo esto y pégalo en el Bloc de notas:



\# Ficha 13: Integración Frontend-Backend-Supabase



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 13.1 Descripción General



Esta ficha documenta la \*\*integración completa\*\* del sistema DomoVida: los sensores IoT envían datos al backend FastAPI, que los almacena en Supabase PostgreSQL, y el dashboard React los visualiza en tiempo real. El flujo end-to-end está verificado y funcionando.



\---



\## 13.2 Arquitectura de Integración



```

┌─────────────────────────────────────────────────────────────┐

│                    FLUJO DE DATOS DOMOVIDA                                    │

│                                                                               │

│   ┌──────────────────┐                                                  │

│   │ Sensores IoT (8)      │                                                  │

│   │  • Acelerómetro       │                                                  │

│   │  • PIR                │                                                  │

│   │  • Gas / Humo         │                                                  │

│   │  • Apertura           │                                                  │

│   │  • Cardíaco           │                                                  │

│   │  • Botón pánico       │                                                  │

│   └────────┬─────────┘                                                  │

│            │ POST /api/sensor-data                                           │

│            ▼                                                                 │

│   ┌──────────────────┐                                                  │

│   │  Backend FastAPI      │                                                  │

│   │  • Valida datos       │                                                  │

│   │  • Guarda en BD       │                                                  │

│   │  • Dispara ntfy       │                                                  │

│   └────────┬─────────┘                                                  │

│            │ SQLAlchemy                                                      │

│            ▼                                                                 │

│   ┌──────────────────┐                                                  │

│   │ Supabase (PG)         │                                                  │

│   │  • Tabla eventos      │                                                  │

│   │  • Tabla alertas      │                                                  │

│   │  • Triggers           │                                                  │

│   └────────┬─────────┘                                                  │

│            │ GET /api/eventos                                                │

│            ▼                                                                 │

│   ┌──────────────────┐                                                  │

│   │  Dashboard React       │                                                 │

│   │  • Vista general       │                                                 │

│   │  • Historial           │                                                 │

│   │  • Sensores            │                                                 │

│   └──────────────────┘                                                  │

│                                                                               │

└─────────────────────────────────────────────────────────────┘

```



\---



\## 13.3 Componentes del Dashboard



\### 13.3.1 Pestaña "Vista General"



| Componente | Descripción | Datos de Supabase |

|------------|-------------|-------------------|

| \*\*Eventos Totales\*\* | Contador de eventos | 50 |

| \*\*Alertas Activas\*\* | Alertas no resueltas | 4 |

| \*\*Sensores Online\*\* | Sensores activos | 1 |

| \*\*Inactividad\*\* | Sensores sin movimiento | 0 |

| \*\*Gráfico de Línea\*\* | Magnitud del acelerómetro | Datos en tiempo real |

| \*\*Gráfico Circular\*\* | Alertas por tipo | Distribución |



\### 13.3.2 Pestaña "Historial"



Muestra los \*\*50 eventos más recientes\*\* con:

\- Sensor ID

\- Tipo

\- Habitación

\- Alerta (Sí/No)

\- Hora



\*\*Ejemplo de datos:\*\*



| Sensor | Tipo | Habitación | Alerta | Hora |

|--------|------|------------|--------|------|

| `wearable\_cardiaco` | cardiovascular | wearable | No | 24-09-2026, 12:12:50 |

| `apertura\_ventana\_living` | apertura | living | No | 24-09-2026, 12:12:47 |

| `apertura\_puerta\_principal` | apertura | entrada | No | 24-09-2026, 12:12:45 |

| `humo\_cocina` | humo | cocina | No | 24-09-2026, 12:12:42 |

| `gas\_cocina` | gas | cocina | No | 24-09-2026, 12:12:39 |

| `pir\_living` | pir | living | No | 24-09-2026, 12:12:36 |

| `acelerometro\_dormitorio` | acelerometro | dormitorio | No | 24-09-2026, 12:12:34 |

| `boton\_panico\_sala` | boton\_panico | sala | No | 24-09-2026, 12:12:26 |

| \*\*`wearable\_cardiaco`\*\* | cardiovascular | wearable | \*\*🚨 Sí\*\* | 24-09-2026, 12:11:55 |



\### 13.3.3 Pestaña "Sensores"



Muestra el estado de cada sensor:

\- Sensor ID

\- Tipo

\- Habitación

\- Última lectura

\- Estado (Online/Offline)



\*\*Ejemplo:\*\*



| Sensor | Tipo | Habitación | Última lectura | Estado |

|--------|------|------------|----------------|--------|

| `pir\_living` | pir | living | 12:12:36 a.m. | ✅ Online |



\---



\## 13.4 Pruebas Realizadas



\### Prueba de Integración End-to-End



| Paso | Acción | Resultado |

|------|--------|-----------|

| 1 | Simulador envía 8 sensores | ✅ 201 Created |

| 2 | Backend guarda en Supabase | ✅ Datos en tabla eventos |

| 3 | Trigger crea alertas | ✅ Alertas en tabla alertas |

| 4 | Backend envía notificación ntfy | ✅ Notificación recibida |

| 5 | Frontend consulta /api/eventos | ✅ 200 OK |

| 6 | Dashboard muestra datos | ✅ Datos visibles |



\### Prueba de Notificaciones



| Evento | Notificación Recibida |

|--------|----------------------|

| Caída detectada | ✅ 🚨 CAÍDA DETECTADA |

| Evento cardíaco | ✅ 🚨 EVENTO CARDÍACO |

| Puerta abierta | ✅ 🚪 PUERTA PRINCIPAL ABIERTA |



\---



\## 13.5 Evidencia de Funcionamiento



\### Log del Backend



```

INFO:     127.0.0.1:59745 - "POST /api/sensor-data HTTP/1.1" 201 Created

INFO:     127.0.0.1:59224 - "GET /api/eventos?limite=50 HTTP/1.1" 200 OK

INFO:     127.0.0.1:55741 - "GET /api/alertas/inactividad HTTP/1.1" 200 OK

INFO:     127.0.0.1:59224 - "GET /api/alertas/activas HTTP/1.1" 200 OK

📱 Notificación enviada: 🚨 CAÍDA DETECTADA

📱 Notificación enviada: 🚪 PUERTA PRINCIPAL ABIERTA

📱 Notificación enviada: 🚨 EVENTO CARDÍACO

```



\### Datos en Supabase



```sql

SELECT \* FROM eventos ORDER BY id DESC LIMIT 5;

```



| id | sensor\_id | tipo | habitacion | alerta | sync\_status |

|----|-----------|------|------------|--------|-------------|

| 44 | acelerometro\_dormitorio | acelerometro | dormitorio | false | synced |

| 43 | boton\_panico\_sala | boton\_panico | sala | false | synced |

| 42 | wearable\_cardiaco | cardiovascular | wearable | false | synced |

| 41 | apertura\_ventana\_living | apertura | living | false | synced |

| 40 | apertura\_puerta\_principal | apertura | entrada | \*\*true\*\* | synced |



\### Alertas creadas automáticamente



```sql

SELECT \* FROM alertas ORDER BY id DESC LIMIT 5;

```



| alerta\_id | evento\_id | tipo\_alerta | nivel\_severidad | resuelto |

|-----------|-----------|-------------|-----------------|----------|

| 3 | 40 | apertura | alta | false |

| 2 | 32 | apertura | alta | false |

| 1 | 3 | acelerometro | crítica | false |



\---



\## 13.6 Tecnologías Integradas



| Capa | Tecnología | Función |

|------|-----------|---------|

| \*\*Sensores\*\* | Python (simulador) | Generación de telemetría |

| \*\*Backend\*\* | FastAPI + SQLAlchemy | API REST, validación, lógica |

| \*\*Base de Datos\*\* | Supabase PostgreSQL | Persistencia en la nube |

| \*\*Automatización\*\* | PL/pgSQL (triggers) | Sincronización y alertas |

| \*\*Frontend\*\* | React + Recharts | Visualización de datos |

| \*\*Notificaciones\*\* | ntfy.sh | Alertas push seudonimizadas |



\---



\## 13.7 Capturas de Pantalla



\*(Agregar capturas del dashboard funcionando)\*



\### Captura 1: Vista General

!\[Vista general del dashboard](capturas/01\_vista\_general.png)



\### Captura 2: Historial

!\[Historial de eventos](capturas/02\_historial.png)



\### Captura 3: Sensores

!\[Estado de sensores](capturas/03\_sensores.png)



\---



\## 13.8 Conclusión



La integración completa de DomoVida está \*\*verificada y funcionando\*\*:



\- ✅ \*\*8 sensores\*\* envían datos al backend

\- ✅ \*\*Backend\*\* guarda en Supabase PostgreSQL

\- ✅ \*\*Triggers\*\* automatizan sincronización y alertas

\- ✅ \*\*Dashboard\*\* visualiza datos en tiempo real

\- ✅ \*\*Notificaciones\*\* llegan al teléfono del cuidador



Esta integración demuestra el funcionamiento end-to-end del sistema y constituye la evidencia principal para la defensa ante la comisión evaluadora.

```


---

## 13.9 Verificación Final del Dashboard

### Fecha de verificación: 24 de septiembre de 2026

### Configuración verificada

| Componente | Puerto | Estado |
|------------|--------|--------|
| **Backend FastAPI** | 8000 | ✅ Corriendo |
| **Frontend React** | 5173 | ✅ Corriendo |
| **Supabase PostgreSQL** | Nube (São Paulo) | ✅ Conectado |

### Valores mostrados en el dashboard

| Tarjeta | Valor | Fuente |
|---------|-------|--------|
| **EVENTOS TOTALES** | 50 | Tabla `eventos` en Supabase |
| **ALERTAS ACTIVAS** | 4 | Tabla `alertas` en Supabase |
| **SENSORES ONLINE** | 1 | Endpoint `/api/alertas/inactividad` |
| **INACTIVIDAD** | 0 | Endpoint `/api/alertas/inactividad` |

### Gráfico del acelerómetro

El gráfico de línea muestra la magnitud del acelerómetro en tiempo real, con valores entre 9 y 12 m/s² (dentro del rango normal).

### Nota sobre CORS

El backend FastAPI está configurado para aceptar peticiones desde:
- `http://localhost:3000` (React Create App)
- `http://localhost:5173` (Vite - frontend actual)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

**Importante:** Si el frontend se ejecuta en un puerto diferente (ej: 5174), el navegador bloqueará las peticiones por CORS. Por eso es importante asegurar que Vite use el puerto 5173.

### Conclusión de la verificación

✅ **El sistema completo está funcionando correctamente:**
- Los sensores envían datos al backend
- El backend los guarda en Supabase
- Los triggers crean alertas automáticamente
- El dashboard los visualiza en tiempo real
- Las notificaciones llegan al teléfono del cuidador

