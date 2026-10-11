// PR-01c · Latencia de la alerta crítica en Oracle Cloud Santiago (DomoVida)
// Mismo procedimiento que PR-01 y PR-01b: 30 caídas simuladas y tiempo hasta que
// cada alerta vuelve por WebSocket (sensor → backend → BD → panel).
// Servidor: Oracle Cloud, región Chile Central (Santiago), VM.Standard.E2.1.Micro
// (Always Free), Docker con backend + SQLite en la misma máquina.
// Uso: abrir http://155.181.166.37:8000/api/health en Chrome, F12 → Consola → pegar.
// (Se ejecuta desde esa página para usar http/ws sin bloqueo de contenido mixto.)
(async () => {
  // La clave se pide en una ventana: nunca se escribe en el archivo ni en la consola.
  const CLAVE = (prompt("Clave de API de los sensores (DOMOVIDA_API_KEY)") || "").trim();
  const API = "http://155.181.166.37:8000";
  const WS = "ws://155.181.166.37:8000/api/ws/alertas";
  const N = 30;
  const ws = new WebSocket(WS);
  await new Promise((ok, err) => { ws.onopen = ok; ws.onerror = err; });
  console.log("✅ WebSocket de prueba conectado. Enviando " + N + " caídas...");
  const tiempos = [];
  for (let i = 1; i <= N; i++) {
    const marca = "PR01c-" + i + "-" + Date.now();
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
      headers: { "Content-Type": "application/json", "X-API-Key": CLAVE },
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
