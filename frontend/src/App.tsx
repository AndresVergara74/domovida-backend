// src/App.tsx
import { useState } from "react";
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { useDomovida } from "./useDomovida";
import "./App.css";

const COLORES = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];

function App() {
  const { eventos, alertas, sensores, cargando } = useDomovida();
  const [pestana, setPestana] = useState<"general" | "historial" | "sensores">("general");

  if (cargando) {
    return <div className="cargando">Cargando DomoVida...</div>;
  }

  // Datos para gráficos
  const datosRitmo = eventos
    .filter((e) => e.tipo === "acelerometro")
    .slice(-12)
    .map((e) => ({
      hora: new Date(e.timestamp).toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" }),
      magnitud: e.valor?.magnitud || 0,
    }));

  const datosAlertasTipo = Object.entries(
    alertas.reduce((acc: Record<string, number>, a) => {
      acc[a.tipo] = (acc[a.tipo] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const totalEventos = eventos.length;
  const totalAlertas = alertas.length;
  const sensoresOnline = sensores.filter((s) => s.online).length;
  const sensoresInactivos = sensores.filter((s) => !s.online).length;

  return (
    <div className="app">
      <header className="header">
        <h1>🏠 DomoVida</h1>
        <p className="subtitulo">Monitoreo predictivo para el adulto mayor</p>
      </header>

      <nav className="tabs">
        <button className={pestana === "general" ? "activo" : ""} onClick={() => setPestana("general")}>Vista general</button>
        <button className={pestana === "historial" ? "activo" : ""} onClick={() => setPestana("historial")}>Historial</button>
        <button className={pestana === "sensores" ? "activo" : ""} onClick={() => setPestana("sensores")}>Sensores</button>
      </nav>

      {pestana === "general" && (
        <>
          <section className="tarjetas">
            <div className="tarjeta">
              <span className="etiqueta">Eventos totales</span>
              <span className="valor">{totalEventos}</span>
            </div>
            <div className="tarjeta alerta">
              <span className="etiqueta">Alertas activas</span>
              <span className="valor">{totalAlertas}</span>
            </div>
            <div className="tarjeta">
              <span className="etiqueta">Sensores online</span>
              <span className="valor">{sensoresOnline}</span>
            </div>
            <div className="tarjeta advertencia">
              <span className="etiqueta">Inactividad</span>
              <span className="valor">{sensoresInactivos}</span>
            </div>
          </section>

          <section className="graficos">
            <div className="grafico">
              <h3>Magnitud del acelerómetro (últimas lecturas)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={datosRitmo}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hora" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="magnitud" stroke="#10b981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grafico">
              <h3>Alertas por tipo</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={datosAlertasTipo} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
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
                    <strong>{a.tipo}</strong>: {a.mensaje}
                    <span className="hora">{new Date(a.timestamp).toLocaleTimeString("es-CL")}</span>
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
                <tr key={e.id} className={e.alerta || e.caida_detectada ? "fila-alerta" : ""}>
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
              <div key={s.sensor_id} className={`sensor-card ${s.online ? "online" : "offline"}`}>
                <h4>{s.sensor_id}</h4>
                <p>Tipo: {s.tipo}</p>
                <p>Habitación: {s.habitacion}</p>
                <p>Última lectura: {new Date(s.ultima_lectura).toLocaleTimeString("es-CL")}</p>
                <p><strong>{s.online ? "✅ Online" : "⚠️ Inactivo"}</strong></p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;