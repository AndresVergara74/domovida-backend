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

  async function cargarTodo() {
    const [ev, al, se] = await Promise.all([
      obtenerEventos(50),
      obtenerAlertasActivas(),
      obtenerInactividad(),
    ]);
    setEventos(ev);
    setAlertas(al);
    setSensores(se);
    setCargando(false);
  }

  useEffect(() => {
    cargarTodo();
    const intervalo = setInterval(cargarTodo, 10000); // cada 10s
    return () => clearInterval(intervalo);
  }, []);

  return { eventos, alertas, sensores, cargando, refrescar: cargarTodo };
}