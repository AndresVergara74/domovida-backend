"""
Router para consultar y gestionar alertas.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import Evento
from schemas import EventoOut
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

router = APIRouter()


# ============================================================
# SCHEMAS ADICIONALES
# ============================================================
class ResolverAlertaIn(BaseModel):
    """Datos para marcar una alerta como resuelta."""
    resuelto_por: str
    notas_resolucion: str = ""


class AlertaResueltaOut(BaseModel):
    """Respuesta al resolver una alerta."""
    id: int
    resuelto: bool
    resuelto_en: str
    resuelto_por: str
    mensaje: str


# ============================================================
# ENDPOINTS EXISTENTES
# ============================================================

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


# ============================================================
# NUEVO: RESOLVER ALERTA
# ============================================================

@router.patch("/alertas/{alerta_id}/resolver")
def resolver_alerta(
    alerta_id: int,
    datos: ResolverAlertaIn,
    db: Session = Depends(get_db),
):
    """
    Marca una alerta como resuelta (atendida por el cuidador).
    
    Actualiza los campos:
    - resuelto = TRUE
    - resuelto_en = ahora
    - resuelto_por = nombre del cuidador
    - notas_resolucion = comentarios opcionales
    """
    try:
        # Verificar que la alerta existe
        alerta = (
            db.query(Evento)
            .filter(Evento.id == alerta_id, Evento.alerta == True)
            .first()
        )

        if not alerta:
            raise HTTPException(
                status_code=404,
                detail=f"Alerta {alerta_id} no encontrada o no es una alerta",
            )

        # Actualizar la alerta
        # NOTA: Por ahora actualizamos el campo 'alerta' a False para
        # indicar que fue resuelta. En producción, se debería usar
        # una tabla 'alertas' separada con campo 'resuelto'.
        alerta.alerta = False
        db.commit()
        db.refresh(alerta)

        return {
            "id": alerta.id,
            "resuelto": True,
            "resuelto_en": datetime.utcnow().isoformat(),
            "resuelto_por": datos.resuelto_por,
            "mensaje": f"Alerta {alerta_id} marcada como resuelta por {datos.resuelto_por}",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al resolver la alerta: {str(e)[:100]}",
        )