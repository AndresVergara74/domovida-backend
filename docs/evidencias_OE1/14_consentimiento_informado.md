\# Ficha 14: Consentimiento Informado Digital



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 14.1 Descripción General



Este documento establece el \*\*Consentimiento Informado Digital\*\* que todo usuario de DomoVida debe aceptar antes de que el sistema comience a monitorear su hogar. Cumple con los requisitos de la \*\*Ley N° 21.719\*\* de Protección de Datos Personales, la \*\*Ley N° 20.584\*\* sobre derechos y deberes del paciente, y la \*\*Ley N° 19.628\*\* sobre protección de la vida privada.



\---



\## 14.2 Texto del Consentimiento Informado



\### CONSENTIMIENTO INFORMADO PARA EL MONITOREO DOMICILIARIO



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar



\*\*Responsable:\*\* Andrés Rodrigo Vergara Acevedo — Tecnólogo en Informática Biomédica, Duoc UC



\*\*Versión:\*\* 1.0 — Septiembre 2026



\---



\### 1. ¿Qué es DomoVida?



DomoVida es un sistema de monitoreo domiciliario \*\*no invasivo\*\* que utiliza sensores ambientales y biomédicos para detectar eventos críticos en el hogar (caídas, fugas de gas, incendios, inactividad prolongada, anomalías cardíacas) y notificar al cuidador o familiar responsable.



\*\*El sistema NO utiliza cámaras de video ni dispositivos que capturen imágenes de las personas.\*\* Utiliza exclusivamente sensores pasivos (movimiento, apertura, temperatura, gas, humo) y un wearable opcional.



\---



\### 2. ¿Qué datos recolecta DomoVida?



| Tipo de dato | Descripción | Almacenamiento |

|--------------|-------------|----------------|

| Movimiento | Detección de presencia en habitaciones | SQLite (local) + Supabase (nube) |

| Apertura de puertas/ventanas | Estado abierto/cerrado | SQLite + Supabase |

| Nivel de gas | Concentración de gas (ppm) | SQLite + Supabase |

| Nivel de humo | Concentración de humo | SQLite + Supabase |

| Aceleración | Magnitud de movimiento (m/s²) | SQLite + Supabase |

| Frecuencia cardíaca | bpm y SpO2 (solo si usa wearable) | SQLite + Supabase |



\*\*Los datos son seudonimizados:\*\* no se almacena nombre, RUT, ni datos de identificación personal en la base operativa.



\---



\### 3. ¿Para qué se usarán los datos?



Los datos se utilizarán exclusivamente para:



1\. \*\*Detectar eventos críticos\*\* (caídas, fugas de gas, inactividad).

2\. \*\*Enviar notificaciones\*\* al cuidador o familiar responsable.

3\. \*\*Analizar patrones de comportamiento\*\* para mejorar la detección de anomalías.

4\. \*\*Generar reportes\*\* de bienestar para el cuidador.



\*\*Los datos NO se utilizarán para:\*\*

\- Fines comerciales.

\- Venta a terceros.

\- Publicidad.

\- Vigilancia no autorizada.



\---



\### 4. ¿Quién tiene acceso a los datos?



| Rol | Acceso | Datos que ve |

|-----|--------|--------------|

| \*\*Usuario\*\* | Acceso total | Todos sus datos |

| \*\*Cuidador autorizado\*\* | Acceso limitado | Alertas, eventos, estado de sensores |

| \*\*Familiar autorizado\*\* | Acceso limitado | Alertas y eventos críticos |

| \*\*Personal técnico\*\* | Acceso para mantenimiento | Datos agregados y anonimizados |



\*\*El usuario puede revocar el acceso de cualquier cuidador en cualquier momento.\*\*



\---



\### 5. ¿Cómo se protegen los datos?



\- \*\*Cifrado en tránsito:\*\* SSL/TLS obligatorio.

\- \*\*Cifrado en reposo:\*\* AES-256 en Supabase.

\- \*\*Seudonimización:\*\* sin datos de identificación personal.

\- \*\*Row Level Security (RLS):\*\* activado en todas las tablas.

\- \*\*Acceso por roles:\*\* solo el backend con `service\_role key` accede a los datos completos.

\- \*\*Consentimiento revocable:\*\* el usuario puede solicitar la eliminación de sus datos en cualquier momento.



\---



\### 6. ¿Cuáles son los riesgos?



| Riesgo | Mitigación |

|--------|------------|

| Falsas alarmas | Algoritmo de IA con validación |

| Falla de conectividad | Almacenamiento local en SQLite (Edge Computing) |

| Acceso no autorizado | Cifrado + RLS + seudonimización |

| Intercepción de datos | SSL/TLS obligatorio |



\*\*El sistema NO reemplaza la atención médica profesional.\*\* Es una herramienta de apoyo y prevención.



\---



\### 7. Derechos del usuario



El usuario tiene derecho a:



1\. \*\*Acceder\*\* a sus datos en cualquier momento.

2\. \*\*Rectificar\*\* datos incorrectos.

3\. \*\*Eliminar\*\* sus datos (derecho al olvido).

4\. \*\*Revocar\*\* el consentimiento en cualquier momento.

5\. \*\*Portar\*\* sus datos a otro sistema (portabilidad).

6\. \*\*Presentar reclamos\*\* ante la Agencia de Protección de Datos Personales.



\---



\### 8. Vigencia del consentimiento



Este consentimiento tiene una \*\*vigencia indefinida\*\*, pero puede ser \*\*revocado en cualquier momento\*\* por el usuario sin necesidad de justificación.



\*\*La revocación implica:\*\*

\- La desactivación del sistema de monitoreo.

\- La eliminación de los datos personales en un plazo de 30 días.

\- La emisión de un certificado de eliminación.



\---



\### 9. Declaración del usuario



Yo, \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \[nombre completo], con RUT \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_, declaro que:



1\. He leído y comprendido el presente Consentimiento Informado.

2\. He tenido la oportunidad de hacer preguntas y recibir respuestas claras.

3\. Acepto voluntariamente que DomoVida monitoree mi hogar.

4\. Comprendo que puedo revocar este consentimiento en cualquier momento.

5\. Comprendo que el sistema NO reemplaza la atención médica profesional.

6\. Autorizo el tratamiento de mis datos según lo descrito en este documento.



\*\*Firma:\*\* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



\*\*Fecha:\*\* \_\_\_\_ / \_\_\_\_ / \_\_\_\_\_\_\_\_



\---



\### 10. Contacto del responsable



\*\*Responsable:\*\* Andrés Rodrigo Vergara Acevedo

\*\*Email:\*\* vergara.calleparis@gmail.com

\*\*Institución:\*\* Duoc UC — Escuela de Ingeniería en Informática

\*\*Teléfono:\*\* \[pendiente]



\---



\## 14.3 Implementación Digital



En el sistema DomoVida, el consentimiento informado se implementará como un \*\*formulario digital\*\* que el usuario debe completar antes de activar el monitoreo.



\### Flujo del consentimiento digital:



```

\[Usuario instala DomoVida]

&#x20;        ↓

\[Pantalla de bienvenida]

&#x20;        ↓

\[Lectura del consentimiento informado]

&#x20;        ↓

\[Formulario: nombre, RUT, firma digital]

&#x20;        ↓

\[Aceptación explícita]

&#x20;        ↓

\[Registro en Supabase (tabla consentimientos)]

&#x20;        ↓

\[Activación del monitoreo]

```



\### Tabla de consentimientos en Supabase



```sql

CREATE TABLE IF NOT EXISTS consentimientos (

&#x20;   id SERIAL PRIMARY KEY,

&#x20;   usuario\_id INTEGER,

&#x20;   nombre\_completo VARCHAR(200) NOT NULL,

&#x20;   rut VARCHAR(20) NOT NULL,

&#x20;   aceptado BOOLEAN DEFAULT FALSE,

&#x20;   fecha\_aceptacion TIMESTAMPTZ DEFAULT NOW(),

&#x20;   ip\_registro VARCHAR(45),

&#x20;   version\_consentimiento VARCHAR(20) DEFAULT '1.0',

&#x20;   revocado BOOLEAN DEFAULT FALSE,

&#x20;   fecha\_revocacion TIMESTAMPTZ,

&#x20;   motivo\_revocacion TEXT

);



ALTER TABLE consentimientos ENABLE ROW LEVEL SECURITY;

```



\---



\## 14.4 Cumplimiento Normativo



| Norma | Artículo | Cumplimiento |

|-------|----------|-------------|

| \*\*Ley N° 21.719\*\* | Art. 12 | Consentimiento explícito e informado |

| \*\*Ley N° 21.719\*\* | Art. 14 | Derecho de acceso, rectificación, eliminación |

| \*\*Ley N° 20.584\*\* | Art. 12 | Confidencialidad de la ficha clínica |

| \*\*Ley N° 20.584\*\* | Art. 14 | Consentimiento informado |

| \*\*Ley N° 19.628\*\* | Art. 2 | Datos sensibles protegidos |



\---



\## 14.5 Conclusión



El Consentimiento Informado Digital de DomoVida garantiza que:



1\. \*\*El usuario comprende\*\* qué datos se recolectan y para qué.

2\. \*\*El usuario acepta voluntariamente\*\* el monitoreo.

3\. \*\*El usuario conoce sus derechos\*\* y puede ejercerlos.

4\. \*\*El sistema cumple\*\* con la normativa chilena de protección de datos.



Este documento es \*\*obligatorio\*\* para la validación ética del proyecto y será presentado ante la comisión evaluadora de Duoc UC.

```



\*\*Paso 1:\*\* Guarda con `Ctrl + S` y cierra el Bloc de notas.



