"""PU-02 · Prueba unitaria de las reglas de detección por umbral (reglas_sensores.py, HU-04 y HU-05).
Uso (desde la carpeta backend):  python test_reglas_sensores.py
"""
from datetime import datetime, timedelta, timezone
from reglas_sensores import evaluar_sensor, reiniciar_estado

casos = []


def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)


T0 = datetime(2026, 10, 31, 15, 0, tzinfo=timezone.utc)

# Caída (acelerómetro, umbral 17 m/s²)
caso("Acelerómetro en reposo (9,8 m/s²)", evaluar_sensor("acc", "acelerometro", {"magnitud": 9.8}), (False, None))
caso("Acelerómetro justo en 17 m/s² (no supera)", evaluar_sensor("acc", "acelerometro", {"magnitud": 17.0}), (False, None))
caso("Caída: 24,5 m/s²", evaluar_sensor("acc", "acelerometro", {"magnitud": 24.5}), (True, "caida"))
caso("Caída calculada desde los ejes (az = 25)", evaluar_sensor("acc", "acelerometro", {"ax": 1, "ay": 1, "az": 25}), (True, "caida"))

# Gas (umbral 500 ppm)
caso("Gas normal: 40 ppm", evaluar_sensor("gas", "gas", {"nivel_ppm": 40}), (False, None))
caso("Gas 200 ppm (antes el simulador lo marcaba como fuga)", evaluar_sensor("gas", "gas", {"nivel_ppm": 200}), (False, None))
caso("Fuga de gas: 620 ppm", evaluar_sensor("gas", "gas", {"nivel_ppm": 620}), (True, "gas_sobre_umbral"))

# Humo (umbral 800)
caso("Humo normal: 20", evaluar_sensor("humo", "humo", {"nivel": 20}), (False, None))
caso("Humo detectado: 850", evaluar_sensor("humo", "humo", {"nivel": 850}), (True, "humo_sobre_umbral"))

# Sin el valor que la regla necesita: se respeta el aviso del sensor
caso("Lectura sin valor medido: la regla no opina", evaluar_sensor("humo", "humo", {"detectado": True}), (None, None))
caso("Tipo sin regla de umbral (botón de pánico)", evaluar_sensor("boton", "boton_panico", {"presionado": True}), (None, None))

# Inactividad (sensor PIR, umbral 30 min)
reiniciar_estado()
caso("PIR: movimiento a las 15:00", evaluar_sensor("pir", "pir", {"movimiento": True}, T0), (False, None))
caso("PIR: 20 min sin movimiento", evaluar_sensor("pir", "pir", {"movimiento": False}, T0 + timedelta(minutes=20)), (False, None))
caso("PIR: 31 min sin movimiento → alerta", evaluar_sensor("pir", "pir", {"movimiento": False}, T0 + timedelta(minutes=31)), (True, "inactividad"))
caso("PIR: 45 min sin movimiento (no repite)", evaluar_sensor("pir", "pir", {"movimiento": False}, T0 + timedelta(minutes=45)), (False, None))
caso("PIR: vuelve el movimiento", evaluar_sensor("pir", "pir", {"movimiento": True}, T0 + timedelta(minutes=46)), (False, None))
caso("PIR: 31 min después, nuevo período → alerta", evaluar_sensor("pir", "pir", {"movimiento": False}, T0 + timedelta(minutes=78)), (True, "inactividad"))

print(f"\nResultado: {sum(casos)}/{len(casos)} casos aprobados")
raise SystemExit(0 if all(casos) else 1)
