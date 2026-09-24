\# Ficha 4: Sensores IoT



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 4.1 Descripción General



DomoVida integra una red de \*\*8 sensores IoT\*\* que monitorean de forma no invasiva el hogar y el estado del adulto mayor. Cada sensor envía telemetría al backend FastAPI cada 5 segundos a través del endpoint `/api/sensor-data`.



En esta fase académica, los sensores son \*\*simulados\*\* mediante el script `simulate\_sensors.py`, lo que permite validar la arquitectura completa sin depender de hardware físico.



\---



\## 4.2 Catálogo de Sensores



| # | Sensor                  | Tipo (`tipo`)    | Habitación | Métrica                          | Umbral de Alerta     |

|---|-------------------------|------------------|------------|----------------------------------|----------------------|

| 1 | Acelerómetro/Giroscopio | `acelerometro`   | Dormitorio | ax, ay, az, gx, gy, gz, magnitud | Magnitud > 20 m/s²   |

| 2 | PIR Movimiento          | `pir`            | Living     | movimiento, minutos\_inactivo    | Inactividad > 12h    |

| 3 | Gas                     | `gas`            | Cocina     | nivel\_ppm                       | > 200 ppm            |

| 4 | Humo                    | `humo`           | Cocina     | nivel                            | > 500                |

| 5 | Apertura puerta         | `apertura`       | Entrada    | abierto (bool)                   | Si está abierta      |

| 6 | Apertura ventana        | `apertura`       | Living     | abierto (bool)                   | No genera alerta     |

| 7 | Cardíaco (wearable)     | `cardiovascular` | Wearable   | bpm, spo2, evento                | bpm > 150 o bpm < 40 |

| 8 | Botón de pánico         | `boton\_panico`  | Sala       | activado (bool)                  | Si está activado     |



\---



\## 4.3 Descripción Detallada



\### 4.3.1 Acelerómetro/Giroscopio (Detección de Caídas)



\*\*Función:\*\* Detecta caídas mediante el análisis de la magnitud de aceleración en los 3 ejes (X, Y, Z) y rotación (GX, GY, GZ).



\*\*Lógica:\*\*

\- Estado normal: magnitud entre 8-11 m/s² (gravedad terrestre)

\- Caída detectada: magnitud > 20 m/s² (pico brusco)



\*\*Probabilidad simulada:\*\* 5% por ciclo



\*\*Ejemplo de datos:\*\*

```json

{

&#x20; "sensor\_id": "acelerometro\_dormitorio",

&#x20; "tipo": "acelerometro",

&#x20; "habitacion": "dormitorio",

&#x20; "valor": {

&#x20;   "ax": -2.35,

&#x20;   "ay": 6.74,

&#x20;   "az": 25.55,

&#x20;   "gx": 3.68,

&#x20;   "gy": -2.96,

&#x20;   "gz": 3.50,

&#x20;   "magnitud": 26.53

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T17:41:23"

}



\## 4.3.2 PIR (Detección de Movimiento/Inactividad)

Función: Detecta presencia y movimiento en el living. Si no hay movimiento por más de 12 horas, se genera una alerta de inactividad prolongada.



Probabilidad de movimiento: 80% por ciclo



\## 4.3.3 Gas (Detección de Fugas)

Función: Mide concentración de gas en partes por millón (ppm).



Lógica:



Estado normal: 0-50 ppm



Fuga detectada: > 200 ppm



Probabilidad de fuga: 2% por ciclo



\## 4.3.5 Apertura (Puertas y Ventanas)

Función: Detecta si puertas o ventanas están abiertas.



Sensores:



Puerta principal (genera alerta si está abierta)



Ventana del living (no genera alerta)



Probabilidad de apertura: 30% por ciclo



\## 4.3.6 Cardíaco (Wearable — Detección de Infarto/Arritmia)

Función: Monitorea la frecuencia cardíaca y el oxígeno en sangre (SpO2) mediante un wearable.



Lógica:



Estado normal: 60-90 bpm, SpO2 > 95%



Taquicardia: > 150 bpm



Bradicardia: < 40 bpm



Probabilidad de evento: 3% por ciclo



Ejemplo de evento:



{

&#x20; "sensor\_id": "wearable\_cardiaco",

&#x20; "tipo": "cardiovascular",

&#x20; "valor": {

&#x20;   "bpm": 175.3,

&#x20;   "spo2": 88.5,

&#x20;   "evento": "taquicardia"

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T21:29:43"

}



\## 4.3.7 Botón de Pánico

Función: Permite al usuario activar manualmente una alerta crítica cuando se siente en peligro o malestar.



Lógica: Es un evento booleano (activado: true/false).



Probabilidad simulada: 2% por ciclo (representa pulsaciones poco frecuentes)



\## 4.4 Script Simulador

Ubicación: backend/simulate\_sensors.py



Tecnologías:



Python 3.12



Librería requests para envío HTTP POST



Librería random para simulación probabilística



Librería datetime para timestamps



Bucle principal: Envía los 8 sensores cada 5 segundos.



Comando de ejecución:



cd backend

python simulate\_sensors.py



\## 4.5 Salida del Simulador



🏠 DOMOVIDA - SIMULADOR DE SENSORES IoT

📡 Backend: http://localhost:8000/api/sensor-data

⏱️  Intervalo: 5 segundos



📊 Ciclo #1 - 21:33:07

✅ acelerometro\_dormitorio       | tipo: acelerometro

✅ pir\_living                    | tipo: pir

✅ gas\_cocina                    | tipo: gas

✅ humo\_cocina                   | tipo: humo

✅ apertura\_puerta\_principal    | tipo: apertura

✅ apertura\_ventana\_living      | tipo: apertura

✅ wearable\_cardiaco             | tipo: cardiovascular

✅ boton\_panico\_sala            | tipo: boton\_panico



Cuando ocurre una alerta:



🚨 ¡CAÍDA DETECTADA! Aceleración Z: 26.53 m/s²

🚨 ¡TAQUICARDIA! 175 bpm

🚨 ¡BOTÓN DE PÁNICO ACTIVADO!



\## 4.6 Validación

Los sensores han sido validados mediante:



✅ 965+ eventos registrados en la base de datos SQLite3



✅ 7 tipos de alertas visibles en el dashboard (gráfico circular)



✅ Detección de caída visible en el gráfico de línea del acelerómetro



✅ Botón de pánico apareciendo en la lista de alertas recientes



✅ Sensor cardíaco registrando eventos de taquicardia



\## 4.7 Diferenciación con Soluciones Existentes

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\

Característica	                  DomoVida	        Soluciones Comerciales

Sensores pasivos sin cámaras	    ✅ Sí	                  ✅ Sí (algunas)

Detección de caídas	              ✅ Sí	                  ✅ Sí

Detección de infarto	            ✅ Sí (sensor cardíaco)	🟡 Solo en wearables premium

Botón de pánico	                  ✅ Sí	                  ✅ Sí

Código abierto	                  ✅ Sí	                  ❌ No

Interoperabilidad HL7 FHIR	      🔜 Futuro	              ❌ No reportado

Edge Computing (offline)	        🔜 Futuro	            ❌ No reportado

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\



\## 4.8 Próximas Mejoras



🔜 Integración de sensores físicos (Raspberry Pi + módulos)



🔜 Pulsera wearable propia con ESP32 + MAX30102 + MPU6050



🔜 Sensores de temperatura y humedad ambiental



🔜 Sensor de puerta con reed switch



🔜 Cámara de profundidad para detección de siluetas (privacidad)








