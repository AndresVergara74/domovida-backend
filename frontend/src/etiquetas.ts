// src/etiquetas.ts
// Lenguaje del cuidador: nombres claros en vez de identificadores técnicos.
import {
  Activity, Footprints, Flame, CloudFog, DoorOpen, HeartPulse, Siren, Gauge,
  Cpu, Server, Database, RadioTower, Smartphone,
  type LucideIcon,
} from "lucide-react";

const TIPOS: Record<string, { nombre: string; icono: LucideIcon }> = {
  acelerometro: { nombre: "Caída", icono: Activity },
  pir: { nombre: "Movimiento", icono: Footprints },
  humo: { nombre: "Humo", icono: Flame },
  gas: { nombre: "Gas", icono: CloudFog },
  apertura: { nombre: "Puerta o ventana", icono: DoorOpen },
  cardiovascular: { nombre: "Ritmo cardíaco", icono: HeartPulse },
  boton_panico: { nombre: "Botón de pánico", icono: Siren },
};

export function nombreTipo(tipo?: string): string {
  return (tipo && TIPOS[tipo]?.nombre) || (tipo ?? "Sensor");
}

export function iconoTipo(tipo?: string): LucideIcon {
  return (tipo && TIPOS[tipo]?.icono) || Gauge;
}

export function nombreHabitacion(h?: string): string {
  if (!h) return "Sin ubicación";
  const limpio = h.replace(/_/g, " ");
  return limpio.charAt(0).toUpperCase() + limpio.slice(1);
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
  if (!fecha) return "sin datos";
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
