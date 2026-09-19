\# Ficha 3: Frontend React



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 3.1 Descripción General



El frontend de DomoVida es una aplicación web desarrollada en \*\*React\*\* con \*\*TypeScript\*\* y \*\*Vite\*\* como bundler. Proporciona un dashboard interactivo para que familiares y cuidadores puedan visualizar en tiempo real el estado del adulto mayor, las alertas activas y el historial de eventos.



\---



\## 3.2 Stack Tecnológico



| Componente | Tecnología | Propósito |

|------------|-----------|-----------|

| Framework | React 18+ | Interfaz de usuario |

| Lenguaje | TypeScript | Tipado estático |

| Bundler | Vite | Compilación y servidor de desarrollo |

| Gráficos | Recharts | Visualización de datos |

| Mapa (futuro) | React-Leaflet | Geolocalización |

| HTTP Client | Fetch API | Comunicación con backend |



\---



\## 3.3 Estructura del Proyecto





\---



\## 3.4 Componentes del Dashboard



\### 3.4.1 Tarjetas de Resumen



| Tarjeta | Descripción | Datos |

|---------|-------------|-------|

| \*\*Eventos Totales\*\* | Total de eventos recibidos | Últimos 50 |

| \*\*Alertas Activas\*\* | Eventos con alerta en últimas 24h | Tiempo real |

| \*\*Sensores Online\*\* | Sensores PIR activos | Últimas 12h |

| \*\*Inactividad\*\* | Sensores PIR sin movimiento | Últimas 12h |



\### 3.4.2 Gráficos



\- \*\*Gráfico de línea:\*\* Magnitud del acelerómetro (últimas lecturas) — permite visualizar picos de caída (>20 m/s²)

\- \*\*Gráfico circular (dona):\*\* Alertas por tipo de sensor — muestra la distribución de alertas entre los 8 sensores



\### 3.4.3 Lista de Alertas Recientes



Tabla con las últimas alertas registradas, mostrando:

\- Tipo de sensor (acelerometro, cardiovascular, boton\_panico, etc.)

\- Timestamp del evento

\- Ordenadas cronológicamente



\---



\## 3.5 Hook Personalizado: useDomovida



El hook `useDomovida.ts` encapsula toda la lógica de conexión con el backend:



```typescript

export function useDomovida() {

&#x20; const \[eventos, setEventos] = useState<Evento\[]>(\[]);

&#x20; const \[alertas, setAlertas] = useState<Alerta\[]>(\[]);

&#x20; const \[sensores, setSensores] = useState<SensorEstado\[]>(\[]);

&#x20; const \[cargando, setCargando] = useState(true);



&#x20; async function cargarTodo() {

&#x20;   const \[ev, al, se] = await Promise.all(\[

&#x20;     obtenerEventos(50),

&#x20;     obtenerAlertasActivas(),

&#x20;     obtenerInactividad(),

&#x20;   ]);

&#x20;   setEventos(ev);

&#x20;   setAlertas(al);

&#x20;   setSensores(se);

&#x20;   setCargando(false);

&#x20; }



&#x20; useEffect(() => {

&#x20;   cargarTodo();

&#x20;   const intervalo = setInterval(cargarTodo, 10000); // Actualización cada 10s

&#x20;   return () => clearInterval(intervalo);

&#x20; }, \[]);



&#x20; return { eventos, alertas, sensores, cargando, refrescar: cargarTodo };

}



\## 3.6 Configuración de API

El archivo api.ts centraliza todas las llamadas al backend:



const API\_URL = import.meta.env.VITE\_API\_URL || "http://localhost:8000";



export async function obtenerEventos(limite: number = 50): Promise<Evento\[]> {

&#x20; const response = await fetch(`${API\_URL}/api/eventos?limite=${limite}`);

&#x20; return await response.json();

}



export async function obtenerAlertasActivas(): Promise<Alerta\[]> {

&#x20; const response = await fetch(`${API\_URL}/api/alertas/activas`);

&#x20; return await response.json();

}



export async function obtenerInactividad(): Promise<SensorEstado\[]> {

&#x20; const response = await fetch(`${API\_URL}/api/alertas/inactividad`);

&#x20; return await response.json();

}



\## 3.7 Variables de Entorno

Archivo .env:





VITE\_API\_URL=http://localhost:8000



\## 3.8 Comandos de Ejecución



Instalar dependencias:



cd frontend

npm install



Ejecutar en desarrollo:



npm run dev



Salida esperada:



VITE v8.2.2  ready in 523 ms

➜  Local:   http://localhost:5173/



3.9 Características Implementadas

✅ Dashboard con diseño clínico profesional (colores verdes/azules)



✅ 4 tarjetas de resumen con actualización automática



✅ Gráfico de línea del acelerómetro en tiempo real



✅ Gráfico circular de distribución de alertas



✅ Lista de alertas recientes con timestamps



✅ Actualización automática cada 10 segundos



✅ Conexión estable con el backend FastAPI



✅ Pestañas: Vista general, Historial, Sensores



3.10 Capturas de Pantalla







3.11 Próximas Mejoras

🔜 Pestaña de mapa con geolocalización (React-Leaflet)



🔜 Autenticación con JWT



🔜 Modo oscuro/claro



🔜 Notificaciones push en el navegador



🔜 Exportación de reportes a PDF



🔜 Diseño responsive para móviles





\*\*Paso 2:\*\* Guarda con `Ctrl + S` y cierra el Bloc de notas.



\*\*Paso 3:\*\* Vuelve a la terminal y dime \*\*"listo"\*\*.









