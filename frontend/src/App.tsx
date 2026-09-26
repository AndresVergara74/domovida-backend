// src/App.tsx
import { useState, useEffect } from "react";
import {
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { useDomovida } from "./useDomovida";
import { useWebSocket } from "./useWebSocket";
import "./App.css";

const COLORES = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];

// URL base de la API (usa variable de entorno o fallback)
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const { eventos, alertas, sensores, cargando, conectado, refrescar } = useDomovida();
  const { conectado: wsConectado, alertasTiempoReal } = useWebSocket();
  const [pestana, setPestana] = useState<"general" | "historial" | "sensores">("general");
  const [estadoSistema, setEstadoSistema] = useState<any[]>([]);
  const [notificacionVisible, setNotificacionVisible] = useState(false);
  const [ultimaAlertaRT, setUltimaAlertaRT] = useState<any>(null);

  // ============================================================
  // Estados para "Marcar como atendida"
  // ============================================================
  const [resolviendoId, setResolviendoId] = useState<number | null>(null);
  const [alertasResueltas, setAlertasResueltas] = useState<Set<number>>(new Set());

  // ============================================================
  // Cargar estado del sistema desde /api/health
  // ============================================================
  useEffect(() => {
    async function cargarHealth() {
      try {
        const response = await fetch(`${API_URL}/api/health`);
        const data = await response.json();
        setEstadoSistema(data.componentes || []);
      } catch (error) {
        console.error("Error al cargar health:", error);
      }
    }
    cargarHealth();
    const intervalo = setInterval(cargarHealth, 30000);
    return () => clearInterval(intervalo);
  }, []);

  // ============================================================
  // Mostrar notificación flotante cuando llega una alerta en tiempo real
  // ============================================================
  useEffect(() => {
    if (alertasTiempoReal.length > 0) {
      const ultima = alertasTiempoReal[0];
      if (!ultimaAlertaRT || ultima.id !== ultimaAlertaRT.id) {
        setUltimaAlertaRT(ultima);
        setNotificacionVisible(true);
        const timeout = setTimeout(() => setNotificacionVisible(false), 5000);
        return () => clearTimeout(timeout);
      }
    }
  }, [alertasTiempoReal, ultimaAlertaRT]);

  // ============================================================
  // FUNCIÓN: Marcar una alerta como atendida
  // ============================================================
  async function resolverAlerta(alertaId: number) {
    setResolviendoId(alertaId);

    try {
      const response = await fetch(`${API_URL}/api/alertas/${alertaId}/resolver`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resuelto_por: "Cuidador DomoVida",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Marcar como resuelta en el estado local
      setAlertasResueltas((prev) => new Set(prev).add(alertaId));

      // Refrescar los datos del backend
      if (refrescar) {
        await refrescar();
      }

      console.log(`✅ Alerta ${alertaId} marcada como atendida`);
    } catch (error) {
      console.error(`❌ Error al resolver alerta ${alertaId}:`, error);
      alert("No se pudo marcar la alerta como atendida. Intenta de nuevo.");
    } finally {
      setResolviendoId(null);
    }
  }

  if (cargando) {
    return <div className="cargando">Cargando DomoVida...</div>;
  }

  // ============================================================
  // Combinar alertas del backend + alertas del WebSocket
  // ============================================================
  const todasLasAlertas = [
    ...alertasTiempoReal,
    ...alertas.filter((a) => !alertasTiempoReal.some((rt) => rt.id === a.id)),
  ];

  // ============================================================
  // Eventos de HOY
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
  // Última actividad PIR
  // ============================================================
  const actividadesPIR = eventos
    .filter((e) => e.tipo === "pir" && e.valor?.movimiento === true)
    .sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

  const ultimaActividad = actividadesPIR[0];

  const minutosInactivo = ultimaActividad
    ? Math.floor(
        (Date.now() - new Date(ultimaActividad.timestamp).getTime()) / 60000
      )
    : null;

  // ============================================================
  // Gráfico: Actividad del hogar
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
    todasLasAlertas.reduce((acc: Record<string, number>, a) => {
      acc[a.tipo] = (acc[a.tipo] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  // ============================================================
  // KPIs
  // ============================================================
  const totalEventosHoy = eventosHoy.length;
  const totalAlertas = todasLasAlertas.length;
  const sensoresOnline = sensores.filter((s) => s.online).length;
  const totalSensores = sensores.length;

  return (
    <div className="app">
      {/* ============================================ */}
      {/* NOTIFICACIÓN FLOTANTE DE ALERTA EN TIEMPO REAL */}
      {/* ============================================ */}
      {notificacionVisible && ultimaAlertaRT && (
        <div className="notificacion-tiempo-real">
          <div className="notificacion-icono">🚨</div>
          <div className="notificacion-contenido">
            <strong>Alerta en tiempo real</strong>
            <p>
              {ultimaAlertaRT.sensor_id} · {ultimaAlertaRT.habitacion}
            </p>
          </div>
          <button
            className="notificacion-cerrar"
            onClick={() => setNotificacionVisible(false)}
          >
            ✕
          </button>
        </div>
      )}

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
            {conectado ? "API conectada" : "API desconectada"}
          </span>
          <span className={`status-badge ${wsConectado ? "online" : "offline"}`}>
            <span className={`status-dot ${wsConectado ? "online" : "offline"}`}></span>
            {wsConectado ? "Tiempo real activo" : "Tiempo real inactivo"}
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
          {/* ESTADO DEL SISTEMA (desde /api/health) */}
          {/* ============================================ */}
          <section className="estado-sistema">
            <h3>Estado del sistema</h3>
            <div className="estado-grid">
              {estadoSistema.map((s) => (
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
            <h3>
              Alertas recientes
              {wsConectado && <span className="live-badge">● EN VIVO</span>}
            </h3>
            {todasLasAlertas.length === 0 ? (
              <p className="vacio">Sin alertas activas</p>
            ) : (
              <ul>
                {todasLasAlertas.slice(0, 8).map((a) => {
                  const resuelta = alertasResueltas.has(a.id);
                  const resolviendo = resolviendoId === a.id;

                  return (
                    <li key={a.id} className={`alerta-item ${a.severidad || "alta"}`}>
                      <div className="alerta-info">
                        <strong>{a.tipo}</strong>
                        {a.habitacion && ` · ${a.habitacion}`}
                        <span className="hora">
                          {new Date(a.timestamp).toLocaleTimeString("es-CL")}
                        </span>
                      </div>

                      {resuelta ? (
                        <span className="alerta-resuelta-badge">✓ Atendida</span>
                      ) : (
                        <button
                          className="btn-atender"
                          onClick={() => resolverAlerta(a.id)}
                          disabled={resolviendo}
                        >
                          {resolviendo ? "Atendiendo..." : "✓ Atender"}
                        </button>
                      )}
                    </li>
                  );
                })}
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