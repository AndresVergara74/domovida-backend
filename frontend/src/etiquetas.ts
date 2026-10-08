// src/etiquetas.ts
// Lenguaje del cuidador: nombres claros en vez de identificadores técnicos.
import {
  Activity, Footprints, Flame, CloudFog, DoorOpen, HeartPulse, Siren, Gauge,
  Cpu, Server, Database, RadioTower, Smartphone,
  type LucideIcon,
} from "lucide-react";

// sensor: nombre del dispositivo · alerta: qué significa cuando una regla lo marca como alerta
const TIPOS: Record<string, { sensor: string; alerta: string; icono: LucideIcon }> = {
  acelerometro: { sensor: "Detector de caídas", alerta: "Posible caída", icono: Activity },
  pir: { sensor: "Sensor de movimiento", alerta: "Inactividad prolongada", icono: Footprints },
  movimiento: { sensor: "Sensor de movimiento", alerta: "Inactividad prolongada", icono: Footprints },
  humo: { sensor: "Detector de humo", alerta: "Humo detectado", icono: Flame },
  gas: { sensor: "Detector de gas", alerta: "Fuga de gas", icono: CloudFog },
  apertura: { sensor: "Puerta o ventana", alerta: "Puerta abierta fuera de lo habitual", icono: DoorOpen },
  cardiovascular: { sensor: "Ritmo cardíaco", alerta: "Ritmo cardíaco fuera de rango", icono: HeartPulse },
  boton_panico: { sensor: "Botón de pánico", alerta: "Botón de pánico presionado", icono: Siren },
};

function legible(texto: string): string {
  const limpio = texto.replace(/_/g, " ");
  return limpio.charAt(0).toUpperCase() + limpio.slice(1);
}

/** Nombre del sensor (dispositivo). */
export function nombreTipo(tipo?: string): string {
  if (!tipo) return "Sensor";
  return TIPOS[tipo]?.sensor ?? legible(tipo);
}

/** Qué ocurrió cuando el sensor generó una alerta. */
export function nombreAlerta(tipo?: string): string {
  if (!tipo) return "Alerta";
  return TIPOS[tipo]?.alerta ?? `Alerta de ${nombreTipo(tipo).toLowerCase()}`;
}

/** Descripción de una lectura: evento ≠ alerta. Solo las alertas dicen que algo pasó. */
export function describirEvento(e: { tipo: string; alerta?: boolean; caida_detectada?: boolean; valor?: Record<string, any> }): string {
  if (e.alerta || e.caida_detectada) return nombreAlerta(e.tipo);
  const v = e.valor ?? {};
  switch (e.tipo) {
    case "pir":
    case "movimiento":
      return v.movimiento ? "Movimiento detectado" : "Sin movimiento";
    case "apertura":
      return v.abierto ? "Puerta o ventana abierta" : "Puerta o ventana cerrada";
    case "acelerometro":
      return "Sin caídas";
    case "humo":
      return "Sin humo";
    case "gas":
      return "Sin gas";
    case "cardiovascular":
      return "Ritmo cardíaco normal";
    case "boton_panico":
      return "Botón sin presionar";
    default:
      return `${nombreTipo(e.tipo)}: lectura normal`;
  }
}

export function iconoTipo(tipo?: string): LucideIcon {
  return (tipo && TIPOS[tipo]?.icono) || Gauge;
}

// Inventario instalado en el hogar p001 (los 8 sensores del proyecto).
// El estado se calcula con las lecturas; un identificador fuera de esta lista
// (por ejemplo, el de un script de prueba) no cuenta como sensor del hogar.
export const SENSORES_HOGAR: Array<{ sensor_id: string; tipo: string; habitacion: string }> = [
  { sensor_id: "acelerometro_dormitorio", tipo: "acelerometro", habitacion: "dormitorio" },
  { sensor_id: "pir_living", tipo: "pir", habitacion: "living" },
  { sensor_id: "gas_cocina", tipo: "gas", habitacion: "cocina" },
  { sensor_id: "humo_cocina", tipo: "humo", habitacion: "cocina" },
  { sensor_id: "apertura_puerta_principal", tipo: "apertura", habitacion: "entrada" },
  { sensor_id: "apertura_ventana_living", tipo: "apertura", habitacion: "living" },
  { sensor_id: "wearable_cardiaco", tipo: "cardiovascular", habitacion: "wearable" },
  { sensor_id: "boton_panico_sala", tipo: "boton_panico", habitacion: "sala" },
];

/** Un sensor está activo si envió una lectura en la última hora. */
export const MINUTOS_SENSOR_ACTIVO = 60;

export function inventarioSensores(
  lecturas: Array<{ sensor_id: string; ultima_lectura: string }>,
  ahora: number = Date.now()
): Array<{ sensor_id: string; tipo: string; habitacion: string; ultima_lectura: string; online: boolean }> {
  return SENSORES_HOGAR.map((s) => {
    const l = lecturas.find((x) => x.sensor_id === s.sensor_id);
    const ultima = l?.ultima_lectura ?? "";
    const online = !!ultima && ahora - new Date(ultima).getTime() <= MINUTOS_SENSOR_ACTIVO * 60000;
    return { ...s, ultima_lectura: ultima, online };
  });
}

export function nombreHabitacion(h?: string): string {
  if (!h) return "Sin ubicación";
  return legible(h);
}

const COMPONENTES: Array<[RegExp, LucideIcon, string]> = [
  [/raspberry/i, Cpu, "Equipo del hogar"],
  [/api/i, Server, "Servidor"],
  [/postgres|sqlite|supabase/i, Database, "Base de datos"],
  [/mqtt/i, RadioTower, "Red de sensores"],
  [/ntfy/i, Smartphone, "Avisos al celular"],
];

export function componenteSistema(nombre: string): { icono: LucideIcon; nombre: string; detalle: string } {
  for (const [re, icono, claro] of COMPONENTES) {
    if (re.test(nombre)) return { icono, nombre: claro, detalle: nombre };
  }
  return { icono: Server, nombre, detalle: nombre };
}

export function haceCuanto(fecha: string | Date | undefined, ahora: number = Date.now()): string {
  if (!fecha) return "sin lecturas";
  const t = new Date(fecha).getTime();
  const min = Math.round((ahora - t) / 60000);
  if (min < 1) return "hace un momento";
  if (min < 60) return `hace ${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `hace ${h} h`;
  return new Date(fecha).toLocaleDateString("es-CL", { day: "numeric", month: "short" });
}

export function hora(fecha: string | Date): string {
  return new Date(fecha).toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
}

export function esHoy(fecha: string | Date, ahora = new Date()): boolean {
  const f = new Date(fecha);
  return f.getDate() === ahora.getDate() && f.getMonth() === ahora.getMonth() && f.getFullYear() === ahora.getFullYear();
}
