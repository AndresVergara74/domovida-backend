"""
Manejo uniforme de fechas en DomoVida (ficha técnica 19, problema D4).

Regla: todas las fechas se guardan y viajan en UTC con zona horaria
(ISO 8601 con +00:00). El panel las muestra en hora de Chile.

- ahora_utc(): la hora actual en UTC, con zona.
- a_utc(dt): convierte cualquier fecha a UTC con zona. Una fecha sin zona
  se interpreta como UTC (así la devuelven SQLite y las columnas antiguas).
- entrada_a_utc(dt): para fechas que llegan desde los sensores. Una fecha sin
  zona se interpreta como hora de Chile, porque los dispositivos están en el
  hogar (compatibilidad con versiones antiguas del simulador).
"""
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

ZONA_CHILE = ZoneInfo("America/Santiago")


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def a_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def entrada_a_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZONA_CHILE)
    return dt.astimezone(timezone.utc)
