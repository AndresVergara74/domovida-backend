
\# Ficha 6: Dashboard y Capturas



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 6.1 Descripción General



El dashboard de DomoVida es la interfaz principal para familiares y cuidadores. Muestra en tiempo real el estado del adulto mayor, las alertas activas y el historial de eventos, transformando datos técnicos complejos en información visual clara y accionable.



\---



\## 6.2 Estructura Visual



El dashboard está organizado en las siguientes secciones:



```

┌─────────────────────────────────────────────────────────────┐

│  🏠 DomoVida                                              

│  Monitoreo predictivo para el adulto mayor                  

├─────────────────────────────────────────────────────────────┤

│  \[Vista general]  \[Historial]  \[Sensores]                   

├─────────────────────────────────────────────────────────────┤

│                                                              │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │

│  │ EVENTOS  │  │ ALERTAS  │  │ SENSORES │                  │

│  │ TOTALES  │  │ ACTIVAS  │  │  ONLINE  │                  │

│  │    50    │  │    71    │  │    2     │                  │

│  └──────────┘  └──────────┘  └──────────┘         │

│                                                              │

│  ┌──────────┐                                             │

│  │INACTIVIDAD│                                               │

│  │     0     │                                               │

│  └──────────┘                                             │

│                                                               │

│  ┌────────────────────────────────────────────────────┐    │

│  │  Magnitud del acelerómetro (últimas lecturas)      │    │

│  │  \[Gráfico de línea con picos de caída]             │    │

│  └────────────────────────────────────────────────────┘    │

│                                                              │

│  ┌────────────────────────────────────────────────────┐    │

│  │  Alertas por tipo                                   │    │

│  │  \[Gráfico circular: apertura, acelerometro, humo,   │    │

│  │   cardiovascular, boton\_panico]                     │    │

│  └────────────────────────────────────────────────────┘    │

│                                                              │

│  ┌────────────────────────────────────────────────────┐    │

│  │  Alertas recientes                                  │    │

│  │  • cardiovascular  09:29:43 p.m.                    │    │

│  │  • boton\_panico    09:39:57 p.m.                    │    │

│  │  • apertura        09:40:12 p.m.                    │    │

│  └────────────────────────────────────────────────────┘    │

└─────────────────────────────────────────────────────────────┘

```



\---



cardiovascular   09:29:43 p.m.

cardiovascular   09:29:00 p.m.

apertura         09:28:56 p.m.

boton\_panico     09:39:57 p.m.

```



\---



\## 6.3 Tarjetas de Resumen



| Tarjeta             | Descripción                            | Fuente                 |

|---------------------|----------------------------------------|--------                | 

| \*\*Eventos Totales\*\* | Total de eventos recibidos (últimos 50)| `/api/eventos`         |

| \*\*Alertas Activas\*\* | Eventos con alerta=True en últimas 24h | `/api/alertas/activas` |

| \*\*Sensores Online\*\* | Sensores PIR activos en últimas 12h    | /api/alertas/inactividad` | \*\*Inactividad\*\*     | Sensores PIR sin movimiento            | /api/alertas/inactividad` |





\## 6.4 Gráficos Implementados



\### 6.4.1 Gráfico de Línea: Magnitud del Acelerómetro



\*\*Tipo:\*\* Line Chart (Recharts)



\*\*Propósito:\*\* Visualizar la magnitud de aceleración a lo largo del tiempo. Los picos > 20 m/s² indican caídas detectadas.



\*\*Datos:\*\* Últimas 12 lecturas del acelerómetro.



\### 6.4.2 Gráfico Circular: Alertas por Tipo



\*\*Tipo:\*\* Pie Chart / Donut Chart (Recharts)



\*\*Propósito:\*\* Mostrar la distribución de alertas por tipo de sensor.



\*\*Categorías visibles:\*\*

\- `acelerometro` (rojo)

\- `apertura` (verde)

\- `boton\_panico` (azul claro)

\- `cardiovascular` (amarillo)

\- `humo` (azul oscuro)





\## 6.5 Lista de Alertas Recientes



Tabla con las últimas alertas registradas. Muestra:

\- Tipo de sensor

\- Timestamp del evento



\*\*Ejemplo de alertas mostradas:\*\*



cardiovascular 09:29:43 p.m.

cardiovascular 09:29:00 p.m.

apertura 09:28:56 p.m.

boton\_panico 09:39:57 p.m.





\## 6.6 Actualización Automática



El dashboard se actualiza automáticamente cada \*\*10 segundos\*\* mediante el hook `useDomovida`:



```typescript

useEffect(() => {

&#x20; cargarTodo();

&#x20; const intervalo = setInterval(cargarTodo, 10000); // Cada 10s

&#x20; return () => clearInterval(intervalo);

}, \[]);





\## 6.7 Capturas de Pantalla



\*(Las capturas se agregarán en la carpeta `capturas/` de esta misma sección.)\*



\### Captura 1: Vista General



!\[Vista general del dashboard](capturas/01\_vista\_general.png)



\*\*Descripción:\*\* Muestra las 4 tarjetas de resumen (Eventos Totales, Alertas Activas, Sensores Online, Inactividad) y el gráfico de línea del acelerómetro con un pico de caída.



\### Captura 2: Alertas por Tipo



!\[Gráfico circular de alertas](capturas/02\_alertas\_por\_tipo.png)



\*\*Descripción:\*\* Gráfico circular que muestra la distribución de alertas entre los diferentes tipos de sensores.



\### Captura 3: Alertas Recientes



!\[Lista de alertas recientes](capturas/03\_alertas\_recientes.png)



\*\*Descripción:\*\* Lista cronológica de las últimas alertas, incluyendo eventos cardiovasculares y botón de pánico.



\---



\## 6.8 Diseño Visual



\### Paleta de Colores



| Color              | Uso                     |

|--------------------|-------------------------|

| Verde (#10b981)    | Estados normales, éxito |

| Azul (#3b82f6)     | Información, datos      |

| Rojo (#ef4444)     | Alertas críticas        |

| Amarillo (#f59e0b) | Advertencias            |

| Gris (#6b7280)     | Texto secundario        |



\### Tipografía



\- Fuente principal: \*\*DM Sans\*\*

\- Títulos: Bold, 24-32px

\- Cuerpo: Regular, 14-16px



\### Estilo General



\- Diseño clínico profesional

\- Tarjetas con sombras suaves

\- Bordes redondeados (radius: 8-12px)

\- Espaciado generoso entre elementos



\---



\## 6.9 Validación de Usabilidad



La validación se realizará con la \*\*Escala SUS (System Usability Scale)\*\*:



\- \*\*Instrumento:\*\* Cuestionario de 10 ítems

\- \*\*Puntuación objetivo:\*\* > 70 puntos (usabilidad "excelente")

\- \*\*Participantes:\*\* Familiares y cuidadores voluntarios





\## 6.10 Estado Actual



| Característica                               | Estado          |

|----------------------------------------------|-----------------|

| 4 tarjetas de resumen                        | ✅ Implementado |

| Gráfico de línea (acelerómetro)              | ✅ Implementado |

| Gráfico circular (alertas por tipo)          | ✅ Implementado |

| Lista de alertas recientes                   | ✅ Implementado |

| Actualización automática (10s)               | ✅ Implementado |

| Pestañas: Vista general, Historial, Sensores | ✅ Implementado |

| Mapa de geolocalización                      | 🔜 Futuro       |

| Modo oscuro                                  | 🔜 Futuro       |





\## 6.11 Próximas Mejoras



\- 🔜 Agregar mapa con React-Leaflet para geolocalización

\- 🔜 Implementar notificaciones push en el navegador

\- 🔜 Exportación de reportes a PDF

\- 🔜 Diseño responsive para móviles

\- 🔜 Modo oscuro/claro

\- 🔜 Personalización de umbrales por usuario








