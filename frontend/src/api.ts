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
  mensaje?: string;
  severidad?: "baja" | "media" | "alta" | "critica";
  habitacion?: string;
  sensor_id?: string;
  valor?: Record<string, any>;
  alerta?: boolean;
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
 * Obtiene el estado de los sensores derivado de los últimos eventos.
 * Cada sensor único (por sensor_id) aparece una vez, con su última lectura.
 */
export async function obtenerSensores(): Promise<SensorEstado[]> {
  try {
    const eventos = await obtenerEventos(200);
    const mapaSensores = new Map<string, SensorEstado>();

    for (const evento of eventos) {
      if (!mapaSensores.has(evento.sensor_id)) {
        mapaSensores.set(evento.sensor_id, {
          sensor_id: evento.sensor_id,
          tipo: evento.tipo,
          habitacion: evento.habitacion || "desconocida",
          ultima_lectura: evento.timestamp,
          online: true,
        });
      }
    }

    return Array.from(mapaSensores.values());
  } catch (error) {
    console.error("Error al obtener sensores:", error);
    return [];
  }
}

/**
 * Obtiene los minutos de inactividad desde el último evento PIR
 */
export async function obtenerInactividad(): Promise<number> {
  try {
    const eventos = await obtenerEventos(50);
    const eventosPIR = eventos
      .filter((e) => e.tipo === "pir" && e.valor?.movimiento === true)
      .sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

    if (eventosPIR.length === 0) return 0;

    const ultimaActividad = eventosPIR[0];
    const minutos = Math.floor(
      (Date.now() - new Date(ultimaActividad.timestamp).getTime()) / 60000
    );

    return minutos;
  } catch (error) {
    console.error("Error al obtener inactividad:", error);
    return 0;
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