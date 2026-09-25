"""
Router de WebSocket para DomoVida.

Permite la comunicación en tiempo real entre el backend y el frontend.
Cuando ocurre una alerta, se envía inmediatamente a todos los clientes
conectados (cuidadores) sin necesidad de polling.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from datetime import datetime

# Importar el manager compartido (evita importaciones circulares)
from websocket_manager import manager

router = APIRouter()


# ============================================================
# ENDPOINT WEBSOCKET
# ============================================================

@router.websocket("/ws/alertas")
async def websocket_alertas(websocket: WebSocket):
    """
    Endpoint WebSocket para recibir alertas en tiempo real.
    
    Uso desde el frontend:
    const ws = new WebSocket("ws://localhost:8000/api/ws/alertas");
    ws.onmessage = (event) => {
        const alerta = JSON.parse(event.data);
        console.log("Alerta recibida:", alerta);
    };
    """
    await manager.connect(websocket)

    try:
        # Enviar mensaje de bienvenida
        await websocket.send_text(json.dumps({
            "tipo": "bienvenida",
            "mensaje": "Conectado al sistema de alertas en tiempo real",
            "timestamp": datetime.utcnow().isoformat(),
        }))

        # Mantener la conexión abierta
        while True:
            # Esperar mensajes del cliente (ping/pong)
            data = await websocket.receive_text()

            # Si el cliente envía "ping", respondemos "pong"
            if data == "ping":
                await websocket.send_text(json.dumps({
                    "tipo": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
        manager.disconnect(websocket)