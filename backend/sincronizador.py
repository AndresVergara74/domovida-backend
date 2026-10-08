"""
HU-03 · Sincronización del modo borde con la nube (almacenar y reenviar).

En el hogar, el backend local guarda cada evento en SQLite con un UUID y
`sync_status = 'pendiente'`. Este módulo revisa cada cierto tiempo los
pendientes y los envía a la API en la nube (POST /api/sensor-data, con la
clave de los sensores). Cuando la nube confirma (HTTP 200 o 201), el evento
queda como 'synced'. Si no hay conexión, los eventos esperan al siguiente ciclo.

La nube reconoce el UUID: si un evento llega dos veces (por ejemplo, por un
corte justo después de enviarlo), no se duplica.

Variables de entorno (solo en el equipo del hogar, nunca en Render):
    NUBE_API_URL        URL de la API en la nube, p. ej. https://domovida-backend.onrender.com
    NUBE_API_KEY        clave de los sensores de la nube (si no, usa DOMOVIDA_API_KEY)
    SYNC_INTERVALO_SEG  segundos entre ciclos (por defecto 30)
"""
import logging
import os
import threading
import time
from typing import Callable, Optional

import requests

from database import SessionLocal
from models import Evento
from tiempo import a_utc

logger = logging.getLogger("domovida.sync")
_estado = {"ultimo_intento": None, "ultimo_ok": None, "ultimo_error": None, "enviados_total": 0}


def url_nube() -> Optional[str]:
    url = os.getenv("NUBE_API_URL", "").strip().rstrip("/")
    return url or None


def sincronizacion_activa() -> bool:
    return url_nube() is not None


def _clave() -> str:
    return (os.getenv("NUBE_API_KEY") or os.getenv("DOMOVIDA_API_KEY") or "").strip()


def _enviar_http(url: str, payload: dict, headers: dict) -> int:
    return requests.post(url, json=payload, headers=headers, timeout=10).status_code


def _payload(ev: Evento) -> dict:
    return {
        "uuid": ev.uuid,
        "origen": "borde",
        "notificado": bool(ev.notificado),
        "sensor_id": ev.sensor_id,
        "tipo": ev.tipo,
        "habitacion": ev.habitacion,
        "valor": ev.valor or {},
        "alerta": bool(ev.alerta),
        "timestamp": a_utc(ev.timestamp).isoformat() if ev.timestamp else None,
    }


def contar_pendientes() -> int:
    db = SessionLocal()
    try:
        return db.query(Evento).filter(Evento.sync_status == "pendiente").count()
    finally:
        db.close()


def sincronizar_una_vez(enviar: Callable[[str, dict, dict], int] = _enviar_http, lote: int = 50) -> dict:
    """Envía hasta `lote` eventos pendientes, en orden. Se detiene en el primer fallo
    para respetar el orden y reintentar en el siguiente ciclo."""
    url = url_nube()
    resultado = {"enviados": 0, "fallo": None, "pendientes": 0}
    if not url:
        resultado["fallo"] = "NUBE_API_URL no definida"
        return resultado
    _estado["ultimo_intento"] = time.time()
    headers = {"X-API-Key": _clave()}
    db = SessionLocal()
    try:
        pendientes = (
            db.query(Evento)
            .filter(Evento.sync_status == "pendiente")
            .order_by(Evento.id)
            .limit(lote)
            .all()
        )
        for ev in pendientes:
            try:
                codigo = enviar(f"{url}/api/sensor-data", _payload(ev), headers)
            except requests.RequestException as e:
                resultado["fallo"] = f"sin conexión: {type(e).__name__}"
                break
            if codigo in (200, 201):
                ev.sync_status = "synced"
                db.commit()
                resultado["enviados"] += 1
            else:
                resultado["fallo"] = f"HTTP {codigo}"
                break
        resultado["pendientes"] = db.query(Evento).filter(Evento.sync_status == "pendiente").count()
    finally:
        db.close()
    _estado["enviados_total"] += resultado["enviados"]
    if resultado["fallo"]:
        _estado["ultimo_error"] = resultado["fallo"]
    else:
        _estado["ultimo_ok"] = time.time()
    return resultado


def estado() -> dict:
    """Resumen para /api/health."""
    if not sincronizacion_activa():
        return {"activa": False}
    return {
        "activa": True,
        "pendientes": contar_pendientes(),
        "enviados_desde_inicio": _estado["enviados_total"],
        "ultimo_error": _estado["ultimo_error"],
    }


def _ciclo(intervalo: int):
    while True:
        try:
            r = sincronizar_una_vez()
            if r["enviados"] or r["fallo"]:
                logger.warning("Sincronización: %s enviados, %s pendientes%s", r["enviados"], r["pendientes"],
                               f", fallo: {r['fallo']}" if r["fallo"] else "")
        except Exception as e:  # nunca detener el hilo
            logger.warning("Sincronización con error: %s", e)
        time.sleep(intervalo)


def iniciar_en_segundo_plano():
    if not sincronizacion_activa():
        return
    intervalo = int(os.getenv("SYNC_INTERVALO_SEG", "30") or 30)
    threading.Thread(target=_ciclo, args=(intervalo,), daemon=True, name="domovida-sync").start()
    logger.warning("Sincronizador del modo borde activo: cada %s s hacia %s", intervalo, url_nube())
