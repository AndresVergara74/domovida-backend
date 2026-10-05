"""
PI-05 · Validación HL7 FHIR R4 del recurso Patient seudonimizado de DomoVida.

Comprueba en una base SQLite temporal que:
1. GET /api/fhir/Patient/domovida-p001 es un Patient válido según FHIR R4.
2. El Patient no contiene datos identificatorios (nombre, RUT, nacimiento, dirección, teléfono).
3. GET /api/fhir/Patient es un Bundle válido.
4. Un paciente inexistente responde 404.
5. Las Observation apuntan a ese Patient (subject) y la búsqueda
   /api/fhir/Observation?patient=domovida-p001 las devuelve; otro paciente devuelve 0.

Uso (desde la carpeta backend):
    pip install "fhir.resources>=8"
    python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PI-05_validacion_fhir_patient.py
"""
import os, sys, tempfile
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_pi05.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
os.environ.pop("DOMOVIDA_API_KEY", None)  # prueba local sin clave de sensores
sys.path.insert(0, os.getcwd())

import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None  # sin notificaciones ntfy durante la prueba

from fastapi.testclient import TestClient
from main import app
from fhir.resources.patient import Patient
from fhir.resources.bundle import Bundle

c = TestClient(app)
casos = []

def caso(nombre, ok, detalle=""):
    casos.append(bool(ok))
    print(("✅" if ok else "❌"), nombre, ("→ " + detalle) if detalle else "")

# 1. Patient válido
r = c.get("/api/fhir/Patient/domovida-p001")
p = r.json()
Patient.model_validate(p)
caso("Patient válido según FHIR R4", r.status_code == 200 and r.headers["content-type"].startswith("application/fhir+json"),
     f"HTTP {r.status_code}, id {p['id']}, seguridad {p['meta']['security'][0]['code']}")

# 2. Sin datos identificatorios
prohibidos = ["name", "birthDate", "address", "telecom", "photo", "contact"]
presentes = [k for k in prohibidos if k in p]
texto = str(p).lower()
caso("Sin nombre, nacimiento, dirección, teléfono ni foto", not presentes, f"campos presentes: {presentes or 'ninguno'}")
caso("Sin RUT en el recurso", "rut" not in texto.replace("ruta", ""), "solo el seudónimo domovida-p001")

# 3. Bundle de pacientes
b = c.get("/api/fhir/Patient").json()
Bundle.model_validate(b)
caso("Bundle de Patient válido", b["total"] == 1, f"{b['total']} paciente")

# 4. Paciente inexistente
caso("Paciente inexistente responde 404", c.get("/api/fhir/Patient/otro").status_code == 404)

# 5. Enlace Observation → Patient
r = c.post("/api/sensor-data", json={"sensor_id": "acelerometro_dormitorio", "tipo": "acelerometro",
                                     "habitacion": "dormitorio", "valor": {"magnitud": 25.3, "caida": True}, "alerta": True})
assert r.status_code == 201, r.text
obs = c.get(f"/api/fhir/Observation/{r.json()['id']}").json()
caso("Observation.subject apunta al Patient", obs["subject"]["reference"] == "Patient/domovida-p001", obs["subject"]["reference"])
bp = c.get("/api/fhir/Observation?patient=domovida-p001").json()
Bundle.model_validate(bp)
caso("Búsqueda Observation?patient=domovida-p001", bp["total"] >= 1, f"{bp['total']} observación(es)")
bo = c.get("/api/fhir/Observation?patient=Patient/otro").json()
caso("Búsqueda con otro paciente devuelve 0", bo["total"] == 0, f"{bo['total']} observaciones")

print(f"\nResultado PI-05: {sum(casos)}/{len(casos)} casos aprobados")
