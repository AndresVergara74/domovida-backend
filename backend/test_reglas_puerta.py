"""PU-04 · Prueba unitaria de la regla de la puerta principal (reglas_puerta.py).
Uso (desde la carpeta backend):  python test_reglas_puerta.py
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from reglas_puerta import evaluar_puerta, reiniciar_estado

CL = ZoneInfo("America/Santiago")
S = "apertura_puerta_principal"
casos = []

def caso(nombre, obtenido, esperado):
    ok = obtenido == esperado
    casos.append(ok)
    print(("✅" if ok else "❌"), nombre, "→", obtenido)

# 1. Apertura de día: no alerta
reiniciar_estado()
caso("Apertura a las 15:00 (día)", evaluar_puerta(S, True, datetime(2026, 10, 5, 15, 0, tzinfo=CL))[:2], (False, None))

# 2. Sigue abierta 5 min: no alerta
caso("Sigue abierta 5 min", evaluar_puerta(S, True, datetime(2026, 10, 5, 15, 5, tzinfo=CL))[:2], (False, None))

# 3. Abierta 10 min: alerta por tiempo
caso("Abierta 10 min", evaluar_puerta(S, True, datetime(2026, 10, 5, 15, 10, tzinfo=CL))[:2], (True, "abierta_mucho_tiempo"))

# 4. Abierta 15 min: no repite la alerta
caso("Abierta 15 min (no repite)", evaluar_puerta(S, True, datetime(2026, 10, 5, 15, 15, tzinfo=CL))[:2], (False, None))

# 5. Se cierra: no alerta y reinicia
caso("Se cierra", evaluar_puerta(S, False, datetime(2026, 10, 5, 15, 16, tzinfo=CL))[:2], (False, None))

# 6. Apertura nocturna a las 23:30: alerta
caso("Apertura a las 23:30 (noche)", evaluar_puerta(S, True, datetime(2026, 10, 5, 23, 30, tzinfo=CL))[:2], (True, "apertura_nocturna"))

# 7. Sigue abierta 1 min de noche: no repite
caso("Sigue abierta de noche (no repite)", evaluar_puerta(S, True, datetime(2026, 10, 5, 23, 31, tzinfo=CL))[:2], (False, None))

# 8. Apertura a las 06:59: noche
reiniciar_estado()
caso("Apertura a las 06:59 (noche)", evaluar_puerta(S, True, datetime(2026, 10, 6, 6, 59, tzinfo=CL))[:2], (True, "apertura_nocturna"))

# 9. Apertura a las 07:00: día
reiniciar_estado()
caso("Apertura a las 07:00 (día)", evaluar_puerta(S, True, datetime(2026, 10, 6, 7, 0, tzinfo=CL))[:2], (False, None))

# 10. Hora en UTC: 02:30 UTC = 23:30 en Chile (horario de verano, UTC-3) -> noche
reiniciar_estado()
caso("02:30 UTC = 23:30 Chile (noche)", evaluar_puerta(S, True, datetime(2026, 10, 6, 2, 30, tzinfo=ZoneInfo("UTC")))[:2], (True, "apertura_nocturna"))

print(f"\nResultado: {sum(casos)}/{len(casos)} casos aprobados")
