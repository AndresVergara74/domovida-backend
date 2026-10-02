from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    sensor_router,
    evento_router,
    alerta_router,
    health_router,
    websocket_router,
    fhir_router,
)

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DomoVida API",
    version="0.3.0",
    description="Backend para monitoreo de adultos mayores con WebSocket en tiempo real"
)

# CORS - orígenes permitidos: desarrollo local, Docker local, Vercel
# y orígenes extra definidos en la variable de entorno CORS_ORIGINS
# (por ejemplo, la IP pública de AWS EC2, que cambia en cada sesión del Learner Lab)
import os

origenes_extra = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Desarrollo local
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        # Docker local (frontend en Nginx, puerto 80)
        "http://localhost",
        # Producción en Vercel
        "https://domovida-backend.vercel.app",
        "https://domovida-backend-git-main-andresvergara74.vercel.app",
        # Orígenes adicionales desde CORS_ORIGINS
        *origenes_extra,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers REST
app.include_router(sensor_router.router, prefix="/api", tags=["Sensores"])
app.include_router(evento_router.router, prefix="/api", tags=["Eventos"])
app.include_router(alerta_router.router, prefix="/api", tags=["Alertas"])
app.include_router(health_router.router, prefix="/api", tags=["Health"])
app.include_router(fhir_router.router, prefix="/api", tags=["HL7 FHIR"])

# Incluir router WebSocket
app.include_router(websocket_router.router, prefix="/api", tags=["WebSocket"])


@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a DomoVida API",
        "version": "0.3.0",
        "endpoints": {
            "sensores": "/api/sensor-data",
            "eventos": "/api/eventos",
            "alertas": "/api/alertas/activas",
            "inactividad": "/api/alertas/inactividad",
            "resolver_alerta": "PATCH /api/alertas/{id}/resolver",
            "health": "/api/health",
            "fhir": "/api/fhir/Observation",
            "websocket": "wss://domovida-backend.onrender.com/api/ws/alertas",
            "docs": "/docs",
        },
    }