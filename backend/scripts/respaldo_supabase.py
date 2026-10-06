"""
Respaldo de las tablas de DomoVida (Supabase/PostgreSQL) en archivos JSON.

Lee DATABASE_URL desde backend/.env (o desde la variable de entorno) y guarda
cada tabla en un archivo JSON dentro de una carpeta con fecha y hora, FUERA del
repositorio. No muestra la cadena de conexión ni contraseñas.

Uso (desde la carpeta backend):
    python scripts/respaldo_supabase.py
    python scripts/respaldo_supabase.py C:\\ruta\\de\\respaldos      (carpeta opcional)

Por defecto guarda en:  <carpeta de usuario>/Documents/respaldos_domovida/AAAA-MM-DD_HHMM
"""
import json
import os
import sys
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND / ".env")
URL = os.getenv("DATABASE_URL", "")
if not URL.startswith("postgres"):
    sys.exit("DATABASE_URL no apunta a PostgreSQL (Supabase). Revisa backend/.env.")

base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "respaldos_domovida"
destino = base / datetime.now().strftime("%Y-%m-%d_%H%M")
destino.mkdir(parents=True, exist_ok=True)

def a_json(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return str(v)

engine = create_engine(URL)
resumen = {}
with engine.connect() as cx:
    tablas = [r[0] for r in cx.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"))]
    for t in tablas:
        filas = [dict(r._mapping) for r in cx.execute(text(f'SELECT * FROM public."{t}"'))]
        with open(destino / f"{t}.json", "w", encoding="utf-8") as f:
            json.dump(filas, f, ensure_ascii=False, default=a_json)
        columnas = [dict(r._mapping) for r in cx.execute(text(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :t ORDER BY ordinal_position"), {"t": t})]
        resumen[t] = {"filas": len(filas), "columnas": columnas}
        print(f"  {t}: {len(filas)} filas")

with open(destino / "_resumen.json", "w", encoding="utf-8") as f:
    json.dump({"fecha": datetime.now().isoformat(), "tablas": resumen}, f, ensure_ascii=False, indent=2)
print(f"\nRespaldo guardado en: {destino}")
