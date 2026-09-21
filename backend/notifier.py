"""
Notificador de alertas para DomoVida.
Envía notificaciones push al teléfono del cuidador mediante ntfy.sh.
"""

import requests
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
NTFY_TOPIC = "domovida-alertas-2026"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


# ============================================================
# PLANTILLAS DE MENSAJES POR TIPO DE ALERTA
# ============================================================

def formatear_alerta(evento: dict) -> tuple:
    """
    Recibe un evento del backend y devuelve (titulo, mensaje, prioridad).
    """
    tipo = evento.get("tipo", "desconocido")
    sensor_id = evento.get("sensor_id", "sin_id")
    habitacion = evento.get("habitacion", "sin_ubicacion")
    valor = evento.get("valor", {})
    hora = datetime.now().strftime("%H:%M:%S")

    # --- CAÍDA ---
    if tipo == "acelerometro" and valor.get("magnitud", 0) > 20:
        return (
            "🚨 CAÍDA DETECTADA",
            f"Se detectó una caída en {habitacion}.\n"
            f"Magnitud: {valor.get('magnitud')} m/s²\n"
            f"Sensor: {sensor_id}\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- EMERGENCIA CARDÍACA ---
    if tipo == "cardiovascular":
        bpm = valor.get("bpm", 0)
        spo2 = valor.get("spo2", 0)
        evento_card = valor.get("evento", "normal")

        if evento_card == "taquicardia":
            return (
                "🚨 TAQUICARDIA DETECTADA",
                f"Frecuencia cardíaca elevada: {bpm} bpm\n"
                f"SpO2: {spo2}%\n"
                f"Hora: {hora}",
                "urgent",
            )

        if evento_card == "bradicardia":
            return (
                "🚨 BRADICARDIA DETECTADA",
                f"Frecuencia cardíaca baja: {bpm} bpm\n"
                f"SpO2: {spo2}%\n"
                f"Hora: {hora}",
                "urgent",
            )

    # --- BOTÓN DE PÁNICO ---
    if tipo == "boton_panico" and valor.get("activado"):
        return (
            "🚨 BOTÓN DE PÁNICO ACTIVADO",
            f"El adulto mayor activó el botón de pánico.\n"
            f"Ubicación: {habitacion}\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- FUGA DE GAS ---
    if tipo == "gas" and valor.get("nivel_ppm", 0) > 200:
        return (
            "🚨 FUGA DE GAS DETECTADA",
            f"Nivel de gas: {valor.get('nivel_ppm')} ppm\n"
            f"Ubicación: {habitacion}\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- HUMO ---
    if tipo == "humo" and valor.get("nivel", 0) > 500:
        return (
            "🚨 HUMO DETECTADO",
            f"Nivel de humo: {valor.get('nivel')}\n"
            f"Ubicación: {habitacion}\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- APERTURA (con títulos descriptivos por ubicación) ---
    if tipo == "apertura" and valor.get("abierto"):
        if habitacion == "entrada":
            return (
                "🚪 PUERTA PRINCIPAL ABIERTA",
                f"La puerta de entrada se encuentra abierta.\n"
                f"Sensor: {sensor_id}\n"
                f"Hora: {hora}",
                "high",
            )
        if habitacion == "living":
            return (
                "🪟 VENTANA DEL LIVING ABIERTA",
                f"La ventana del living se encuentra abierta.\n"
                f"Sensor: {sensor_id}\n"
                f"Hora: {hora}",
                "default",
            )
        # Apertura genérica
        return (
            f"🚪 APERTURA DETECTADA en {habitacion}",
            f"Sensor: {sensor_id}\nHora: {hora}",
            "default",
        )

    # --- INACTIVIDAD PROLONGADA ---
    if tipo == "pir" and valor.get("minutos_inactivo", 0) > 12 * 60:
        return (
            "⚠️ INACTIVIDAD PROLONGADA",
            f"Sin movimiento detectado por más de 12 horas.\n"
            f"Ubicación: {habitacion}\n"
            f"Hora: {hora}",
            "high",
        )

    # --- ALERTA GENÉRICA ---
    return (
        f"⚠️ Alerta: {tipo}",
        f"Evento detectado en {habitacion}. Sensor: {sensor_id}\nHora: {hora}",
        "default",
    )


# ============================================================
# ENVÍO DE NOTIFICACIÓN
# ============================================================

def enviar_notificacion(evento: dict) -> bool:
    """
    Envía una notificación push si el evento tiene alerta=True.
    Devuelve True si se envió correctamente.
    """
    if not evento.get("alerta"):
        return False

    titulo, mensaje, prioridad = formatear_alerta(evento)

    try:
        response = requests.post(
            NTFY_URL,
            data=mensaje.encode("utf-8"),
            headers={
                "Title": titulo.encode("utf-8"),
                "Priority": prioridad,
                "Tags": "rotating_light,warning",
            },
            timeout=5,
        )
        if response.status_code == 200:
            print(f"📱 Notificación enviada: {titulo}")
            return True
        else:
            print(f"⚠️ Error ntfy HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return False


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":
    print("🧪 Probando notificador de DomoVida...")

    # Prueba 1: Caída
    enviar_notificacion({
        "sensor_id": "acelerometro_dormitorio",
        "tipo": "acelerometro",
        "habitacion": "dormitorio",
        "valor": {"magnitud": 26.53},
        "alerta": True,
    })

    # Prueba 2: Apertura de puerta principal
    enviar_notificacion({
        "sensor_id": "apertura_puerta_principal",
        "tipo": "apertura",
        "habitacion": "entrada",
        "valor": {"abierto": True},
        "alerta": True,
    })

    print("✅ Pruebas completadas. Revisa tu teléfono.")