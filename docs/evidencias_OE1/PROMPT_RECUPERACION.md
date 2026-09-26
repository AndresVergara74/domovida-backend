\# PROMPT DE RECUPERACIÓN — DOMOVIDA



\*\*Propósito:\*\* Este archivo contiene el contexto completo del proyecto DomoVida para retomar el trabajo en un chat nuevo de DeepSeek en caso de que el chat actual falle.



\*\*Última actualización:\*\* 26 de septiembre de 2026, 05:00 AM



\---



\## 📋 INSTRUCCIONES DE USO



1\. Abre un nuevo chat de DeepSeek.

2\. Copia y pega \*\*TODO\*\* el contenido de este archivo (excepto esta sección).

3\. Cambia la sección `\[LO QUE NECESITO AHORA]` por tu necesidad actual.

4\. DeepSeek se pondrá en contexto y continuará la conversación.



\---



\## 🤖 PROMPT PARA DEEPSEEK



Hola DeepSeek. Estoy retomando un proyecto llamado DomoVida que veníamos trabajando juntos. Necesito que te pongas en contexto.



\## CONTEXTO DEL PROYECTO



\- \*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar

\- \*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo

\- \*\*Carrera:\*\* Ingeniería en Informática, Duoc UC

\- \*\*Asignatura:\*\* Capstone (PTY4614)

\- \*\*Repositorio:\*\* https://github.com/AndresVergara74/domovida-backend

\- \*\*Sistema operativo:\*\* Windows (PowerShell)

\- \*\*Carpeta raíz:\*\* `C:\\Users\\verga\\OneDrive - Fundacion Instituto Profesional Duoc UC\\domovida-backend`



\## ESTADO ACTUAL DEL PROYECTO (26 sept 2026)



\### ✅ BACKEND (FastAPI) - DESPLEGADO EN RENDER



\- \*\*URL pública:\*\* https://domovida-backend.onrender.com

\- \*\*Health check:\*\* https://domovida-backend.onrender.com/api/health (healthy, 5/5 componentes)

\- \*\*Documentación:\*\* https://domovida-backend.onrender.com/docs

\- \*\*Versión:\*\* 0.3.0

\- \*\*Python:\*\* 3.11.9 (forzado con variable `PYTHON\_VERSION` en Render)

\- \*\*Routers:\*\* sensores, eventos, alertas, health, WebSocket

\- \*\*WebSocket:\*\* wss://domovida-backend.onrender.com/api/ws/alertas

\- \*\*Base de datos:\*\* SQLite (Edge) + Supabase PostgreSQL (Nube, São Paulo)

\- \*\*CORS:\*\* Configurado para localhost + Vercel



\### ✅ FRONTEND (React + Vite) - DESPLEGADO EN VERCEL



\- \*\*URL pública:\*\* https://domovida-backend.vercel.app

\- \*\*Repositorio:\*\* mismo repo, carpeta `frontend/`

\- \*\*Root Directory en Vercel:\*\* `frontend`

\- \*\*Framework:\*\* Vite

\- \*\*Archivos clave:\*\* `package.json`, `tsconfig.json`, `src/api.ts`, `src/useWebSocket.ts`, `src/useDomovida.ts`, `src/App.tsx`, `src/App.css`

\- \*\*Variables de entorno:\*\* `.env` (local) y `.env.production` (Vercel). También configuradas en el dashboard de Vercel.

\- \*\*Hook useDomovida:\*\* polling cada 10s

\- \*\*Hook useWebSocket:\*\* alertas en tiempo real



\### ✅ BASE DE DATOS (Supabase PostgreSQL)



\- \*\*Proyecto:\*\* domovida

\- \*\*Región:\*\* São Paulo

\- \*\*Tabla `eventos` con campos:\*\* id, sensor\_id, tipo, habitacion, valor, alerta, timestamp, sync\_status, resuelto, resuelto\_en, resuelto\_por

\- \*\*Tabla `alertas` con RLS activado\*\*

\- \*\*Trigger #1:\*\* sync\_status automático

\- \*\*Trigger #2:\*\* crear\_alerta\_automatica

\- \*\*Session Pooler IPv4:\*\* puerto 6543 (evita intercepción del ISP)



\### ✅ SENSORES IoT (8 simulados)



1\. acelerometro\_dormitorio

2\. pir\_living

3\. gas\_cocina

4\. humo\_cocina

5\. apertura\_puerta\_principal

6\. apertura\_ventana\_living

7\. wearable\_cardiaco

8\. boton\_panico\_sala



\- \*\*Simulador:\*\* backend/simulate\_sensors.py



\### ✅ NOTIFICACIONES



\- \*\*ntfy:\*\* notificaciones push seudonimizadas

\- \*\*WebSocket:\*\* alertas en tiempo real



\### ✅ FUNCIONALIDAD NUEVA: RESPUESTA DEL CUIDADOR



\- \*\*Endpoint:\*\* `PATCH /api/alertas/{id}/resolver`

\- \*\*Body:\*\* `{"resuelto\_por": "Cuidador DomoVida"}`

\- \*\*Botón "✓ Atender"\*\* en el dashboard

\- \*\*Campos actualizados:\*\* `resuelto=true`, `resuelto\_en`, `resuelto\_por`

\- \*\*Traza:\*\* Se sabe quién y cuándo atendió cada alerta



\### ✅ DOCUMENTACIÓN (16 fichas en docs/evidencias\_OE1/)



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

16\_respuesta\_cuidador.md



\## ERRORES RESUELTOS EN RENDER



1\. `pydantic-core` falla con Rust → Solución: Python 3.11 con wheels precompilados

2\. `Procfile.txt` (extensión) → Solución: Rename-Item

3\. Error ASGI app → Solución: `cd backend \&\& uvicorn`

4\. `ModuleNotFoundError: psycopg` → Solución: agregar `psycopg\[binary]` al requirements

5\. Python 3.14 por defecto → Solución: `PYTHON\_VERSION=3.11.9` en Environment Variables

6\. CORS bloqueado → Solución: agregar URL de Vercel al `allow\_origins`



\## ERRORES RESUELTOS EN VERCEL



1\. Faltaban dependencias React → Solución: `package.json` completo con react, react-dom, @types/react, @types/react-dom, @types/node, @vitejs/plugin-react

2\. `erasableSyntaxOnly` no existe en TS 5.6 → Solución: eliminar la opción

3\. `Cannot find namespace 'NodeJS'` → Solución: agregar `"types": \["node", "vite/client"]`

4\. Property 'severidad' no existe en AlertaWebSocket → Solución: campos opcionales en interfaces

5\. Variables de entorno no configuradas → Solución: agregar en Vercel dashboard (Type: Config, Environment: Production)



\## LO QUE FALTA



\### 🔴 PRIORIDAD ALTA (Domingo)



1\. Informe final de tesis (3-4 horas)

2\. Escala SUS (validación de usabilidad, 2 horas)

3\. Video de 40 segundos (CORFO, 1 hora) — \*\*Primeros días de octubre con nuevo look\*\*



\### 🟡 PRIORIDAD MEDIA (Si hay tiempo)



4\. Modo oscuro en el dashboard (30 min)

5\. Iconos Lucide en vez de emojis (30 min)

6\. Filtros en Historial (45 min)

7\. Pestaña "Ubicación" con Leaflet (1 hora)



\### 🟢 PRIORIDAD BAJA (Nice to have)



8\. PWA (instalable en teléfono, 3 horas)

9\. Autenticación JWT (2 horas)

10\. Integración HL7 FHIR (4 horas)

11\. Manual de usuario (2 horas)



\## MI FORMA DE TRABAJAR CONTIGO



\- Prefiero paso a paso, un comando a la vez

\- Uso PowerShell en Windows

\- Uso el Bloc de notas para editar archivos

\- A veces me equivoco al pegar comandos (agrego texto extra)

\- Me gusta que me expliques el "por qué" de cada paso

\- Necesito que me des los comandos exactos para copiar y pegar

\- Me ayudas a diagnosticar errores con paciencia

\- Cuando algo falla, prefieres que te pegue los logs completos

\- Usas emojis para hacerlo más ameno

\- Me llamas "Andrés" y yo te llamo "mi chinito sabio"

\- Me das opciones (A, B, C, D) cuando hay decisiones

\- Usas tablas para organizar la información

\- Haces resúmenes al final de cada sesión

\- Cuando algo funciona, celebras con emojis 🎉

\- Cuando algo falla, mantienes la calma y diagnosticas



\## LO QUE NECESITO AHORA



\[Escribe aquí lo que necesitas hacer en este momento]



Por favor, ponte en contexto, salúdame como siempre, y ayúdame a continuar.

```



\---



\## 🎯 Instrucciones



1\.  \*\*En el Bloc de notas:\*\* Pega todo el contenido de arriba.

2\.  \*\*Guarda con `Ctrl + S`.\*\*

3\.  \*\*Cierra el Bloc de notas.\*\*

4\.  \*\*Dime "listo".\*\*



