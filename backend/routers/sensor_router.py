"""
Router para recibir datos de sensores IoT.
Integra notificaciones automáticas vía ntfy.sh cuando hay alertas.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import SensorDataIn, EventoOut
from notifier import enviar_notificacion

router = APIRouter()


@router.post("/sensor-data", response_model=EventoOut, status_code=201)
def recibir_datos_sensor(datos: SensorDataIn, db: Session = Depends(get_db)):
    """
    Recibe los datos de un sensor, los guarda en la base de datos
    y envía una notificación push si el evento contiene alerta=True.
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

    # 2. Si es una alerta, enviar notificación push
    if datos.alerta:
        try:
            enviar_notificacion({
                "sensor_id": datos.sensor_id,
                "tipo": datos.tipo,
                "habitacion": datos.habitacion,
                "valor": datos.valor,
                "alerta": datos.alerta,
            })
        except Exception as e:
            # La notificación no debe romper el flujo del backend
            print(f"⚠️ Error al enviar notificación: {e}")

    return evento