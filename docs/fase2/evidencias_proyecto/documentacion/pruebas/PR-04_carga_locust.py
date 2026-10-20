"""
PR-04 · Prueba de carga sobre los endpoints REST de DomoVida (Locust)

Meta (Guía 1.5, Tabla 3, OE2): tiempo de respuesta menor a 200 ms por solicitud
bajo usuarios concurrentes, en /api/sensor-data y /api/eventos.

Servidor probado: Oracle Cloud Chile Central (Santiago), backend + SQLite en la
misma máquina, publicado con HTTPS en https://domovida.duckdns.org.

Usuarios simulados:
  - SensorHogar: un hogar que envía lecturas de sensores (como el simulador).
  - CuidadorPanel: un cuidador que consulta el historial y el estado del sistema.

Las claves NUNCA se escriben en este archivo: se leen de variables de entorno.
  DOMOVIDA_API_KEY   clave de los sensores (obligatoria)
  DOMOVIDA_TOKEN     token de sesión del cuidador (opcional; solo si el servidor
                     protege las lecturas con inicio de sesión)

Ejecución (PowerShell, desde la carpeta del repositorio):
  pip install locust
  $env:DOMOVIDA_API_KEY=(Get-Content C:\\Users\\verga\\Documents\\claves-oracle\\domovida_api_key.txt -Raw).Trim()
  locust -f docs\\fase2\\evidencias_proyecto\\documentacion\\pruebas\\PR-04_carga_locust.py `
         --host https://domovida.duckdns.org --headless -u 20 -r 2 -t 2m `
         --html docs\\fase2\\evidencias_proyecto\\documentacion\\pruebas\\PR-04_reporte_locust.html `
         --csv docs\\fase2\\evidencias_proyecto\\documentacion\\pruebas\\PR-04
"""
import os
import random
from datetime import datetime, timezone

from locust import HttpUser, between, task

CLAVE = os.environ.get("DOMOVIDA_API_KEY", "").strip()
TOKEN = os.environ.get("DOMOVIDA_TOKEN", "").strip()

SENSORES = [
    ("acelerometro_dormitorio", "acelerometro", "dormitorio", lambda: {"magnitud": round(random.uniform(0.8, 1.2), 2)}),
    ("movimiento_living", "movimiento", "living", lambda: {"movimiento": random.random() < 0.3}),
    ("apertura_puerta_principal", "apertura", "entrada", lambda: {"abierto": False}),  # siempre cerrada: no dispara la regla de la puerta
    ("gas_cocina", "gas", "cocina", lambda: {"ppm": random.randint(5, 40)}),
    ("humo_cocina", "humo", "cocina", lambda: {"detectado": False}),
    ("wearable_cardiaco", "cardiovascular", "wearable", lambda: {"bpm": random.randint(60, 95)}),
]


class SensorHogar(HttpUser):
    """Hogar que envía una lectura cada 1 a 3 segundos."""
    weight = 3
    wait_time = between(1, 3)

    @task
    def enviar_lectura(self):
        sensor_id, tipo, habitacion, valor = random.choice(SENSORES)
        self.client.post(
            "/api/sensor-data",
            name="POST /api/sensor-data",
            headers={"X-API-Key": CLAVE},
            json={
                "sensor_id": sensor_id,
                "tipo": tipo,
                "habitacion": habitacion,
                "valor": {**valor(), "prueba": "PR-04"},
                "alerta": False,  # lecturas normales: la prueba no debe disparar avisos ntfy
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


class CuidadorPanel(HttpUser):
    """Cuidador que revisa el panel cada 3 a 6 segundos."""
    weight = 1
    wait_time = between(3, 6)

    def on_start(self):
        self.cabeceras = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

    @task(3)
    def ver_historial(self):
        self.client.get("/api/eventos?limit=50", name="GET /api/eventos", headers=self.cabeceras)

    @task(1)
    def ver_estado(self):
        self.client.get("/api/health", name="GET /api/health")
