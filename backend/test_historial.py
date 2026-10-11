"""PU-08 · Filtros del historial en el servidor (ajuste 20, hallazgo del ensayo SUS T4).
Base SQLite temporal, sin internet ni Supabase.
Uso (desde la carpeta backend):  python test_historial.py
"""
import os, tempfile
from datetime import datetime, timedelta, timezone
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_pu08.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
for v in ("DOMOVIDA_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"):
    os.environ.pop(v, None)

import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

def enviar(tipo, habitacion, alerta, hace_min=0):
    ts = (datetime.now(timezone.utc) - timedelta(minutes=hace_min)).isoformat()
    r = c.post("/api/sensor-data", json={"sensor_id": f"{tipo}_{habitacion}", "tipo": tipo,
               "habitacion": habitacion, "valor": {"prueba": True}, "alerta": alerta, "timestamp": ts})
    assert r.status_code == 201, r.text

# Una caída hace 10 minutos, tapada por 80 lecturas normales más recientes
enviar("acelerometro", "dormitorio", True, hace_min=10)
for i in range(80):
    enviar(["pir", "gas", "humo", "acelerometro"][i % 4], "cocina" if i % 2 else "living", False)
enviar("acelerometro", "dormitorio", False, hace_min=60 * 30)  # lectura de hace 30 horas

ultimas = c.get("/api/eventos?limit=50").json()
caso("Sin filtros: la caída queda fuera de las últimas 50 (el problema)", any(e["alerta"] for e in ultimas), False)

r = c.get("/api/eventos?tipo=acelerometro&solo_alertas=true&limit=200").json()
caso("Filtro tipo + solo alertas encuentra la caída", len(r), 1)
caso("La caída encontrada es del dormitorio", r[0]["habitacion"] if r else None, "dormitorio")

r = c.get("/api/eventos?habitacion=dormitorio&limit=200").json()
caso("Filtro por habitación devuelve solo dormitorio", {e["habitacion"] for e in r}, {"dormitorio"})

r = c.get("/api/eventos?sin_alertas=true&limit=500").json()
caso("Filtro sin alertas no incluye alertas", any(e["alerta"] for e in r), False)

desde = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
r = c.get("/api/eventos", params={"tipo": "acelerometro", "desde": desde, "limit": 500}).json()
caso("Filtro desde (24 h) excluye la lectura de hace 30 h", len(r), 21)

r = c.get("/api/eventos?limit=10").json()
caso("Sin filtros sigue igual: orden más reciente primero", r[0]["timestamp"] >= r[-1]["timestamp"], True)
caso("El límite máximo se respeta (le=500)", c.get("/api/eventos?limit=501").status_code, 422)

print(f"\n{sum(casos)}/{len(casos)} casos aprobados")
