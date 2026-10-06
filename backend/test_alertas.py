"""PU-06 · La tabla `alertas` como fuente única de verdad de la atención (ajuste 17).
Base SQLite temporal, sin internet ni Supabase.
Uso (desde la carpeta backend):  python test_alertas.py
Requiere fastapi y httpx (pip install fastapi httpx).
"""
import os, tempfile
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_pu06.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
for v in ("DOMOVIDA_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"):
    os.environ.pop(v, None)

import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None  # sin ntfy durante la prueba
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Evento, Alerta
from alertas_servicio import registrar_alerta

c = TestClient(app)
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

def enviar(tipo, alerta, habitacion="sala"):
    r = c.post("/api/sensor-data", json={"sensor_id": f"{tipo}_{habitacion}", "tipo": tipo,
                                         "habitacion": habitacion, "valor": {"prueba": True}, "alerta": alerta})
    return r.json()["id"]

def alertas_de(evento_id):
    db = SessionLocal()
    filas = db.query(Alerta).filter(Alerta.evento_id == evento_id).all()
    db.expunge_all(); db.close()
    return filas

# 1-3. Creación de la alerta junto con el evento
e_caida = enviar("acelerometro", True, "dormitorio")
caso("Evento con alerta crea 1 fila en alertas", len(alertas_de(e_caida)), 1)
caso("Severidad de una caída", alertas_de(e_caida)[0].nivel_severidad, "critica")
e_puerta = enviar("apertura", True, "cocina")
caso("Severidad de una apertura (no crítica)", alertas_de(e_puerta)[0].nivel_severidad, "alta")
e_normal = enviar("pir", False)
caso("Evento sin alerta no crea fila en alertas", len(alertas_de(e_normal)), 0)

# 5. Sin duplicados: si la alerta ya existe (trigger antiguo de Supabase) se reutiliza
db = SessionLocal()
ev = db.get(Evento, e_caida)
registrar_alerta(db, ev); db.commit(); db.close()
caso("No se duplica si la alerta ya existe (trigger antiguo)", len(alertas_de(e_caida)), 1)

# 6-9. Atención: se registra en alertas y se copia a eventos
activas = [a["id"] for a in c.get("/api/alertas/activas").json()]
caso("La alerta aparece como activa", e_caida in activas, True)
r = c.patch(f"/api/alertas/{e_caida}/resolver", json={"resuelto_por": "Cuidador de prueba"})
caso("Atender la alerta responde 200", r.status_code, 200)
a = alertas_de(e_caida)[0]
caso("alertas.resuelto / resuelto_por (fuente de verdad)", (a.resuelto, a.resuelto_por), (True, "Cuidador de prueba"))
db = SessionLocal(); ev = db.get(Evento, e_caida); db.close()
caso("Copia en eventos (compatibilidad)", (ev.resuelto, ev.resuelto_por), (True, "Cuidador de prueba"))
activas = [a["id"] for a in c.get("/api/alertas/activas").json()]
caso("La alerta atendida deja de estar activa", e_caida in activas, False)
caso("No se puede atender dos veces", c.patch(f"/api/alertas/{e_caida}/resolver", json={}).status_code, 404)

# 12. Evento antiguo sin fila en alertas (base local previa): se crea al atenderlo
db = SessionLocal()
viejo = Evento(sensor_id="gas_cocina", tipo="gas", habitacion="cocina", valor={}, alerta=True)
db.add(viejo); db.commit(); id_viejo = viejo.id; db.close()
r = c.patch(f"/api/alertas/{id_viejo}/resolver", json={"resuelto_por": "Cuidador de prueba"})
caso("Evento antiguo sin fila en alertas se puede atender", (r.status_code, len(alertas_de(id_viejo))), (200, 1))
caso("Un evento sin alerta no se puede atender", c.patch(f"/api/alertas/{e_normal}/resolver", json={}).status_code, 404)

print(f"\nResultado PU-06: {sum(casos)}/{len(casos)} casos aprobados")
