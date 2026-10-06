"""
Modelos de base de datos para DomoVida.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from tiempo import ahora_utc
from database import Base


class Sensor(Base):
    """Tabla de sensores registrados."""
    __tablename__ = "sensores"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, unique=True, index=True)
    tipo = Column(String)  # acelerometro, pir, gas, humo, apertura
    habitacion = Column(String)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), default=ahora_utc)


class Evento(Base):
    """Tabla de eventos capturados por los sensores."""
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    tipo = Column(String)
    habitacion = Column(String)
    valor = Column(JSON)  # Datos específicos del sensor
    alerta = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), default=ahora_utc, index=True)

    # ============================================================
    # CAMPOS PARA GESTIÓN DE ALERTAS
    # ============================================================
    # Estos campos permiten saber si una alerta fue atendida
    # por el cuidador y quién la resolvió.
    # ============================================================
    resuelto = Column(Boolean, default=False, index=True)
    resuelto_en = Column(DateTime(timezone=True), nullable=True)
    resuelto_por = Column(String(100), nullable=True)