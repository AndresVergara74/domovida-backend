"""PS-01 (parte 2) · Prueba de la sesión del cuidador para atender alertas (auth_cuidador.py).
Simula las respuestas de Supabase Auth, sin conexión a internet.
Uso (desde la carpeta backend):  python test_auth_cuidador.py
Requiere fastapi y httpx (pip install fastapi httpx).
"""
import os, tempfile
ruta_db = os.path.join(tempfile.gettempdir(), "domovida_ps01b.db")
if os.path.exists(ruta_db):
    os.remove(ruta_db)
os.environ["DATABASE_URL"] = "sqlite:///" + ruta_db
os.environ.pop("DOMOVIDA_API_KEY", None)
for v in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):
    os.environ.pop(v, None)

import requests
import routers.sensor_router as sr
sr.enviar_notificacion = lambda e: None  # sin ntfy durante la prueba
import auth_cuidador
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

def nueva_alerta():
    r = c.post("/api/sensor-data", json={"sensor_id": "boton_panico_sala", "tipo": "boton_panico",
                                         "habitacion": "sala", "valor": {"activado": True}, "alerta": True})
    return r.json()["id"]

class RespuestaFalsa:
    def __init__(self, codigo, datos=None):
        self.status_code = codigo; self._d = datos or {}
    def json(self):
        return self._d

TOKEN_OK = "token-valido"
def supabase_falso(url, headers=None, timeout=None):
    assert url == "https://proyecto-prueba.supabase.co/auth/v1/user"
    assert headers["apikey"] == "clave-publica-prueba"
    if headers["Authorization"] == f"Bearer {TOKEN_OK}":
        return RespuestaFalsa(200, {"email": "cuidador.prueba@domovida.cl"})
    return RespuestaFalsa(401, {"msg": "invalid JWT"})

def resolver(alerta_id, token=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return c.patch(f"/api/alertas/{alerta_id}/resolver", json={"resuelto_por": "Cuidador DomoVida"}, headers=h)

# 1. Sin configurar Supabase (modo desarrollo / borde): se puede atender sin sesión
caso("Auth desactivada: atender sin sesión", resolver(nueva_alerta()).status_code, 200)

# Activar la autenticación con un Supabase simulado
os.environ["SUPABASE_URL"] = "https://proyecto-prueba.supabase.co/"
os.environ["SUPABASE_ANON_KEY"] = "clave-publica-prueba"
auth_cuidador.requests.get = supabase_falso

a = nueva_alerta()
caso("Auth activa: sin sesión", resolver(a).status_code, 401)
caso("Auth activa: token inválido", resolver(a, "token-falso").status_code, 401)
r = resolver(a, TOKEN_OK)
caso("Auth activa: token válido", r.status_code, 200)
from database import SessionLocal
from models import Evento
db = SessionLocal(); ev = db.get(Evento, a); db.close()
caso("Se registra el correo del cuidador en resuelto_por", ev.resuelto_por, "cuidador.prueba@domovida.cl")
caso("La misma alerta no se puede atender dos veces", resolver(a, TOKEN_OK).status_code, 404)

def supabase_caido(*a, **k):
    raise requests.ConnectionError("sin conexión")
auth_cuidador.requests.get = supabase_caido
caso("Supabase no responde", resolver(nueva_alerta(), TOKEN_OK).status_code, 503)

print(f"\nResultado PS-01 (sesión del cuidador): {sum(casos)}/{len(casos)} casos aprobados")
