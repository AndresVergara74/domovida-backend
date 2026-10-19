# Sesión de usabilidad P02 — notas del facilitador

- **Fecha:** sábado 17/10/2026, 19:30 (adelantada desde el domingo 18/10 19:00)
- **Modalidad:** videollamada Google Meet (anfitrión: cuenta sistemadomovida). Sin grabación.
- **Perfil del participante:** cuidador familiar, rango 30–44 años, usa aplicaciones a diario (según formulario)
- **Cuenta usada:** cuenta de prueba (contraseña simplificada tras el hallazgo H-P01-1)
- **Simulador:** modo tranquilo (`DOMOVIDA_SIM_EMERGENCIAS=0`); alerta de T3 generada con `04_generar_alerta_prueba.js`

## Resultado por tarea

| Tarea | Resultado | Observación |
| --- | --- | --- |
| T1 Ingresar al panel | Completada | Ingreso rápido. La contraseña simplificada resolvió la barrera de P01. |
| T2 Decir si hay alertas activas y si el sistema funciona | Completada | Rápido. |
| T3 Atender la alerta de caída | Completada | Rápido. Hizo varias preguntas sobre la alarma, pero el flujo le quedó claro. |
| T4 Buscar en el historial las caídas de hoy | Completada | Rápido; le pareció buena la información. Notó que la hora de la caída en el panel no coincidía con la hora de su teléfono (ver H-P02-5). |
| T5 Decir en qué parte de la casa ocurrió la última alerta | Sin registro específico | Respuesta correcta: dormitorio. |

## Encuesta SUS

- Enviada el 17/10/2026 20:31 (código P02).

| Ítem | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Respuesta | 4 | 2 | 3 | 2 | 4 | 1 | 4 | 1 | 4 | 2 |
| Aporte | 3 | 3 | 2 | 3 | 3 | 4 | 3 | 4 | 3 | 3 |

- Cálculo: ítems impares (respuesta − 1) = 14; ítems pares (5 − respuesta) = 17; total 31 × 2,5 = **77,5 / 100**. Sobre el promedio de referencia de la escala SUS (68).
- Ítem más bajo: 3 ("fácil de usar" = 3), coherente con su comentario de exceso de información.
- **Más fácil de usar (respuesta abierta):** "Visualizar las alertas que van apareciendo".
- **Qué cambiaría (respuesta abierta):** "La actividad de cada sensor debe ser individual (gráfico por sensor) e indicar cuál está inactivo y desde cuándo. El detalle del sensor dejarlo en la pestaña de sensor y en el resumen indicar que están funcionando y registrando datos, para simplificar la visual del usuario."

## Comentarios del participante

- Percibe **demasiada información** de sensores en el panel.
- Necesita **distinguir lo normal de lo relevante**: qué datos están bien y cuáles son realmente alarmas.
- Quiere saber **si cada sensor está funcionando**: si está desactivado o desconectado, que el panel lo indique (por ejemplo, "no está enviando información").
- Sugiere un **semáforo** para distinguir de un vistazo lo normal, lo que requiere atención y lo peligroso.
- El **detector de caídas** le pareció muy bueno: "es lo que se necesitaba" y lo que espera de un sistema así.
- Quería probar **más tipos de alarma** (ventanas, puertas).
- Sus padres tienen **mascotas**: le preocupa que los sensores de movimiento y de puertas generen ruido o falsas alarmas, y preguntó cómo se configura y programa el sistema.
- Prefiere **gráficos más presentes** y un dashboard más visual.
- Espera que el uso sea **tan fácil como entrar a Netflix**.
- En un audio posterior a la sesión: no ve viable que alguien **monitoree a diario todos los sensores de todos los clientes** ("8 sensores por 10 clientes son 80 sensores"). El modelo debe ser **más reactivo que proactivo**: el sistema avisa cuando algo falla, como una compañía de internet que no te llama a diario, sino que actúa cuando hay un problema.

## Hallazgos

- **H-P02-1 · Jerarquía de información.** El panel muestra todas las lecturas con el mismo peso. Propuesta: separar visualmente "todo normal" de "requiere atención" con un semáforo de severidad (verde / amarillo / rojo), resumen arriba, alarmas destacadas y lecturas normales colapsadas.
- **H-P02-2 · Estado de conexión de sensores.** No se informa cuando un sensor deja de enviar datos. Propuesta: indicador por sensor (en línea / sin datos desde hh:mm) según la última lectura recibida.
- **H-P02-3 · Dashboard visual y simple.** Pide más gráficos y menos texto técnico; referencia de simplicidad: apps de consumo masivo.
- **H-P02-4 · Operación por excepción (escalabilidad).** Revisar sensores manualmente no escala con muchos hogares. Propuesta: el sistema vigila solo y avisa únicamente ante excepciones (alarma real, sensor desconectado, batería baja); el panel queda para consulta, no para vigilancia constante. Refuerza el enfoque actual de avisos al cuidador y se complementa con H-P02-2 (aviso automático de sensor sin datos).
- **H-P02-5 · Hora incorrecta en el panel (defecto).** La hora de la caída de prueba no coincidía con la hora real del teléfono. Hipótesis: el panel o el historial muestran la hora en UTC y no en hora de Chile (UTC−3). Verificar y corregir antes de la próxima sesión si es posible.
- **H-P02-6 · Configuración y falsas alarmas por mascotas.** En hogares con mascotas, los sensores de movimiento y puertas pueden generar ruido. Propuesta: configuración por hogar (sensibilidad, horarios, sensores activos/inactivos) y documentar cómo se programa.
- **H-P02-7 · El mapa del hogar no se entiende.** Los sensores aparecen dispersos sobre un mapa de calles (algunos fuera de la casa, cruzando calles), así que no se lee en qué habitación está cada uno. Propuesta: reemplazar el mapa geográfico por un plano simple de la casa, con una caja por habitación (entrada, living, cocina, dormitorio, sala) y sus sensores dentro, coloreados por estado. Beneficio adicional: en una instalación real, un mapa de calles revelaría la dirección del hogar; un plano no.
- **Corrección aplicada (17/10/2026):** H-P02-5 corregido en el commit 5f95c1c (`timeZone: "America/Santiago"` en el panel). Verificado: el historial muestra las caídas de prueba a las 19:44 y 20:02.
- **Validación de ajuste previo:** T1 completada sin problemas, lo que confirma que la barrera de ingreso de P01 (H-P01-1) se debía a la contraseña compleja en el celular.

## Incidentes de la sesión

- Al final de la sesión falló la tarjeta Wi-Fi del computador del facilitador. El cierre se hizo por WhatsApp. La encuesta SUS se envió igual. No afectó las tareas.
