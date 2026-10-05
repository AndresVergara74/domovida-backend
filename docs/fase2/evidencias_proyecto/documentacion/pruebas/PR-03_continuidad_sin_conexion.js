// PR-03 · Continuidad sin conexión a internet (modo borde, DomoVida)
// Con el computador SIN internet, envía 10 caídas simuladas al backend local
// (FastAPI + SQLite en el mismo equipo) y mide si cada alerta llega al panel
// local por WebSocket. Criterio del hito H3 (Guía 1.5): una caída simulada es
// detectada y guardada en SQLite3 sin conexión a internet.
// Uso: pegar en la Consola de Chrome con el panel local (http://localhost:5173) abierto.
(async () => {
  // PS-01: desde el 05-10-2026 el backend exige la clave de API de los sensores.
  // Pegar aquí la clave (la misma de DOMOVIDA_API_KEY en Render). No subirla al repositorio.
  const CLAVE = "PEGA_AQUI_LA_CLAVE";
  const API = "http://localhost:8000";
  const WS = "ws://localhost:8000/api/ws/alertas";
  const N = 10;
  // navigator.onLine no es confiable en Windows (los adaptadores virtuales lo dejan en true),
  // así que se comprueba el acceso real a internet intentando llegar a ntfy.sh.
  let internet = true;
  try { await fetch("https://ntfy.sh/v1/health", { mode: "no-cors", signal: AbortSignal.timeout(4000) }); }
  catch (e) { internet = false; }
  const ws = new WebSocket(WS);
  await new Promise((ok, err) => { ws.onopen = ok; ws.onerror = err; });
  console.log("✅ WebSocket local conectado. Acceso real a internet: " + internet + ". Enviando " + N + " caídas...");
  const tiempos = []; let guardadas = 0;
  for (let i = 1; i <= N; i++) {
    const marca = "PR03-" + i + "-" + Date.now();
    const t0 = performance.now();
    const llegada = new Promise((ok) => {
      const h = (e) => { if (e.data.includes(marca)) { ws.removeEventListener("message", h); ok(performance.now() - t0); } };
      ws.addEventListener("message", h);
      setTimeout(() => { ws.removeEventListener("message", h); ok(null); }, 10000);
    });
    const r = await fetch(API + "/api/sensor-data", {
      method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": CLAVE },
      body: JSON.stringify({ sensor_id: "acelerometro_dormitorio", tipo: "acelerometro", habitacion: "dormitorio",
        valor: { magnitud: 25.0, caida: true, prueba: marca }, alerta: true, timestamp: new Date().toISOString() }),
    });
    if (r.ok) guardadas++;
    const ms = await llegada; tiempos.push(ms);
    console.log("Caída " + i + ": API " + r.status + " · WebSocket " + (ms === null ? "❌ no llegó" : Math.round(ms) + " ms"));
    await new Promise((x) => setTimeout(x, 1500));
  }
  ws.close();
  const ok = tiempos.filter((t) => t !== null);
  console.table({
    "Acceso real a internet (debe ser false)": internet,
    "Caídas enviadas": N,
    "Guardadas por el backend local (HTTP 2xx)": guardadas,
    "Alertas recibidas por WebSocket": ok.length + " (" + Math.round((ok.length / N) * 100) + "%)",
    "Promedio WebSocket (ms)": ok.length ? Math.round(ok.reduce((a, b) => a + b, 0) / ok.length) : "-",
  });
})();
