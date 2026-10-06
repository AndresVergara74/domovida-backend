"""
Gestión de alertas: la tabla `alertas` es la fuente única de verdad (ajuste 17,
ficha técnica 19, etapa 3).

- registrar_alerta: crea la alerta de un evento en la misma transacción.
  Si ya existe (por ejemplo, creada por el trigger antiguo de Supabase
  antes de aplicar la migración 002), la reutiliza y no la duplica.
- resolver: marca la alerta como atendida y copia el dato a las columnas
  obsoletas de `eventos` para que el panel actual siga funcionando.
"""
from typing import Optional
from sqlalchemy.orm import Session

from models import Alerta, Evento
from tiempo import ahora_utc

# Misma regla que tenía el trigger crear_alerta_automatica (ficha técnica 11, PI-02)
TIPOS_CRITICOS = {"acelerometro", "cardiovascular", "boton_panico", "gas", "humo"}


def severidad(tipo: Optional[str]) -> str:
    return "critica" if tipo in TIPOS_CRITICOS else "alta"


def alerta_de_evento(db: Session, evento_id: int) -> Optional[Alerta]:
    return (
        db.query(Alerta)
        .filter(Alerta.evento_id == evento_id)
        .order_by(Alerta.id)
        .first()
    )


def registrar_alerta(db: Session, evento: Evento) -> Alerta:
    """Crea (o reutiliza) la alerta del evento. Requiere que el evento ya tenga id (flush)."""
    existente = alerta_de_evento(db, evento.id)
    if existente:
        return existente
    alerta = Alerta(
        evento_id=evento.id,
        tipo_alerta=evento.tipo,
        nivel_severidad=severidad(evento.tipo),
        payload_fhir=evento.valor,
        resuelto=bool(evento.resuelto),
        resuelto_en=evento.resuelto_en,
        resuelto_por=evento.resuelto_por,
        creado_en=ahora_utc(),
    )
    db.add(alerta)
    db.flush()
    return alerta


def resolver(db: Session, evento: Evento, alerta: Alerta, cuidador: str) -> Alerta:
    """Marca la alerta como atendida (fuente de verdad) y copia el dato al evento."""
    momento = ahora_utc()
    alerta.resuelto = True
    alerta.resuelto_en = momento
    alerta.resuelto_por = cuidador
    # Copia de compatibilidad (columnas obsoletas de eventos)
    evento.resuelto = True
    evento.resuelto_en = momento
    evento.resuelto_por = cuidador
    return alerta
