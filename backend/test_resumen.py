"""PU-09 · Resumen de actividad contado en el servidor (ajuste 21, hallazgo del ensayo SUS).
Base SQLite temporal, sin internet ni Supabase.
Uso (desde la carpeta backend):  python test_resumen.py
"""
import os, tempfile
from datetime import datetime, timedelta, timezone
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_pu09.db")
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

ahora = datetime.now(timezone.utc)
def enviar(tipo, alerta, hace_min):
    ts = (ahora - timedelta(minutes=hace_min)).isoformat()
    r = c.post("/api/sensor-data", json={"sensor_id": f"{tipo}_x", "tipo": tipo, "habitacion": "sala",
               "valor": {}, "alerta": alerta, "timestamp": ts})
    assert r.status_code == 201, r.text

enviar("acelerometro", True, 90)          # una caída hace 1,5 h
for i in range(120):                      # 120 lecturas normales en los últimos minutos
    enviar("pir", False, i % 30)
enviar("gas", False, 60 * 20)             # lectura de hace 20 h (fuera del gráfico de 12 h)

medianoche = (ahora - timedelta(hours=3)).isoformat()  # "hoy" para la prueba: últimas 3 h
r = c.get("/api/eventos/resumen", params={"horas": 12, "hoy_desde": medianoche})
caso("Responde 200", r.status_code, 200)
d = r.json()
caso("Devuelve 12 horas", len(d["horas"]), 12)
caso("Cuenta las 120 lecturas normales recientes", sum(h["lecturas"] for h in d["horas"]), 120)
caso("Cuenta la caída aunque haya 120 lecturas después", sum(h["alertas"] for h in d["horas"]), 1)
caso("Lecturas de hoy (desde la medianoche indicada)", d["lecturas_hoy"], 121)
caso("Alertas de hoy incluye la caída con su sensor", [a["sensor_id"] for a in d["alertas_hoy"]], ["acelerometro_x"])
caso("La última hora del gráfico es la actual", d["horas"][-1]["inicio"] <= ahora.isoformat(), True)
caso("Rango de horas validado (máx. 48)", c.get("/api/eventos/resumen?horas=49").status_code, 422)
caso("El listado normal sigue funcionando", c.get("/api/eventos?limit=5").status_code, 200)

print(f"\n{sum(casos)}/{len(casos)} casos aprobados")
