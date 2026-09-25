"""
Router para recibir datos de sensores IoT.

Integra:
- Persistencia en base de datos
- Notificaciones push vía ntfy.sh
- Notificaciones en tiempo real vía WebSocket
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import SensorDataIn, EventoOut
from notifier import enviar_notificacion

# Importar la función de notificación desde el manager compartido
from websocket_manager import notificar_alerta

router = APIRouter()


@router.post("/sensor-data", response_model=EventoOut, status_code=201)
async def recibir_datos_sensor(datos: SensorDataIn, db: Session = Depends(get_db)):
    """
    Recibe los datos de un sensor, los guarda en la base de datos
    y envía notificaciones si el evento contiene alerta=True.
    
    Flujo:
    1. Guardar evento en BD (SQLite/Supabase)
    2. Si alerta=True → notificar a ntfy.sh (push)
    3. Si alerta=True → notificar a WebSocket (tiempo real)
    """
    # 1. Guardar el evento en la base de datos
    evento = Evento(
        sensor_id=datos.sensor_id,
        tipo=datos.tipo,
        habitacion=datos.habitacion,
        valor=datos.valor,
        alerta=datos.alerta,
        timestamp=datos.timestamp,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    # 2. Si es una alerta, enviar notificaciones
    if datos.alerta:
        evento_dict = {
            "id": evento.id,
            "sensor_id": datos.sensor_id,
            "tipo": datos.tipo,
            "habitacion": datos.habitacion,
            "valor": datos.valor,
            "alerta": datos.alerta,
            "timestamp": datos.timestamp.isoformat() if datos.timestamp else None,
        }

        # 2a. Notificación push vía ntfy
        try:
            enviar_notificacion(evento_dict)
        except Exception as e:
            print(f"⚠️ Error al enviar notificación ntfy: {e}")

        # 2b. Notificación en tiempo real vía WebSocket
        try:
            await notificar_alerta(evento_dict)
        except Exception as e:
            print(f"⚠️ Error al enviar notificación WebSocket: {e}")

    return evento