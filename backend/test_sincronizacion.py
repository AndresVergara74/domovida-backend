"""PU-07 · HU-03: sincronización del modo borde con la nube (sincronizador.py).
Base SQLite temporal; la nube y la red se simulan, sin internet.
Uso (desde la carpeta backend):  python test_sincronizacion.py
Requiere fastapi y httpx (pip install fastapi httpx).
"""
import os, tempfile, sqlite3
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_pu07.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
for v in ("DOMOVIDA_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "PROTEGER_LECTURAS", "NUBE_API_URL", "NUBE_API_KEY"):
    os.environ.pop(v, None)

import requests
import routers.sensor_router as sr
avisos = []
sr.enviar_notificacion = lambda e: avisos.append(e["id"]) or True
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Evento, Alerta
import sincronizador

c = TestClient(app)
casos = []
def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

def enviar(tipo="pir", alerta=False, **extra):
    datos = {"sensor_id": f"{tipo}_sala", "tipo": tipo, "habitacion": "sala",
             "valor": {"prueba": "PU-07"}, "alerta": alerta, **extra}
    return c.post("/api/sensor-data", json=datos).json()["id"]

def ev(id_):
    db = SessionLocal(); e = db.get(Evento, id_); db.close(); return e

# 1. Modo nube (sin NUBE_API_URL): no queda pendiente
e = ev(enviar())
caso("Modo nube: evento con UUID, origen 'nube' y sin pendiente", (len(e.uuid), e.origen, e.sync_status), (36, "nube", None))

# 2-3. Modo borde (con NUBE_API_URL): los eventos quedan pendientes
os.environ["NUBE_API_URL"] = "https://nube-de-prueba.example"
ids = [enviar(), enviar("acelerometro", True), enviar()]
caso("Modo borde: 3 eventos pendientes con origen 'borde'", [(ev(i).sync_status, ev(i).origen) for i in ids], [("pendiente", "borde")] * 3)
h = c.get("/api/health").json()["sincronizacion_borde"]
caso("/api/health informa la sincronización y los pendientes", (h["activa"], h["pendientes"]), (True, 3))

# 4. Sin internet: nada se pierde
def sin_red(url, payload, headers):
    raise requests.ConnectionError("sin internet")
r = sincronizador.sincronizar_una_vez(enviar=sin_red)
caso("Sin internet: 0 enviados y siguen 3 pendientes", (r["enviados"], r["pendientes"], r["fallo"][:12]), (0, 3, "sin conexión"))

# 5-6. Vuelve internet: se suben en orden y quedan sincronizados
nube = []
def nube_ok(url, payload, headers):
    nube.append(payload); return 201
r = sincronizador.sincronizar_una_vez(enviar=nube_ok)
caso("Vuelve internet: 3 enviados, 0 pendientes", (r["enviados"], r["pendientes"]), (3, 0))
caso("Se envían en orden, con UUID, origen 'borde' y la clave", ([p["uuid"] for p in nube] == [ev(i).uuid for i in ids], {p["origen"] for p in nube}), (True, {"borde"}))
caso("Un segundo ciclo no reenvía nada", sincronizador.sincronizar_una_vez(enviar=nube_ok)["enviados"], 0)

# 7. Falla a medias: lo que no se confirmó se reintenta en el ciclo siguiente
nuevos = [enviar(), enviar()]
respuestas = iter([201, 503])
r1 = sincronizador.sincronizar_una_vez(enviar=lambda u, p, h: next(respuestas))
r2 = sincronizador.sincronizar_una_vez(enviar=nube_ok)
caso("Falla a medias: 1 enviado, 1 pendiente; el ciclo siguiente envía el resto", (r1["enviados"], r1["pendientes"], r2["enviados"], r2["pendientes"]), (1, 1, 1, 0))

# 8-9. La nube no duplica: el mismo UUID enviado dos veces queda una sola vez
del os.environ["NUBE_API_URL"]
paquete = dict(nube[1]); paquete["uuid"] = "11111111-2222-3333-4444-555555555555"
a = c.post("/api/sensor-data", json=paquete).json()["id"]
b = c.post("/api/sensor-data", json=paquete).json()["id"]
db = SessionLocal()
filas = db.query(Evento).filter(Evento.uuid == paquete["uuid"]).count()
alertas = db.query(Alerta).filter(Alerta.evento_id == a).count()
db.close()
caso("Nube: el mismo UUID dos veces = 1 evento (mismo id)", (a == b, filas), (True, 1))
caso("Nube: la alerta del evento sincronizado se crea una sola vez", alertas, 1)

# 10. Sin avisos repetidos: si el borde ya avisó, la nube no repite el ntfy
avisos.clear()
p2 = dict(paquete); p2["uuid"] = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"; p2["notificado"] = True
c.post("/api/sensor-data", json=p2)
p3 = dict(paquete); p3["uuid"] = "ffffffff-bbbb-cccc-dddd-eeeeeeeeeeee"; p3["notificado"] = False
id3 = c.post("/api/sensor-data", json=p3).json()["id"]
caso("ntfy solo si el borde no había avisado", avisos, [id3])

# 11. Una base SQLite antigua (sin las columnas nuevas) se actualiza sola
import database
from sqlalchemy import create_engine, inspect
vieja = os.path.join(tempfile.gettempdir(), "domovida_pu07_vieja.db")
if os.path.exists(vieja): os.remove(vieja)
con = sqlite3.connect(vieja); con.execute("CREATE TABLE eventos (id INTEGER PRIMARY KEY, sensor_id VARCHAR)"); con.commit(); con.close()
orig = (database.engine, database.DATABASE_URL)
database.engine = create_engine("sqlite:///" + vieja); database.DATABASE_URL = "sqlite:///" + vieja
database.asegurar_columnas_borde()
cols = {x["name"] for x in inspect(database.engine).get_columns("eventos")}
database.engine, database.DATABASE_URL = orig
caso("Base SQLite antigua: se agregan uuid, origen, sync_status y notificado", {"uuid", "origen", "sync_status", "notificado"} <= cols, True)

print(f"\nResultado PU-07 (HU-03): {sum(casos)}/{len(casos)} casos aprobados")
