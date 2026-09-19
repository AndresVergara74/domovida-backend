from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import sensor_router, evento_router, alerta_router

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DomoVida API",
    version="0.1.0",
    description="Backend para monitoreo de adultos mayores"
)

# CORS - permite frontend en Vite (5173) y CRA (3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(sensor_router.router, prefix="/api", tags=["Sensores"])
app.include_router(evento_router.router, prefix="/api", tags=["Eventos"])
app.include_router(alerta_router.router, prefix="/api", tags=["Alertas"])

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a DomoVida API", "version": "0.1.0"}