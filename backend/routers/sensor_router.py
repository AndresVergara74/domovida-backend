"""
Router para recibir datos de sensores.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Evento, Sensor
from schemas import SensorDataIn, EventoOut
from datetime import datetime

router = APIRouter()


@router.post("/sensor-data", response_model=EventoOut, status_code=201)
def recibir_datos_sensor(data: SensorDataIn, db: Session = Depends(get_db)):
    """Recibe datos de un sensor y los almacena como evento."""
    # Registrar o actualizar el sensor
    sensor = db.query(Sensor).filter(Sensor.sensor_id == data.sensor_id).first()
    if not sensor:
        sensor = Sensor(
            sensor_id=data.sensor_id,
            tipo=data.tipo,
            habitacion=data.habitacion,
        )
        db.add(sensor)

    # Crear el evento
    evento = Evento(
        sensor_id=data.sensor_id,
        tipo=data.tipo,
        habitacion=data.habitacion,
        valor=data.valor,
        alerta=data.alerta,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    return evento