# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

# Importar routers (los crearemos en el Paso 3)
# from app.routers import events

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DomoVida API",
    description="Plataforma IoT de detección de caídas y aviso de emergencias médicas",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "DomoVida API - Fase 2", "status": "ok"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "version": "0.1.0"}