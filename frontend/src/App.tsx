// src/App.tsx — Panel del cuidador DomoVida (diseño "clínico sereno", 08-10-2026)
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import {
  House, Moon, Sun, Shield, LogIn, LogOut, Bell, X, CircleCheck, TriangleAlert, Clock, WifiOff, Footprints, Radio, RefreshCw,
} from "lucide-react";
import { useDomovida } from "./useDomovida";
import { useWebSocket } from "./useWebSocket";
import Consentimiento from "./Consentimiento";
import MapaHogar from "./MapaHogar";
import LoginCuidador from "./LoginCuidador";
import { authHabilitada, leerSesion, cerrarSesion, type Sesion } from "./auth";
import { nombreTipo, nombreAlerta, describirEvento, iconoTipo, nombreHabitacion, componenteSistema, haceCuanto, hora, esHoy, inventarioSensores, MINUTOS_SENSOR_ACTIVO } from "./etiquetas";
import "./App.css";

// URL base de la API (usa variable de entorno o fallback)
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

type Pestana = "general" | "historial" | "sensores" | "ubicacion";
const PESTANAS: Array<[Pestana, string]> = [
  ["general", "Resumen"],
  ["historial", "Historial"],
  ["sensores", "Sensores"],
  ["ubicacion", "Mapa del hogar"],
];

function App() {
  const { eventos, alertas, sensores, minutosInactivo, cargando, conectado, refrescar } = useDomovida();
  const { conectado: wsConectado, alertasTiempoReal } = useWebSocket();
  const [pestana, setPestana] = useState<Pestana>("general");
  const [estadoSistema, setEstadoSistema] = useState<any[]>([]);
  const [lecturasProtegidas, setLecturasProtegidas] = useState(false); // HU-17
  const [notificacionVisible, setNotificacionVisible] = useState(false);
  const [ultimaAlertaRT, setUltimaAlertaRT] = useState<any>(null);

  // ============================================================
  // Estado para CONSENTIMIENTO INFORMADO
  // ============================================================
  const [consentimientoAceptado, setConsentimientoAceptado] = useState<boolean>(() => {
    return localStorage.getItem("domovida-consentimiento") !== null;
  });
  const [mostrarConsentimiento, setMostrarConsentimiento] = useState<boolean>(false);

  // ============================================================
  // Estados para "Marcar como atendida"
  // ============================================================
  const [resolviendoId, setResolviendoId] = useState<number | null>(null);
  const [alertasResueltas, setAlertasResueltas] = useState<Map<number, Date>>(new Map());

  // ============================================================
  // Sesión del cuidador (PS-01): necesaria para atender alertas
  // ============================================================
  const [sesion, setSesion] = useState<Sesion | null>(() => leerSesion());
  const [mostrarLogin, setMostrarLogin] = useState(false);
  const [alertaPendiente, setAlertaPendiente] = useState<number[] | null>(null);

  // ============================================================
  // Estados para FILTROS DEL HISTORIAL
  // ============================================================
  const [filtroSensor, setFiltroSensor] = useState<string>("todos");
  const [filtroTipo, setFiltroTipo] = useState<string>("todos");
  const [filtroHabitacion, setFiltroHabitacion] = useState<string>("todas");
  const [filtroAlerta, setFiltroAlerta] = useState<string>("todos");

  // ============================================================
  // Estado para MODO OSCURO
  // ============================================================
  const [temaOscuro, setTemaOscuro] = useState<boolean>(() => {
    const guardado = localStorage.getItem("domovida-tema");
    if (guardado) return guardado === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  // ============================================================
  // Efecto: aplicar/quitar clase "dark" al body
  // ============================================================
  useEffect(() => {
    if (temaOscuro) {
      document.body.classList.add("dark");
      localStorage.setItem("domovida-tema", "dark");
    } else {
      document.body.classList.remove("dark");
      localStorage.setItem("domovida-tema", "light");
    }
  }, [temaOscuro]);

  // ============================================================
  // Cargar estado del sistema desde /api/health
  // ============================================================
  useEffect(() => {
    async function cargarHealth() {
      try {
        const response = await fetch(`${API_URL}/api/health`);
        const data = await response.json();
        setEstadoSistema(data.componentes || []);
        setLecturasProtegidas(Boolean(data.auth_cuidador?.lecturas_protegidas));
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
  async function resolverAlerta(alertaId: number | number[], sesionActual: Sesion | null = sesion) {
    // Acepta una alerta o un grupo de avisos repetidos (mismo sensor, mismos minutos)
    const ids = Array.isArray(alertaId) ? alertaId : [alertaId];
    const principal = ids[0];
    // Si el inicio de sesión está configurado y no hay sesión vigente, pedirla primero
    const vigente = sesionActual && sesionActual.expira > Date.now() ? sesionActual : null;
    if (authHabilitada && !vigente) {
      setAlertaPendiente(ids);
      setMostrarLogin(true);
      return;
    }

    setResolviendoId(principal);

    try {
      const cabeceras: Record<string, string> = { "Content-Type": "application/json" };
      if (vigente) cabeceras["Authorization"] = `Bearer ${vigente.token}`;
      for (const id of ids) {
        const response = await fetch(`${API_URL}/api/alertas/${id}/resolver`, {
          method: "PATCH",
          headers: cabeceras,
          body: JSON.stringify({
            resuelto_por: "Cuidador DomoVida",
          }),
        });

        if (response.status === 401) {
          // Sesión vencida o rechazada por el backend: volver a pedirla
          cerrarSesion();
          setSesion(null);
          setAlertaPendiente(ids);
          setMostrarLogin(true);
          return;
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        setAlertasResueltas((prev) => new Map(prev).set(id, new Date()));
        console.log(`✅ Alerta ${id} marcada como atendida`);
      }

      if (refrescar) {
        await refrescar();
      }
    } catch (error) {
      console.error(`❌ Error al resolver alerta ${principal}:`, error);
      alert("No se pudo marcar la alerta como atendida. Intenta de nuevo.");
    } finally {
      setResolviendoId(null);
    }
  }

  // ============================================================
  // FUNCIONES: Sesión del cuidador
  // ============================================================
  function handleLoginExitoso(nueva: Sesion) {
    setSesion(nueva);
    setMostrarLogin(false);
    refrescar?.(); // HU-17: con la sesión iniciada se cargan los datos protegidos
    if (alertaPendiente !== null) {
      const id = alertaPendiente;
      setAlertaPendiente(null);
      resolverAlerta(id, nueva);
    }
  }

  function handleCerrarSesion() {
    cerrarSesion();
    setSesion(null);
  }

  // ============================================================
  // FUNCIONES: Consentimiento
  // ============================================================
  function handleAceptarConsentimiento() {
    setConsentimientoAceptado(true);
    setMostrarConsentimiento(false);
  }

  function handleRechazarConsentimiento() {
    setMostrarConsentimiento(false);
    alert(
      "Has rechazado el consentimiento. DomoVida no puede activar el monitoreo sin tu autorización."
    );
  }

  if (cargando) {
    return (
      <div className="cargando" role="status">
        <House size={28} aria-hidden="true" />
        <span>Cargando DomoVida…</span>
      </div>
    );
  }

  if (!consentimientoAceptado || mostrarConsentimiento) {
    return (
      <Consentimiento
        onAceptar={handleAceptarConsentimiento}
        onRechazar={handleRechazarConsentimiento}
      />
    );
  }

  // ------------------------------------------------------------
  // Datos derivados
  // ------------------------------------------------------------
  const todasLasAlertas = [
    ...alertasTiempoReal,
    ...alertas.filter((a) => !alertasTiempoReal.some((rt) => rt.id === a.id)),
  ];
  const pendientes = todasLasAlertas.filter((a) => !alertasResueltas.has(a.id));

  // Avisos repetidos del mismo sensor en pocos minutos se muestran como una sola alerta
  const VENTANA_GRUPO_MS = 10 * 60 * 1000;
  type GrupoAlertas = { principal: (typeof todasLasAlertas)[number]; ids: number[] };
  function agrupar(lista: typeof todasLasAlertas): GrupoAlertas[] {
    const ordenadas = [...lista].sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp));
    const grupos: GrupoAlertas[] = [];
    for (const a of ordenadas) {
      const g = grupos.find(
        (x) =>
          x.principal.tipo === a.tipo &&
          x.principal.habitacion === a.habitacion &&
          alertasResueltas.has(x.principal.id) === alertasResueltas.has(a.id) &&
          +new Date(x.principal.timestamp) - +new Date(a.timestamp) <= VENTANA_GRUPO_MS
      );
      if (g) g.ids.push(a.id);
      else grupos.push({ principal: a, ids: [a.id] });
    }
    return grupos;
  }
  const gruposPendientes = agrupar(pendientes);
  const gruposAlertas = agrupar(todasLasAlertas);
  const esAlerta = (e: (typeof eventos)[number]) => !!(e.alerta || e.caida_detectada);
  const eventosHoy = eventos.filter((e) => esHoy(e.timestamp));

  // Episodios de alerta de hoy: lecturas en alerta del mismo sensor separadas por menos de 10 min cuentan como una
  const episodiosHoy = (() => {
    const ultimos = new Map<string, number>();
    let n = 0;
    for (const e of [...eventosHoy].filter(esAlerta).sort((a, b) => +new Date(a.timestamp) - +new Date(b.timestamp))) {
      const t = +new Date(e.timestamp);
      const prev = ultimos.get(e.sensor_id);
      if (prev === undefined || t - prev > VENTANA_GRUPO_MS) n++;
      ultimos.set(e.sensor_id, t);
    }
    return n;
  })();

  // Última actividad: lecturas iguales y seguidas se juntan en una fila
  const ultimaActividad = (() => {
    const filas: Array<{ e: (typeof eventos)[number]; n: number }> = [];
    for (const e of eventos) {
      const f = filas[filas.length - 1];
      if (
        f &&
        f.e.sensor_id === e.sensor_id &&
        describirEvento(f.e) === describirEvento(e) &&
        +new Date(f.e.timestamp) - +new Date(e.timestamp) <= VENTANA_GRUPO_MS
      ) {
        f.n++;
      } else {
        if (filas.length === 6) break;
        filas.push({ e, n: 1 });
      }
    }
    return filas;
  })();

  const ultimoMovimiento = eventos.find((e) => (e.tipo === "pir" || e.tipo === "movimiento") && e.valor?.movimiento);
  const ultimoDato = eventos[0]?.timestamp;
  const minutosSinDatos = ultimoDato ? Math.floor((Date.now() - +new Date(ultimoDato)) / 60000) : null;
  const inventario = inventarioSensores(sensores);
  const sensoresOnline = inventario.filter((s) => s.online).length;
  const totalSensores = inventario.length;
  const sinAcceso = lecturasProtegidas && !sesion;

  // Actividad por hora (últimas 12 horas), a partir de los eventos cargados
  const ahora = new Date();
  const datosActividad = Array.from({ length: 12 }, (_, k) => {
    const inicio = new Date(ahora);
    inicio.setMinutes(0, 0, 0);
    inicio.setHours(inicio.getHours() - (11 - k));
    const fin = inicio.getTime() + 3600000;
    const enHora = eventos.filter((e) => {
      const t = new Date(e.timestamp).getTime();
      return t >= inicio.getTime() && t < fin;
    });
    return {
      hora: `${String(inicio.getHours()).padStart(2, "0")}:00`,
      eventos: enHora.filter((e) => !(e.alerta || e.caida_detectada)).length,
      alertas: enHora.filter((e) => e.alerta || e.caida_detectada).length,
    };
  });

  // Filtros del historial
  const sensoresUnicos = Array.from(new Set(eventos.map((e) => e.sensor_id))).sort();
  const tiposUnicos = Array.from(new Set(eventos.map((e) => e.tipo))).sort();
  const habitacionesUnicas = Array.from(new Set(eventos.map((e) => e.habitacion).filter(Boolean))).sort() as string[];
  const eventosFiltrados = eventos.filter((e) => {
    if (filtroSensor !== "todos" && e.sensor_id !== filtroSensor) return false;
    if (filtroTipo !== "todos" && e.tipo !== filtroTipo) return false;
    if (filtroHabitacion !== "todas" && e.habitacion !== filtroHabitacion) return false;
    if (filtroAlerta === "solo_alertas" && !e.alerta && !e.caida_detectada) return false;
    if (filtroAlerta === "sin_alertas" && (e.alerta || e.caida_detectada)) return false;
    return true;
  });
  const hayFiltrosActivos =
    filtroSensor !== "todos" || filtroTipo !== "todos" || filtroHabitacion !== "todas" || filtroAlerta !== "todos";
  function limpiarFiltros() {
    setFiltroSensor("todos");
    setFiltroTipo("todos");
    setFiltroHabitacion("todas");
    setFiltroAlerta("todos");
  }

  // ------------------------------------------------------------
  // Estado del hogar (lo primero que ve el cuidador)
  // ------------------------------------------------------------
  const grupoPrimero = gruposPendientes[0];
  const primera = grupoPrimero?.principal;
  let estado: "ok" | "alerta" | "sin-acceso" | "sin-conexion" | "sin-datos" = "ok";
  if (sinAcceso) estado = "sin-acceso";
  else if (pendientes.length > 0) estado = "alerta";
  else if (!conectado) estado = "sin-conexion";
  else if (!cargando && (minutosSinDatos === null || minutosSinDatos > MINUTOS_SENSOR_ACTIVO)) estado = "sin-datos";

  const lineaDetalle = [
    ultimoMovimiento
      ? `Último movimiento: ${nombreHabitacion(ultimoMovimiento.habitacion)}, ${haceCuanto(ultimoMovimiento.timestamp)}`
      : `Sin movimiento en las últimas ${eventos.length} lecturas`,
    `${sensoresOnline} de ${totalSensores} sensores enviando datos`,
  ].filter(Boolean);

  return (
    <div className="app">
      {mostrarLogin && (
        <LoginCuidador
          onExito={handleLoginExitoso}
          onCancelar={() => {
            setMostrarLogin(false);
            setAlertaPendiente(null);
          }}
        />
      )}

      {notificacionVisible && ultimaAlertaRT && (
        <div className="aviso-vivo" role="alert">
          <Bell size={22} aria-hidden="true" />
          <div>
            <strong>{nombreAlerta(ultimaAlertaRT.tipo)} en {nombreHabitacion(ultimaAlertaRT.habitacion).toLowerCase()}</strong>
            <span>Alerta recibida a las {hora(ultimaAlertaRT.timestamp || new Date())}</span>
          </div>
          <button className="icono-btn" onClick={() => setNotificacionVisible(false)} aria-label="Cerrar aviso">
            <X size={18} />
          </button>
        </div>
      )}

      {/* ===================== Barra superior ===================== */}
      <header className="barra">
        <div className="barra-marca">
          <span className="marca-icono" aria-hidden="true"><House size={20} /></span>
          <div>
            <span className="marca-nombre">DomoVida</span>
            <span className="marca-hogar">Hogar p001</span>
          </div>
        </div>

        <div className="barra-acciones">
          <span className={`conexion ${conectado ? (wsConectado ? "ok" : "parcial") : "caida"}`}>
            <span className="conexion-punto" aria-hidden="true" />
            {conectado ? (wsConectado ? "En línea" : "En línea, sin tiempo real") : "Sin conexión"}
          </span>

          {authHabilitada &&
            (sesion ? (
              <button className="btn-quiet" onClick={handleCerrarSesion} title="Cerrar sesión">
                <LogOut size={17} aria-hidden="true" />
                <span className="btn-texto">{sesion.email}</span>
              </button>
            ) : (
              <button className="btn-primario btn-chico" onClick={() => setMostrarLogin(true)}>
                <LogIn size={17} aria-hidden="true" />
                Ingresar
              </button>
            ))}

          <button className="icono-btn" onClick={() => setMostrarConsentimiento(true)} title="Ver consentimiento informado" aria-label="Ver consentimiento informado">
            <Shield size={19} />
          </button>
          <button
            className="icono-btn"
            onClick={() => setTemaOscuro(!temaOscuro)}
            title={temaOscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
            aria-label={temaOscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
          >
            {temaOscuro ? <Sun size={19} /> : <Moon size={19} />}
          </button>
        </div>
      </header>

      <nav className="pestanas" aria-label="Secciones del panel">
        {PESTANAS.map(([id, texto]) => (
          <button
            key={id}
            className={pestana === id ? "activa" : ""}
            aria-current={pestana === id ? "page" : undefined}
            onClick={() => setPestana(id)}
          >
            {texto}
            {id === "general" && gruposPendientes.length > 0 && <span className="pestana-cuenta">{gruposPendientes.length}</span>}
          </button>
        ))}
      </nav>

      <main className="contenido">
        {/* ===================== RESUMEN ===================== */}
        {pestana === "general" && (
          <>
            <section className={`estado-hogar ${estado}`} aria-live="polite">
              {estado === "ok" && (
                <>
                  <CircleCheck className="estado-icono" size={30} aria-hidden="true" />
                  <div className="estado-texto">
                    <h1>Todo en orden en casa.</h1>
                    <p>{lineaDetalle.join(". ")}.</p>
                  </div>
                </>
              )}
              {estado === "alerta" && primera && (
                <>
                  <TriangleAlert className="estado-icono" size={30} aria-hidden="true" />
                  <div className="estado-texto">
                    <h1>
                      {nombreAlerta(primera.tipo)} en {nombreHabitacion(primera.habitacion).toLowerCase()} a las {hora(primera.timestamp)}
                    </h1>
                    <p>
                      {gruposPendientes.length === 1
                        ? grupoPrimero.ids.length > 1
                          ? `El sensor avisó ${grupoPrimero.ids.length} veces seguidas. Comuníquese con su familiar o acuda al hogar.`
                          : "Hay una alerta sin atender. Comuníquese con su familiar o acuda al hogar."
                        : `Hay ${gruposPendientes.length} alertas sin atender. Comience por la más reciente.`}
                    </p>
                  </div>
                  <button className="btn-alerta" onClick={() => resolverAlerta(grupoPrimero.ids)} disabled={resolviendoId === primera.id}>
                    {resolviendoId === primera.id ? "Registrando…" : "Marcar como atendida"}
                  </button>
                </>
              )}
              {estado === "sin-acceso" && (
                <>
                  <Shield className="estado-icono" size={30} aria-hidden="true" />
                  <div className="estado-texto">
                    <h1>Inicie sesión para ver el estado del hogar.</h1>
                    <p>Los datos están protegidos y solo los ve el cuidador autorizado.</p>
                  </div>
                  <button className="btn-primario" onClick={() => setMostrarLogin(true)}>
                    <LogIn size={18} aria-hidden="true" /> Ingresar
                  </button>
                </>
              )}
              {estado === "sin-datos" && (
                <>
                  <Clock className="estado-icono" size={30} aria-hidden="true" />
                  <div className="estado-texto">
                    <h1>{minutosSinDatos === null ? "Aún no llegan datos del hogar." : `No llegan datos del hogar desde ${haceCuanto(ultimoDato)}.`}</h1>
                    <p>Revise que el equipo del hogar esté encendido y con internet. Sin datos, DomoVida no puede detectar emergencias.</p>
                  </div>
                </>
              )}
              {estado === "sin-conexion" && (
                <>
                  <WifiOff className="estado-icono" size={30} aria-hidden="true" />
                  <div className="estado-texto">
                    <h1>No hay conexión con el servidor.</h1>
                    <p>El panel se actualizará solo cuando vuelva la conexión. Las alertas siguen llegando al celular.</p>
                  </div>
                </>
              )}
            </section>

            <div className="resumen-grid">
              <div className="columna">
              <section className="panel">
                <div className="panel-cabecera">
                  <h2>Alertas recientes</h2>
                  {wsConectado && <span className="en-vivo">En vivo</span>}
                </div>
                {todasLasAlertas.length === 0 ? (
                  <p className="vacio sin-pendientes"><CircleCheck size={18} aria-hidden="true" /> No hay alertas sin atender.</p>
                ) : (
                  <ul className="lista-alertas">
                    {gruposAlertas.slice(0, 6).map(({ principal: a, ids }) => {
                      const atendida = alertasResueltas.get(a.id);
                      const Icono = iconoTipo(a.tipo);
                      return (
                        <li key={a.id} className={atendida ? "atendida" : "pendiente"}>
                          <time className="alerta-hora">{hora(a.timestamp)}</time>
                          <Icono className="alerta-icono" size={20} aria-hidden="true" />
                          <div className="alerta-texto">
                            <strong>
                              {nombreAlerta(a.tipo)}
                              {ids.length > 1 && <span className="repeticiones">{ids.length} avisos</span>}
                            </strong>
                            <span>{nombreHabitacion(a.habitacion)}</span>
                          </div>
                          {atendida ? (
                            <span className="sello-atendida">
                              <CircleCheck size={16} aria-hidden="true" /> Atendida {hora(atendida)}
                            </span>
                          ) : (
                            <button className="btn-secundario" onClick={() => resolverAlerta(ids)} disabled={resolviendoId === a.id}>
                              {resolviendoId === a.id ? "Registrando…" : "Atender"}
                            </button>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </section>

              <section className="panel">
                <div className="panel-cabecera">
                  <h2>Última actividad</h2>
                  <button className="btn-enlace" onClick={() => setPestana("historial")}>Ver historial</button>
                </div>
                {ultimaActividad.length === 0 ? (
                  <p className="vacio">Aún no hay lecturas registradas.</p>
                ) : (
                  <ul className="lista-actividad">
                    {ultimaActividad.map(({ e, n }) => {
                      const Icono = iconoTipo(e.tipo);
                      return (
                        <li key={e.id} className={esAlerta(e) ? "es-alerta" : ""}>
                          <time>{hora(e.timestamp)}</time>
                          <Icono size={18} aria-hidden="true" />
                          <span className="actividad-tipo">
                            {describirEvento(e)}
                            {n > 1 && <span className="actividad-veces">{n} lecturas</span>}
                          </span>
                          <span className="actividad-lugar">{nombreHabitacion(e.habitacion)}</span>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </section>
              </div>

              <div className="columna">
                <section className="panel">
                  <div className="panel-cabecera">
                    <h2>Actividad de hoy</h2>
                    <span className="panel-nota">{eventosHoy.length} lecturas, {episodiosHoy} {episodiosHoy === 1 ? "alerta" : "alertas"}</span>
                  </div>
                  <div className="grafico" aria-label="Lecturas por hora en las últimas 12 horas">
                    <ResponsiveContainer width="100%" height={180}>
                      <BarChart data={datosActividad} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                        <CartesianGrid vertical={false} stroke="var(--linea)" />
                        <XAxis dataKey="hora" tick={{ fontSize: 12, fill: "var(--tinta-suave)" }} tickLine={false} axisLine={false} interval={2} />
                        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "var(--tinta-suave)" }} tickLine={false} axisLine={false} />
                        <Tooltip cursor={{ fill: "var(--fondo)" }} contentStyle={{ borderRadius: 8, border: "1px solid var(--linea)", fontFamily: "inherit" }} />
                        <Bar dataKey="eventos" name="Lecturas" stackId="a" fill="var(--petroleo)" />
                        <Bar dataKey="alertas" name="Alertas" stackId="a" fill="var(--rojo)" radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </section>

                <section className="panel">
                  <div className="panel-cabecera">
                    <h2>Estado del sistema</h2>
                  </div>
                  <ul className="lista-sistema">
                    {estadoSistema.map((s) => {
                      const c = componenteSistema(s.nombre);
                      const Icono = c.icono;
                      const clase = s.simulado ? "simulado" : s.online ? "ok" : "caido";
                      return (
                        <li key={s.nombre} title={`${c.detalle}: ${s.mensaje}`}>
                          <Icono size={18} aria-hidden="true" />
                          <span className="sistema-nombre">{c.nombre}</span>
                          <span className={`sistema-estado ${clase}`}>
                            {s.simulado ? "Simulado" : s.online ? "Funcionando" : "Sin conexión"}
                          </span>
                        </li>
                      );
                    })}
                    <li title="Sensores del hogar con una lectura en la última hora">
                      <Footprints size={18} aria-hidden="true" />
                      <span className="sistema-nombre">Sensores</span>
                      <span className={`sistema-estado ${sensoresOnline === totalSensores ? "ok" : sensoresOnline === 0 ? "caido" : "parcial"}`}>
                        {sensoresOnline} de {totalSensores} activos
                      </span>
                    </li>
                    <li title="Conexión en vivo (WebSocket) entre el servidor y este panel">
                      <Radio size={18} aria-hidden="true" />
                      <span className="sistema-nombre">Actualización en vivo</span>
                      <span className={`sistema-estado ${wsConectado ? "ok" : "parcial"}`}>{wsConectado ? "Conectada" : "Cada 10 s"}</span>
                    </li>
                  </ul>
                  {ultimoDato && (
                    <p className="panel-pie">
                      <RefreshCw size={15} aria-hidden="true" /> Último dato recibido del hogar: {haceCuanto(ultimoDato)} ({hora(ultimoDato)})
                    </p>
                  )}
                  {minutosInactivo !== null && (
                    <p className="panel-pie">
                      <Clock size={15} aria-hidden="true" /> Sin movimiento hace {minutosInactivo} min
                      {minutosInactivo >= 30 ? " — conviene comunicarse" : ""}
                    </p>
                  )}
                </section>
              </div>
            </div>
          </>
        )}

        {/* ===================== HISTORIAL ===================== */}
        {pestana === "historial" && (
          <section className="panel">
            <div className="panel-cabecera">
              <h2>Historial de lecturas</h2>
              <span className="panel-nota">{eventosFiltrados.length} de {eventos.length}</span>
            </div>
            <div className="filtros">
              <label>
                Sensor
                <select value={filtroSensor} onChange={(e) => setFiltroSensor(e.target.value)}>
                  <option value="todos">Todos</option>
                  {sensoresUnicos.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
              <label>
                Tipo
                <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
                  <option value="todos">Todos</option>
                  {tiposUnicos.map((t) => <option key={t} value={t}>{nombreTipo(t)}</option>)}
                </select>
              </label>
              <label>
                Habitación
                <select value={filtroHabitacion} onChange={(e) => setFiltroHabitacion(e.target.value)}>
                  <option value="todas">Todas</option>
                  {habitacionesUnicas.map((h) => <option key={h} value={h}>{nombreHabitacion(h)}</option>)}
                </select>
              </label>
              <label>
                Alertas
                <select value={filtroAlerta} onChange={(e) => setFiltroAlerta(e.target.value)}>
                  <option value="todos">Todas las lecturas</option>
                  <option value="solo_alertas">Solo alertas</option>
                  <option value="sin_alertas">Sin alertas</option>
                </select>
              </label>
              {hayFiltrosActivos && (
                <button className="btn-quiet" onClick={limpiarFiltros}>
                  <X size={15} aria-hidden="true" /> Quitar filtros
                </button>
              )}
            </div>
            <div className="tabla-envoltura">
              <table>
                <thead>
                  <tr>
                    <th>Fecha y hora</th>
                    <th>Tipo</th>
                    <th>Habitación</th>
                    <th>Sensor</th>
                    <th>Resultado</th>
                  </tr>
                </thead>
                <tbody>
                  {eventosFiltrados.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="vacio">No hay lecturas con estos filtros. Pruebe quitando alguno.</td>
                    </tr>
                  ) : (
                    eventosFiltrados.slice(0, 50).map((e) => {
                      const alerta = e.alerta || e.caida_detectada;
                      return (
                        <tr key={e.id} className={alerta ? "fila-alerta" : ""}>
                          <td className="num">{new Date(e.timestamp).toLocaleString("es-CL", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" })}</td>
                          <td>{nombreTipo(e.tipo)}</td>
                          <td>{nombreHabitacion(e.habitacion)}</td>
                          <td className="tenue">{e.sensor_id}</td>
                          <td>{alerta ? <span className="etiqueta-alerta">Alerta</span> : <span className="tenue">Normal</span>}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* ===================== SENSORES ===================== */}
        {pestana === "sensores" && (
          <section className="panel">
            <div className="panel-cabecera">
              <h2>Sensores del hogar</h2>
              <span className="panel-nota">{sensoresOnline} de {totalSensores} con lecturas en la última hora</span>
            </div>
            {inventario.length === 0 ? (
              <p className="vacio">Aún no hay sensores registrados.</p>
            ) : (
              <ul className="lista-sensores">
                {inventario.map((s) => {
                  const Icono = iconoTipo(s.tipo);
                  return (
                    <li key={s.sensor_id}>
                      <Icono size={20} aria-hidden="true" />
                      <div className="sensor-texto">
                        <strong>{nombreTipo(s.tipo)}</strong>
                        <span>{nombreHabitacion(s.habitacion)}, {s.sensor_id}</span>
                      </div>
                      <span className="tenue">{s.ultima_lectura ? `Última lectura ${haceCuanto(s.ultima_lectura)}` : "Sin lecturas"}</span>
                      <span className={`sistema-estado ${s.online ? "ok" : "parcial"}`}>{s.online ? "Activo" : "Sin datos recientes"}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        )}

        {/* ===================== MAPA ===================== */}
        {pestana === "ubicacion" && (
          <section className="panel">
            <MapaHogar sensores={inventario} />
          </section>
        )}
      </main>

      <footer className="pie">
        DomoVida, proyecto de título de Ingeniería en Informática (Duoc UC). Datos seudonimizados según la Ley N° 21.719.
      </footer>
    </div>
  );
}

export default App;
