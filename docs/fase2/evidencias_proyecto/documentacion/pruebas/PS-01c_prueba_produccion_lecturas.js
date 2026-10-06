// PS-01c · HU-17 · Prueba en producción: las consultas de lectura exigen la sesión del cuidador (DomoVida)
// Requiere PROTEGER_LECTURAS=1 en Render. No pide ninguna clave: usa la sesión ya iniciada en el panel.
// Esperado: /api/health informa lecturas_protegidas = true; sin sesión 401, token falso 401, con sesión 200.
// Uso: iniciar sesión en el panel (domovida-backend.vercel.app) y pegar este script en su Consola (F12).
(async () => {
  const API = "https://domovida-backend.onrender.com";
  const sesion = JSON.parse(sessionStorage.getItem("domovida-sesion") || "null");
  if (!sesion || sesion.expira < Date.now()) { console.log("❌ No hay sesión vigente: presiona Ingresar en el panel y vuelve a ejecutar"); return; }
  const h = await (await fetch(API + "/api/health")).json();
  const protegidas = h.auth_cuidador && h.auth_cuidador.lecturas_protegidas === true;
  console.log((protegidas ? "✅" : "❌") + " /api/health → lecturas_protegidas = " + (h.auth_cuidador && h.auth_cuidador.lecturas_protegidas));
  const rutas = ["/api/eventos?limit=5", "/api/alertas/activas", "/api/alertas/inactividad", "/api/fhir/Patient/domovida-p001"];
  const casos = [
    { nombre: "sin sesión", cab: {}, esperado: 401 },
    { nombre: "token falso", cab: { Authorization: "Bearer token-falso-123" }, esperado: 401 },
    { nombre: "sesión del cuidador", cab: { Authorization: "Bearer " + sesion.token }, esperado: 200 },
  ];
  let aprobados = 0, total = 0;
  for (const c of casos) {
    const codigos = [];
    for (const r of rutas) codigos.push((await fetch(API + r, { headers: c.cab })).status);
    const ok = codigos.every((x) => x === c.esperado);
    total++; if (ok) aprobados++;
    console.log((ok ? "✅ " : "❌ ") + c.nombre + " → " + codigos.join(", ") + " (esperado " + c.esperado + " en las " + rutas.length + " consultas)");
  }
  console.log("📊 PS-01c en producción: " + aprobados + "/" + total + " casos aprobados" + (protegidas ? "" : " · ⚠️ la protección no está activa en Render") + " (sesión de " + sesion.email + ")");
})();
