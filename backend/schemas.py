"""
Schemas Pydantic para validación de datos.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SensorDataIn(BaseModel):
    """Datos entrantes de un sensor."""
    sensor_id: str
    tipo: str
    habitacion: str
    valor: Dict[str, Any]
    alerta: bool = False
    timestamp: Optional[datetime] = None


class EventoOut(BaseModel):
    """Datos de salida de un evento."""
    id: int
    sensor_id: str
    tipo: str
    habitacion: str
    valor: Dict[str, Any]
    alerta: bool
    timestamp: datetime

    class Config:
        from_attributes = True