// src/useDomovida.ts
// Hook personalizado que conecta el dashboard con el backend

import { useState, useEffect } from "react";
import {
  obtenerEventos,
  obtenerAlertasActivas,
  obtenerInactividad,
  type Evento,
  type Alerta,
  type SensorEstado,
} from "./api";

export function useDomovida() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [sensores, setSensores] = useState<SensorEstado[]>([]);
  const [cargando, setCargando] = useState(true);
  const [conectado, setConectado] = useState(false);
  const [ultimaActualizacion, setUltimaActualizacion] = useState<Date | null>(null);

  async function cargarTodo() {
    try {
      const [ev, al, se] = await Promise.all([
        obtenerEventos(50),
        obtenerAlertasActivas(),
        obtenerInactividad(),
      ]);

      // Si llegamos aquí, la API respondió correctamente
      setEventos(ev);
      setAlertas(al);
      setSensores(se);
      setConectado(true);
      setUltimaActualizacion(new Date());
    } catch (error) {
      console.error("Error al cargar datos:", error);
      setConectado(false);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargarTodo();
    const intervalo = setInterval(cargarTodo, 10000); // cada 10s
    return () => clearInterval(intervalo);
  }, []);

  return {
    eventos,
    alertas,
    sensores,
    cargando,
    conectado,
    ultimaActualizacion,
    refrescar: cargarTodo,
  };
}