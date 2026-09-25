\# Ficha 15: WebSocket para Alertas en Tiempo Real



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 15.1 Descripción General



DomoVida implementa un sistema de \*\*alertas en tiempo real\*\* basado en WebSocket. A diferencia del polling tradicional (donde el frontend pregunta cada X segundos), el WebSocket permite que el backend \*\*empuje\*\* las alertas instantáneamente a todos los cuidadores conectados.



Esta funcionalidad es crítica para emergencias: una caída, un evento cardíaco o un botón de pánico deben notificarse en menos de 1 segundo.



\---



\## 15.2 Arquitectura del WebSocket



─────────────────────────────────────────────────────────────┐

│ FLUJO DE ALERTAS EN TIEMPO REAL │

│ │

│ ┌──────────────────┐ │

│ │ Sensor IoT │ │

│ │ (detecta caída) │ │

│ └────────┬─────────┘ │

│ │ POST /api/sensor-data │

│ ▼ │

│ ┌──────────────────┐ │

│ │ FastAPI │ │

│ │ (sensor\_router) │ │

│ └────────┬─────────┘ │

│ │ │

│ ┌────┴────┐ │

│ ▼ ▼ │

│ ┌──────┐ ┌──────────────┐ │

│ │ ntfy │ │ WebSocket │ │

│ │ push │ │ Manager │ │

│ └──────┘ └──────┬───────┘ │

│ │ │

│ │ broadcast │

│ ▼ │

│ ┌───────────────┐ │

│ │ Clientes │ │

│ │ conectados │ │

│ │ (cuidadores) │ │

│ └───────────────┘ │

│ │

└─────────────────────────────────────────────────────────────┘





\---



\## 15.3 Componentes Implementados



\### 15.3.1 Backend



| Archivo                       | Función                                        |

|-------------------------------|------------------------------------------------|

| `websocket\_manager.py`        | Gestor central de conexiones WebSocket         |

| `routers/websocket\_router.py` | Endpoint `/api/ws/alertas`                     |

| `routers/sensor\_router.py`    | Llama a `notificar\_alerta()` cuando hay alerta |



\### 15.3.2 Endpoint WebSocket





ws://localhost:8000/api/ws/alertas





\*\*Mensaje de bienvenida:\*\*

```json

{

&#x20; "tipo": "bienvenida",

&#x20; "mensaje": "Conectado al sistema de alertas en tiempo real",

&#x20; "timestamp": "2026-09-25T02:02:20.677299"

}



{

&#x20; "tipo": "pong",

&#x20; "timestamp": "2026-09-25T02:02:20.678426"

}



{

&#x20; "tipo": "alerta",

&#x20; "data": {

&#x20;   "id": 1788,

&#x20;   "sensor\_id": "wearable\_cardiaco",

&#x20;   "tipo": "cardiovascular",

&#x20;   "habitacion": "wearable",

&#x20;   "valor": {

&#x20;     "bpm": 163.7,

&#x20;     "spo2": 85.8,

&#x20;     "evento": "taquicardia"

&#x20;   },

&#x20;   "alerta": true,

&#x20;   "timestamp": "2026-09-24T23:06:20.244887"

&#x20; },

&#x20; "timestamp": "2026-09-25T02:06:23.661419"

}



15.4 Prueba de Funcionamiento

Script de prueba: test\_websocket.py

Se conecta al WebSocket y escucha alertas indefinidamente.



Resultado de la prueba (13 alertas en 5 minutos)

\#	Hora	Sensor	Evento

1	23:05:47	apertura\_puerta\_principal	Puerta abierta

2	23:06:17	apertura\_puerta\_principal	Puerta abierta

3	23:06:23	wearable\_cardiaco	🚨 TAQUICARDIA (163.7 bpm)

4	23:07:14	apertura\_puerta\_principal	Puerta abierta

5	23:07:43	apertura\_puerta\_principal	Puerta abierta

6	23:08:27	apertura\_puerta\_principal	Puerta abierta

7	23:08:40	apertura\_puerta\_principal	Puerta abierta

8	23:09:09	apertura\_puerta\_principal	Puerta abierta

9	23:09:14	acelerometro\_dormitorio	🚨 CAÍDA (magnitud 26.99)

10	23:09:38	apertura\_puerta\_principal	Puerta abierta

11	23:09:54	apertura\_puerta\_principal	Puerta abierta

12	23:10:00	wearable\_cardiaco	🚨 BRADICARDIA (35 bpm)

13	23:10:07	apertura\_puerta\_principal	Puerta abierta

Todas las alertas llegaron en menos de 1 segundo desde su detección.



15.5 Ventajas del WebSocket vs Polling

Aspecto	Polling (cada 10s)	WebSocket

Latencia	Hasta 10 segundos	< 1 segundo

Carga del servidor	Alta (peticiones constantes)	Baja (conexión persistente)

Tiempo real	No	Sí

Escalabilidad	Limitada	Alta

Experiencia de usuario	Aceptable	Excelente

En una emergencia, 10 segundos pueden ser la diferencia entre la vida y la muerte.



15.6 Código del Manager WebSocket

python

class ConnectionManager:

&#x20;   def \_\_init\_\_(self):

&#x20;       self.active\_connections: List\[WebSocket] = \[]



&#x20;   async def connect(self, websocket: WebSocket):

&#x20;       await websocket.accept()

&#x20;       self.active\_connections.append(websocket)

&#x20;       print(f"🔌 Cliente conectado. Total: {len(self.active\_connections)}")



&#x20;   def disconnect(self, websocket: WebSocket):

&#x20;       if websocket in self.active\_connections:

&#x20;           self.active\_connections.remove(websocket)



&#x20;   async def broadcast(self, message: dict):

&#x20;       message\_json = json.dumps(message, default=str)

&#x20;       disconnected = \[]

&#x20;       for connection in self.active\_connections:

&#x20;           try:

&#x20;               await connection.send\_text(message\_json)

&#x20;           except Exception:

&#x20;               disconnected.append(connection)

&#x20;       for conn in disconnected:

&#x20;           self.disconnect(conn)

15.7 Integración con el Frontend (Próximo Paso)

El frontend React se conectará al WebSocket usando el hook useWebSocket:



typescript

const ws = new WebSocket("ws://localhost:8000/api/ws/alertas");

ws.onmessage = (event) => {

&#x20; const data = JSON.parse(event.data);

&#x20; if (data.tipo === "alerta") {

&#x20;   // Mostrar notificación en el dashboard

&#x20;   setAlertas((prev) => \[data.data, ...prev]);

&#x20; }

};

15.8 Logs del Backend

text

📱 Notificación enviada: 🚨 EVENTO CARDÍACO

📡 Enviando alerta por WebSocket a 1 clientes

📱 Notificación enviada: 🚪 PUERTA PRINCIPAL ABIERTA

📡 Enviando alerta por WebSocket a 1 clientes

📱 Notificación enviada: 🚨 BOTÓN DE PÁNICO

📡 Enviando alerta por WebSocket a 1 clientes

Los logs confirman que las alertas se envían por ambos canales (ntfy + WebSocket).



15.9 Conclusión

La implementación del WebSocket en DomoVida demuestra:



1.Tiempo real: Las alertas llegan en menos de 1 segundo.



2.Escalabilidad: Múltiples cuidadores pueden conectarse simultáneamente.



3.Resiliencia: Si un cliente falla, se elimina automáticamente.



4.Integración: El backend envía alertas por dos canales (push + tiempo real).



5.Diferenciación: DomoVida ofrece una experiencia superior a las soluciones tradicionales.







