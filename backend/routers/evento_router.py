"""
Router para consultar eventos.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import EventoOut
from typing import List, Optional

router = APIRouter()


@router.get("/eventos", response_model=List[EventoOut])
def listar_eventos(
    sensor_id: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db)
):
    """Lista los últimos eventos, opcionalmente filtrados por sensor."""
    query = db.query(Evento).order_by(Evento.timestamp.desc())
    if sensor_id:
        query = query.filter(Evento.sensor_id == sensor_id)
    return query.limit(limit).all()