// src/api.ts
// Configuración de la API para DomoVida

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Evento {
  id: number;
  sensor_id: string;
  tipo: string;
  habitacion?: string;
  valor: Record<string, any>;
  alerta: boolean;
  caida_detectada?: boolean;
  timestamp: string;
}

export interface Alerta {
  id: number;
  tipo: string;
  mensaje: string;
  severidad: "baja" | "media" | "alta" | "critica";
  timestamp: string;
}

export interface SensorEstado {
  sensor_id: string;
  tipo: string;
  habitacion: string;
  ultima_lectura: string;
  online: boolean;
}

/**
 * Obtiene los últimos eventos registrados
 */
export async function obtenerEventos(limite: number = 50): Promise<Evento[]> {
  try {
    const response = await fetch(`${API_URL}/api/eventos?limite=${limite}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Error al obtener eventos:", error);
    return [];
  }
}

/**
 * Obtiene las alertas activas (últimas 24h)
 */
export async function obtenerAlertasActivas(): Promise<Alerta[]> {
  try {
    const response = await fetch(`${API_URL}/api/alertas/activas`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Error al obtener alertas:", error);
    return [];
  }
}

/**
 * Obtiene el estado de los sensores (para detectar inactividad)
 */
export async function obtenerInactividad(): Promise<SensorEstado[]> {
  try {
    const response = await fetch(`${API_URL}/api/alertas/inactividad`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Error al obtener inactividad:", error);
    return [];
  }
}

/**
 * Envía datos de un sensor (útil para pruebas desde el frontend)
 */
export async function enviarDatosSensor(datos: Partial<Evento>): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/sensor-data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    return response.ok;
  } catch (error) {
    console.error("Error al enviar datos:", error);
    return false;
  }
}