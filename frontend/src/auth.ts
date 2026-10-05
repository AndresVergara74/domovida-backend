// src/auth.ts
// PS-01 (parte 2): inicio de sesión del cuidador con Supabase Auth.
// Usa la API REST de Supabase Auth directamente (sin dependencias nuevas).
// La URL del proyecto y la clave pública (anon) son datos públicos por diseño;
// la protección real está en la contraseña del cuidador y en que el backend
// valida el token antes de permitir marcar una alerta como atendida.

const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL as string | undefined)?.replace(/\/+$/, "");
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

// Si no hay configuración (por ejemplo, en modo borde sin internet), el panel funciona sin inicio de sesión.
export const authHabilitada = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

export interface Sesion {
  token: string;
  email: string;
  expira: number; // milisegundos desde 1970
}

const CLAVE_SESION = "domovida-sesion";

export function leerSesion(): Sesion | null {
  try {
    const s = JSON.parse(sessionStorage.getItem(CLAVE_SESION) || "null") as Sesion | null;
    if (s && s.token && s.expira > Date.now()) return s;
  } catch {
    // sin acceso a sessionStorage: se trata como sesión cerrada
  }
  return null;
}

export function cerrarSesion(): void {
  try {
    sessionStorage.removeItem(CLAVE_SESION);
  } catch {
    // nada que limpiar
  }
}

export async function iniciarSesion(email: string, password: string): Promise<Sesion> {
  if (!authHabilitada) throw new Error("El inicio de sesión no está configurado");
  const r = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
    method: "POST",
    headers: { "Content-Type": "application/json", apikey: SUPABASE_ANON_KEY as string },
    body: JSON.stringify({ email, password }),
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok || !datos.access_token) {
    throw new Error("Correo o contraseña incorrectos");
  }
  const sesion: Sesion = {
    token: datos.access_token,
    email: datos.user?.email ?? email,
    // se renueva un minuto antes de que expire el token
    expira: Date.now() + Math.max(60, (datos.expires_in ?? 3600) - 60) * 1000,
  };
  try {
    sessionStorage.setItem(CLAVE_SESION, JSON.stringify(sesion));
  } catch {
    // si no se puede guardar, la sesión dura mientras la página esté abierta
  }
  return sesion;
}
