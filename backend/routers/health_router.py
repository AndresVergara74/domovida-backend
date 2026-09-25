"""
Router de Health Check para DomoVida.

Proporciona el estado de salud de cada componente del sistema:
- Raspberry Pi (Edge)
- API FastAPI
- PostgreSQL (Supabase)
- MQTT Broker
- ntfy (Notificaciones)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import requests
import os
from datetime import datetime

router = APIRouter()


# ============================================================
# CONFIGURACIÓN
# ============================================================
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "domovida-seguro-2026")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


# ============================================================
# HEALTH CHECK DE COMPONENTES
# ============================================================

def check_postgresql(db: Session) -> dict:
    """Verifica la conexión a PostgreSQL (Supabase)."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "nombre": "PostgreSQL (Supabase)",
            "icono": "🗄️",
            "online": True,
            "mensaje": "Conexión activa",
            "latencia_ms": None,
        }
    except Exception as e:
        return {
            "nombre": "PostgreSQL (Supabase)",
            "icono": "🗄️",
            "online": False,
            "mensaje": f"Error: {str(e)[:50]}",
            "latencia_ms": None,
        }


def check_ntfy() -> dict:
    """Verifica que ntfy.sh esté accesible."""
    try:
        # Verificar que el servidor de ntfy responde
        response = requests.get(
            f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1&since=all",
            timeout=5,
        )
        return {
            "nombre": "ntfy (Notificaciones)",
            "icono": "📱",
            "online": response.status_code == 200,
            "mensaje": "Servicio activo",
            "latencia_ms": round(response.elapsed.total_seconds() * 1000, 2),
        }
    except Exception as e:
        return {
            "nombre": "ntfy (Notificaciones)",
            "icono": "📱",
            "online": False,
            "mensaje": f"Error: {str(e)[:50]}",
            "latencia_ms": None,
        }


def check_raspberry_pi() -> dict:
    """
    Verifica el estado de la Raspberry Pi (Edge).
    
    NOTA: Actualmente simulado. En producción, la Raspberry Pi
    enviará un heartbeat periódico al backend.
    """
    return {
        "nombre": "Raspberry Pi (Edge)",
        "icono": "🍓",
        "online": True,  # Simulado
        "mensaje": "Modo simulado",
        "latencia_ms": None,
    }


def check_mqtt() -> dict:
    """
    Verifica el estado del broker MQTT.
    
    NOTA: Actualmente simulado. En producción, se verificará
    la conexión al broker MQTT (Mosquitto o similar).
    """
    return {
        "nombre": "MQTT Broker",
        "icono": "📡",
        "online": True,  # Simulado
        "mensaje": "Modo simulado",
        "latencia_ms": None,
    }


# ============================================================
# ENDPOINT DE HEALTH CHECK
# ============================================================

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Devuelve el estado de salud de cada componente de DomoVida.
    
    Retorna:
    - estado_general: "healthy" | "degraded" | "unhealthy"
    - componentes: Lista con el estado de cada componente
    - timestamp: Fecha y hora de la verificación
    """
    componentes = [
        check_raspberry_pi(),
        {
            "nombre": "API FastAPI",
            "icono": "⚙️",
            "online": True,  # Si responde, está online
            "mensaje": "Servicio activo",
            "latencia_ms": None,
        },
        check_postgresql(db),
        check_mqtt(),
        check_ntfy(),
    ]

    # Calcular estado general
    total = len(componentes)
    online = sum(1 for c in componentes if c["online"])

    if online == total:
        estado_general = "healthy"
    elif online >= total / 2:
        estado_general = "degraded"
    else:
        estado_general = "unhealthy"

    return {
        "estado_general": estado_general,
        "componentes_online": online,
        "componentes_total": total,
        "componentes": componentes,
        "timestamp": datetime.utcnow().isoformat(),
    }