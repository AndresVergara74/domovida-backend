// SUS · Tarea 3 · Genera UNA caída de prueba para que el participante la atienda (DomoVida)
// Uso (solo el facilitador): con el panel abierto en domovida-backend.vercel.app, F12 → Consola → pegar.
// Pide la clave de API de los sensores en una ventana (nunca se escribe en la consola ni en el chat).
(async () => {
  const CLAVE = (prompt("Clave de API de los sensores (DOMOVIDA_API_KEY)") || "").trim();
  const r = await fetch("https://domovida-backend.onrender.com/api/sensor-data", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": CLAVE },
    body: JSON.stringify({ sensor_id: "acelerometro_dormitorio", tipo: "acelerometro", habitacion: "dormitorio",
      valor: { magnitud: 24.5, prueba: "SUS" }, alerta: true, timestamp: new Date().toISOString() }),
  });
  console.log(r.status === 201 ? "✅ Caída de prueba enviada (id " + (await r.json()).id + ")" : "❌ HTTP " + r.status);
})();
