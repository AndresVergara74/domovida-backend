"""
Schemas Pydantic para validación de datos.
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Dict, Any

from tiempo import a_utc, entrada_a_utc


class SensorDataIn(BaseModel):
    """Datos entrantes de un sensor."""
    sensor_id: str
    tipo: str
    habitacion: str
    valor: Dict[str, Any]
    alerta: bool = False
    timestamp: Optional[datetime] = None

    @field_validator("timestamp")
    @classmethod
    def _timestamp_utc(cls, v):
        # Sin zona = hora de Chile (dispositivo en el hogar); se guarda en UTC
        return entrada_a_utc(v)


class EventoOut(BaseModel):
    """Datos de salida de un evento."""
    id: int
    sensor_id: str
    tipo: str
    habitacion: str
    valor: Dict[str, Any]
    alerta: bool
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def _salida_utc(cls, v):
        # Siempre se entrega con zona (+00:00) para que el panel convierta a hora de Chile
        return a_utc(v)

    class Config:
        from_attributes = True