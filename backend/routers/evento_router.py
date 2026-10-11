"""
Router para consultar eventos.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import EventoOut
from typing import List, Optional
from datetime import datetime
from auth_cuidador import verificar_lectura

router = APIRouter()


@router.get("/eventos", response_model=List[EventoOut], dependencies=[Depends(verificar_lectura)])  # HU-17
def listar_eventos(
    sensor_id: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None, description="Tipo de sensor, ej. acelerometro"),
    habitacion: Optional[str] = Query(None),
    solo_alertas: bool = Query(False, description="Solo lecturas que generaron alerta"),
    sin_alertas: bool = Query(False, description="Solo lecturas normales"),
    desde: Optional[datetime] = Query(None, description="Fecha/hora mínima (ISO 8601)"),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db)
):
    """Lista los últimos eventos con filtros opcionales.

    Los filtros se aplican en el servidor (ajuste 20): con el simulador enviando
    8 lecturas cada pocos segundos, filtrar solo las últimas 50 en el panel dejaba
    fuera las alertas de hace unos minutos (hallazgo del ensayo SUS, tarea T4).
    """
    query = db.query(Evento)
    if sensor_id:
        query = query.filter(Evento.sensor_id == sensor_id)
    if tipo:
        query = query.filter(Evento.tipo == tipo)
    if habitacion:
        query = query.filter(Evento.habitacion == habitacion)
    if solo_alertas:
        query = query.filter(Evento.alerta.is_(True))
    elif sin_alertas:
        query = query.filter(Evento.alerta.isnot(True))
    if desde is not None:
        query = query.filter(Evento.timestamp >= desde)
    return query.order_by(Evento.timestamp.desc()).limit(limit).all()
