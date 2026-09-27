Hola DeepSeek. Estoy retomando mi proyecto DomoVida. Necesito que te pongas en contexto.



\## CONTEXTO DEL PROYECTO



\- Proyecto: DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar

\- Autor: Andrés Rodrigo Vergara Acevedo

\- Carrera: Ingeniería en Informática, Duoc UC

\- Asignatura: Capstone (PTY4614)

\- Repositorio: https://github.com/AndresVergara74/domovida-backend

\- Sistema operativo: Windows (PowerShell)

\- Carpeta raíz: C:\\Users\\verga\\OneDrive - Fundacion Instituto Profesional Duoc UC\\domovida-backend

\- Python: 3.14.7 (instalado independiente de Miniconda)

\- Comando para ejecutar backend: py -3 -m uvicorn main:app --reload



\## FECHAS CLAVE



\- Primera revisión Fase 2: 13-14 de octubre 2026

\- Segunda revisión Fase 2: 20-21 de octubre 2026

\- Entrega informe Fase 2: probablemente 30 sept - 1 oct 2026

\- Fase 3: 17-18 o 24-25 de noviembre 2026

\- Defensa final: primera semana de diciembre 2026



\## ESTADO ACTUAL DEL SISTEMA (27 sept 2026)



\### ✅ Backend FastAPI v0.3.0 — Desplegado en Render

\- URL pública: https://domovida-backend.onrender.com

\- Health check: https://domovida-backend.onrender.com/api/health (healthy, 5/5 componentes)

\- Documentación: https://domovida-backend.onrender.com/docs

\- Python: 3.11.9 (forzado con variable PYTHON\_VERSION en Render)

\- Routers: sensores, eventos, alertas, health, WebSocket

\- WebSocket: wss://domovida-backend.onrender.com/api/ws/alertas

\- Base de datos: SQLite (Edge) + Supabase PostgreSQL (Nube, São Paulo)



\### ✅ Frontend React — Desplegado en Vercel

\- URL pública: https://domovida-backend.vercel.app

\- Root Directory en Vercel: frontend

\- Framework: Vite

\- Variables de entorno: .env (local) y .env.production (Vercel)

\- Hook useDomovida: polling cada 10s

\- Hook useWebSocket: alertas en tiempo real

\- Dashboard con 3 pestañas: Vista general, Historial, Sensores

\- Diseño moderno (gradientes, tipografía Inter, responsive)



\### ✅ Base de Datos Supabase PostgreSQL

\- Proyecto: domovida

\- Región: São Paulo

\- Tabla eventos: id, sensor\_id, tipo, habitacion, valor, alerta, timestamp, sync\_status, resuelto, resuelto\_en, resuelto\_por

\- Tabla alertas: id, evento\_id, tipo\_alerta, nivel\_severidad, payload\_fhir, resuelto, resuelto\_en, resuelto\_por, notas\_resolucion, creado\_en

\- Trigger #1: sync\_status automático en INSERT

\- Trigger #2: crear\_alerta\_automatica en INSERT (cuando alerta=true)

\- RLS activado en todas las tablas

\- Session Pooler IPv4: puerto 6543

\- Cadena de conexión en .env (NO subir a GitHub)



\### ✅ 8 Sensores IoT Simulados

1\. acelerometro\_dormitorio (detección de caídas)

2\. pir\_living (movimiento/inactividad)

3\. gas\_cocina (fugas)

4\. humo\_cocina (incendios)

5\. apertura\_puerta\_principal

6\. apertura\_ventana\_living

7\. wearable\_cardiaco (taquicardia/bradicardia)

8\. boton\_panico\_sala

\- Simulador: backend/simulate\_sensors.py



\### ✅ Notificaciones

\- ntfy: notificaciones push seudonimizadas (topic: domovida-seguro-2026)

\- WebSocket: alertas en tiempo real (13 alertas en 5 min, < 1 seg)

\- Ciclo del cuidador: botón "Marcar como atendida" + trazabilidad



\### ✅ Documentación (15 fichas en docs/evidencias\_OE1/)

01\_arquitectura\_general.md

02\_backend\_fastapi.md

03\_frontend\_react.md

04\_sensores\_iot.md

05\_base\_datos.md

06\_dashboard\_capturas.md

07\_alarmas\_criticas.md

08\_comandos\_ejecucion.md

09\_sistema\_notificaciones.md

10\_conexion\_supabase.md

11\_triggers\_supabase.md

12\_guion\_presentacion.md

13\_integracion\_completa.md

14\_consentimiento\_informado.md

15\_websocket\_tiempo\_real.md



\## CORRECCIONES DEL PROFESOR (16 sept 2026)



El profesor me pidió ajustar el proyecto a 3 objetivos específicos que sean REALES y medibles:



\### OE1: Diseñar e implementar el sistema IoT con sensores simulados

Diseñar e implementar una infraestructura IoT con 8 sensores simulados (acelerómetro para detección de caídas, PIR para movimiento, gas, humo, apertura de puertas/ventanas, cardíaco y botón de pánico) que permitan monitorear la actividad del adulto mayor de forma no invasiva, garantizando la captura continua de datos y la resiliencia ante fallas de conectividad mediante persistencia local en SQLite3.



KPIs: 8 sensores operativos, persistencia SQLite3 100%, latencia < 5 seg, tasa captura > 99%



\### OE2: Implementar la infraestructura híbrida Edge-Cloud con automatización en base de datos

Implementar una arquitectura de persistencia híbrida que combine SQLite3 (Edge local) con Supabase PostgreSQL (nube), sincronización automática mediante triggers PL/pgSQL, y procesamiento en el borde (Edge Computing) con detección de anomalías, garantizando la seudonimización de datos sensibles conforme a la Ley N° 21.719 y la disponibilidad del sistema en producción (Render + Vercel).



KPIs: Sincronización 100%, creación alertas 100%, seudonimización 100%, uptime > 99%, RLS 100%



\### OE3: Desarrollar el dashboard y el sistema de notificaciones en tiempo real

Desarrollar un dashboard web en React desplegado en Vercel que permita visualizar el estado del adulto mayor en tiempo real, recibir alertas vía WebSocket en menos de 1 segundo, notificaciones push vía ntfy, y gestionar el ciclo de atención de alertas con trazabilidad completa, validado mediante la Escala SUS con una puntuación objetivo superior a 70 puntos.



KPIs: Latencia WebSocket < 1 seg, entrega ntfy > 95%, trazabilidad 100%, Escala SUS > 70, despliegue 100%



\## LO QUE SE DESCARTÓ



\- ❌ AWS (no se pudo crear la cuenta)

\- ❌ Azure (no se pudo crear la cuenta)

\- ❌ Neon (el ISP intercepta conexiones SSL al puerto 5432)

\- ❌ Twilio (se reemplazó por ntfy)

\- ✅ Alternativa elegida: Supabase (PostgreSQL) + Render (backend) + Vercel (frontend) + ntfy (notificaciones)



\## SCRUM APLICADO A LA FASE 2



Sprints:

\- Sprint 3 (S7-S8): Definición y diseño (Guía 2.1, 2.2, 2.3)

\- Sprint 4 (S9-S10): Backend + BD híbrida (API + Supabase + Triggers)

\- Sprint 5 (S11-S12): Frontend + WebSocket (Dashboard + ntfy + tiempo real)

\- Sprint 6 (S13-S14): Certificación (SUS + Pruebas + Documentación)



Artefactos: Product Backlog (GitHub Projects), Sprint Backlog, DoD (Ficha 01), Sprint Review (URLs), Sprint Retrospective (Obsidian)



\## LO QUE FALTA



\### 🔴 Prioridad Alta

1\. Reformular los 3 OE en el informe Fase 2

2\. Actualizar el PPT con los 3 OE reformulados

3\. Redactar Abstract (español + inglés) del informe Fase 2

4\. Redactar apartados del informe Fase 2 (Relevancia, Objetivos, Metodología, Desarrollo, Evidencias, Intereses)

5\. Aplicar Escala SUS (> 70 pts)

6\. Verificar despliegue en producción (Render + Vercel + Supabase)



\### 🟡 Prioridad Media

7\. Modo oscuro + Iconos Lucide

8\. Filtros en Historial

9\. Botón "Marcar atendida" en el frontend (el endpoint existe)

10\. Pestaña Ubicación (Leaflet)



\### 🟢 Prioridad Baja

11\. PWA (instalable en teléfono)

12\. Autenticación JWT

13\. Integración HL7 FHIR

14\. Manual de usuario



\## ESTRUCTURA DEL INFORME FASE 2



Según la guía del profesor, el informe debe contener:

1\. Relevancia del proyecto APT

2\. Objetivos (general y específicos)

3\. Metodología utilizada (Scrum)

4\. Desarrollo (etapas, dificultades, facilitadores, ajustes)

5\. Evidencias del avance

6\. Intereses y proyecciones profesionales



Formato: Portada, índice, abstract (español e inglés), desarrollo de ingeniería, conclusiones (solo inglés), reflexión (solo inglés), bibliografía, anexos.

Letra: Arial/Verdana/Calibri 11-12, interlineado 1.0-1.5.



\## MI FORMA DE TRABAJAR CONTIGO



\- Prefiero paso a paso, un comando a la vez

\- Uso PowerShell en Windows

\- Uso el Bloc de notas para editar archivos

\- A veces me equivoco al pegar comandos

\- Me gusta que me expliques el "por qué" de cada paso

\- Necesito comandos exactos para copiar y pegar

\- Me ayudas a diagnosticar errores con paciencia

\- Usas emojis para hacerlo más ameno

\- Me llamas "Andrés"

\- Me das opciones (A, B, C, D) cuando hay decisiones

\- Usas tablas para organizar la información

\- Haces resúmenes al final de cada sesión

\- Cuando algo funciona, celebras con emojis 🎉

\- NO preguntar por AWS ni Twilio (descartados)



\## LO QUE NECESITO AHORA



\[Escribe aquí lo que necesitas hacer en este momento]



Por favor, ponte en contexto, salúdame como siempre, y ayúdame a continuar.

