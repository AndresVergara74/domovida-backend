# Ficha 03: Frontend React

**Proyecto:** DomoVida — Plataforma IoT de Monitoreo Predictivo y Asistencia Inteligente para el Adulto Mayor en el Hogar

**Autor:** Andrés Rodrigo Vergara Acevedo

**Fecha:** Septiembre 2026

**Commit de referencia:** `61aa583`

---

## 3.1 Descripción General

El frontend de DomoVida es una aplicación web desarrollada en **React 18** con **TypeScript** y **Vite** como bundler. Proporciona un dashboard interactivo para que familiares y cuidadores puedan visualizar en tiempo real el estado del adulto mayor, las alertas activas, el historial de eventos, el estado de los sensores y su ubicación geográfica en el hogar.

La aplicación fue desplegada en **Vercel** con integración continua desde GitHub, y está disponible en: `https://domovida-backend.vercel.app`

---

## 3.2 Stack Tecnológico

| Componente    | Tecnología   | Versión | Propósito                            |
|---------------|--------------|---------|--------------------------------------|
| Framework     | React        | 18.3.1  | Interfaz de usuario                  |
| Lenguaje      | TypeScript   | 5.x     | Tipado estático                      |
| Bundler       | Vite         | 6.4.3   | Compilación y servidor de desarrollo |
| Gráficos      | Recharts     | 2.x     | Visualización de datos               |
| Iconos        | Lucide React | 1.48.0  | Iconografía vectorial                |
| Mapas         | Leaflet      | 1.9.4   | Geolocalización de sensores          |
| Mapas (React) | React-Leaflet| 4.2.1   | Componente React para Leaflet        |
| HTTP Client   | Fetch API    | nativa  | Comunicación con backend             |
| WebSocket     | API nativa   | nativa   | Alertas en tiempo real              |

**Decisión técnica documentada (Leaflet v4.2.1 vs v5):** Se identificó un conflicto de peer dependencies: Leaflet v5 requiere React 19, mientras que el proyecto usa React 18.3.1. Para no arriesgar breaking changes en componentes existentes (dashboard, filtros, WebSocket, consentimiento), se optó por Leaflet v4.2.1 (compatible con React 18). Ver Ficha 17 para más detalle.

---

## 3.3 Estructura del Proyecto

```
frontend/
├── src/
│   ├── App.tsx              → Componente principal (dashboard + pestañas)
│   ├── App.css              → Estilos globales + modo oscuro + responsive
│   ├── api.ts               → Llamadas al backend + tipos TypeScript
│   ├── useDomovida.ts       → Hook de conexión con el backend
│   ├── useWebSocket.ts      → Hook de WebSocket para alertas en tiempo real
│   ├── Consentimiento.tsx   → Modal de consentimiento informado (Ley 21.719)
│   ├── MapaHogar.tsx        → Componente del mapa Leaflet con 8 sensores
│   └── main.tsx             → Punto de entrada de React
├── public/
│   └── favicon.svg
├── .env                     → Variables de entorno (local)
├── .env.production          → Variables de entorno (Vercel)
├── package.json
└── vite.config.ts
```

---

## 3.4 Componentes del Dashboard

### 3.4.1 Tarjetas de Resumen

| Tarjeta | Descripción | Datos | Estado |
|---------|-------------|-------|--------|
| **Eventos Detectados** | Eventos de hoy | Últimos 50 | ✅ |
| **Alertas Activas** | Alertas sin resolver | Tiempo real (WebSocket) | ✅ |
| **Sensores Operativos** | Sensores online/total | Derivados de eventos | ✅ |
| **Inactividad** | Minutos sin movimiento PIR | Derivados de eventos | ✅ |

### 3.4.2 Estado del Sistema

Panel que consulta `/api/health` cada 30 segundos y muestra el estado de los 5 componentes del sistema:

| Componente | Icono | Estado |
|------------|-------|--------|
| Raspberry Pi (Edge) | 🍓 | Online (modo simulado) |
| API FastAPI | ⚙️ | Online |
| PostgreSQL (Supabase) | 🗄️ | Online |
| MQTT Broker | 📡 | Online (modo simulado) |
| ntfy (Notificaciones) | 📱 | Online (latencia medible) |

### 3.4.3 Gráficos

- **Gráfico de línea:** Actividad del hogar (últimas 12 lecturas PIR) — visualiza presencia/ausencia
- **Gráfico circular (dona):** Alertas por tipo de sensor — distribución de alertas entre los 8 sensores

### 3.4.4 Lista de Alertas Recientes

Lista con las últimas 8 alertas registradas, mostrando:
- Tipo de sensor (acelerometro, cardiovascular, boton_panico, etc.)
- Habitación afectada
- Timestamp del evento
- Botón "Marcar como atendida" (PATCH `/api/alertas/{id}/resolver`)

### 3.4.5 Notificación Flotante en Tiempo Real

Cuando llega una alerta vía WebSocket, aparece una notificación flotante en la esquina superior derecha con animación de entrada, que se cierra automáticamente después de 5 segundos o al hacer clic en la X.

---

## 3.5 Pestañas del Dashboard (4 pestañas)

| # | Pestaña | Funcionalidad | Estado |
|---|---------|---------------|--------|
| 1 | **Vista general** | Estado del sistema, tarjetas de resumen, gráficos, alertas recientes | ✅ |
| 2 | **Historial** | Tabla con 50 eventos + filtros por sensor, tipo, habitación, alerta | ✅ |
| 3 | **Sensores** | Cards con estado individual de cada sensor (8 tarjetas) | ✅ |
| 4 | **Ubicación** | Mapa Leaflet con los 8 sensores geolocalizados | ✅ |

### 3.5.1 Pestaña Historial — Filtros

La pestaña Historial incluye 4 filtros dinámicos con contador de resultados:

| Filtro | Opciones | Ejemplo |
|--------|----------|---------|
| **Sensor** | Lista única de sensores (derivada de eventos) | `acelerometro_dormitorio` |
| **Tipo** | Lista única de tipos (derivada de eventos) | `pir`, `gas`, `humo` |
| **Habitación** | Lista única de habitaciones | `dormitorio`, `cocina`, `living` |
| **Alerta** | Todas / Solo con alerta / Sin alerta | `solo_alertas` |

El contador muestra "X de Y eventos" y hay un botón **"Limpiar filtros"** que aparece solo cuando hay filtros activos.

### 3.5.2 Pestaña Ubicación — Mapa Leaflet

Ver **Ficha 17** para el detalle completo. Resumen:
- 8 marcadores (uno por sensor) con color según estado (verde online, rojo offline)
- Círculo punteado que representa el área del hogar
- Popup con información detallada del sensor
- Leyenda inferior (online, offline, área del hogar)

---

## 3.6 Modo Oscuro/Claro

El dashboard incluye un **toggle de tema** con persistencia en `localStorage` y detección automática de la preferencia del sistema operativo.

**Comportamiento:**
1. Al cargar, lee `localStorage.getItem("domovida-tema")`
2. Si no existe, usa `window.matchMedia("(prefers-color-scheme: dark)")`
3. Al hacer clic, alterna la clase `.dark` en el `<body>`
4. Persiste la preferencia en `localStorage`

**Implementación:**

```tsx
const [temaOscuro, setTemaOscuro] = useState<boolean>(() => {
  const guardado = localStorage.getItem("domovida-tema");
  if (guardado) return guardado === "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
});

useEffect(() => {
  if (temaOscuro) {
    document.body.classList.add("dark");
    localStorage.setItem("domovida-tema", "dark");
  } else {
    document.body.classList.remove("dark");
    localStorage.setItem("domovida-tema", "light");
  }
}, [temaOscuro]);
```

**CSS:** Las variables CSS (`--bg`, `--text`, `--border`, etc.) se redefinen en `body.dark`, lo que permite cambiar todo el tema con 10 líneas de CSS.

---

## 3.7 Iconos Lucide

Se reemplazaron los emojis por iconos vectoriales de **Lucide React** (1.48.0) para un diseño más profesional y consistente.

| Emoji anterior | Icono Lucide | Uso |
|----------------|--------------|-----|
| 🏠 | `<Home />` | Título "DomoVida" |
| 🌙 / ☀️ | `<Moon />` / `<Sun />` | Toggle de tema |
| 🚨 | `<Bell />` | Notificación flotante |
| ⚠️ | `<AlertTriangle />` | Tarjeta de alertas |
| 🔍 | `<Filter />` | Filtros del historial |
| ❌ | `<X />` | Botón limpiar filtros |
| 🛡️ | `<Shield />` | Botón consentimiento informado |
| 📍 | `<MapPin />` | Pestaña Ubicación |

---

## 3.8 Hook Personalizado: useDomovida

El hook `useDomovida.ts` encapsula toda la lógica de conexión con el backend:

```typescript
export function useDomovida() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [sensores, setSensores] = useState<SensorEstado[]>([]);
  const [minutosInactivo, setMinutosInactivo] = useState<number>(0);
  const [cargando, setCargando] = useState(true);

  async function cargarTodo() {
    const [ev, al, se, inac] = await Promise.all([
      obtenerEventos(50),
      obtenerAlertasActivas(),
      obtenerSensores(),      // Derivado de eventos
      obtenerInactividad(),   // Minutos sin movimiento PIR
    ]);
    setEventos(ev);
    setAlertas(al);
    setSensores(se);
    setMinutosInactivo(inac);
    setCargando(false);
  }

  useEffect(() => {
    cargarTodo();
    const intervalo = setInterval(cargarTodo, 10000); // Actualización cada 10s
    return () => clearInterval(intervalo);
  }, []);

  return { eventos, alertas, sensores, minutosInactivo, cargando, refrescar: cargarTodo };
}
```

**Decisión técnica documentada (derivar sensores de eventos):** El backend no expone un endpoint `/api/sensores` específico. Se implementó la función `obtenerSensores()` en `api.ts`, que deriva la lista única de sensores a partir de los últimos 200 eventos, tomando la lectura más reciente de cada `sensor_id`. Esta decisión elimina la necesidad de un endpoint adicional en el backend y garantiza que el mapa siempre refleje el estado actual del sistema.

---

## 3.9 Configuración de API

El archivo `api.ts` centraliza todas las llamadas al backend:

```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function obtenerEventos(limite: number = 50): Promise<Evento[]> {
  const response = await fetch(`${API_URL}/api/eventos?limite=${limite}`);
  return await response.json();
}

export async function obtenerAlertasActivas(): Promise<Alerta[]> {
  const response = await fetch(`${API_URL}/api/alertas/activas`);
  return await response.json();
}

export async function obtenerSensores(): Promise<SensorEstado[]> {
  const eventos = await obtenerEventos(200);
  const mapaSensores = new Map<string, SensorEstado>();
  for (const evento of eventos) {
    if (!mapaSensores.has(evento.sensor_id)) {
      mapaSensores.set(evento.sensor_id, {
        sensor_id: evento.sensor_id,
        tipo: evento.tipo,
        habitacion: evento.habitacion || "desconocida",
        ultima_lectura: evento.timestamp,
        online: true,
      });
    }
  }
  return Array.from(mapaSensores.values());
}

export async function obtenerInactividad(): Promise<number> {
  const eventos = await obtenerEventos(50);
  const eventosPIR = eventos
    .filter((e) => e.tipo === "pir" && e.valor?.movimiento === true)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  if (eventosPIR.length === 0) return 0;
  return Math.floor((Date.now() - new Date(eventosPIR[0].timestamp).getTime()) / 60000);
}
```

---

## 3.10 WebSocket para Alertas en Tiempo Real

El hook `useWebSocket.ts` conecta al endpoint `wss://[backend]/api/ws/alertas` y mantiene un canal bidireccional para recibir alertas instantáneas.

**Reconexión automática:** Si la conexión se pierde, el hook reintenta cada 5 segundos automáticamente.

**Integración:** Las alertas recibidas vía WebSocket se agregan a `todasLasAlertas` (combinadas con las del backend), evitando duplicados por `id`.

---

## 3.11 Consentimiento Informado Digital

Ver **Ficha 14** para el contenido completo. El componente `Consentimiento.tsx` renderiza un modal con:
- 4 secciones informativas (¿Qué es DomoVida?, ¿Qué datos recolecta?, Tus derechos, Advertencia)
- Formulario con nombre + RUT (seudonimizado)
- 2 checkboxes de aceptación
- Botones "Acepto" / "Rechazar"

**Seudonimización:** El nombre se reduce a iniciales y el RUT se guarda como hash base64 (no en texto plano). Cumplimiento con Ley N° 21.719.

---

## 3.12 Variables de Entorno

**Archivo `.env` (local):**
```
VITE_API_URL=http://localhost:8000
```

**Archivo `.env.production` (Vercel):**
```
VITE_API_URL=https://domovida-backend.onrender.com
```

---

## 3.13 Comandos de Ejecución

**Instalar dependencias:**
```
cd frontend
npm install
```

**Ejecutar en desarrollo:**
```
npm run dev
```

**Salida esperada:**
```
VITE v6.4.3  ready in 400 ms
➜  Local:   http://localhost:5173/
```

**Build de producción:**
```
npm run build
```

---

## 3.14 Características Implementadas

- ✅ Dashboard con diseño clínico profesional (paleta verde/azul)
- ✅ 4 tarjetas de resumen con actualización automática cada 10s
- ✅ Estado del sistema en tiempo real (5 componentes monitoreados)
- ✅ Gráfico de línea (actividad del hogar)
- ✅ Gráfico circular (distribución de alertas)
- ✅ Lista de alertas recientes con botón "Marcar como atendida"
- ✅ Notificación flotante en tiempo real (WebSocket)
- ✅ Pestañas: Vista general, Historial, Sensores, **Ubicación**
- ✅ **Filtros dinámicos** en Historial (4 filtros + botón limpiar)
- ✅ **Modo oscuro/claro** con persistencia en localStorage
- ✅ **Iconos Lucide** (reemplazo de emojis)
- ✅ **Consentimiento informado** (modal digital, Ley 21.719)
- ✅ **Mapa Leaflet** con 8 sensores geolocalizados
- ✅ **Responsive** (móvil/tablet/desktop)

---

## 3.15 Capturas de Pantalla

Ver carpeta `docs/capturas/` (pendiente agregar):
- `03_vista_general.png`
- `03_historial_filtros.png`
- `03_sensores.png`
- `03_ubicacion_mapa.png`
- `03_modo_oscuro.png`
- `03_consentimiento.png`

---

## 3.16 Próximas Mejoras

- 🔜 **PWA** (Progressive Web App) — instalable en celular
- 🔜 **Autenticación JWT** para cuidadores
- 🔜 **HL7 FHIR** — interoperabilidad con sistemas de salud (trabajo futuro)
- 🔜 **Exportación de reportes a PDF**
- 🔜 **Filtros de fecha** en Historial (rango personalizado)

---

## 3.17 Trazabilidad

| Elemento | Referencia |
|----------|-----------|
| **Commit del dashboard base** | `0edf181` — feat: WebSocket integrado en frontend |
| **Commit del botón atender** | `d3d25b4` — feat: boton 'Marcar como atendida' |
| **Commit de modo oscuro** | `dbba8bb` — feat: modo oscuro con toggle |
| **Commit de iconos Lucide** | `a1a0d42` — feat: iconos Lucide en header |
| **Commit de filtros** | `5cb0784` — feat: filtros en historial |
| **Commit de consentimiento** | `998a37a` — feat: consentimiento informado digital |
| **Commit de mapa Leaflet** | `55e09ca` — feat: pestana ubicacion con mapa |
| **Commit del fix de sensores** | `6f20e26` — fix: derivar sensores desde eventos |
| **Fichas relacionadas** | Ficha 14 (Consentimiento), Ficha 15 (WebSocket), Ficha 17 (Mapa Leaflet) |
| **URL de producción** | https://domovida-backend.vercel.app |

---


