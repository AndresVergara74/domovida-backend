"""
Configuración de base de datos para DomoVida.
Soporta SQLite (desarrollo local) y PostgreSQL (producción en Neon).
La cadena de conexión se lee desde la variable de entorno DATABASE_URL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Leer la cadena de conexión
# Si no existe DATABASE_URL, usa SQLite por defecto (desarrollo)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./domovida.db")

# Configurar el engine según el tipo de base de datos
if DATABASE_URL.startswith("sqlite"):
    # SQLite: necesita check_same_thread=False para FastAPI
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL: usar pool_pre_ping para reconectar si la conexión se cae
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI para obtener una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def asegurar_columnas_borde():
    """HU-03: agrega a una base SQLite existente las columnas nuevas de `eventos`.
    En PostgreSQL (Supabase) esto lo hace la migración 003."""
    if not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if "eventos" not in insp.get_table_names():
        return
    existentes = {c["name"] for c in insp.get_columns("eventos")}
    nuevas = {
        "uuid": "VARCHAR(36)",
        "origen": "VARCHAR(10) DEFAULT 'nube'",
        "sync_status": "VARCHAR",
        "notificado": "BOOLEAN DEFAULT 0",
    }
    with engine.begin() as con:
        for nombre, tipo in nuevas.items():
            if nombre not in existentes:
                con.execute(text(f"ALTER TABLE eventos ADD COLUMN {nombre} {tipo}"))
        con.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_eventos_uuid ON eventos (uuid)"))

