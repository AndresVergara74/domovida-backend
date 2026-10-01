# ============================================================
# DomoVida - Frontend React
# Build multi-etapa: compila con Node, sirve con Nginx
# ============================================================

# ============================================================
# ETAPA 1: BUILD (compilación)
# ============================================================
FROM node:18-alpine AS builder

LABEL maintainer="Andrés Vergara <andres.vergara@duocuc.cl>"
LABEL description="DomoVida - Frontend React"

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias (usar ci si hay package-lock.json)
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copiar el resto del código
COPY . .

# URL del backend y del WebSocket para el build de Vite
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ARG VITE_WS_URL=ws://localhost:8000/api/ws/alertas
ENV VITE_WS_URL=$VITE_WS_URL

# Compilar la aplicación React
RUN npx vite build

# ============================================================
# ETAPA 2: SERVE (servidor de producción)
# ============================================================
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]