\# Ficha 7: Alarmas Críticas



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 7.1 Descripción General



DomoVida identifica \*\*3 alarmas críticas\*\* que representan riesgos inmediatos para la vida o la salud del adulto mayor:



1\. 🚨 \*\*Caída\*\* (detectada por acelerómetro)

2\. 🚨 \*\*Emergencia cardíaca\*\* (detectada por sensor cardiovascular)

3\. 🚨 \*\*Botón de pánico\*\* (activado manualmente por el usuario)



Cada una tiene un origen, umbral y nivel de severidad específico.



\---



\## 7.2 Tabla Resumen

&#x20;  

| Alarma                  | Tipo de Sensor   | Severidad                     | Umbral             | Acción                    |

|-------------------------|------------------|-------------------------------|--------------------|---------------------------|

| \*\*Caída\*\*               | `acelerometro`   | 🔴 Alta                      | Magnitud > 20 m/s²  | SMS al cuidador           |

| \*\*Emergencia cardíaca\*\* | `cardiovascular` | 🚨 Crítica                   | bpm > 150 o bpm < 40| SMS + escalado            |

| \*\*Botón de pánico\*\*     | `boton\_panico`   | 🚨 Crítica                   | activado = true     | SMS inmediato             |



\## 7.3 Alarma 1: Detección de Caída



\### 7.3.1 Descripción



Detecta caídas mediante el análisis de la magnitud de aceleración en los 3 ejes. Una caída genera un pico brusco que supera los 20 m/s².



\### 7.3.2 Lógica de Detección



```

Magnitud = √(ax² + ay² + az²)



Si Magnitud > 20 m/s² → 🚨 CAÍDA DETECTADA

```



\### 7.3.3 Valores Típicos



| Estado            | Magnitud  |

|-------------------|-----------|

| Reposo            | 8-11 m/s² |

| Movimiento normal | 9-12 m/s² |

| Caída             | > 20 m/s² |



\### 7.3.4 Ejemplo de Evento



json



{

&#x20; "sensor\_id": "acelerometro\_dormitorio",

&#x20; "tipo": "acelerometro",

&#x20; "valor": {

&#x20;   "ax": -2.35,

&#x20;   "ay": 6.74,

&#x20;   "az": 25.55,

&#x20;   "magnitud": 26.53

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T17:41:23"

}





\### 7.3.5 Impacto Clínico



Las caídas son la \*\*primera causa de muerte accidental en adultos mayores\*\*. 

La detección temprana reduce la "latencia de rescate" y mejora el pronóstico de recuperación funcional.





\## 7.4 Alarma 2: Emergencia Cardíaca



\### 7.4.1 Descripción



Detecta anomalías en la frecuencia cardíaca mediante un sensor wearable. 

Puede identificar \*\*taquicardia\*\* (ritmo acelerado) o \*\*bradicardia severa\*\* (ritmo muy lento).



\### 7.4.2 Lógica de Detección





Si bpm > 150 → 🚨 TAQUICARDIA

Si bpm < 40  → 🚨 BRADICARDIA

Si SpO2 < 93% → 🚨 HIPOXEMIA

```



\### 7.4.3 Valores Típicos



| Estado             | BPM    | SpO2   |

|--------------------|--------|--------|

| Reposo normal      | 60-90  | 95-99% |

| Actividad física   | 90-140 | 95-99% |

| Taquicardia        | > 150  | 85-93% |

| Bradicardia severa | < 40   | 85-93% |



\### 7.4.4 Ejemplo de Evento



&#x20;  json

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



\### 7.4.5 Impacto Clínico



La detección temprana de arritmias puede prevenir un \*\*infarto agudo de miocardio\*\*. 

El tiempo entre el evento y la atención médica es determinante para la supervivencia.







\## 7.5 Alarma 3: Botón de Pánico



\### 7.5.1 Descripción



Es una alarma \*\*activa\*\* (el usuario la controla). Se activa cuando el adulto mayor presiona un botón físico o virtual al sentir peligro o malestar.



\### 7.5.2 Lógica de Detección



```

Si activado = true → 🚨 BOTÓN DE PÁNICO ACTIVADO

```



\### 7.5.3 Ejemplo de Evento



```json

{

&#x20; "sensor\_id": "boton\_panico\_sala",

&#x20; "tipo": "boton\_panico",

&#x20; "valor": {

&#x20;   "activado": true

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T21:39:57"

}

```



\### 7.5.4 Diferencia con Otras Alarmas



| Aspecto                         | Caída / Cardíaco        | Botón de Pánico             |

|---------------------------------|-------------------------|-----------------------------|

| Tipo | Pasivo (sistema detecta) | Activo (usuario decide) |                             |

| Requiere hardware               | Sí (sensor)             | Sí (botón físico)           |

| Requiere acción del usuario     | No                      | Sí                          |

| Casos de uso                    | Emergencias objetivas   | Malestar, peligro percibido |







\## 7.6 Flujo de Alerta (Futuro — Objetivo 3)





\[Evento crítico detectado]

&#x20;        ↓

\[Backend evalúa: alerta = true]

&#x20;        ↓

\[Se guarda en base de datos]

&#x20;        ↓

\[Twilio envía SMS al cuidador] ← 🔜 PRÓXIMO PASO

&#x20;        ↓

\[Si no responde en 5 min → Escala a contacto 2]

&#x20;        ↓

\[Si no responde en 10 min → Central de teleasistencia]









\## 7.7 Estado Actual



| Alarma              | Detección | Visualización en Dashboard | Notificación SMS |

|---------------------|-----------|----------------------------|------------------|

| Caída               | ✅ Sí     | ✅ Sí (gráfico de línea)  | 🔜 Objetivo 3    |

| Emergencia cardíaca | ✅ Sí     | ✅ Sí (lista de alertas)  | 🔜 Objetivo 3    |

| Botón de pánico     | ✅ Sí     | ✅ Sí (lista de alertas)  | 🔜 Objetivo 3    |







\## 7.8 Diferenciación con Competidores



| Competidor   | Detección de caídas | Detección de infarto          | Botón de pánico |

|--------------|---------------------|-------------------------------|-----------------|

| \*\*Mistatas\*\* | ✅ Sí              | ❌ No reportado               | ✅ Sí           |

| \*\*Quida\*\*    | ✅ Sí              | ❌ No reportado               | ❌ No reportado |

| \*\*GCare\*\*    | ✅ Sí              | ❌ No reportado               | ✅ Sí           |

| \*\*DomoVida\*\* | ✅ Sí              | ✅ \*\*Sí (wearable cardíaco)\*\* | ✅ Sí           |



\*\*Ventaja competitiva:\*\* DomoVida es el único que integra las \*\*3 alarmas críticas\*\* en una plataforma modular.







\## 7.9 Próximas Mejoras



\- 🔜 Integrar \*\*Twilio\*\* para envío de SMS/WhatsApp

\- 🔜 Implementar \*\*escalado de alertas\*\* (contacto 2, contacto 3)

\- 🔜 Añadir \*\*detección de caídas por Machine Learning\*\* (Isolation Forest)

\- 🔜 Implementar \*\*detección de convulsiones\*\* (acelerómetro + patrones)

\- 🔜 Integrar \*\*alertas al CESFAM\*\* más cercano

\- 🔜 Añadir \*\*detección de incendios\*\* con cámara termal

\- 🔜 Implementar \*\*detección de fugas de gas\*\* con sensor MQ-2





\*\*Paso 2:\*\* Guarda con `Ctrl + S` y cierra el Bloc de notas.



\*\*Paso 3:\*\* Vuelve a la terminal y dime \*\*"listo"\*\*.

