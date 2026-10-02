\# Guion de Presentación — DomoVida



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Carrera:\*\* Ingeniería en Informática



\*\*Asignatura:\*\* Capstone (PTY4614)



\*\*Duración estimada:\*\* 15-20 minutos



\---



\## Diapositiva 1: Portada



\### Texto de la diapositiva:

\- \*\*Título:\*\* DomoVida

\- \*\*Subtítulo:\*\* Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar

\- \*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo

\- \*\*Carrera:\*\* Ingeniería en Informática

\- \*\*Duoc UC — Septiembre 2026\*\*

\- \*\*Imagen de fondo:\*\* Hogar acogedor o adulto mayor sonriendo



\### Guion del orador (30 segundos):



> "Buenos días, profesor y comisión. Mi nombre es Andrés Vergara, y les presento \*\*DomoVida\*\*, una plataforma IoT de monitoreo predictivo y asistencia inteligente para el adulto mayor en el hogar.

>

> DomoVida nace de una necesidad real: Chile envejece aceleradamente, y nuestros adultos mayores necesitan vivir seguros y con dignidad en sus propios hogares. Esta es mi respuesta tecnológica a ese desafío."



\---



\## Diapositiva 2: El Problema



\### Texto de la diapositiva:

\- \*\*32%\*\* de la población chilena será mayor de 60 años en 2050 (INE)

\- \*\*84%\*\* cree que Chile no está preparado para el envejecimiento (UC/Confuturo)

\- \*\*1 de cada 3\*\* adultos mayores vive solo

\- Las caídas son una de las principales causas de pérdida de autonomía (MINSAL)

\- \*\*Problema:\*\* No existe una plataforma interoperable, accesible y ética para el cuidado domiciliario



\### Guion del orador (1.5 minutos):



> "Chile está envejeciendo de forma acelerada. Según el INE, para 2050, el 32% de la población será mayor de 60 años. Pero el 84% de los chilenos cree que el país no está preparado para este desafío.

>

> Miles de adultos mayores viven solos. Una caída, una descompensación cardíaca, o una fuga de gas pueden pasar horas sin ser detectadas. La 'latencia de rescate' —el tiempo entre el evento y la atención— es determinante en el pronóstico.

>

> Los sistemas actuales son reactivos: funcionan con botones de pánico, pero no anticipan riesgos. Y las soluciones existentes no están adaptadas al contexto sociosanitario chileno: no son interoperables con el sistema de salud, y a menudo violan la privacidad del usuario."



\---



\## Diapositiva 3: La Solución — DomoVida



\### Texto de la diapositiva:

\- \*\*DomoVida:\*\* Sistema de monitoreo proactivo y no invasivo

\- \*\*8 sensores IoT:\*\* movimiento, caídas, gas, humo, apertura, cardíaco, botón de pánico

\- \*\*Edge Computing:\*\* procesamiento local, funciona sin internet

\- \*\*Notificaciones instantáneas:\*\* al teléfono del cuidador

\- \*\*Interoperabilidad clínica:\*\* HL7 FHIR + CENS

\- \*\*Privacidad por diseño:\*\* sin cámaras invasivas, datos seudonimizados

\- \*\*Imagen:\*\* Diagrama de los 8 sensores alrededor de una casa



\### Guion del orador (1.5 minutos):



> "DomoVida es una plataforma modular que transforma el hogar del adulto mayor en un entorno inteligente y seguro.

>

> Utiliza \*\*8 sensores IoT\*\* que monitorean de forma no invasiva: movimiento, caídas, gas, humo, apertura de puertas, frecuencia cardíaca, y un botón de pánico.

>

> A diferencia de las soluciones convencionales, DomoVida procesa los datos \*\*localmente en el borde (Edge Computing)\*\*. Esto significa que si se corta el internet, el sistema sigue funcionando y almacenando datos localmente en SQLite.

>

> Cuando ocurre una alerta, el cuidador recibe una \*\*notificación instantánea\*\* en su teléfono, con información seudonimizada que cumple con la Ley 21.719 de protección de datos.

>

> Y todo está diseñado bajo el principio de \*\*Privacy by Design\*\*: sin cámaras invasivas, sin datos sensibles expuestos."



\---

## Diapositiva 7: Interoperabilidad Clínica con HL7 FHIR

### Texto de la diapositiva:
- **Estándar:** HL7 FHIR (Fast Healthcare Interoperability Resources)
- **Recursos utilizados:** Patient, Observation, Device
- **Formato:** JSON estructurado
- **Validación:** CENS (Centro Nacional en Sistemas de Información en Salud)
- **Beneficio:** Integración con FONASA, ISAPRES y mutuales
- **Imagen:** Diagrama de flujo de datos hacia sistemas de salud

### Guion del orador (1.5 minutos):

> "Uno de los diferenciadores más importantes de DomoVida es su **interoperabilidad clínica**. No somos solo un sistema de domótica; somos una plataforma que puede integrarse con el ecosistema de salud chileno.
>
> Utilizamos el estándar **HL7 FHIR** (Fast Healthcare Interoperability Resources), que es el estándar internacional para el intercambio de información clínica. Cada evento que capturamos se estructura como un recurso FHIR: por ejemplo, una caída se modela como un recurso *Observation*, con el código LOINC correspondiente.
>
> Esto permite que los datos de DomoVida sean **legibles por cualquier sistema de salud**: FONASA, ISAPRES, mutuales de seguridad, o el propio CENS. Es decir, si el adulto mayor sufre una caída, el reporte puede llegar directamente a su ficha clínica electrónica.
>
> Esta interoperabilidad está alineada con los lineamientos del **CENS** (Centro Nacional en Sistemas de Información en Salud), que es el organismo que certifica la madurez digital en salud en Chile."

---

## Diapositiva 8: Seguridad y Privacidad

### Texto de la diapositiva:
- **Ley N° 21.719:** Protección de datos personales (2024)
- **Ley N° 19.628:** Protección de la vida privada
- **Ley N° 20.584:** Derechos y deberes del paciente
- **Privacy by Design:** sin cámaras invasivas
- **Seudonimización:** notificaciones sin datos sensibles
- **RLS (Row Level Security):** activado en Supabase
- **Cifrado:** SSL/TLS en tránsito

### Guion del orador (1.5 minutos):

> "La privacidad es un pilar fundamental de DomoVida, y está diseñada desde el inicio bajo el principio de **Privacy by Design**.
>
> A diferencia de otras soluciones que usan cámaras, DomoVida utiliza **sensores pasivos**: no hay imágenes, no hay video, no hay violación de la intimidad. Esto es especialmente importante porque estamos monitoreando a personas en su hogar, en sus momentos más privados.
>
> Cumplimos con la **Ley N° 21.719** de protección de datos personales, que entró en vigencia en 2024. Esto significa que:
>
> 1. Las notificaciones push están **seudonimizadas**: no contienen nombre, RUT, ni datos biomédicos específicos. Solo dicen 'caída detectada en dormitorio' o 'evento cardíaco, revisar panel'.
>
> 2. Los datos en Supabase están protegidos con **RLS (Row Level Security)**, lo que significa que solo el backend con service_role key puede acceder a ellos.
>
> 3. Toda la comunicación está cifrada con **SSL/TLS**.
>
> Y también cumplimos con la **Ley N° 19.628** sobre protección de la vida privada, y la **Ley N° 20.584** sobre derechos del paciente."

---

## Diapositiva 9: Persistencia Híbrida (Edge + Cloud)

### Texto de la diapositiva:


## Diapositiva 7: Interoperabilidad Clínica con HL7 FHIR

### Texto de la diapositiva:
- **Estándar:** HL7 FHIR (Fast Healthcare Interoperability Resources)
- **Recursos utilizados:** Patient, Observation, Device
- **Formato:** JSON estructurado
- **Validación:** CENS (Centro Nacional en Sistemas de Información en Salud)
- **Beneficio:** Integración con FONASA, ISAPRES y mutuales
- **Imagen:** Diagrama de flujo de datos hacia sistemas de salud

### Guion del orador (1.5 minutos):

> "Uno de los diferenciadores más importantes de DomoVida es su **interoperabilidad clínica**. No somos solo un sistema de domótica; somos una plataforma que puede integrarse con el ecosistema de salud chileno.
>
> Utilizamos el estándar **HL7 FHIR** (Fast Healthcare Interoperability Resources), que es el estándar internacional para el intercambio de información clínica. Cada evento que capturamos se estructura como un recurso FHIR: por ejemplo, una caída se modela como un recurso *Observation*, con el código LOINC correspondiente.
>
> Esto permite que los datos de DomoVida sean **legibles por cualquier sistema de salud**: FONASA, ISAPRES, mutuales de seguridad, o el propio CENS. Es decir, si el adulto mayor sufre una caída, el reporte puede llegar directamente a su ficha clínica electrónica.
>
> Esta interoperabilidad está alineada con los lineamientos del **CENS** (Centro Nacional en Sistemas de Información en Salud), que es el organismo que certifica la madurez digital en salud en Chile."

---

## Diapositiva 8: Seguridad y Privacidad

### Texto de la diapositiva:
- **Ley N° 21.719:** Protección de datos personales (2024)
- **Ley N° 19.628:** Protección de la vida privada
- **Ley N° 20.584:** Derechos y deberes del paciente
- **Privacy by Design:** sin cámaras invasivas
- **Seudonimización:** notificaciones sin datos sensibles
- **RLS (Row Level Security):** activado en Supabase
- **Cifrado:** SSL/TLS en tránsito

### Guion del orador (1.5 minutos):

> "La privacidad es un pilar fundamental de DomoVida, y está diseñada desde el inicio bajo el principio de **Privacy by Design**.
>
> A diferencia de otras soluciones que usan cámaras, DomoVida utiliza **sensores pasivos**: no hay imágenes, no hay video, no hay violación de la intimidad. Esto es especialmente importante porque estamos monitoreando a personas en su hogar, en sus momentos más privados.
>
> Cumplimos con la **Ley N° 21.719** de protección de datos personales, que entró en vigencia en 2024. Esto significa que:
>
> 1. Las notificaciones push están **seudonimizadas**: no contienen nombre, RUT, ni datos biomédicos específicos. Solo dicen 'caída detectada en dormitorio' o 'evento cardíaco, revisar panel'.
>
> 2. Los datos en Supabase están protegidos con **RLS (Row Level Security)**, lo que significa que solo el backend con service_role key puede acceder a ellos.
>
> 3. Toda la comunicación está cifrada con **SSL/TLS**.
>
> Y también cumplimos con la **Ley N° 19.628** sobre protección de la vida privada, y la **Ley N° 20.584** sobre derechos del paciente."

---

## Diapositiva 9: Persistencia Híbrida (Edge + Cloud)

### Texto de la diapositiva:

┌──────────────────────┐
│ SQLite3 (Edge)              
│ ───────────────         
│ • Resiliencia               
│ • Sin internet              
│ • Datos locales             
└──────────┬───────────┘
│ Sincronización
▼
┌──────────────────────┐
│ Supabase (Nube)             
│ ───────────────         
│ • PostgreSQL                
│ • Análisis                  
│ • Escalabilidad             
└──────────────────────┘

- **Session Pooler IPv4:** puerto 6543
- **Región:** São Paulo (Sudamérica)
- **Beneficio:** Continuidad operativa incluso sin internet

### Guion del orador (1.5 minutos):

> "DomoVida utiliza una **arquitectura de persistencia híbrida** que combina SQLite3 local con Supabase PostgreSQL en la nube.
>
> En el **Edge**, SQLite3 almacena los datos localmente. Esto garantiza que el sistema siga funcionando incluso si se corta el internet. Los datos se acumulan, y cuando la conexión se restaura, se sincronizan automáticamente con la nube.
>
> En la **Nube**, Supabase PostgreSQL proporciona persistencia centralizada, análisis a escala, y acceso desde cualquier lugar. Usamos **Session Pooler con IPv4** en el puerto 6543, que evita los problemas de intercepción de algunos ISPs.
>
> Durante el desarrollo, descubrimos que algunos proveedores de internet en Chile interceptan conexiones SSL al puerto 5432. La solución fue usar el **Session Pooler de Supabase**, que opera sobre IPv4 y es más resistente a estas intercepciones.
>
> Esta arquitectura está alineada con el concepto de **Edge Computing** documentado en mi tesis: el procesamiento y almacenamiento crítico se realiza localmente, mientras que la nube proporciona análisis y visualización."

---

## Diapositiva 10: Triggers y Automatización en PostgreSQL

### Texto de la diapositiva:
- **Trigger #1:** `sync_status` automático en cada INSERT
- **Trigger #2:** Creación automática de alertas
- **PL/pgSQL:** lenguaje procedimental de PostgreSQL
- **Ventajas:** consistencia, rendimiento, integridad
- **Ejemplo:** evento con `alerta=true` → alerta crítica creada automáticamente

### Guion del orador (1.5 minutos):

> "Para garantizar la **consistencia y automatización** de los datos, implementé dos triggers en PostgreSQL usando PL/pgSQL.
>
> El **Trigger #1** se dispara antes de cada INSERT en la tabla `eventos`. Su función es actualizar automáticamente el campo `sync_status` a 'synced', indicando que el dato ya está en la nube. Esto elimina la necesidad de que el backend haga esta actualización manualmente.
>
> El **Trigger #2** se dispara después de cada INSERT en la tabla `eventos`. Si el evento tiene `alerta=true`, el trigger crea automáticamente un registro en la tabla `alertas`, asignando severidad según el tipo: 'critica' para caídas, eventos cardíacos, fugas de gas, humo y botón de pánico; 'alta' para otras alertas.
>
> Esta automatización tiene tres ventajas:
>
> 1. **Rendimiento:** PostgreSQL es más rápido que Python para estas tareas.
> 2. **Consistencia:** no importa qué aplicación inserte datos, el comportamiento es el mismo.
> 3. **Mantenibilidad:** las reglas de negocio están en un solo lugar: la base de datos.
>
> Esto demuestra un nivel avanzado de dominio de PostgreSQL y PL/pgSQL."

---

## Diapositiva 11: Dashboard y Usabilidad

### Texto de la diapositiva:
- **Tecnología:** React + Recharts
- **Componentes:**
  - 4 tarjetas de resumen (eventos, alertas, sensores, inactividad)
  - Gráfico de línea (acelerómetro)
  - Gráfico circular (alertas por tipo)
  - Lista de alertas recientes
- **Actualización:** cada 10 segundos
- **Validación:** Escala SUS (System Usability Scale)
- **Objetivo:** puntuación > 70

### Guion del orador (1.5 minutos):

> "El dashboard de DomoVida está diseñado para ser **claro, accionable y de mínima fricción**. Utiliza React con Recharts para la visualización de datos.
>
> La interfaz incluye:
>
> - **4 tarjetas de resumen** que muestran eventos totales, alertas activas, sensores online e inactividad.
> - **Un gráfico de línea** que muestra la magnitud del acelerómetro en tiempo real, permitiendo visualizar picos de caída.
> - **Un gráfico circular** que distribuye las alertas por tipo de sensor.
> - **Una lista de alertas recientes** con timestamps.
>
> El dashboard se actualiza automáticamente cada 10 segundos, sin necesidad de recargar la página.
>
> Para validar la usabilidad, aplicaré la **Escala SUS** (System Usability Scale), un cuestionario estandarizado de 10 ítems. El objetivo es obtener una puntuación superior a 70 puntos, que se considera 'excelente' en términos de usabilidad.
>
> Esta validación es especialmente importante porque los usuarios finales son familiares y cuidadores, que pueden no tener experiencia técnica."

---

## Diapositiva 12: Resultados y Trabajo Futuro

### Texto de la diapositiva:

**Resultados alcanzados:**
- ✅ 8 sensores IoT funcionando
- ✅ Dashboard en tiempo real
- ✅ Arquitectura híbrida Edge-Cloud
- ✅ Triggers automáticos en Supabase
- ✅ Notificaciones seudonimizadas
- ✅ 12 fichas de evidencia documentadas

**Trabajo futuro:**
- 🔜 Sincronización automática SQLite → Supabase
- 🔜 Integración HL7 FHIR con CENS
- 🔜 Aplicación móvil (PWA o React Native)
- 🔜 Despliegue en Render + Vercel
- 🔜 Piloto con usuarios reales
- 🔜 Postulación a CORFO Semilla Inicia

### Guion del orador (1.5 minutos):

> "Para cerrar, quiero resumir los **resultados alcanzados** y el **trabajo futuro**.
>
> Hemos completado:
>
> - Los **8 sensores IoT** funcionando con datos en tiempo real.
> - El **dashboard en React** que visualiza todo en tiempo real.
> - La **arquitectura híbrida Edge-Cloud** con SQLite y Supabase.
> - Los **triggers automáticos** en PostgreSQL.
> - Las **notificaciones seudonimizadas** con ntfy.
> - Y **12 fichas de evidencia** documentadas en GitHub.
>
> Como **trabajo futuro**, planeamos:
>
> - Implementar la **sincronización automática** SQLite → Supabase.
> - Integrar **HL7 FHIR** con validación del CENS.
> - Desarrollar una **aplicación móvil** (PWA o React Native).
> - Desplegar en **Render y Vercel** para tener URLs públicas.
> - Realizar un **piloto con usuarios reales** (familiares y cuidadores).
> - Y postular a **CORFO Semilla Inicia** para financiar la siguiente etapa.
>
> DomoVida no es solo un proyecto de tesis. Es una solución real a un problema real. Y mi objetivo es que, en el futuro, cada adulto mayor en Chile pueda vivir seguro y con dignidad en su propio hogar.
>
> Muchas gracias."

---

## Notas finales para el orador

| Aspecto | Recomendación |
|---------|---------------|
| **Tiempo total** | 18-20 minutos (1.5 min por diapositiva) |
| **Tono** | Profesional pero cálido, conectando con el impacto humano |
| **Pausas** | Hacer pausas después de cada idea clave |
| **Contacto visual** | Mirar a la comisión, no solo a las diapositivas |
| **Preguntas** | Anticipar preguntas sobre: privacidad, escalabilidad, competencia, costos, y viabilidad comercial |
| **Cierre** | Terminar con la frase: "DomoVida no es solo un proyecto de tesis. Es una solución real a un problema real." |
