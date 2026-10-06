"""PS-01c · HU-17: las consultas de lectura exigen la sesión del cuidador (auth_cuidador.verificar_lectura).
Simula Supabase Auth, sin internet. Base SQLite temporal.
Uso (desde la carpeta backend):  python test_lecturas.py
Requiere fastapi y httpx (pip install fastapi httpx).
"""
import os, tempfile
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_ps01c.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
for v in ("DOMOVIDA_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "PROTEGER_LECTURAS"):
    os.environ.pop(v, None)

import requests
import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None
import auth_cuidador
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

class RespuestaFalsa:
    def __init__(self, codigo, datos=None):
        self.status_code = codigo; self._d = datos or {}
    def json(self):
        return self._d

llamadas = {"n": 0}
def supabase_falso(url, headers=None, timeout=None):
    llamadas["n"] += 1
    if headers["Authorization"] == "Bearer token-valido":
        return RespuestaFalsa(200, {"email": "cuidador.prueba@domovida.cl"})
    return RespuestaFalsa(401)
auth_cuidador.requests.get = supabase_falso

r = c.post("/api/sensor-data", json={"sensor_id": "acelerometro_dormitorio", "tipo": "acelerometro",
                                     "habitacion": "dormitorio", "valor": {"z": 20}, "alerta": True})
id_ev = r.json()["id"]
RUTAS = ["/api/eventos", "/api/alertas/activas", "/api/alertas/inactividad",
         f"/api/fhir/Observation/{id_ev}", "/api/fhir/Patient/domovida-p001"]
OK = {"Authorization": "Bearer token-valido"}
FALSO = {"Authorization": "Bearer token-falso"}

# 1. Interruptor apagado (por defecto): todo sigue abierto, como hoy
caso("Interruptor apagado: lecturas sin sesión", [c.get(u).status_code for u in RUTAS], [200] * 5)

# 2. Interruptor encendido sin Supabase configurado (modo borde): no se puede exigir sesión
os.environ["PROTEGER_LECTURAS"] = "1"
caso("Encendido sin Supabase (modo borde): lecturas abiertas", c.get("/api/eventos").status_code, 200)

# 3-6. Interruptor encendido con Supabase
os.environ["SUPABASE_URL"] = "https://proyecto-prueba.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "clave-publica-prueba"
caso("Sin sesión: 401 en las 5 consultas", [c.get(u).status_code for u in RUTAS], [401] * 5)
caso("Token falso: 401", c.get("/api/eventos", headers=FALSO).status_code, 401)
llamadas["n"] = 0
caso("Sesión válida: 200 en las 5 consultas", [c.get(u, headers=OK).status_code for u in RUTAS], [200] * 5)
caso("Token recordado 60 s: 1 sola consulta a Supabase", llamadas["n"], 1)

# 7-8. Lo que sigue abierto a propósito
caso("/api/health sigue público e informa la protección",
     (c.get("/api/health").status_code, c.get("/api/health").json()["auth_cuidador"]["lecturas_protegidas"]), (200, True))
caso("Los sensores siguen enviando con su clave (POST no cambia)",
     c.post("/api/sensor-data", json={"sensor_id": "pir_living", "tipo": "pir", "habitacion": "living",
                                      "valor": {"movimiento": True}, "alerta": False}).status_code, 201)

print(f"\nResultado PS-01c (HU-17): {sum(casos)}/{len(casos)} casos aprobados")
