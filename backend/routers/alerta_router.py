"""
Router para consultar y gestionar alertas.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import or_, and_
from models import Evento, Alerta
from alertas_servicio import alerta_de_evento, registrar_alerta, resolver as resolver_en_bd
from schemas import EventoOut
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from auth_cuidador import verificar_cuidador
from tiempo import ahora_utc, a_utc

router = APIRouter()


# ============================================================
# SCHEMAS ADICIONALES
# ============================================================
class ResolverAlertaIn(BaseModel):
    """Datos para marcar una alerta como resuelta."""
    resuelto_por: str = "Cuidador DomoVida"


class AlertaResueltaOut(BaseModel):
    """Respuesta al resolver una alerta."""
    id: int
    resuelto: bool
    resuelto_en: str
    resuelto_por: str
    mensaje: str


# ============================================================
# ENDPOINTS DE ALERTAS
# ============================================================

@router.get("/alertas/activas", response_model=List[EventoOut])
def alertas_activas(db: Session = Depends(get_db)):
    """
    Devuelve las alertas ACTIVAS (no resueltas).
    
    Filtros aplicados:
    - alerta = TRUE (es una alerta)
    - no atendida según la tabla `alertas` (fuente de verdad, ajuste 17).
      Si un evento antiguo no tiene fila en `alertas` (base local previa),
      se usa la columna obsoleta de `eventos`.
    - timestamp >= ahora - 24h (últimas 24 horas)
    """
    hace_24h = ahora_utc() - timedelta(hours=24)
    return (
        db.query(Evento)
        .outerjoin(Alerta, Alerta.evento_id == Evento.id)
        .filter(
            Evento.alerta == True,
            or_(
                Alerta.resuelto == False,
                and_(Alerta.id == None, Evento.resuelto == False),
            ),
            Evento.timestamp >= hace_24h,
        )
        .order_by(Evento.timestamp.desc())
        .all()
    )


@router.get("/alertas/inactividad")
def alertas_inactividad(db: Session = Depends(get_db)):
    """Devuelve el estado de los sensores PIR con su nivel de inactividad."""
    sensores = (
        db.query(Evento.sensor_id, Evento.habitacion)
        .filter(Evento.tipo == "pir")
        .distinct()
        .all()
    )

    resultado = []
    for sensor_id, habitacion in sensores:
        ultima = (
            db.query(Evento)
            .filter(Evento.sensor_id == sensor_id, Evento.tipo == "pir")
            .order_by(Evento.timestamp.desc())
            .first()
        )

        if ultima:
            segundos_inactivo = (ahora_utc() - a_utc(ultima.timestamp)).total_seconds()
            horas_inactivo = segundos_inactivo / 3600

            resultado.append({
                "sensor_id": sensor_id,
                "tipo": "pir",
                "habitacion": habitacion or "sin_habitacion",
                "ultima_lectura": a_utc(ultima.timestamp).isoformat(),
                "online": horas_inactivo < 12,
            })

    return resultado


# ============================================================
# RESOLVER ALERTA
# ============================================================

@router.patch("/alertas/{alerta_id}/resolver")
def resolver_alerta(
    alerta_id: int,
    datos: ResolverAlertaIn,
    db: Session = Depends(get_db),
    cuidador: Optional[str] = Depends(verificar_cuidador),  # PS-01: sesión del cuidador
):
    """
    Marca una alerta como resuelta (atendida por el cuidador).

    `alerta_id` es el id del evento que generó la alerta (el que muestra el panel).
    La atención se registra en la tabla `alertas` (fuente única de verdad,
    ajuste 17) y se copia a las columnas obsoletas de `eventos` en la misma
    transacción.
    """
    try:
        evento = (
            db.query(Evento)
            .filter(Evento.id == alerta_id, Evento.alerta == True)
            .first()
        )
        if not evento:
            raise HTTPException(
                status_code=404,
                detail=f"Alerta {alerta_id} no encontrada o ya fue resuelta",
            )

        alerta = alerta_de_evento(db, evento.id) or registrar_alerta(db, evento)
        if alerta.resuelto:
            raise HTTPException(
                status_code=404,
                detail=f"Alerta {alerta_id} no encontrada o ya fue resuelta",
            )

        # Con sesión iniciada se registra el correo del cuidador (trazabilidad)
        resolver_en_bd(db, evento, alerta, cuidador or datos.resuelto_por)
        db.commit()
        db.refresh(alerta)

        return {
            "id": evento.id,
            "alerta_id": alerta.id,
            "resuelto": True,
            "resuelto_en": a_utc(alerta.resuelto_en).isoformat(),
            "resuelto_por": alerta.resuelto_por,
            "mensaje": f"Alerta {alerta_id} marcada como resuelta por {alerta.resuelto_por}",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al resolver la alerta: {str(e)[:100]}",
        )