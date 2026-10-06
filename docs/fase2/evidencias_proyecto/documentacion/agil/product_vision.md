# DomoVida · Product Vision

**Proyecto APT:** DomoVida: Plataforma IoT de Monitoreo y Asistencia para el Adulto Mayor en el Hogar
**Autor:** Andrés Rodrigo Vergara Acevedo · Capstone PTY4614 · Duoc UC, sede Viña del Mar
**Versión:** 6 de octubre de 2026 (formato según la Guía de apoyo del estudiante, sección 5.1)

---

## 1. ¿Qué problema queremos resolver?

Chile envejece rápidamente: las personas de 60 años y más pasaron del 9,5 % de la población en 1992 al 18,1 % en 2022, y se proyecta que lleguen al 32,1 % en 2050 (INE, 2022). Cada vez más personas mayores viven solas, y entre el 28 % y el 35 % de las personas de 65 años o más sufre al menos una caída al año (OMS, 2021). Cuando la persona vive sola, la caída puede pasar horas sin que nadie lo sepa, y el tiempo hasta recibir ayuda aumenta las complicaciones.

## 2. ¿Quiénes son los usuarios?

| Usuario | Necesidad |
|---|---|
| **Cuidador o familiar** (usuario principal) | Saber a tiempo si ocurrió una caída u otra emergencia, aunque no esté en el hogar, y registrar que la atendió. |
| **Persona mayor que vive sola** | Seguir viviendo en su casa con autonomía, sabiendo que alguien será avisado si le pasa algo, y decidir sobre sus datos (consentimiento). |
| **Equipo de salud (CESFAM)** (parte interesada) | Recibir información del hogar en un formato estándar que pueda integrar a la ficha clínica. |

## 3. ¿Qué solución proponemos?

Una plataforma IoT que monitorea el hogar con sensores (caídas, movimiento, gas, humo, apertura de puerta, frecuencia cardíaca y botón de pánico), detecta los eventos de riesgo con reglas en el borde y alerta al cuidador en tiempo real en un panel web y en su celular. Si se corta internet, el sistema sigue funcionando en el hogar.

## 4. Declaración de visión

| Elemento | Contenido |
|---|---|
| **Para** | cuidadores y familiares de personas mayores que viven solas en Chile |
| **Que necesita** | enterarse de inmediato cuando ocurre una caída u otra emergencia en el hogar |
| **Nuestro producto** | DomoVida, una plataforma IoT de monitoreo y asistencia del hogar |
| **Permite** | recibir la alerta en el panel y en el celular en segundos, registrar quién la atendió y seguir monitoreando aunque no haya internet |
| **A diferencia de** | los botones de emergencia que dependen de que la persona los presione, o de las llamadas periódicas de la familia |
| **Se distingue por** | detectar el evento sin intervención de la persona, funcionar sin internet (modo borde), proteger los datos según la Ley N° 21.719 y usar el estándar de salud HL7 FHIR para integrarse con la red asistencial |

## 5. ¿Cuál es la propuesta de valor?

- **Rapidez:** la alerta llega al panel en 216 ms en una infraestructura con backend y base de datos en la misma región, y el 100 % de las notificaciones llegó al celular en las pruebas (PR-01b y PR-02).
- **Continuidad:** sin internet, el modo borde guardó y mostró el 100 % de las caídas (PR-03).
- **Confianza:** consentimiento informado, seudonimización del RUT, RLS, clave para los sensores y sesión para el cuidador (PU-03, PI-03, PS-01 y PS-01b).
- **Interoperabilidad:** los eventos y el paciente seudonimizado se exponen como recursos HL7 FHIR R4 válidos (PI-04 y PI-05).
- **Bajo costo:** el prototipo funciona sobre servicios gratuitos (Render, Vercel y Supabase).

## 6. ¿Qué incluye el MVP?

| Incluido en el MVP | Fuera del MVP (trabajo futuro) |
|---|---|
| Simulador de 8 sensores y reglas de detección (caída, gas, humo, inactividad, puerta) | Sensores físicos y Raspberry Pi real con MQTT |
| Alertas en tiempo real (WebSocket) y notificaciones push (ntfy) | Detección con Machine Learning (Isolation Forest) |
| Panel del cuidador: vista general, historial con filtros, sensores y mapa del hogar | Pulsera o botón de pánico portátil |
| Registro de la atención de cada alerta con sesión del cuidador | Aplicación móvil nativa |
| Modo borde sin internet (SQLite) | Integración real con la ficha clínica de un CESFAM |
| Consentimiento informado, seudonimización y RLS | |
| Recursos HL7 FHIR R4 (Observation y Patient) | |

El backlog priorizado (HU-01 a HU-12, método MoSCoW) está en la Guía 1.5 y en el tablero Kanban: https://github.com/users/AndresVergara74/projects/1

---

**Referencias**

- Instituto Nacional de Estadísticas (INE). (2022). *Estimaciones y proyecciones de la población de Chile 1992-2050*. https://www.ine.gob.cl
- Organización Mundial de la Salud (OMS). (2021). *Caídas* [Nota descriptiva]. https://www.who.int/es/news-room/fact-sheets/detail/falls
