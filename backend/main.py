from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    sensor_router,
    evento_router,
    alerta_router,
    health_router,
    websocket_router,
)

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DomoVida API",
    version="0.3.0",
    description="Backend para monitoreo de adultos mayores con WebSocket en tiempo real"
)

# CORS - permite frontend en Vite (5173, 5174), CRA (3000) y producción en Vercel
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
        # Producción en Vercel
        "https://domovida-backend.vercel.app",
        "https://domovida-backend-git-main-andresvergara74.vercel.app",
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
            "websocket": "wss://domovida-backend.onrender.com/api/ws/alertas",
            "docs": "/docs",
        },
    }