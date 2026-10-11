"""
Router para consultar eventos.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Evento
from schemas import EventoOut
from typing import List, Optional
from datetime import datetime, timedelta
from tiempo import ahora_utc, a_utc
from auth_cuidador import verificar_lectura

router = APIRouter()


@router.get("/eventos/resumen", dependencies=[Depends(verificar_lectura)])  # HU-17
def resumen_actividad(
    horas: int = Query(12, ge=1, le=48, description="Horas hacia atrás del gráfico"),
    hoy_desde: Optional[datetime] = Query(None, description="Medianoche local del cuidador (ISO 8601)"),
    db: Session = Depends(get_db)
):
    """Conteo real de lecturas y alertas para el gráfico «Actividad de hoy» (ajuste 21).

    Antes el panel contaba solo las últimas 50 lecturas descargadas y mostraba
    «0 alertas» aunque hubiera habido una caída horas antes (hallazgo del ensayo SUS).
    Se cuenta en Python para que funcione igual en Supabase (nube) y en SQLite (borde).
    """
    ahora = ahora_utc()
    fin = ahora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    inicio = fin - timedelta(hours=horas)
    buckets = [{"inicio": (inicio + timedelta(hours=k)).isoformat(), "lecturas": 0, "alertas": 0}
               for k in range(horas)]
    filas = (db.query(Evento.timestamp, Evento.alerta)
               .filter(Evento.timestamp >= inicio).all())
    for ts, alerta in filas:
        ts = a_utc(ts)
        k = int((ts - inicio).total_seconds() // 3600)
        if 0 <= k < horas:
            buckets[k]["alertas" if alerta else "lecturas"] += 1

    desde = a_utc(hoy_desde) if hoy_desde else ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    lecturas_hoy = db.query(Evento).filter(Evento.timestamp >= desde).count()
    alertas_hoy = (db.query(Evento.sensor_id, Evento.timestamp)
                     .filter(Evento.timestamp >= desde, Evento.alerta.is_(True))
                     .order_by(Evento.timestamp.asc()).limit(500).all())
    return {
        "horas": buckets,
        "lecturas_hoy": lecturas_hoy,
        "alertas_hoy": [{"sensor_id": sid, "timestamp": a_utc(ts).isoformat()} for sid, ts in alertas_hoy],
    }


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
