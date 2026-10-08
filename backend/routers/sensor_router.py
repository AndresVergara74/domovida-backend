"""
Router para recibir datos de sensores IoT.

Integra:
- Persistencia en base de datos
- Notificaciones push vía ntfy.sh
- Notificaciones en tiempo real vía WebSocket
"""
import asyncio
import uuid as uuidlib

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
import sincronizador
from models import Evento
from schemas import SensorDataIn, EventoOut
from notifier import enviar_notificacion

# Importar la función de notificación desde el manager compartido
from alertas_servicio import registrar_alerta
from websocket_manager import notificar_alerta

from reglas_puerta import evaluar_puerta
from seguridad import verificar_clave_sensor

router = APIRouter()


@router.post(
    "/sensor-data",
    response_model=EventoOut,
    status_code=201,
    dependencies=[Depends(verificar_clave_sensor)],  # PS-01
)
async def recibir_datos_sensor(datos: SensorDataIn, db: Session = Depends(get_db)):
    """
    Recibe los datos de un sensor, los guarda en la base de datos
    y envía notificaciones si el evento contiene alerta=True.
    
    Flujo:
    1. Guardar evento en BD (SQLite/Supabase)
    2. Si alerta=True → notificar a ntfy.sh (push)
    3. Si alerta=True → notificar a WebSocket (tiempo real)
    """
    # 0a. HU-03: un evento que ya existe (mismo UUID) no se guarda dos veces
    if datos.uuid:
        existente = db.query(Evento).filter(Evento.uuid == datos.uuid).first()
        if existente:
            return existente

    # 0b. Regla de la puerta principal (la decide el backend, no el sensor):
    #    alerta si se abre de noche o si queda abierta 10 minutos o más.
    #    Un evento sincronizado desde el borde ya trae la regla aplicada.
    if datos.tipo == "apertura" and datos.habitacion == "entrada" and datos.origen != "borde":
        valor = dict(datos.valor or {})
        alerta, motivo, minutos = evaluar_puerta(
            datos.sensor_id, bool(valor.get("abierto")), datos.timestamp
        )
        if motivo:
            valor["motivo"] = motivo
        if minutos:
            valor["minutos_abierta"] = minutos
        datos.valor = valor
        datos.alerta = alerta

    # 1. Guardar el evento en la base de datos
    evento = Evento(
        sensor_id=datos.sensor_id,
        tipo=datos.tipo,
        habitacion=datos.habitacion,
        valor=datos.valor,
        alerta=datos.alerta,
        timestamp=datos.timestamp,
        # HU-03: en el borde el evento queda pendiente de subir a la nube
        uuid=datos.uuid or str(uuidlib.uuid4()),
        origen=datos.origen or ("borde" if sincronizador.sincronizacion_activa() else "nube"),
        sync_status="pendiente" if sincronizador.sincronizacion_activa() else None,
        notificado=bool(datos.notificado),
    )
    db.add(evento)
    db.flush()  # asigna el id del evento dentro de la transacción
    # 1b. Si es una alerta, se registra en la tabla alertas en la MISMA transacción
    #     (ajuste 17: alertas es la fuente única de verdad de la atención).
    if datos.alerta:
        registrar_alerta(db, evento)
    db.commit()
    db.refresh(evento)

    # 2. Si es una alerta, enviar notificaciones
    if datos.alerta:
        evento_dict = {
            "id": evento.id,
            "sensor_id": datos.sensor_id,
            "tipo": datos.tipo,
            "habitacion": datos.habitacion,
            "valor": datos.valor,
            "alerta": datos.alerta,
            "timestamp": datos.timestamp.isoformat() if datos.timestamp else None,
        }

        # 2a. Notificación en tiempo real vía WebSocket (primero: es el canal más rápido)
        try:
            await notificar_alerta(evento_dict)
        except Exception as e:
            print(f"⚠️ Error al enviar notificación WebSocket: {e}")

        # 2b. Notificación push vía ntfy en segundo plano (no bloquea la respuesta).
        # Ajuste PR-01 (02-10-2026): antes ntfy se enviaba primero y el WebSocket
        # esperaba a que terminara la llamada HTTP a ntfy.sh.
        # HU-03: si el borde ya avisó al celular, la nube no repite el aviso.
        if not datos.notificado:
            asyncio.get_running_loop().run_in_executor(None, _enviar_ntfy_seguro, evento_dict)

    return evento


def _enviar_ntfy_seguro(evento_dict: dict) -> None:
    """Envía la notificación ntfy capturando errores (se ejecuta en un hilo aparte)."""
    try:
        if enviar_notificacion(evento_dict):
            _marcar_notificado(evento_dict["id"])
    except Exception as e:
        print(f"⚠️ Error al enviar notificación ntfy: {e}")


def _marcar_notificado(evento_id: int) -> None:
    """HU-03: registra que el aviso ntfy ya salió, para no repetirlo al sincronizar."""
    db = SessionLocal()
    try:
        ev = db.get(Evento, evento_id)
        if ev is not None:
            ev.notificado = True
            db.commit()
    finally:
        db.close()
