"""PS-01 · Prueba de la clave de API de los sensores (seguridad.py).
Uso (desde la carpeta backend):  python test_seguridad.py
Requiere fastapi y httpx (pip install fastapi httpx).
"""
import os
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import seguridad

app = FastAPI()

@app.post("/api/sensor-data", dependencies=[Depends(seguridad.verificar_clave_sensor)])
def recibir():
    return {"ok": True}

cliente = TestClient(app)
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→ HTTP", obtenido)

CLAVE = "clave-de-prueba-123"
os.environ["DOMOVIDA_API_KEY"] = CLAVE
caso("Sin cabecera X-API-Key", cliente.post("/api/sensor-data").status_code, 401)
caso("Clave incorrecta", cliente.post("/api/sensor-data", headers={"X-API-Key": "otra"}).status_code, 401)
caso("Clave vacía", cliente.post("/api/sensor-data", headers={"X-API-Key": ""}).status_code, 401)
caso("Clave correcta", cliente.post("/api/sensor-data", headers={"X-API-Key": CLAVE}).status_code, 200)
caso("Clave correcta con mayúsculas cambiadas", cliente.post("/api/sensor-data", headers={"X-API-Key": CLAVE.upper()}).status_code, 401)
os.environ.pop("DOMOVIDA_API_KEY")
caso("Sin DOMOVIDA_API_KEY en el servidor (modo desarrollo)", cliente.post("/api/sensor-data").status_code, 200)

print(f"\nResultado PS-01: {sum(casos)}/{len(casos)} casos aprobados")
