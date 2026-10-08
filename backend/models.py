"""
Modelos de base de datos para DomoVida.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey
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

    # HU-03 · Sincronización del modo borde (migración 003)
    uuid = Column(String(36), unique=True, nullable=True, index=True)  # id generado en el origen
    origen = Column(String(10), default="nube")      # borde | nube
    sync_status = Column(String, nullable=True)       # pendiente | synced
    notificado = Column(Boolean, default=False)       # ntfy ya enviado (evita avisos repetidos)

    # ============================================================
    # CAMPOS DE ATENCIÓN (OBSOLETOS · ajuste 17, ficha 19 etapa 3)
    # ============================================================
    # La fuente de verdad de la atención es la tabla `alertas`.
    # Estas columnas se siguen copiando por compatibilidad con el panel
    # y se eliminarán en una migración posterior.
    # ============================================================
    resuelto = Column(Boolean, default=False, index=True)
    resuelto_en = Column(DateTime(timezone=True), nullable=True)
    resuelto_por = Column(String(100), nullable=True)


class Alerta(Base):
    """Alerta generada por un evento: fuente única de verdad de su atención (ajuste 17).

    En Supabase existía el trigger `crear_alerta_automatica`; desde la migración 002
    la alerta la crea el backend, así que también existe en SQLite (modo borde).
    """
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    tipo_alerta = Column(String, nullable=False)
    nivel_severidad = Column(String, nullable=False)  # critica | alta
    payload_fhir = Column(JSON)
    resuelto = Column(Boolean, default=False)
    resuelto_en = Column(DateTime(timezone=True), nullable=True)
    resuelto_por = Column(String, nullable=True)
    notas_resolucion = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), default=ahora_utc)
