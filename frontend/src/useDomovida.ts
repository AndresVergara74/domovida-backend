// src/useDomovida.ts
// Hook personalizado que conecta el dashboard con el backend

import { useState, useEffect, useRef } from "react";
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

// pausado = true mientras las lecturas están protegidas y no hay sesión (HU-17):
// así el panel no consulta cada 10 s para recibir solo respuestas 401.
export function useDomovida(pausado: boolean = false) {
  const pausadoRef = useRef(pausado);
  pausadoRef.current = pausado;
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [sensores, setSensores] = useState<SensorEstado[]>([]);
  const [minutosInactivo, setMinutosInactivo] = useState<number>(0);
  const [cargando, setCargando] = useState(true);
  const [conectado, setConectado] = useState(false);

  async function cargarTodo() {
    if (pausadoRef.current) {
      setConectado(await verificarConexion());
      setCargando(false);
      return;
    }
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

  // Al iniciar sesión se carga de inmediato, sin esperar el próximo ciclo
  useEffect(() => {
    if (!pausado) cargarTodo();
  }, [pausado]);

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
