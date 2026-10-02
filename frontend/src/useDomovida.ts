// src/useDomovida.ts
// Hook personalizado que conecta el dashboard con el backend

import { useState, useEffect } from "react";
import {
  obtenerEventos,
  obtenerAlertasActivas,
  obtenerSensores,
  obtenerInactividad,
  verificarConexion,
  type Evento,
  type Alerta,
  type SensorEstado,
} from "./api";

export function useDomovida() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [sensores, setSensores] = useState<SensorEstado[]>([]);
  const [minutosInactivo, setMinutosInactivo] = useState<number>(0);
  const [cargando, setCargando] = useState(true);
  const [conectado, setConectado] = useState(false);

  async function cargarTodo() {
    const [ev, al, se, inac, ok] = await Promise.all([
      obtenerEventos(50),
      obtenerAlertasActivas(),
      obtenerSensores(),
      obtenerInactividad(),
      verificarConexion(),
    ]);
    setEventos(ev);
    setAlertas(al);
    setSensores(se);
    setMinutosInactivo(inac);
    setConectado(ok);
    setCargando(false);
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
    minutosInactivo,
    cargando,
    conectado,
    refrescar: cargarTodo,
  };
}
