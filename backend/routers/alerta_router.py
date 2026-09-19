"""
Router para consultar alertas.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import EventoOut
from datetime import datetime, timedelta
from typing import List

router = APIRouter()


@router.get("/alertas/activas", response_model=List[EventoOut])
def alertas_activas(db: Session = Depends(get_db)):
    """Eventos con alerta=True en las últimas 24 horas."""
    hace_24h = datetime.utcnow() - timedelta(hours=24)
    return (
        db.query(Evento)
        .filter(Evento.alerta == True, Evento.timestamp >= hace_24h)
        .order_by(Evento.timestamp.desc())
        .all()
    )


@router.get("/alertas/inactividad")
def alertas_inactividad(db: Session = Depends(get_db)):
    """Devuelve el estado de los sensores PIR con su nivel de inactividad."""
    hace_24h = datetime.utcnow() - timedelta(hours=24)

    # Obtener todos los sensores PIR únicos
    sensores = (
        db.query(Evento.sensor_id, Evento.habitacion)
        .filter(Evento.tipo == "pir")
        .distinct()
        .all()
    )

    resultado = []
    for sensor_id, habitacion in sensores:
        # Última lectura de este sensor
        ultima = (
            db.query(Evento)
            .filter(Evento.sensor_id == sensor_id, Evento.tipo == "pir")
            .order_by(Evento.timestamp.desc())
            .first()
        )

        if ultima:
            segundos_inactivo = (datetime.utcnow() - ultima.timestamp).total_seconds()
            horas_inactivo = segundos_inactivo / 3600

            resultado.append({
                "sensor_id": sensor_id,
                "tipo": "pir",
                "habitacion": habitacion or "sin_habitacion",
                "ultima_lectura": ultima.timestamp.isoformat(),
                "online": horas_inactivo < 12,
            })

    return resultado