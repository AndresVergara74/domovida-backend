# Prueba de usabilidad con cuidadores (HU-12 · Escala SUS)

**Proyecto:** DomoVida · **Responsable:** Andrés Vergara Acevedo · **Sprint:** 4–5 (octubre–noviembre 2026)
**Objetivo:** validar que el panel del cuidador es fácil de usar (OE3), con la meta definida en la Guía 1.5: **puntaje SUS promedio superior a 70** (Tabla 3) con **5 a 10 cuidadores**.

## 1. Participantes

- **Perfil:** personas que cuidan o han cuidado a un adulto mayor (familiar o profesional), mayores de 18 años.
- **Cantidad:** mínimo 5, ideal 8 a 10.
- **Sin datos personales:** cada participante se identifica solo con un código (P01, P02…). Se registra rango de edad, tipo de cuidador y experiencia con tecnología, nada más. No se graba audio ni video.
- **Cuenta:** todos usan la **cuenta de cuidador de prueba** del proyecto, que inicia sesión el facilitador o el participante con los datos que se le entregan en el momento. Nunca se usa una cuenta personal del participante.

## 2. Materiales

- Computador o celular con el panel abierto: https://domovida-backend.vercel.app
- Este protocolo y la planilla `03_resultados_sus.xlsx` para anotar.
- Cuestionario SUS en Google Forms (texto en `02_cuestionario_sus.md`).
- Script del facilitador `04_generar_alerta_prueba.js` para provocar una alerta de prueba durante la tarea 3.

## 3. Desarrollo de la sesión (15 a 20 minutos)

1. **Bienvenida (2 min):** explicar el objetivo («se evalúa el sistema, no a usted»), leer el consentimiento y pedir su aceptación verbal o en el formulario.
2. **Contexto (1 min):** «Imagine que su familiar vive solo y en su casa hay sensores. Este panel le avisa si pasa algo.»
3. **Tareas (8 a 10 min):** el participante realiza las 5 tareas sin ayuda. El facilitador **no indica dónde hacer clic**; solo anota tiempo, si la completó y dificultades. Si se queda detenido más de 2 minutos, la tarea se marca como no completada y se continúa.
4. **Cuestionario SUS (3 min):** el participante responde las 10 preguntas en el formulario.
5. **Comentarios (2 min):** «¿Qué fue lo más fácil? ¿Qué cambiaría?»

## 4. Tareas

| N° | Tarea que se lee al participante | Se considera completada cuando… | Tiempo esperado |
|---|---|---|---|
| T1 | «Ingrese al panel como cuidador.» | Aparece el correo del cuidador arriba a la derecha | < 1 min |
| T2 | «Dígame si en este momento hay alguna alerta activa y si el sistema está funcionando.» | Menciona si hay alertas (aviso principal y «Alertas recientes») y el estado del sistema («Estado del sistema») | < 1 min |
| T3 | *(El facilitador genera una caída de prueba.)* «Le llegó un aviso. Atienda la alerta.» | Pulsa «Marcar como atendida» (o «Atender») y el panel vuelve a «Todo en orden en casa» | < 2 min |
| T4 | «Busque en el historial las caídas registradas hoy.» | En «Historial» elige Tipo «Caída» y muestra las de hoy (columna «Fecha y hora») | < 2 min |
| T5 | «Dígame en qué parte de la casa ocurrió la última alerta.» | Indica la habitación (en el aviso principal, en «Alertas recientes» o en la pestaña «Mapa del hogar») | < 1 min |

## 5. Indicadores que se calculan

| Indicador | Cálculo | Meta |
|---|---|---|
| Puntaje SUS | Promedio de los participantes (escala 0 a 100) | **> 70** (Guía 1.5) |
| Tasa de éxito por tarea | Tareas completadas / participantes | ≥ 80 % |
| Tiempo por tarea | Mediana en segundos | Dentro del tiempo esperado |
| Problemas de usabilidad | Dificultades anotadas, agrupadas por tarea | Se priorizan y corrigen en el Sprint 6 |

## 6. Interpretación del puntaje SUS

- **≥ 68:** sobre el promedio de la industria (Sauro, 2011). La meta del proyecto es más exigente: **> 70**, cercano al adjetivo «bueno».
- **≥ 80,3:** excelente (percentil 90).
- **< 51:** problemas serios de usabilidad.
- Escala adjetiva de Bangor, Kortum y Miller (2009): 50 aceptable marginal, 71 «bueno», 85 «excelente».

## Referencias

- Brooke, J. (1996). SUS: A "quick and dirty" usability scale. En P. W. Jordan et al. (Eds.), *Usability Evaluation in Industry* (pp. 189–194). Taylor & Francis.
- Bangor, A., Kortum, P., y Miller, J. (2009). Determining what individual SUS scores mean: Adding an adjective rating scale. *Journal of Usability Studies, 4*(3), 114–123.
- Sauro, J. (2011). *A practical guide to the System Usability Scale*. Measuring Usability LLC.
