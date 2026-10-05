"""
Router para recibir datos de sensores IoT.

Integra:
- Persistencia en base de datos
- Notificaciones push vía ntfy.sh
- Notificaciones en tiempo real vía WebSocket
"""
import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import SensorDataIn, EventoOut
from notifier import enviar_notificacion

# Importar la función de notificación desde el manager compartido
from websocket_manager import notificar_alerta

from reglas_puerta import evaluar_puerta
from seguridad import verificar_clave_sensor

router = APIRouter()


@router.post(
    "/sensor-data",
    response_model=EventoOut,
    status_code=201,
    dependencies=[Depends(verificar_clave_sensor)],  # PS-01
)
async def recibir_datos_sensor(datos: SensorDataIn, db: Session = Depends(get_db)):
    """
    Recibe los datos de un sensor, los guarda en la base de datos
    y envía notificaciones si el evento contiene alerta=True.
    
    Flujo:
    1. Guardar evento en BD (SQLite/Supabase)
    2. Si alerta=True → notificar a ntfy.sh (push)
    3. Si alerta=True → notificar a WebSocket (tiempo real)
    """
    # 0. Regla de la puerta principal (la decide el backend, no el sensor):
    #    alerta si se abre de noche o si queda abierta 10 minutos o más.
    if datos.tipo == "apertura" and datos.habitacion == "entrada":
        valor = dict(datos.valor or {})
        alerta, motivo, minutos = evaluar_puerta(
            datos.sensor_id, bool(valor.get("abierto")), datos.timestamp
        )
        if motivo:
            valor["motivo"] = motivo
        if minutos:
            valor["minutos_abierta"] = minutos
        datos.valor = valor
        datos.alerta = alerta

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

        # 2a. Notificación en tiempo real vía WebSocket (primero: es el canal más rápido)
        try:
            await notificar_alerta(evento_dict)
        except Exception as e:
            print(f"⚠️ Error al enviar notificación WebSocket: {e}")

        # 2b. Notificación push vía ntfy en segundo plano (no bloquea la respuesta).
        # Ajuste PR-01 (02-10-2026): antes ntfy se enviaba primero y el WebSocket
        # esperaba a que terminara la llamada HTTP a ntfy.sh.
        asyncio.get_running_loop().run_in_executor(None, _enviar_ntfy_seguro, evento_dict)

    return evento


def _enviar_ntfy_seguro(evento_dict: dict) -> None:
    """Envía la notificación ntfy capturando errores (se ejecuta en un hilo aparte)."""
    try:
        enviar_notificacion(evento_dict)
    except Exception as e:
        print(f"⚠️ Error al enviar notificación ntfy: {e}")
