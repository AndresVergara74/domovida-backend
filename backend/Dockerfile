# ============================================================
# DomoVida - Backend FastAPI
# Imagen Docker para despliegue en Render, AWS EC2 y local
# ============================================================

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Andrés Vergara <andres.vergara@duocuc.cl>"
LABEL description="DomoVida - Backend FastAPI"
LABEL version="0.3.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (mejor caché de capas)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Healthcheck para verificar que el servicio responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]