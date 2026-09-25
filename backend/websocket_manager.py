"""
Gestor de conexiones WebSocket para DomoVida.

Este módulo contiene el manager de conexiones y la función
notificar_alerta(), que puede ser importada desde cualquier
router sin causar importaciones circulares.
"""

from typing import List
import json
from datetime import datetime
from fastapi import WebSocket


# ============================================================
# GESTOR DE CONEXIONES WEBSOCKET
# ============================================================

class ConnectionManager:
    """
    Gestiona las conexiones WebSocket activas.
    
    Permite:
    - Conectar nuevos clientes
    - Desconectar clientes
    - Enviar mensajes a un cliente específico
    - Enviar mensajes a todos los clientes (broadcast)
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Acepta una nueva conexión WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 Cliente WebSocket conectado. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Elimina una conexión WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔌 Cliente WebSocket desconectado. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envía un mensaje a un cliente específico."""
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """
        Envía un mensaje a TODOS los clientes conectados.
        
        Si un cliente falla, se elimina automáticamente.
        """
        message_json = json.dumps(message, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"⚠️ Error al enviar a un cliente: {e}")
                disconnected.append(connection)

        # Limpiar conexiones fallidas
        for conn in disconnected:
            self.disconnect(conn)


# ============================================================
# INSTANCIA GLOBAL DEL MANAGER
# ============================================================

manager = ConnectionManager()


# ============================================================
# FUNCIÓN PARA NOTIFICAR ALERTAS
# ============================================================

async def notificar_alerta(alerta: dict):
    """
    Envía una alerta a todos los clientes WebSocket conectados.
    
    Esta función es llamada desde el sensor_router cuando se
    detecta un evento con alerta=True.
    """
    print(f"📡 Enviando alerta por WebSocket a {len(manager.active_connections)} clientes")

    if len(manager.active_connections) == 0:
        print("⚠️ No hay clientes WebSocket conectados")
        return

    await manager.broadcast({
        "tipo": "alerta",
        "data": alerta,
        "timestamp": datetime.utcnow().isoformat(),
    })