// src/useWebSocket.ts
// Hook personalizado para conectar al WebSocket de DomoVida
// y recibir alertas en tiempo real.

import { useEffect, useRef, useState, useCallback } from "react";

// Tipo de alerta recibida por WebSocket
export interface AlertaWebSocket {
  id: number;
  sensor_id?: string;
  tipo: string;
  habitacion?: string;
  valor?: Record<string, any>;
  alerta?: boolean;
  mensaje?: string;
  severidad?: "baja" | "media" | "alta" | "critica";
  timestamp: string;
}

interface MensajeWebSocket {
  tipo: "bienvenida" | "pong" | "alerta";
  data?: AlertaWebSocket;
  mensaje?: string;
  timestamp: string;
}

export function useWebSocket() {
  const [conectado, setConectado] = useState(false);
  const [ultimaAlerta, setUltimaAlerta] = useState<AlertaWebSocket | null>(null);
  const [alertasTiempoReal, setAlertasTiempoReal] = useState<AlertaWebSocket[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // URL del WebSocket (configurable desde .env)
  const WS_URL =
    import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/ws/alertas";

  const conectar = useCallback(() => {
    // Si ya hay una conexión, no hacer nada
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    console.log("🔌 Conectando al WebSocket...");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("✅ WebSocket conectado");
      setConectado(true);

      // Enviar ping cada 30 segundos para mantener la conexión
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send("ping");
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const mensaje: MensajeWebSocket = JSON.parse(event.data);

        if (mensaje.tipo === "alerta" && mensaje.data) {
          console.log("🚨 Alerta recibida:", mensaje.data);

          // Guardar la última alerta
          setUltimaAlerta(mensaje.data);

          // Agregar al historial de alertas en tiempo real
          setAlertasTiempoReal((prev) => [mensaje.data!, ...prev].slice(0, 50));
        } else if (mensaje.tipo === "bienvenida") {
          console.log("📩 Bienvenida:", mensaje.mensaje);
        } else if (mensaje.tipo === "pong") {
          // Ping/pong OK
        }
      } catch (error) {
        console.error("❌ Error al parsear mensaje WebSocket:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("❌ Error en WebSocket:", error);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket desconectado");
      setConectado(false);

      // Limpiar el intervalo de ping
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }

      // Intentar reconectar después de 5 segundos
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log("🔄 Intentando reconectar...");
        conectar();
      }, 5000);
    };

    wsRef.current = ws;
  }, [WS_URL]);

  useEffect(() => {
    conectar();

    // Limpiar al desmontar
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [conectar]);

  // Función para limpiar las alertas de tiempo real
  const limpiarAlertas = useCallback(() => {
    setAlertasTiempoReal([]);
  }, []);

  return {
    conectado,
    ultimaAlerta,
    alertasTiempoReal,
    limpiarAlertas,
  };
}