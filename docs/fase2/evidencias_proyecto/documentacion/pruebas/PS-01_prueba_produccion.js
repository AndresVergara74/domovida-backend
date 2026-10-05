// PS-01 · Prueba en producción de la clave de API de los sensores (DomoVida)
// Envía 3 lecturas a /api/sensor-data en Render: sin clave, con clave falsa y con la clave real.
// Esperado: 401, 401 y 201. La clave real se pide en una ventana y no queda escrita en la consola.
// Uso: pegar en la Consola de Chrome con el panel (domovida-backend.vercel.app) abierto.
(async () => {
  const API = "https://domovida-backend.onrender.com";
  const CLAVE = (prompt("PS-01: pega la clave de API (DOMOVIDA_API_KEY)") || "").trim();
  // Diagnóstico sin exponer la clave: largo y huella SHA-256 (8 caracteres), igual que /api/health
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(CLAVE));
  const huella = [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 8);
  const salud = await (await fetch(API + "/api/health")).json();
  const srv = salud.clave_api_sensores || {};
  console.log("🔑 Clave pegada: largo " + CLAVE.length + ", huella " + huella);
  console.log("🔑 Clave en servidor: activa " + srv.activa + ", largo " + srv.longitud + ", huella " + srv.huella);
  const lectura = (n) => JSON.stringify({
    sensor_id: "movimiento_living", tipo: "movimiento", habitacion: "living",
    valor: { movimiento: true, prueba: "PS01-" + n }, alerta: false,
    timestamp: new Date().toISOString(),
  });
  const casos = [
    { nombre: "Sin clave", cabeceras: {}, esperado: 401 },
    { nombre: "Clave falsa", cabeceras: { "X-API-Key": "clave-falsa-123" }, esperado: 401 },
    { nombre: "Clave real", cabeceras: { "X-API-Key": CLAVE }, esperado: 201 },
  ];
  let aprobados = 0;
  for (let i = 0; i < casos.length; i++) {
    const c = casos[i];
    const r = await fetch(API + "/api/sensor-data", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...c.cabeceras },
      body: lectura(i + 1),
    });
    const ok = r.status === c.esperado;
    if (ok) aprobados++;
    console.log((ok ? "✅ " : "❌ ") + c.nombre + " → HTTP " + r.status + " (esperado " + c.esperado + ")");
  }
  console.log("📊 PS-01 en producción: " + aprobados + "/" + casos.length + " casos aprobados");
})();
