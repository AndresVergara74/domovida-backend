// src/App.tsx
import { useState } from "react";
import {
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { useDomovida } from "./useDomovida";
import "./App.css";

const COLORES = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];

// ============================================================
// ESTADO DEL SISTEMA
// ============================================================
// NOTA: Actualmente es un componente de prototipo. En una etapa
// posterior, estos estados se obtendrán mediante health checks
// del backend (endpoint /api/health).
// ============================================================
const ESTADO_SISTEMA = [
  { nombre: "Raspberry Pi (Edge)", icono: "🍓", online: true },
  { nombre: "API FastAPI", icono: "⚙️", online: true },
  { nombre: "PostgreSQL (Supabase)", icono: "🗄️", online: true },
  { nombre: "MQTT Broker", icono: "📡", online: true },
  { nombre: "ntfy (Notificaciones)", icono: "📱", online: true },
];

function App() {
  const { eventos, alertas, sensores, cargando, conectado } = useDomovida();
  const [pestana, setPestana] = useState<"general" | "historial" | "sensores">("general");

  if (cargando) {
    return <div className="cargando">Cargando DomoVida...</div>;
  }

  // ============================================================
  // CORRECCIÓN 1: Eventos de HOY (no todos)
  // ============================================================
  const hoy = new Date();
  const eventosHoy = eventos.filter((e) => {
    const fecha = new Date(e.timestamp);
    return (
      fecha.getDate() === hoy.getDate() &&
      fecha.getMonth() === hoy.getMonth() &&
      fecha.getFullYear() === hoy.getFullYear()
    );
  });

  // ============================================================
  // CORRECCIÓN 2: Última actividad PIR (ordenada explícitamente)
  // ============================================================
  const actividadesPIR = eventos
    .filter((e) => e.tipo === "pir" && e.valor?.movimiento === true)
    .sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

  const ultimaActividad = actividadesPIR[0];

  // ============================================================
  // CORRECCIÓN 3: Inactividad real (o "Sin datos" si no hay actividad)
  // ============================================================
  const minutosInactivo = ultimaActividad
    ? Math.floor(
        (Date.now() - new Date(ultimaActividad.timestamp).getTime()) / 60000
      )
    : null;

  // ============================================================
  // Gráfico: Actividad del hogar (basado en eventos PIR)
  // ============================================================
  const datosActividad = eventos
    .filter((e) => e.tipo === "pir")
    .slice(-12)
    .map((e) => ({
      hora: new Date(e.timestamp).toLocaleTimeString("es-CL", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      movimiento: e.valor?.movimiento ? 1 : 0,
    }));

  // ============================================================
  // Gráfico: Alertas por tipo
  // ============================================================
  const datosAlertasTipo = Object.entries(
    alertas.reduce((acc: Record<string, number>, a) => {
      acc[a.tipo] = (acc[a.tipo] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  // ============================================================
  // KPIs
  // ============================================================
  const totalEventosHoy = eventosHoy.length;
  const totalAlertas = alertas.length;
  const sensoresOnline = sensores.filter((s) => s.online).length;
  const totalSensores = sensores.length;

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🏠 DomoVida</h1>
          <p className="subtitulo">
            Monitoreo predictivo y asistencia inteligente
          </p>
        </div>
        <div className="header-status">
          <span className={`status-badge ${conectado ? "online" : "offline"}`}>
            <span className={`status-dot ${conectado ? "online" : "offline"}`}></span>
            {conectado ? "Sistema conectado" : "Sistema desconectado"}
          </span>
        </div>
      </header>

      <nav className="tabs">
        <button
          className={pestana === "general" ? "activo" : ""}
          onClick={() => setPestana("general")}
        >
          Vista general
        </button>
        <button
          className={pestana === "historial" ? "activo" : ""}
          onClick={() => setPestana("historial")}
        >
          Historial
        </button>
        <button
          className={pestana === "sensores" ? "activo" : ""}
          onClick={() => setPestana("sensores")}
        >
          Sensores
        </button>
      </nav>

      {pestana === "general" && (
        <>
          {/* ============================================ */}
          {/* ESTADO DEL SISTEMA */}
          {/* ============================================ */}
          <section className="estado-sistema">
            <h3>Estado del sistema</h3>
            <div className="estado-grid">
              {ESTADO_SISTEMA.map((s) => (
                <div
                  key={s.nombre}
                  className={`estado-item ${s.online ? "online" : "offline"}`}
                >
                  <span className="estado-icono">{s.icono}</span>
                  <span className="estado-nombre">{s.nombre}</span>
                  <span
                    className={`estado-badge ${s.online ? "online" : "offline"}`}
                  >
                    {s.online ? "● Online" : "○ Offline"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* ============================================ */}
          {/* TARJETAS DE RESUMEN */}
          {/* ============================================ */}
          <section className="tarjetas">
            <div className="tarjeta">
              <span className="etiqueta">Eventos detectados</span>
              <span className="valor">{totalEventosHoy}</span>
              <span className="detalle">hoy</span>
            </div>
            <div className="tarjeta alerta">
              <span className="etiqueta">Alertas activas</span>
              <span className="valor">{totalAlertas}</span>
              <span className="detalle">
                {totalAlertas > 0 ? "⚠ revisar" : "🟢 sin alertas"}
              </span>
            </div>
            <div className="tarjeta">
              <span className="etiqueta">Sensores operativos</span>
              <span className="valor">
                {sensoresOnline}/{totalSensores}
              </span>
              <span className="detalle">
                {sensoresOnline === totalSensores
                  ? "● todos online"
                  : `⚠ ${totalSensores - sensoresOnline} offline`}
              </span>
            </div>
            <div className="tarjeta advertencia">
              <span className="etiqueta">Inactividad</span>
              <span className="valor">
                {minutosInactivo !== null ? `${minutosInactivo} min` : "Sin datos"}
              </span>
              <span className="detalle">
                {minutosInactivo === null
                  ? "—"
                  : minutosInactivo < 30
                  ? "🟢 normal"
                  : "⚠ revisar"}
              </span>
            </div>
          </section>

          <section className="graficos">
            <div className="grafico">
              <h3>Actividad del hogar (últimas lecturas)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={datosActividad}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hora" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="movimiento"
                    stroke="#10b981"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grafico">
              <h3>Alertas por tipo</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={datosAlertasTipo}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {datosAlertasTipo.map((_, i) => (
                      <Cell key={i} fill={COLORES[i % COLORES.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="alertas-lista">
            <h3>Alertas recientes</h3>
            {alertas.length === 0 ? (
              <p className="vacio">Sin alertas activas</p>
            ) : (
              <ul>
                {alertas.slice(0, 8).map((a) => (
                  <li key={a.id} className={`alerta-item ${a.severidad}`}>
                    <div>
                      <strong>{a.tipo}</strong>
                      {a.mensaje && `: ${a.mensaje}`}
                    </div>
                    <span className="hora">
                      {new Date(a.timestamp).toLocaleTimeString("es-CL")}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}

      {pestana === "historial" && (
        <section className="tabla">
          <h3>Últimos eventos</h3>
          <table>
            <thead>
              <tr>
                <th>Sensor</th>
                <th>Tipo</th>
                <th>Habitación</th>
                <th>Alerta</th>
                <th>Hora</th>
              </tr>
            </thead>
            <tbody>
              {eventos.slice(0, 30).map((e) => (
                <tr
                  key={e.id}
                  className={e.alerta || e.caida_detectada ? "fila-alerta" : ""}
                >
                  <td>{e.sensor_id}</td>
                  <td>{e.tipo}</td>
                  <td>{e.habitacion || "-"}</td>
                  <td>{e.alerta || e.caida_detectada ? "🚨 Sí" : "No"}</td>
                  <td>{new Date(e.timestamp).toLocaleString("es-CL")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {pestana === "sensores" && (
        <section className="sensores">
          <h3>Estado de sensores</h3>
          <div className="grid-sensores">
            {sensores.map((s) => (
              <div
                key={s.sensor_id}
                className={`sensor-card ${s.online ? "online" : "offline"}`}
              >
                <h4>{s.sensor_id}</h4>
                <p>Tipo: {s.tipo}</p>
                <p>Habitación: {s.habitacion}</p>
                <p>
                  Última lectura:{" "}
                  {new Date(s.ultima_lectura).toLocaleTimeString("es-CL")}
                </p>
                <p>
                  <strong>{s.online ? "✅ Online" : "⚠️ Inactivo"}</strong>
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;