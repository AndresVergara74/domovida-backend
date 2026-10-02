

```

\# Ficha 18: Decisiones Técnicas y Evaluación de Alternativas



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\*\*Commit de referencia:\*\* `1511332`



\---



\## 18.1 Descripción General



Esta ficha documenta las \*\*decisiones técnicas fundamentadas\*\* durante el desarrollo de DomoVida. Cada decisión sigue un proceso formal de \*\*evaluación de alternativas\*\* bajo criterios de costo, complejidad, tiempo, compatibilidad técnica y alineación con los objetivos del proyecto.



\*\*Principio rector:\*\* Ninguna decisión fue tomada por "imposibilidad técnica", sino por \*\*evaluación racional de trade-offs\*\* considerando las restricciones de un proyecto académico de 18 semanas.



\---



\## 18.2 Decisión 1: Proveedor de Base de Datos Cloud



\### Contexto



DomoVida requiere una base de datos cloud que cumpla con:

\- Compatibilidad con PostgreSQL (para triggers PL/pgSQL)

\- Capa gratuita suficiente para un prototipo académico

\- Baja complejidad de configuración

\- Acceso sin tarjeta de crédito internacional



\### Alternativas Evaluadas



| Proveedor     | Capa gratuita             | Requiere tarjeta | Complejidad config                   | ¿Seleccionado?      |

|---------------|---------------------------|------------------|--------------------------------------|---------------------|

| \*\*AWS RDS\*\*   | 12 meses (750h t2.micro)  | ✅ Sí            | Alta (VPC, IAM, Security Groups)    | ❌                  |

| \*\*Azure SQL\*\* | 12 meses ($200 crédito)   | ✅ Sí            | Alta (suscripción con facturación)  | ❌                  |

| \*\*Neon DB\*\*   | Ilimitada                 | ❌ No            | Media                               | ❌                  |

| \*\*Supabase\*\*  | Ilimitada (500MB)         | ❌ No            | Baja                                | ✅ \*\*Seleccionado\*\* |



\### Fundamento de la Decisión



\*\*Criterios aplicados (en orden de prioridad):\*\*



1\. \*\*Costo:\*\* Supabase ofrece 500MB gratuitos sin tarjeta de crédito. AWS y Azure requieren tarjeta internacional, que el autor no posee al momento del desarrollo (situación común en estudiantes de pregrado en Chile).



2\. \*\*Complejidad de configuración:\*\* AWS RDS requiere configurar VPC, IAM roles, Security Groups y parámetros de instancia. El tiempo estimado de configuración inicial es de 6-8 horas, lo cual excede el retorno de inversión para un proyecto de 18 semanas. Supabase ofrece PostgreSQL administrado con configuración en 15 minutos.



3\. \*\*Compatibilidad técnica:\*\* Supabase expone una conexión PostgreSQL estándar (puerto 6543 con Session Pooler IPv4), compatible con la librería `asyncpg` utilizada en el backend FastAPI. Los triggers PL/pgSQL del proyecto funcionan sin modificaciones.



4\. \*\*Restricción de red institucional:\*\* Durante las pruebas se detectó que Neon DB presentaba incompatibilidades con el ISP del autor (intercepción SSL en puerto 5432), imposibilitando la conexión desde el entorno de desarrollo local. Supabase mitiga esto con su Session Pooler en puerto 6543.



\*\*Resultado:\*\* Arquitectura híbrida SQLite (Edge) + Supabase PostgreSQL (Cloud) implementada exitosamente. Sincronización automática mediante triggers PL/pgSQL. \*\*Ver Ficha 10 y Ficha 11.\*\*



\---



\## 18.3 Decisión 2: Sistema de Notificaciones Push



\### Contexto



DomoVida requiere notificaciones push para alertas críticas (caídas, fugas de gas, botón de pánico).



\### Alternativas Evaluadas



| Proveedor                    | Capa gratuita           | Costo             | Latencia | Dependencias               |

|------------------------------|-------------------------|-------------------|----------|----------------------------|

| \*\*Twilio SMS\*\*               | Prueba (USD 15 crédito) | USD 0.05-0.10/SMS | <3s      | Infraestructura telefónica |

| \*\*Firebase Cloud Messaging\*\* | Ilimitada               | $0                | <2s      | Requiere app móvil nativa  |

| \*\*ntfy\*\*                     | Ilimitada               | $0                | <2s      | HTTP simple                |

| \*\*Telegram Bot\*\*             | Ilimitada               | $0                | <2s      | Requiere cuenta Telegram   |



\### Fundamento de la Decisión



\*\*Criterios aplicados:\*\*



1\. \*\*Costo proyectado:\*\* Para un prototipo sin usuarios reales, Twilio requiere saldo prepago mínimo de USD 20/mes. En un semestre (18 semanas), el costo sería de USD 60-120, no justificado para un proyecto académico.



2\. \*\*Simplicidad:\*\* ntfy permite notificaciones push vía HTTP GET/POST a un topic (ej: `domovida-seguro-2026`). No requiere autenticación compleja ni SDK.



3\. \*\*Compatibilidad multiplataforma:\*\* ntfy tiene apps oficiales para Android, iOS y web, además de notificaciones vía web push.



4\. \*\*Latencia comparable:\*\* Los benchmarks muestran latencia de ntfy <2s, comparable a Twilio SMS (<3s), cumpliendo el KPI del proyecto (entrega > 95%).



\*\*Resultado:\*\* Notificaciones push vía ntfy implementadas. \*\*Ver Ficha 09.\*\*



\---



\## 18.4 Decisión 3: Broker MQTT vs Simulador IoT



\### Contexto



DomoVida requiere comunicación entre 8 sensores IoT y el backend FastAPI.



\### Alternativas Evaluadas



| Alternativa                 | Ventajas                | Desventajas                                            | ¿Seleccionado? |

|-----------------------------|-------------------------|--------------------------------------------------------|----------------|

| \*\*Mosquitto (MQTT real)\*\*   | Estándar IoT, escalable | Requiere despliegue de broker, hardware físico o ESP32 | ❌             |

| \*\*Simulador Python custom\*\* | Control total, sin hardware, generación de anomalías | No refleja protocolo MQTT real | ✅                   															\*\*Seleccionado\* |



\### Fundamento de la Decisión



\*\*Criterios aplicados:\*\*



1\. \*\*Alcance académico:\*\* El proyecto se enfoca en la lógica de negocio (detección de anomalías, alertas, dashboard), no en la capa de comunicación IoT de bajo nivel.



2\. \*\*Hardware no disponible:\*\* No se dispone de los 8 sensores físicos (acelerómetro, PIR, gas, humo, apertura x2, wearable, botón pánico) para pruebas reales. El costo de adquisición supera los USD 300.



3\. \*\*Generación de anomalías controladas:\*\* El simulador permite programar eventos específicos (caídas simuladas, fugas de gas, inactividad prolongada) para pruebas de estrés del sistema, lo cual sería complejo con hardware real.



4\. \*\*Reproducibilidad:\*\* Un simulador garantiza que la comisión evaluadora pueda reproducir los escenarios sin depender de hardware.



\*\*Resultado:\*\* Simulador Python de 8 sensores implementado en `backend/simulate\_sensors.py`. Envía datos cada 5 segundos al endpoint `/api/sensor-data`. \*\*Ver Ficha 04.\*\*



\*\*Nota de honestidad técnica:\*\* El sistema está diseñado para migrar a MQTT real en producción, con cambios mínimos en el backend (reemplazar el endpoint HTTP por un subscriber MQTT). Esta decisión se documenta en el informe como \*\*trabajo futuro\*\*.



\---



\## 18.5 Decisión 4: Arquitectura Híbrida Edge-Cloud (SQLite + Supabase)



\### Contexto



DomoVida opera en un hogar con conexión a internet potencialmente inestable. Las alertas críticas (caídas, fugas de gas) no pueden depender de la conectividad.



\### Alternativas Evaluadas



| Arquitectura | Ventajas | Desventajas | ¿Seleccionado? |

|--------------|----------|-------------|----------------|

| \*\*Cloud-only (Supabase)\*\* | Simple, acceso multi-dispositivo | Dependencia total de internet | ❌ |

| \*\*Local-only (SQLite)\*\* | Funciona offline, baja latencia | Sin respaldo, sin acceso remoto | ❌ |

| \*\*Edge-Cloud híbrida (SQLite + Supabase)\*\* | Resiliencia offline + respaldo cloud | Mayor complejidad | ✅ \*\*Seleccionado\*\* |



\### Fundamento de la Decisión



\*\*Criterios aplicados:\*\*



1\. \*\*Resiliencia:\*\* En sistemas IoT críticos (salud, seguridad), la pérdida de conectividad no debe interrumpir la detección de eventos. SQLite3 local garantiza operación offline.



2\. \*\*Sincronización automática:\*\* Los triggers PL/pgSQL en Supabase sincronizan automáticamente los eventos cuando la conexión se restaura (basado en `sync\_status`).



3\. \*\*Seudonimización:\*\* La capa cloud puede seudonimizar los datos (sin RUT ni nombre) para cumplir con la Ley N° 21.719, mientras que la capa local mantiene los datos de identificación para el cuidador.



4\. \*\*Acceso multi-dispositivo:\*\* El cuidador puede consultar el dashboard desde cualquier dispositivo conectado a internet.



\*\*Resultado:\*\* Arquitectura implementada. SQLite como capa Edge (backend local + Raspberry Pi), Supabase como capa Cloud. \*\*Ver Ficha 05, Ficha 10, Ficha 11.\*\*



\*\*Concepto de ingeniería:\*\* Este patrón se conoce como \*\*Edge Computing\*\* y es un estándar en sistemas IoT industriales. La decisión no es un parche, sino un diseño intencional alineado con las mejores prácticas.



\---



\## 18.6 Decisión 5: Gestión de Conflicto de Dependencias (React 18 vs 19)



\### Contexto



Durante la Fase 2, la instalación de Leaflet (librería de mapas) generó conflicto de peer dependencies.



\### Alternativas Evaluadas



| Alternativa | Ventajas | Desventajas | ¿Seleccionado? |

|-------------|----------|-------------|----------------|

| \*\*Migrar a React 19\*\* | Nuevas funcionalidades | Riesgo de breaking changes en 5 componentes validados | ❌ |

| \*\*Forzar instalación (`--force`)\*\* | Rápido | Dependencias inestables en producción | ❌ |

| \*\*Usar `react-leaflet@4.2.1`\*\* | Compatible con React 18 | Versión anterior | ✅ \*\*Seleccionado\*\* |



\### Fundamento de la Decisión



\*\*Criterios aplicados:\*\*



1\. \*\*Estabilidad:\*\* La migración a React 19 implica riesgo de breaking changes en:

&#x20;  - Dashboard principal (App.tsx)

&#x20;  - Filtros del historial

&#x20;  - WebSocket

&#x20;  - Consentimiento informado

&#x20;  - Modo oscuro



2\. \*\*No aporta valor:\*\* React 19 no ofrece funcionalidades críticas para el proyecto. Su adopción sería un cambio de "vanidad técnica" sin retorno.



3\. \*\*Gestión de deuda técnica:\*\* Usar `react-leaflet@4.2.1` (compatible con React 18) es una práctica estándar en desarrollo ágil, conocida como \*\*gestión de deuda técnica\*\*. Se documenta la decisión y se planifica la migración para Fase 3.



\*\*Resultado:\*\* Instalación exitosa de `leaflet@1.9.4` + `react-leaflet@4.2.1`. \*\*Ver Ficha 17 (sección 17.2, Decisión 2).\*\*



\---



\## 18.7 Decisión 6: Control de Versiones y Sincronización Cloud



\### Contexto



Durante la Fase 2 se produjo un incidente donde OneDrive (backup institucional de Duoc UC) sobrescribió archivos de código activo (`App.tsx`, `App.css`) con versiones anteriores.



\### Análisis del Incidente



\*\*Causa raíz:\*\* OneDrive sincroniza archivos automáticamente cada cierto tiempo. Cuando se guardan cambios en VS Code, OneDrive puede:

1\. Sobrescribir la versión local con la versión en la nube (si detecta "conflicto")

2\. Generar versiones duplicadas (ej: `App (1).tsx`)



\*\*Impacto:\*\* Se perdió temporalmente el componente `MapaHogar.tsx` del `App.tsx`, causando que la pestaña Ubicación desapareciera.



\### Alternativas Evaluadas



| Alternativa | Ventajas | Desventajas | ¿Seleccionado? |

|-------------|----------|-------------|----------------|

| \*\*Mover el proyecto fuera de OneDrive\*\* | Elimina el problema | Pierde backup institucional | ❌ |

| \*\*Usar solo Git local\*\* | Sin dependencia cloud | Sin respaldo remoto | ❌ |

| \*\*Política híbrida\*\* | OneDrive docs + GitHub código | Requiere disciplina | ✅ \*\*Seleccionado\*\* |



\### Fundamento de la Decisión



\*\*Política implementada:\*\*



1\. \*\*OneDrive\*\* → solo para documentación (Word, PDF, Markdown de fichas)

2\. \*\*GitHub\*\* → exclusivamente para código fuente, con commits cada 1-2 horas de trabajo

3\. \*\*.gitignore\*\* → configurado para excluir `package-lock.json` de la raíz, `node\_modules/`, `.env`, bases de datos locales

4\. \*\*Commits frecuentes\*\* → mínimo 1 commit por tarea completada, con mensaje descriptivo



\*\*Recuperación del incidente:\*\* Se usó `git checkout HEAD -- src/App.tsx` para restaurar la versión correcta desde el último commit.



\*\*Resultado:\*\* Política implementada exitosamente. Durante el resto del desarrollo no hubo más incidentes. \*\*Ver Ficha 17 (sección 17.5, Dificultad 2).\*\*



\*\*Lección aprendida:\*\* Este incidente fortaleció la competencia de \*\*gestión de configuración de software\*\* (Software Configuration Management), un área fundamental de la ingeniería de software profesional.



\---



\## 18.8 Resumen Consolidado de Decisiones



| # | Decisión | Alternativa seleccionada | Criterio principal | Ficha |

|---|----------|--------------------------|---------------------|-------|

| 1 | Proveedor BD Cloud | Supabase | Costo + complejidad | 10, 11 |

| 2 | Notificaciones push | ntfy | Costo + simplicidad | 09 |

| 3 | Broker MQTT | Simulador Python | Alcance académico | 04 |

| 4 | Arquitectura persistencia | Edge-Cloud híbrida | Resiliencia | 05, 10, 11 |

| 5 | Conflicto dependencias | react-leaflet@4.2.1 | Estabilidad | 17 |

| 6 | Control de versiones | GitHub-only para código | Gestión de configuración | 17 |



\---



\## 18.9 Aplicación de las 7 Reglas de Redacción Académica



Esta ficha fue redactada siguiendo las siguientes reglas para asegurar calidad académica:



1\. \*\*Decisión, no excusa:\*\* Cada alternativa descartada se fundamenta con criterios objetivos.

2\. \*\*Números sobre adjetivos:\*\* Se incluyen costos (USD 20/mes, USD 60-120), tiempos (6-8 horas), versiones (React 18.3.1, React 19).

3\. \*\*Trazabilidad total:\*\* Cada decisión referencia la Ficha correspondiente y commits específicos.

4\. \*\*Problema → Decisión → Resultado:\*\* Estructura aplicada en cada sección.

5\. \*\*Voz activa:\*\* "Se evaluaron", "Se seleccionó", "Se implementó".

6\. \*\*Honestidad estratégica:\*\* El simulador Python se documenta como decisión temporal, no como implementación final.

7\. \*\*Indicadores de ingeniería:\*\* Métricas, comparaciones, arquitectura justificada.



\---



\## 18.10 Conclusión



Las \*\*6 decisiones técnicas\*\* documentadas en esta ficha demuestran que el desarrollo de DomoVida no estuvo guiado por "problemas técnicos" o "imposibilidades", sino por \*\*evaluación racional de alternativas\*\* considerando restricciones reales de un proyecto académico:



\- Costo (sin tarjeta de crédito internacional)

\- Tiempo (18 semanas)

\- Alcance (prototipo sin usuarios reales)

\- Restricciones institucionales (red del ISP, OneDrive)



Cada decisión está respaldada por \*\*criterios objetivos, trazabilidad documental y aprendizajes de ingeniería\*\*. Esto constituye la base para la sección \*\*"Desarrollo"\*\* del informe de Fase 2, donde se presentarán estas decisiones como parte del proceso de ingeniería profesional.



\*\*Estado:\*\* ✅ \*\*COMPLETADA\*\* — Septiembre 2026

```





