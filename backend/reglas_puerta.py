"""
Regla de alerta para la puerta principal (DomoVida).

Criterio acordado (05-10-2026), opción combinada:
  1. Apertura NOCTURNA: la puerta se abre entre las 22:00 y las 07:00 (hora de Chile).
  2. Puerta ABIERTA DEMASIADO TIEMPO: sigue abierta por 10 minutos o más.

Para no repetir la misma alerta cada 5 segundos:
  - La alerta nocturna se emite solo cuando la puerta pasa de cerrada a abierta.
  - La alerta por tiempo se emite una sola vez por cada período de apertura.

Los horarios y el tiempo máximo se pueden ajustar con variables de entorno.
El estado se guarda en memoria: si el servidor se reinicia, el conteo vuelve a cero
(limitación aceptada para el prototipo).
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

ZONA_CHILE = ZoneInfo("America/Santiago")
HORA_NOCHE_INICIO = int(os.getenv("PUERTA_HORA_NOCHE_INICIO", "22"))
HORA_NOCHE_FIN = int(os.getenv("PUERTA_HORA_NOCHE_FIN", "7"))
MINUTOS_MAX_ABIERTA = int(os.getenv("PUERTA_MINUTOS_MAX_ABIERTA", "10"))

# sensor_id -> {"desde": datetime en que se abrió, "avisado": bool}
_estado_puertas: dict = {}


def es_horario_nocturno(momento: datetime) -> bool:
    hora = momento.astimezone(ZONA_CHILE).hour
    return hora >= HORA_NOCHE_INICIO or hora < HORA_NOCHE_FIN


def evaluar_puerta(sensor_id: str, abierto: bool, momento: datetime | None = None) -> tuple[bool, str | None, int]:
    """
    Decide si un evento de la puerta principal debe generar alerta.

    Devuelve (alerta, motivo, minutos_abierta):
      motivo = "apertura_nocturna" | "abierta_mucho_tiempo" | None
    """
    momento = momento or datetime.now(ZONA_CHILE)
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=ZONA_CHILE)

    if not abierto:
        _estado_puertas.pop(sensor_id, None)
        return False, None, 0

    estado = _estado_puertas.get(sensor_id)
    if estado is None:
        # Transición cerrada -> abierta
        _estado_puertas[sensor_id] = {"desde": momento, "avisado": False}
        if es_horario_nocturno(momento):
            _estado_puertas[sensor_id]["avisado_noche"] = True
            return True, "apertura_nocturna", 0
        return False, None, 0

    minutos = int((momento - estado["desde"]).total_seconds() // 60)
    if minutos >= MINUTOS_MAX_ABIERTA and not estado["avisado"]:
        estado["avisado"] = True
        return True, "abierta_mucho_tiempo", minutos
    return False, None, minutos


def reiniciar_estado() -> None:
    """Solo para pruebas."""
    _estado_puertas.clear()
