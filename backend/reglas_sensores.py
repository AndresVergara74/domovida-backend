"""
Reglas de detección por umbral de DomoVida (HU-04 y HU-05; complementa a reglas_puerta.py).

El backend decide la alerta a partir del VALOR medido, no del aviso que manda el sensor:
  - Caída (acelerómetro): magnitud de la aceleración mayor a 17 m/s².
  - Gas (cocina): concentración mayor a 500 ppm.
  - Humo (cocina): nivel mayor a 800.
  - Inactividad (sensor de movimiento PIR): más de 30 minutos sin movimiento.

Si la lectura no trae el valor que la regla necesita (por ejemplo, un sensor antiguo
que solo envía «alerta»), la regla no opina y se respeta el aviso del sensor.
Los umbrales se pueden ajustar con variables de entorno.

La inactividad se calcula con la hora del último movimiento de cada sensor y se avisa
una sola vez por período sin movimiento. El estado vive en memoria: si el servidor
se reinicia, el conteo vuelve a cero (misma limitación aceptada en reglas_puerta.py).
"""
import math
import os
from datetime import datetime, timezone
from typing import Optional, Tuple

UMBRAL_CAIDA_MS2 = float(os.getenv("UMBRAL_CAIDA_MS2", "17"))
UMBRAL_GAS_PPM = float(os.getenv("UMBRAL_GAS_PPM", "500"))
UMBRAL_HUMO = float(os.getenv("UMBRAL_HUMO", "800"))
MINUTOS_INACTIVIDAD = float(os.getenv("MINUTOS_INACTIVIDAD", "30"))

# sensor_id -> {"ultimo_movimiento": datetime, "avisado": bool}
_estado_pir: dict = {}


def reiniciar_estado() -> None:
    _estado_pir.clear()


def _numero(valor: dict, *claves) -> Optional[float]:
    for k in claves:
        v = valor.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    return None


def _magnitud(valor: dict) -> Optional[float]:
    m = _numero(valor, "magnitud")
    if m is not None:
        return m
    ejes = [_numero(valor, e) for e in ("ax", "ay", "az")]
    if all(e is not None for e in ejes):
        return math.sqrt(sum(e * e for e in ejes))
    return None


def evaluar_sensor(sensor_id: str, tipo: str, valor: Optional[dict],
                   momento: Optional[datetime] = None) -> Tuple[Optional[bool], Optional[str]]:
    """
    Devuelve (alerta, motivo).
      alerta = True / False según el umbral, o None si la regla no aplica a esta lectura.
      motivo = "caida" | "gas_sobre_umbral" | "humo_sobre_umbral" | "inactividad" | None
    """
    valor = valor or {}
    momento = momento or datetime.now(timezone.utc)
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)

    if tipo == "acelerometro":
        m = _magnitud(valor)
        if m is None:
            return None, None
        return (True, "caida") if m > UMBRAL_CAIDA_MS2 else (False, None)

    if tipo == "gas":
        ppm = _numero(valor, "nivel_ppm", "ppm")
        if ppm is None:
            return None, None
        return (True, "gas_sobre_umbral") if ppm > UMBRAL_GAS_PPM else (False, None)

    if tipo == "humo":
        nivel = _numero(valor, "nivel")
        if nivel is None:
            return None, None
        return (True, "humo_sobre_umbral") if nivel > UMBRAL_HUMO else (False, None)

    if tipo == "pir":
        mov = valor.get("movimiento")
        if not isinstance(mov, bool):
            return None, None
        estado = _estado_pir.get(sensor_id)
        if mov or estado is None:
            # Hay movimiento, o es la primera lectura del sensor: empieza un período nuevo.
            _estado_pir[sensor_id] = {"ultimo_movimiento": momento, "avisado": False}
            return False, None
        minutos = (momento - estado["ultimo_movimiento"]).total_seconds() / 60
        if minutos > MINUTOS_INACTIVIDAD and not estado["avisado"]:
            estado["avisado"] = True
            return True, "inactividad"
        return False, None

    return None, None


def minutos_sin_movimiento(sensor_id: str, momento: Optional[datetime] = None) -> Optional[float]:
    estado = _estado_pir.get(sensor_id)
    if not estado:
        return None
    momento = momento or datetime.now(timezone.utc)
    return round((momento - estado["ultimo_movimiento"]).total_seconds() / 60, 1)
