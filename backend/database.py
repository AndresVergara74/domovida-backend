"""
Configuración de la base de datos para DomoVida.
Soporta SQLite3 (local/edge) y PostgreSQL (AWS RDS).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./domovida.db")

# SQLite necesita check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia para obtener una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()