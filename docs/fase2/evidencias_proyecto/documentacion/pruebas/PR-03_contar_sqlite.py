"""PR-03 · Cuenta en la base SQLite local los eventos de la prueba sin conexión.
Uso (desde la carpeta backend):  python ../docs/fase2/evidencias_proyecto/documentacion/pruebas/PR-03_contar_sqlite.py
"""
import sqlite3, sys
db = sys.argv[1] if len(sys.argv) > 1 else "domovida_offline.db"
con = sqlite3.connect(db)
filas = con.execute("SELECT id, tipo, alerta, timestamp FROM eventos WHERE valor LIKE '%PR03-%' ORDER BY id").fetchall()
print(f"Base de datos: {db}")
print(f"Eventos de la prueba PR-03 guardados en SQLite: {len(filas)}")
for f in filas:
    print("  ", f)
try:
    al = con.execute("SELECT COUNT(*) FROM alertas").fetchone()[0]
    print(f"Filas en la tabla alertas: {al}")
except Exception as e:
    print("Tabla alertas:", e)
