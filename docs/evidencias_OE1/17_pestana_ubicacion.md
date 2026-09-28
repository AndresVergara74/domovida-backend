\# Ficha 17: Pestaña Ubicación + Mapa Leaflet



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\*\*Commit de referencia:\*\* `6f20e26`



\---



\## 17.1 Descripción General



La \*\*Pestaña Ubicación\*\* es una funcionalidad de la Fase 2 que permite visualizar geográficamente la ubicación de los 8 sensores IoT del hogar sobre un mapa interactivo. Esta vista complementa el dashboard numérico con una representación espacial que facilita al cuidador identificar rápidamente qué zona del hogar presenta actividad o inactividad.



La funcionalidad se implementó durante el Sprint 5 (Frontend + WebSocket) y utiliza la librería \*\*Leaflet\*\* (mapa open-source) con OpenStreetMap como proveedor de tiles gratuitos.



\---



\## 17.2 Decisiones Técnicas Fundamentadas



\### Decisión 1: Selección de Leaflet sobre alternativas



Se evaluaron \*\*3 alternativas\*\* de librerías de mapas para React:



| Alternativa                 | Ventajas                             | Desventajas | ¿Seleccionada? |

|-----------------------------|--------------------------------------|-------------|----------------|

| \*\*Google Maps API\*\*  | Mapas actualizados, alto rendimiento  | Requiere tarjeta de crédito + API key + facturación, USD 200/mes crédito inicial| ❌ Descartada por costo y burocracia |



| \*\*Mapbox GL JS\*\* | Diseño moderno, tiles vectoriales | Capa gratuita 50.000 requests/mes, luego USD 0.50/1000 requests | ❌ Descartada por límite de uso  |



| \*\*Leaflet + OpenStreetMap\*\* | Open-source, 0 costo, sin API key, comunidad activa | Tiles menos detallados que Google Maps | ✅ \*\*Seleccionada\*\*|



\*\*Fundamento de la decisión:\*\* Para un prototipo académico sin usuarios reales, la ausencia de costo y la simplicidad de configuración (sin API key) son criterios prioritarios. Leaflet cumple con los requisitos funcionales del proyecto (marcadores, popups, área del hogar) sin comprometer la arquitectura.



\---



\### Decisión 2: Gestión de conflicto de dependencias (React 18 vs React 19)



Durante la instalación de Leaflet se detectó el siguiente conflicto:



```

npm error ERESOLVE unable to resolve dependency tree

npm error peer react@"^19.0.0" from react-leaflet@5.0.0

npm error Found: react@18.3.1

```



\*\*Análisis:\*\* `react-leaflet@5.0.0` requiere React 19, mientras que el proyecto DomoVida está construido sobre \*\*React 18.3.1\*\* (versión estable elegida en Fase 1).



\*\*Alternativas evaluadas:\*\*



| Alternativa | Ventajas | Desventajas | ¿Seleccionada? |

|-------------|----------|-------------|----------------|

| Migrar a React 19 | Acceso a nuevas funcionalidades | Riesgo de breaking changes en dashboard, filtros, WebSocket | ❌ Descartada por riesgo |

| Forzar instalación (`--force`) | Instalación rápida | Dependencias potencialmente rotas (inestable en producción) | ❌ Descartada por estabilidad |

| Usar `react-leaflet@4.2.1` | Compatible con React 18, API estable | Versión anterior | ✅ \*\*Seleccionada\*\* |



\*\*Fundamento de la decisión:\*\* La migración a React 19 implicaba riesgo de breaking changes en componentes ya validados (dashboard, filtros, WebSocket, consentimiento), sin aportar funcionalidades críticas para el objetivo del proyecto. Se optó por `react-leaflet@4.2.1` (compatible con React 18) para mantener la estabilidad del sistema. Esta práctica corresponde a \*\*gestión de deuda técnica\*\* en desarrollo ágil.



\*\*Trazabilidad:\*\* Decisión documentada en `frontend/package.json` (versión `4.2.1`) y commit `55e09ca`.



\---



\## 17.3 Arquitectura de la Funcionalidad



\### Componente `MapaHogar.tsx`



Ubicación: `frontend/src/MapaHogar.tsx`



\*\*Responsabilidades:\*\*

1\. Renderizar un mapa Leaflet centrado en el hogar (coordenadas Santiago, Chile)

2\. Mostrar un marcador por cada sensor IoT (8 marcadores)

3\. Diferenciar visualmente sensores online (verde) vs offline (rojo)

4\. Mostrar un círculo punteado que representa el área del hogar

5\. Incluir popup con información detallada del sensor (tipo, habitación, última lectura)



\*\*Estructura de coordenadas por habitación:\*\*



| Habitación | Coordenadas (lat, lng) |

|------------|------------------------|

| dormitorio | (-33.4485, -70.6695) |

| living     | (-33.4489, -70.6690) |

| cocina     | (-33.4492, -70.6693) |

| entrada    | (-33.4495, -70.6695) |

| sala       | (-33.4487, -70.6688) |

| baño       | (-33.4483, -70.6692) |

| pasillo    | (-33.4490, -70.6691) |

| wearable   | (-33.4489, -70.6693) |



\*\*Iconos por tipo de sensor:\*\*



| Tipo           | Emoji |

|----------------|-------|

| pir            | 🚶   |

| acelerometro   | 📳   |

| gas            | 💨   |

| humo           | 🔥   |

| apertura       | 🚪   |

| cardiovascular | ❤️   |

| boton\_panico   | 🚨   |



\---



\### Integración en `App.tsx`



La pestaña "Ubicación" se agregó al `<nav className="tabs">` como cuarta pestaña. Cuando el usuario la selecciona, se renderiza:



```tsx

{pestana === "ubicacion" \&\& (

&#x20; <section className="ubicacion">

&#x20;   <MapaHogar sensores={sensores} />

&#x20; </section>

)}

```



Los sensores provienen del hook `useDomovida()`, que los deriva desde los últimos 200 eventos del backend.



\---



\## 17.4 KPIs Asociados



| # | KPI                             | Meta      | Estado     | Evidencia                              |

|---|---------------------------------|-----------|------------|----------------------------------------|

| 1 | Sensores visibles en mapa       | 8         | ✅ Logrado | Captura `17\_mapa\_sensores.png`         |

| 2 | Marcadores online diferenciados | 100%      | ✅ Logrado | Marcadores verdes cuando `online=true` |

| 3 | Círculo del área del hogar      | Visible   | ✅ Logrado | Círculo verde punteado                 |

| 4 | Popup con info del sensor       | Funcional | ✅ Logrado | Captura `17\_popup\_sensor.png`          |

| 5 | Responsive (móvil/tablet)       | 100%      | ✅ Logrado | CSS `@media (max-width: 768px)`        |

| 6 | Tiempo de carga del mapa        | < 3 seg   | ✅ Logrado | OpenStreetMap carga en \~1.5s           |

| 7 | Latencia de actualización       | < 10 seg  | ✅ Logrado | Polling cada 10s via `useDomovida`     |



\---



\## 17.5 Dificultades y Mitigaciones



\### Dificultad 1: Conflicto de dependencias React 18 vs React 19



\*\*Problema:\*\* `react-leaflet@5.0.0` requiere React 19, incompatible con React 18.3.1 del proyecto.



\*\*Decisión:\*\* Se evaluaron 3 alternativas (migrar a React 19, forzar instalación, usar versión compatible). Se seleccionó `react-leaflet@4.2.1` por compatibilidad.



\*\*Resultado:\*\* Instalación exitosa sin breaking changes. Tiempo de resolución: 15 minutos. Documentado en la sección 17.2 (Decisión 2).



\### Dificultad 2: Incidente de sincronización OneDrive



\*\*Problema:\*\* Durante el desarrollo, OneDrive (backup institucional) sobrescribió `App.tsx` con una versión anterior, causando que la pestaña Ubicación desapareciera del frontend.



\*\*Decisión:\*\* Se recuperó el archivo mediante `git checkout HEAD -- src/App.tsx`, y se estableció política de control de versiones:

\- OneDrive solo para documentación (Word, PDF, Markdown)

\- Código fuente exclusivamente en GitHub con commits frecuentes (mínimo 1 por tarea completada)

\- `.gitignore` configurado para excluir `package-lock.json` de la raíz



\*\*Resultado:\*\* Archivo recuperado en 5 minutos, política implementada exitosamente. Esta experiencia fortaleció la competencia de gestión de configuración de software.



\---



\## 17.6 Capturas de Evidencia



| Archivo | Descripción |

|---------|-------------|

| `17\_mapa\_sensores.png` | Mapa con 8 sensores marcados (verde = online) |

| `17\_popup\_sensor.png` | Popup de un sensor con información detallada |

| `17\_mapa\_leyenda.png` | Leyenda del mapa (online, offline, área hogar) |

| `17\_modo\_oscuro.png` | Mapa en modo oscuro |



\*\*Ubicación de capturas:\*\* `docs/capturas/` (pendiente agregar)



\---



\## 17.7 Trazabilidad



| Elemento | Referencia |

|----------|-----------|

| \*\*Commit principal\*\* | `55e09ca` — feat: pestana ubicacion con mapa Leaflet de sensores IoT |

| \*\*Commit del fix de sensores\*\* | `6f20e26` — fix: derivar sensores desde eventos en api.ts |

| \*\*Archivo del componente\*\* | `frontend/src/MapaHogar.tsx` |

| \*\*Archivo de integración\*\* | `frontend/src/App.tsx` (línea \~665) |

| \*\*CSS del mapa\*\* | `frontend/src/App.css` (sección MAPA DEL HOGAR) |

| \*\*Dependencias\*\* | `frontend/package.json` (leaflet@1.9.4, react-leaflet@4.2.1) |

| \*\*Ficha relacionada\*\* | Ficha 03 (Frontend React) |



\---



\## 17.8 Conclusión



La Pestaña Ubicación complementa el dashboard numérico con una \*\*representación espacial\*\* de los 8 sensores IoT, permitiendo al cuidador identificar rápidamente la zona del hogar con actividad o inactividad. La implementación aplicó \*\*decisiones técnicas fundamentadas\*\* (selección de Leaflet sobre Google Maps, gestión de conflicto React 18 vs 19) y \*\*gestión de riesgos\*\* (recuperación de archivo tras incidente OneDrive).



Los 7 KPIs asociados fueron alcanzados, con trazabilidad completa en GitHub (commits `55e09ca` y `6f20e26`). Esta funcionalidad corresponde al \*\*OE3\*\* (dashboard + notificaciones en tiempo real), específicamente al componente de visualización geoespacial.



\*\*Estado:\*\* ✅ \*\*COMPLETADA\*\* — Septiembre 2026

```





