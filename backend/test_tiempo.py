"""PU-05 · Prueba del manejo uniforme de fechas (tiempo.py y schemas.py).
Uso (desde la carpeta backend):  python test_tiempo.py
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from tiempo import a_utc, entrada_a_utc, ahora_utc
from schemas import SensorDataIn, EventoOut

casos = []
def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

CL = ZoneInfo("America/Santiago")
caso("ahora_utc tiene zona UTC", ahora_utc().utcoffset(), timedelta(0))
caso("Fecha sin zona de la base se lee como UTC", a_utc(datetime(2026, 10, 6, 15, 0)).isoformat(), "2026-10-06T15:00:00+00:00")
caso("Fecha con zona de Chile se convierte a UTC", a_utc(datetime(2026, 10, 6, 12, 0, tzinfo=CL)).isoformat(), "2026-10-06T15:00:00+00:00")
caso("Sensor sin zona (simulador antiguo) = hora de Chile", entrada_a_utc(datetime(2026, 10, 6, 12, 0)).isoformat(), "2026-10-06T15:00:00+00:00")
caso("Sensor con zona UTC se mantiene", entrada_a_utc(datetime(2026, 10, 6, 15, 0, tzinfo=timezone.utc)).isoformat(), "2026-10-06T15:00:00+00:00")
d = SensorDataIn(sensor_id="s", tipo="pir", habitacion="living", valor={}, timestamp="2026-10-06T15:00:00.000Z")
caso("Entrada del navegador (toISOString con Z)", d.timestamp.isoformat(), "2026-10-06T15:00:00+00:00")
d = SensorDataIn(sensor_id="s", tipo="pir", habitacion="living", valor={}, timestamp="2026-10-06T12:00:00")
caso("Entrada sin zona del simulador antiguo", d.timestamp.isoformat(), "2026-10-06T15:00:00+00:00")
e = EventoOut(id=1, sensor_id="s", tipo="pir", habitacion="living", valor={}, alerta=False, timestamp=datetime(2026, 10, 6, 15, 0))
caso("Salida de la API siempre con +00:00", e.model_dump(mode="json")["timestamp"], "2026-10-06T15:00:00Z")
caso("Invierno en Chile (UTC−4)", entrada_a_utc(datetime(2026, 7, 1, 12, 0)).isoformat(), "2026-07-01T16:00:00+00:00")

print(f"\nResultado PU-05: {sum(casos)}/{len(casos)} casos aprobados")
