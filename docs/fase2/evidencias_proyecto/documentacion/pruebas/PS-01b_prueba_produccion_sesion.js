// PS-01 (parte 2) · Prueba en producción de la sesión del cuidador para atender alertas (DomoVida)
// 1) Crea una alerta de prueba (botón de pánico) con la clave de API de los sensores.
// 2) Intenta marcarla como atendida: sin sesión, con un token falso y con la sesión real del panel.
// Esperado: 401, 401 y 200; el backend guarda el correo del cuidador en resuelto_por.
// Uso: iniciar sesión en el panel (domovida-backend.vercel.app) y pegar este script en su Consola.
(async () => {
  const API = "https://domovida-backend.onrender.com";
  const CLAVE = (prompt("PS-01b: pega la clave de API de los sensores (DOMOVIDA_API_KEY)") || "").trim();
  const sesion = JSON.parse(sessionStorage.getItem("domovida-sesion") || "null");
  if (!sesion || sesion.expira < Date.now()) { console.log("❌ No hay sesión vigente: presiona Ingresar en el panel y vuelve a ejecutar"); return; }
  const r0 = await fetch(API + "/api/sensor-data", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": CLAVE },
    body: JSON.stringify({ sensor_id: "boton_panico_sala", tipo: "boton_panico", habitacion: "sala",
      valor: { activado: true, prueba: "PS01b" }, alerta: true, timestamp: new Date().toISOString() }),
  });
  if (r0.status !== 201) { console.log("❌ No se pudo crear la alerta de prueba: HTTP " + r0.status); return; }
  const id = (await r0.json()).id;
  console.log("🚨 Alerta de prueba creada: id " + id);
  const casos = [
    { nombre: "Atender sin sesión", cab: {}, esperado: 401 },
    { nombre: "Atender con token falso", cab: { Authorization: "Bearer token-falso-123" }, esperado: 401 },
    { nombre: "Atender con la sesión del cuidador", cab: { Authorization: "Bearer " + sesion.token }, esperado: 200 },
  ];
  let aprobados = 0;
  for (const c of casos) {
    const r = await fetch(API + "/api/alertas/" + id + "/resolver", {
      method: "PATCH", headers: { "Content-Type": "application/json", ...c.cab },
      body: JSON.stringify({ resuelto_por: "Cuidador DomoVida" }),
    });
    const ok = r.status === c.esperado;
    if (ok) aprobados++;
    const cuerpo = r.status === 200 ? " " + JSON.stringify(await r.json()) : "";
    console.log((ok ? "✅ " : "❌ ") + c.nombre + " → HTTP " + r.status + " (esperado " + c.esperado + ")" + cuerpo);
  }
  console.log("📊 PS-01b en producción: " + aprobados + "/" + casos.length + " casos aprobados (sesión de " + sesion.email + ")");
})();
