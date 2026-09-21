"""
Notificador de alertas para DomoVida.
Envía notificaciones push al teléfono del cuidador mediante ntfy.sh.

IMPORTANTE - Política de Privacidad:
Este módulo aplica el principio de MINIMIZACIÓN DE DATOS conforme a la
Ley N° 21.719. Las notificaciones NO contienen datos biomédicos sensibles
(bpm, SpO2) ni identificadores personales (RUT, nombres). Los detalles
completos quedan disponibles únicamente en el dashboard autenticado.
"""

import requests
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
# Topic seudonimizado (difícil de adivinar)
NTFY_TOPIC = "domovida-seguro-2026"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


# ============================================================
# PLANTILLAS DE MENSAJES SEUDONIMIZADOS
# ============================================================

def formatear_alerta(evento: dict) -> tuple:
    """
    Recibe un evento del backend y devuelve (titulo, mensaje, prioridad).
    Los mensajes son SEUDONIMIZADOS: no incluyen datos biomédicos específicos.
    """
    tipo = evento.get("tipo", "desconocido")
    habitacion = evento.get("habitacion", "sin_ubicacion")
    valor = evento.get("valor", {})
    hora = datetime.now().strftime("%H:%M:%S")

    # --- CAÍDA ---
    if tipo == "acelerometro" and valor.get("magnitud", 0) > 20:
        return (
            "🚨 CAÍDA DETECTADA",
            f"Evento crítico en {habitacion}.\n"
            f"Revisar panel DomoVida.\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- EMERGENCIA CARDÍACA ---
    if tipo == "cardiovascular":
        evento_card = valor.get("evento", "normal")

        if evento_card == "taquicardia":
            return (
                "🚨 EVENTO CARDÍACO",
                f"Frecuencia cardíaca anómala detectada.\n"
                f"Revisar panel DomoVida.\n"
                f"Hora: {hora}",
                "urgent",
            )

        if evento_card == "bradicardia":
            return (
                "🚨 EVENTO CARDÍACO",
                f"Frecuencia cardíaca anómala detectada.\n"
                f"Revisar panel DomoVida.\n"
                f"Hora: {hora}",
                "urgent",
            )

    # --- BOTÓN DE PÁNICO ---
    if tipo == "boton_panico" and valor.get("activado"):
        return (
            "🚨 BOTÓN DE PÁNICO",
            f"El usuario activó el botón de pánico.\n"
            f"Ubicación: {habitacion}\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- FUGA DE GAS ---
    if tipo == "gas" and valor.get("nivel_ppm", 0) > 200:
        return (
            "🚨 FUGA DE GAS",
            f"Concentración anómala detectada en {habitacion}.\n"
            f"Revisar panel DomoVida.\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- HUMO ---
    if tipo == "humo" and valor.get("nivel", 0) > 500:
        return (
            "🚨 HUMO DETECTADO",
            f"Nivel anómalo detectado en {habitacion}.\n"
            f"Revisar panel DomoVida.\n"
            f"Hora: {hora}",
            "urgent",
        )

    # --- APERTURA ---
    if tipo == "apertura" and valor.get("abierto"):
        if habitacion == "entrada":
            return (
                "🚪 PUERTA PRINCIPAL ABIERTA",
                f"La puerta de entrada se encuentra abierta.\n"
                f"Hora: {hora}",
                "high",
            )
        if habitacion == "living":
            return (
                "🪟 VENTANA ABIERTA",
                f"Ventana del living abierta.\n"
                f"Hora: {hora}",
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
        f"Evento detectado en {habitacion}.\nHora: {hora}",
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
    print(f"📡 Topic: {NTFY_TOPIC}")
    print()

    # Prueba 1: Caída
    enviar_notificacion({
        "sensor_id": "acelerometro_dormitorio",
        "tipo": "acelerometro",
        "habitacion": "dormitorio",
        "valor": {"magnitud": 26.53},
        "alerta": True,
    })

    # Prueba 2: Evento cardíaco
    enviar_notificacion({
        "sensor_id": "wearable_cardiaco",
        "tipo": "cardiovascular",
        "habitacion": "wearable",
        "valor": {"bpm": 175, "spo2": 88, "evento": "taquicardia"},
        "alerta": True,
    })

    # Prueba 3: Botón de pánico
    enviar_notificacion({
        "sensor_id": "boton_panico_sala",
        "tipo": "boton_panico",
        "habitacion": "sala",
        "valor": {"activado": True},
        "alerta": True,
    })

    print()
    print("✅ Pruebas completadas. Revisa tu teléfono/navegador.")