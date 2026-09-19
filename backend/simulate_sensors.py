"""
Simulador de Sensores IoT para DomoVida
Objetivo Específico 1: Diseñar la red de sensores IoT

Sensores simulados:
- Acelerómetro/Giroscopio (detección de caídas)
- Sensor PIR (detección de movimiento/inactividad)
- Sensor de Gas (emergencias ambientales)
- Sensor de Humo (emergencias ambientales)
- Sensor de Apertura (puertas/ventanas)
- Sensor Cardíaco (detección de infarto/arritmia)
- Botón de Pánico (evento manual del usuario)
"""

import requests
import random
import time
import math
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
API_URL = "http://localhost:8000/api/sensor-data"
INTERVALO_SEGUNDOS = 5

# Estado simulado del adulto mayor
estado_usuario = {
    "ultima_actividad": datetime.now(),
    "bpm_base": 75,  # Frecuencia cardíaca base en reposo
}


# ============================================================
# GENERADORES DE DATOS POR TIPO DE SENSOR
# ============================================================

def generar_datos_acelerometro():
    """Simula datos de acelerómetro y giroscopio. Detecta caída si la magnitud supera un umbral."""
    probabilidad_caida = 0.05  # 5% de probabilidad

    if random.random() < probabilidad_caida:
        ax = random.uniform(-15, 15)
        ay = random.uniform(-15, 15)
        az = random.uniform(15, 30)
        gx = random.uniform(-5, 5)
        gy = random.uniform(-5, 5)
        gz = random.uniform(-5, 5)
        caida = True
        print(f"🚨 ¡CAÍDA DETECTADA! Aceleración Z: {az:.2f} m/s²")
    else:
        ax = random.uniform(-2, 2)
        ay = random.uniform(-2, 2)
        az = random.uniform(8, 11)
        gx = random.uniform(-0.5, 0.5)
        gy = random.uniform(-0.5, 0.5)
        gz = random.uniform(-0.5, 0.5)
        caida = False

    magnitud = math.sqrt(ax**2 + ay**2 + az**2)

    return {
        "sensor_id": "acelerometro_dormitorio",
        "tipo": "acelerometro",
        "habitacion": "dormitorio",
        "valor": {
            "ax": round(ax, 2),
            "ay": round(ay, 2),
            "az": round(az, 2),
            "gx": round(gx, 2),
            "gy": round(gy, 2),
            "gz": round(gz, 2),
            "magnitud": round(magnitud, 2),
        },
        "alerta": caida,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_pir():
    """Simula sensor PIR de movimiento. Detecta inactividad prolongada (>12h)."""
    movimiento = random.random() < 0.8

    if movimiento:
        estado_usuario["ultima_actividad"] = datetime.now()

    minutos_inactivo = (
        datetime.now() - estado_usuario["ultima_actividad"]
    ).total_seconds() / 60

    alerta = minutos_inactivo > 12 * 60

    return {
        "sensor_id": "pir_living",
        "tipo": "pir",
        "habitacion": "living",
        "valor": {
            "movimiento": movimiento,
            "minutos_inactivo": round(minutos_inactivo, 2),
        },
        "alerta": alerta,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_gas():
    """Simula sensor de gas."""
    fuga = random.random() < 0.02
    nivel_ppm = random.uniform(200, 800) if fuga else random.uniform(0, 50)

    if fuga:
        print(f"🚨 ¡FUGA DE GAS! Nivel: {nivel_ppm:.2f} ppm")

    return {
        "sensor_id": "gas_cocina",
        "tipo": "gas",
        "habitacion": "cocina",
        "valor": {"nivel_ppm": round(nivel_ppm, 2)},
        "alerta": fuga,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_humo():
    """Simula sensor de humo."""
    humo = random.random() < 0.01
    nivel = random.uniform(500, 1000) if humo else random.uniform(0, 30)

    if humo:
        print(f"🚨 ¡HUMO DETECTADO! Nivel: {nivel:.2f}")

    return {
        "sensor_id": "humo_cocina",
        "tipo": "humo",
        "habitacion": "cocina",
        "valor": {"nivel": round(nivel, 2)},
        "alerta": humo,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_apertura(sensor_id, habitacion):
    """Simula sensor de apertura."""
    abierto = random.random() < 0.3
    alerta = abierto and habitacion == "entrada"

    return {
        "sensor_id": sensor_id,
        "tipo": "apertura",
        "habitacion": habitacion,
        "valor": {"abierto": abierto},
        "alerta": alerta,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_cardiaco():
    """
    Simula sensor cardíaco (wearable).
    Frecuencia normal: 60-90 bpm.
    Taquicardia (>150 bpm) o bradicardia severa (<40 bpm) = alerta crítica.
    """
    # 3% de probabilidad de evento cardíaco
    evento = random.random() < 0.03

    if evento:
        # 50% taquicardia, 50% bradicardia
        if random.random() < 0.5:
            bpm = random.uniform(150, 200)
            tipo_evento = "taquicardia"
            print(f"🚨 ¡TAQUICARDIA! {bpm:.0f} bpm")
        else:
            bpm = random.uniform(30, 40)
            tipo_evento = "bradicardia"
            print(f"🚨 ¡BRADICARDIA! {bpm:.0f} bpm")
        alerta = True
    else:
        # Frecuencia normal con pequeña variación
        bpm = estado_usuario["bpm_base"] + random.uniform(-10, 10)
        tipo_evento = "normal"
        alerta = False

    # SpO2 (oxígeno en sangre) — normal > 95%
    spo2 = random.uniform(95, 99) if not evento else random.uniform(85, 93)

    return {
        "sensor_id": "wearable_cardiaco",
        "tipo": "cardiovascular",
        "habitacion": "wearable",
        "valor": {
            "bpm": round(bpm, 1),
            "spo2": round(spo2, 1),
            "evento": tipo_evento,
        },
        "alerta": alerta,
        "timestamp": datetime.now().isoformat(),
    }


def generar_datos_boton_panico():
    """
    Simula botón de pánico.
    2% de probabilidad de que el usuario presione el botón.
    Cuando se activa, es una alerta crítica inmediata.
    """
    activado = random.random() < 0.02

    if activado:
        print("🚨 ¡BOTÓN DE PÁNICO ACTIVADO!")

    return {
        "sensor_id": "boton_panico_sala",
        "tipo": "boton_panico",
        "habitacion": "sala",
        "valor": {
            "activado": activado,
        },
        "alerta": activado,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================
# ENVÍO DE DATOS AL BACKEND
# ============================================================

def enviar_datos(datos):
    """Envía los datos al backend FastAPI."""
    try:
        response = requests.post(API_URL, json=datos, timeout=5)
        if response.status_code in [200, 201]:
            icono = "🚨" if datos.get("alerta") else "✅"
            print(f"{icono} {datos['sensor_id']:30s} | tipo: {datos['tipo']}")
        else:
            print(f"⚠️  Error HTTP {response.status_code}: {response.text[:100]}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Sin conexión al backend en {API_URL}")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

def main():
    print("=" * 65)
    print("🏠 DOMOVIDA - SIMULADOR DE SENSORES IoT")
    print("=" * 65)
    print(f"📡 Backend: {API_URL}")
    print(f"⏱️  Intervalo: {INTERVALO_SEGUNDOS} segundos")
    print("🛑 Presiona Ctrl+C para detener")
    print("=" * 65)

    contador = 0
    while True:
        try:
            contador += 1
            print(f"\n📊 Ciclo #{contador} - {datetime.now().strftime('%H:%M:%S')}")

            # Sensores ambientales
            enviar_datos(generar_datos_acelerometro())
            enviar_datos(generar_datos_pir())
            enviar_datos(generar_datos_gas())
            enviar_datos(generar_datos_humo())
            enviar_datos(generar_datos_apertura("apertura_puerta_principal", "entrada"))
            enviar_datos(generar_datos_apertura("apertura_ventana_living", "living"))

            # Sensores de emergencia médica
            enviar_datos(generar_datos_cardiaco())
            enviar_datos(generar_datos_boton_panico())

            time.sleep(INTERVALO_SEGUNDOS)

        except KeyboardInterrupt:
            print("\n\n🛑 Simulador detenido por el usuario.")
            break
        except Exception as e:
            print(f"❌ Error en ciclo: {e}")
            time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    main()