// PR-01 · Latencia de la alerta crítica (DomoVida)
// Envía 30 caídas simuladas al backend en Render y mide cuánto tarda cada
// alerta en llegar de vuelta por WebSocket (sensor → backend → BD → panel).
// Uso: pegar en la Consola de Chrome con el panel abierto.
(async () => {
  const API = "https://domovida-backend.onrender.com";
  const WS = "wss://domovida-backend.onrender.com/api/ws/alertas";
  const N = 30;
  const ws = new WebSocket(WS);
  await new Promise((ok, err) => { ws.onopen = ok; ws.onerror = err; });
  console.log("✅ WebSocket de prueba conectado. Enviando " + N + " caídas...");
  const tiempos = [];
  for (let i = 1; i <= N; i++) {
    const marca = "PR01-" + i + "-" + Date.now();
    const t0 = performance.now();
    const llegada = new Promise((ok) => {
      const h = (e) => {
        if (e.data.includes(marca)) { ws.removeEventListener("message", h); ok(performance.now() - t0); }
      };
      ws.addEventListener("message", h);
      setTimeout(() => { ws.removeEventListener("message", h); ok(null); }, 10000);
    });
    await fetch(API + "/api/sensor-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sensor_id: "acelerometro_dormitorio", tipo: "acelerometro", habitacion: "dormitorio",
        valor: { magnitud: 25.0, caida: true, prueba: marca },
        alerta: true, timestamp: new Date().toISOString(),
      }),
    });
    const ms = await llegada;
    tiempos.push(ms);
    console.log("Caída " + i + ": " + (ms === null ? "❌ NO LLEGÓ" : Math.round(ms) + " ms"));
    await new Promise((r) => setTimeout(r, 1500));
  }
  ws.close();
  const ok = tiempos.filter((t) => t !== null).sort((a, b) => a - b);
  const prom = ok.reduce((a, b) => a + b, 0) / ok.length;
  const p95 = ok[Math.min(ok.length - 1, Math.ceil(ok.length * 0.95) - 1)];
  console.table({
    "Caídas enviadas": N,
    "Alertas recibidas por WebSocket": ok.length + " (" + Math.round((ok.length / N) * 100) + "%)",
    "Promedio (ms)": Math.round(prom),
    "Mínimo (ms)": Math.round(ok[0]),
    "Máximo (ms)": Math.round(ok[ok.length - 1]),
    "Percentil 95 (ms)": Math.round(p95),
    "Bajo 1 s": ok.filter((t) => t < 1000).length + " de " + N,
    "Bajo 3 s": ok.filter((t) => t < 3000).length + " de " + N,
  });
})();
