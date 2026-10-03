// PR-02 · Tasa de entrega de notificaciones ntfy (DomoVida)
// Envía 30 caídas simuladas al backend en Render y cuenta cuántas notificaciones
// "CAÍDA DETECTADA" aceptó el servidor ntfy.sh en el tópico del cuidador.
// La recepción en el celular se cuenta a mano en la app ntfy (meta: > 95 %).
// Uso: pegar en la Consola de Chrome con el panel (domovida-backend.vercel.app) abierto.
(async () => {
  const API = "https://domovida-backend.onrender.com";
  const TOPICO = "domovida-seguro-2026";
  const N = 30;
  const ESPERA_MS = 3000; // separación entre caídas (respeta el límite de ntfy.sh)
  const inicio = Math.floor(Date.now() / 1000) - 2;
  let enviadas = 0;
  console.log("🚀 PR-02: enviando " + N + " caídas, una cada " + ESPERA_MS / 1000 + " s...");
  for (let i = 1; i <= N; i++) {
    const r = await fetch(API + "/api/sensor-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sensor_id: "acelerometro_dormitorio", tipo: "acelerometro", habitacion: "dormitorio",
        valor: { magnitud: 25.0, caida: true, prueba: "PR02-" + i },
        alerta: true, timestamp: new Date().toISOString(),
      }),
    });
    if (r.ok) enviadas++;
    console.log("Caída " + i + ": API " + r.status);
    await new Promise((ok) => setTimeout(ok, ESPERA_MS));
  }
  console.log("⏳ Esperando 20 s para que ntfy termine de recibir los avisos...");
  await new Promise((ok) => setTimeout(ok, 20000));
  const res = await fetch("https://ntfy.sh/" + TOPICO + "/json?poll=1&since=" + inicio);
  const lineas = (await res.text()).trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const caidas = lineas.filter((m) => m.event === "message" && (m.title || "").includes("CAÍDA"));
  console.table({
    "Caídas enviadas a la API": N,
    "Aceptadas por la API (HTTP 2xx)": enviadas,
    "Avisos de caída en el servidor ntfy": caidas.length + " (" + Math.round((caidas.length / N) * 100) + "%)",
    "Inicio de la prueba": new Date(inicio * 1000).toLocaleString("es-CL"),
  });
  console.log("📱 Ahora cuenta en la app ntfy del celular cuántos avisos 'CAÍDA DETECTADA' llegaron.");
})();
