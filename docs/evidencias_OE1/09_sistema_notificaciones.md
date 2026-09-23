\# Ficha 9: Sistema de Notificaciones Push



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 9.1 Descripción General



DomoVida integra un sistema de notificaciones push que envía alertas en tiempo real al teléfono o navegador del cuidador cuando ocurre un evento crítico en el hogar del adulto mayor.



El sistema utiliza \*\*ntfy.sh\*\*, una plataforma de notificaciones push de código abierto, gratuita y que no requiere registro.



\---



\## 9.2 Arquitectura del Sistema



```

\[Sensor detecta evento]

&#x20;       ↓

\[Backend evalúa: alerta=True]

&#x20;       ↓

\[Se guarda en base de datos]

&#x20;       ↓

\[Se envía notificación a ntfy.sh]

&#x20;       ↓

\[El cuidador recibe push en su teléfono/navegador]

```



\---



\## 9.3 Tecnología: ntfy.sh



| Característica | Detalle                                  |

|----------------|------------------------------------------|

| \*\*Tipo\*\*       | Servicio de notificaciones push          |

| \*\*Costo\*\*      | Gratuito (sin límites para uso personal) |

| \*\*Registro\*\*   | No requiere cuenta                       |

| \*\*Protocolo\*\*  | HTTP POST                                |

| \*\*Canales\*\*    | Android, iOS, Web                        |

| \*\*Código\*\*     | Open source                              |



\---



\## 9.4 Configuración de Seguridad



\### Seudonimización del Topic



Para cumplir con la \*\*Ley N° 21.719\*\* de protección de datos personales, el topic de ntfy está \*\*seudonimizado\*\*:



```

NTFY\_TOPIC=domovida-seguro-2026

```



El nombre del topic es difícil de adivinar para evitar accesos no autorizados.



\### Minimización de Datos en las Notificaciones



\*\*Las notificaciones NO contienen:\*\*

\- ❌ Frecuencia cardíaca (bpm)

\- ❌ Saturación de oxígeno (SpO2)

\- ❌ Nombres de pacientes

\- ❌ RUT

\- ❌ Datos biomédicos específicos



\*\*Las notificaciones SÍ contienen:\*\*

\- ✅ Tipo de emergencia (caída, evento cardíaco, botón de pánico)

\- ✅ Ubicación genérica (dormitorio, cocina, living)

\- ✅ Hora del evento

\- ✅ Instrucción de acción ("Revisar panel DomoVida")



\*\*Ejemplo de notificación seudonimizada:\*\*



```

🚨 CAÍDA DETECTADA

Evento crítico en dormitorio.

Revisar panel DomoVida.

Hora: 20:30:22

```



\---



\## 9.5 Tipos de Notificaciones



| Evento                 | Título                      | Prioridad |

|------------------------|-----------------------------|-----------|

| Caída detectada        | 🚨 CAÍDA DETECTADA          | Urgente  |

| Taquicardia            | 🚨 EVENTO CARDÍACO          | Urgente  |

| Bradicardia            | 🚨 EVENTO CARDÍACO          | Urgente  |

| Botón de pánico        | 🚨 BOTÓN DE PÁNICO          | Urgente  |

| Fuga de gas            | 🚨 FUGA DE GAS              | Urgente  |

| Humo detectado         | 🚨 HUMO DETECTADO           | Urgente  |

| Puerta abierta         | 🚪 PUERTA PRINCIPAL ABIERTA | Alta     |

| Ventana abierta        | 🪟 VENTANA ABIERTA          | Normal   |

| Inactividad prolongada | ⚠️ INACTIVIDAD PROLONGADA   | Alta     |



\---



\## 9.6 Código de Implementación



El módulo `notifier.py` contiene la lógica de envío:



```python

def enviar\_notificacion(evento: dict) -> bool:

&#x20;   """Envía una notificación push si el evento tiene alerta=True."""

&#x20;   if not evento.get("alerta"):

&#x20;       return False

&#x20;   

&#x20;   titulo, mensaje, prioridad = formatear\_alerta(evento)

&#x20;   

&#x20;   response = requests.post(

&#x20;       NTFY\_URL,

&#x20;       data=mensaje.encode("utf-8"),

&#x20;       headers={

&#x20;           "Title": titulo.encode("utf-8"),

&#x20;           "Priority": prioridad,

&#x20;           "Tags": "rotating\_light,warning",

&#x20;       },

&#x20;       timeout=5,

&#x20;   )

&#x20;   return response.status\_code == 200

```



\---



\## 9.7 Integración con el Backend



El router de sensores (`sensor\_router.py`) llama a `enviar\_notificacion()` cuando un evento tiene `alerta=True`:



```python

if datos.alerta:

&#x20;   enviar\_notificacion({

&#x20;       "sensor\_id": datos.sensor\_id,

&#x20;       "tipo": datos.tipo,

&#x20;       "habitación": datos.habitacion,

&#x20;       "valor": datos.valor,

&#x20;       "alerta": datos.alerta,

&#x20;   })

```



\---



\## 9.8 Pruebas Realizadas



| Prueba                          | Resultado    |

|---------------------------------|--------------|

| Notificación de caída           | ✅ Recibida |

| Notificación de taquicardia     | ✅ Recibida |

| Notificación de botón de pánico | ✅ Recibida |

| Notificación de fuga de gas     | ✅ Recibida |

| Latencia de entrega             | < 3 segundos |



\---



\## 9.9 Ventajas del Sistema



1\. \*\*Gratuito:\*\* No requiere tarjeta de crédito ni suscripción.

2\. \*\*Sin registro:\*\* No expone datos personales a terceros.

3\. \*\*Multiplataforma:\*\* Funciona en Android, iOS y navegador web.

4\. \*\*Privacidad:\*\* Las notificaciones están seudonimizadas.

5\. \*\*Rápido:\*\* Latencia menor a 3 segundos.



\---



\## 9.10 Próximas Mejoras



\- 🔜 Integrar \*\*Twilio\*\* para SMS (cuando el proyecto escale).

\- 🔜 Implementar \*\*escalado de alertas\*\* (contacto 1 → contacto 2 → central).

\- 🔜 Añadir \*\*confirmación de recepción\*\* por parte del cuidador.

\- 🔜 Historial de notificaciones en el dashboard.



\---



\## 9.11 Cumplimiento Normativo



| Norma                                     | Cumplimiento                        |

|-------------------------------------------|-------------------------------------|

| \*\*Ley N° 21.719\*\* (Protección de datos)   | ✅ Notificaciones seudonimizadas    |

| \*\*Ley N° 19.628\*\* (Vida privada)          | ✅ Sin datos sensibles en tránsito  |

| \*\*Ley N° 20.584\*\* (Derechos del paciente) | ✅ Confidencialidad garantizada     |

```



\*\*Paso 1:\*\* Guarda con `Ctrl + S` y cierra el Bloc de notas.



\*\*Paso 2:\*\* Vuelve a la terminal y dime \*\*"listo"\*\*.



\---



\*\*Cuando confirmes, hacemos commit y push de esta ficha, y luego creamos la Ficha 10.\*\* 💪





