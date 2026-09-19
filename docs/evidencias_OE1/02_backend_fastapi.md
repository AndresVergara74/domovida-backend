\# Ficha 2: Backend FastAPI



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 2.1 Descripción General



El backend de DomoVida es una API REST desarrollada en \*\*FastAPI\*\* con \*\*Python 3.12\*\*, diseñada bajo el paradigma API-First y arquitectura asíncrona. Es el núcleo del sistema, encargado de recibir la telemetría de los sensores, procesarla, almacenarla y exponerla al frontend.



\---



\## 2.2 Estructura del Proyecto



\---



\## 2.3 Endpoints Implementados



| Método | Endpoint | Descripción | Estado |

|--------|----------|-------------|--------|

| POST | `/api/sensor-data` | Recibe datos de cualquier sensor | ✅ |

| GET | `/api/eventos` | Lista los últimos eventos registrados | ✅ |

| GET | `/api/alertas/activas` | Eventos con alerta=True en las últimas 24h | ✅ |

| GET | `/api/alertas/inactividad` | Estado de sensores PIR (online/offline) | ✅ |

| GET | `/` | Endpoint raíz de bienvenida | ✅ |



\---



\## 2.4 Configuración de CORS



El backend permite peticiones desde los siguientes orígenes:



```python

allow\_origins=\[

&#x20;   "http://localhost:3000",      # React Create App

&#x20;   "http://localhost:5173",      # Vite (frontend actual)

&#x20;   "http://127.0.0.1:5173",

&#x20;   "http://127.0.0.1:3000",

]



\## 2.5 Modelo de Datos (Evento)

class Evento(Base):

&#x20;   \_\_tablename\_\_ = "eventos"



&#x20;   id = Column(Integer, primary\_key=True, index=True)

&#x20;   sensor\_id = Column(String, index=True)

&#x20;   tipo = Column(String, index=True)

&#x20;   habitacion = Column(String, nullable=True)

&#x20;   valor = Column(JSON)              # Datos específicos del sensor

&#x20;   alerta = Column(Boolean, default=False)

&#x20;   timestamp = Column(DateTime, default=datetime.utcnow)



\## 2.6 Tipos de Sensores Soportados

El endpoint /api/sensor-data acepta los siguientes tipos:



acelerometro → Detección de caídas



pir → Detección de movimiento/inactividad



gas → Detección de fugas



humo → Detección de incendios



apertura → Puertas/ventanas



cardiovascular → Frecuencia cardíaca (wearable)



boton\_panico → Activación manual del usuario



\## 2.7 Ejemplo de Petición



{

&#x20; "sensor\_id": "acelerometro\_dormitorio",

&#x20; "tipo": "acelerometro",

&#x20; "habitacion": "dormitorio",

&#x20; "valor": {

&#x20;   "ax": -2.35,

&#x20;   "ay": 6.74,

&#x20;   "az": 25.55,

&#x20;   "magnitud": 26.53

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T17:41:23.827444"

}

Respuesta: 201 Created



\## 2.8 Ejemplo de Respuesta (Eventos)

\[

&#x20; {

&#x20;   "id": 965,

&#x20;   "sensor\_id": "acelerometro\_dormitorio",

&#x20;   "tipo": "acelerometro",

&#x20;   "habitacion": "dormitorio",

&#x20;   "valor": {

&#x20;     "ax": 0.5,

&#x20;     "ay": 0.3,

&#x20;     "az": 9.8,

&#x20;     "magnitud": 9.82

&#x20;   },

&#x20;   "alerta": false,

&#x20;   "timestamp": "2026-09-18T18:30:00"

&#x20; }

]



\## 2.9 Comando de Ejecución



cd backend

python -m uvicorn main:app --reload



Salida esperada:



INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

INFO:     Started reloader process \[xxxxx] using WatchFiles

INFO:     Application startup complete.



\## 2.10 Documentación Interactiva



FastAPI genera automáticamente documentación interactiva:



Swagger UI: http://localhost:8000/docs



ReDoc: http://localhost:8000/redoc



\## 2.11 Dependencias Principales



fastapi

uvicorn\[standard]

sqlalchemy

pydantic

requests



\## 2.12 Logros Alcanzados



✅ API REST funcional con 4 endpoints operativos



✅ Conexión a base de datos SQLite3 local



✅ CORS configurado para desarrollo



✅ Validación automática de datos con Pydantic



✅ Documentación automática con Swagger



✅ Recibiendo más de 965 eventos de 8 sensores diferentes





\## 2.13 Próximas Mejoras



🟡 Migrar a PostgreSQL en AWS RDS



🔜 Implementar autenticación JWT



🔜 Añadir validación HL7 FHIR



🔜 Implementar seudonimización de datos (Ley 21.719)



🔜 Integrar Twilio para notificaciones SMS





\*\*Paso 1:\*\* Pega esto en el Bloc de notas, justo debajo de lo que ya tenías.



\*\*Paso 2:\*\* Guarda con `Ctrl + S` y cierra.



\*\*Paso 3:\*\* Vuelve a la terminal y dime \*\*"listo"\*\*.





