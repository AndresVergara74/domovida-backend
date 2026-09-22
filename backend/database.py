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