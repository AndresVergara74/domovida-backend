"""PR-03b · HU-03 · Sincronización real del modo borde con la nube (DomoVida).

Requiere el backend local en modo borde (SQLite + NUBE_API_URL) en http://localhost:8000.
Fase 1 (SIN internet): envía 5 caídas al backend local y muestra que quedan pendientes.
Fase 2 (CON internet): espera a que el sincronizador las suba y muestra los UUID enviados.
Uso (desde la carpeta backend):
    python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PR-03b_prueba_sincronizacion.py
"""
import datetime, json, sqlite3, sys, time, urllib.request

LOCAL = "http://localhost:8000"
BASE_SQLITE = "domovida_borde.db"


def get(ruta):
    with urllib.request.urlopen(LOCAL + ruta, timeout=10) as r:
        return json.loads(r.read())


def post(datos):
    req = urllib.request.Request(LOCAL + "/api/sensor-data", data=json.dumps(datos).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def ahora():
    return datetime.datetime.now().strftime("%H:%M:%S")


def sync():
    return get("/api/health")["sincronizacion_borde"]


def hay_internet():
    """Comprueba el acceso real a internet (navigator.onLine no sirve en Windows, ajuste 14)."""
    try:
        urllib.request.urlopen("https://ntfy.sh", timeout=5)
        return True
    except Exception:
        return False


print(f"[{ahora()}] PR-03b · estado inicial del sincronizador:", sync())
if not sync().get("activa"):
    sys.exit("❌ El backend local no está en modo borde (falta NUBE_API_URL).")

input("\n➡️  FASE 1: corta internet (modo avión y, si usas cable, desconéctalo) y presiona Enter...")
while hay_internet():
    input(f"[{ahora()}] ⚠️  Todavía HAY internet (ntfy.sh responde). Córtalo y presiona Enter otra vez...")
print(f"[{ahora()}] ✅ Sin internet confirmado: ntfy.sh no responde")
ids = []
for i in range(1, 6):
    ev = post({"sensor_id": "acelerometro_dormitorio", "tipo": "acelerometro", "habitacion": "dormitorio",
               "valor": {"z": 19.6, "prueba": "PR-03b", "n": i}, "alerta": True})
    ids.append(ev["id"])
    print(f"[{ahora()}] 🚨 caída {i}/5 guardada en el borde (id local {ev['id']})")
time.sleep(35)  # más de dos ciclos del sincronizador (15 s)
s = sync()
print(f"[{ahora()}] Sin internet → pendientes: {s['pendientes']} · último error: {s['ultimo_error']}")

input("\n➡️  FASE 2: vuelve a conectar internet y presiona Enter...")
while not hay_internet():
    input(f"[{ahora()}] ⚠️  Todavía NO hay internet. Reconecta y presiona Enter otra vez...")
print(f"[{ahora()}] ✅ Internet de vuelta")
inicio = time.time()
while time.time() - inicio < 180:
    s = sync()
    print(f"[{ahora()}] pendientes: {s['pendientes']} · enviados desde el inicio: {s['enviados_desde_inicio']}")
    if s["pendientes"] == 0:
        break
    time.sleep(10)

con = sqlite3.connect(BASE_SQLITE)
filas = con.execute(f"SELECT id, uuid, sync_status FROM eventos WHERE id IN ({','.join(map(str, ids))}) ORDER BY id").fetchall()
con.close()
print("\nEventos del borde (id local · uuid · estado):")
for f in filas:
    print("  ", f[0], f[1], f[2])
ok = all(f[2] == "synced" for f in filas) and len(filas) == 5
print(f"\n📊 PR-03b: {sum(f[2] == 'synced' for f in filas)}/5 caídas sincronizadas con la nube "
      f"en {int(time.time() - inicio)} s después de volver internet " + ("✅" if ok else "❌"))
print("\nPara comprobar en Supabase (SQL Editor):")
print("SELECT id, uuid, origen, \"timestamp\" FROM public.eventos WHERE uuid IN (" +
      ", ".join(f"'{f[1]}'" for f in filas) + ");")
