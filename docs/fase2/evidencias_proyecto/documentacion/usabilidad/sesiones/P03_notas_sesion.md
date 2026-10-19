# Sesión de usabilidad P03 — notas del facilitador

- **Fecha:** domingo 18/10/2026, ~13:30–14:00
- **Modalidad:** videollamada Google Meet (anfitrión: cuenta sistemadomovida). Sin grabación.
- **Perfil del participante:** cuidador familiar (de su madre), rango 45–59 años, usa aplicaciones a diario; experiencia laboral en el área de seguridad (según formulario y conversación)
- **Cuenta usada:** cuenta de prueba
- **Simulador:** modo tranquilo; alerta de T3 generada con `04_generar_alerta_prueba.js`
- **Versión del panel:** incluye la corrección de hora del commit 5f95c1c (H-P02-5)

## Resultado por tarea

| Tarea | Resultado | Observación |
| --- | --- | --- |
| T1 Ingresar al panel | Completada | Rápido, con las credenciales enviadas por el chat de Meet. |
| T2 Decir si hay alertas activas y si el sistema funciona | Completada | Sin dificultad. |
| T3 Atender la alerta de caída | Completada | Inmediata. Notó la alerta **sin que se le avisara**, identificó dónde estaba y cómo quedó registrada en el listado. |
| T4 Buscar en el historial las caídas de hoy | Completada | Sin problemas. **La hora mostrada era correcta** (confirma la corrección de H-P02-5). |
| T5 Decir en qué parte de la casa ocurrió la última alerta | Completada | Identificó la ubicación de la alerta. |

## Encuesta SUS

- Enviada el 18/10/2026 13:57 (código "p03").
- Respuestas: ítems 1 a 10 = **5** en todos.
- **Advertencia de validez:** respondió 5 ("muy de acuerdo") también en los ítems negativos (2, 4, 6, 8, 10: "innecesariamente complejo", "necesitaría apoyo", "inconsistente", "engorroso", "necesité aprender mucho"). Esto contradice su desempeño (todas las tareas rápidas) y sus comentarios ("está todo perfecto"). Patrón típico de respuesta en línea recta / sesgo de aquiescencia: probablemente no notó que la escala alterna afirmaciones positivas y negativas.
- Puntaje bruto: impares 4 × 5 = 20; pares (5 − 5) × 5 = 0 → 20 × 2,5 = **50 / 100**.
- Tratamiento propuesto: reportar el puntaje bruto de forma transparente, marcarlo como respuesta inconsistente y presentar el promedio con y sin P03.
- Promedio acumulado: con P03 = (80 + 77,5 + 50) / 3 = **69,2**; sin P03 = **78,75**.
- **Más fácil de usar:** "todas las anteriores".
- **Qué cambiaría:** "está todo perfecto".

## Comentarios del participante

- El sistema funciona y le gustó la página ("perfecta").
- Conoce otros sistemas de monitoreo, pero **no le gustan por las cámaras y el audio**: le complica por su madre. Valoró que DomoVida no capture imágenes ni sonido.
- Le preocupa la **confidencialidad** de la información.

## Hallazgos

- **H-P03-1 · La privacidad es un diferenciador.** Un cuidador con experiencia en seguridad rechaza sistemas con cámaras y micrófono; el enfoque sin imágenes ni audio de DomoVida es un motivo de adopción. Usarlo en la propuesta de valor y en el informe.
- **H-P03-2 · Confianza en el manejo de datos.** Pidió garantías de confidencialidad. Propuesta: explicar en el panel, en lenguaje simple, qué datos se guardan, quién los ve y cuánto tiempo (alineado con la Ley 21.719).
- **H-P03-3 · Redacción del cuestionario SUS.** Respuesta en línea recta en ítems negativos. Para las próximas sesiones: recordar antes de la encuesta que "algunas frases son positivas y otras negativas; lea cada una con calma".
- **Validación de ajustes previos:** T4 con hora correcta (H-P02-5 corregido) y alerta reconocida sin aviso (refuerza el diseño de alertas).
