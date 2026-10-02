"""
PI-04 · Validación HL7 FHIR R4 de los recursos generados por DomoVida.

Crea un evento de cada uno de los 7 tipos de sensor en una base SQLite temporal,
los consulta en /api/fhir/Observation y valida cada respuesta con los modelos
oficiales de FHIR R4 (librería fhir.resources).

Uso (desde la carpeta backend):
    pip install "fhir.resources>=8"
    python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-04_validacion_fhir.py
"""
import os, sys, tempfile
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "domovida_pi04.db")
sys.path.insert(0, os.getcwd())

import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None  # sin notificaciones ntfy durante la prueba

from fastapi.testclient import TestClient
from main import app
from fhir.resources.observation import Observation
from fhir.resources.bundle import Bundle

c = TestClient(app)
eventos = [
    ("acelerometro_dormitorio", "acelerometro", "dormitorio", {"magnitud": 25.3, "caida": True}, True),
    ("wearable_cardiaco", "cardiovascular", "wearable", {"bpm": 132.0, "spo2": 91.5, "evento": "taquicardia"}, True),
    ("gas_cocina", "gas", "cocina", {"nivel_ppm": 620.0}, True),
    ("humo_cocina", "humo", "cocina", {"nivel": 120.0}, False),
    ("apertura_puerta_principal", "apertura", "entrada", {"abierto": True}, True),
    ("pir_living", "pir", "living", {"movimiento": False, "minutos_inactivo": 12.5}, False),
    ("boton_panico_sala", "boton_panico", "sala", {"activado": True}, True),
]
ids = []
for s, t, h, v, a in eventos:
    r = c.post("/api/sensor-data", json={"sensor_id": s, "tipo": t, "habitacion": h, "valor": v, "alerta": a})
    assert r.status_code == 201, r.text
    ids.append(r.json()["id"])

validas = 0
for i in ids:
    r = c.get(f"/api/fhir/Observation/{i}")
    assert r.headers["content-type"].startswith("application/fhir+json")
    Observation.model_validate(r.json())
    validas += 1

b = c.get("/api/fhir/Observation?alerta=true&_count=10").json()
Bundle.model_validate(b)
print(f"PI-04: {validas}/{len(ids)} Observation válidas según FHIR R4; Bundle válido con {b['total']} entradas.")
print("Respuesta para un id inexistente:", c.get("/api/fhir/Observation/999999").status_code)
