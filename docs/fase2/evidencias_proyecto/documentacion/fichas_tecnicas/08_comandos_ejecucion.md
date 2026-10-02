\# Ficha 8: Comandos de Ejecución



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 8.1 Descripción General



Esta ficha documenta todos los comandos necesarios para ejecutar DomoVida en un entorno de desarrollo local. Sirve como guía de instalación y también como evidencia técnica de reproducibilidad del proyecto.



\---



\## 8.2 Requisitos Previos



| Herramienta    | Versión       | Propósito                   |

|----------------|---------------|-----------------------------|

| Python         | 3.12+         | Backend FastAPI + Simulador |

| Node.js        | 18+           | Frontend React              |

| npm            | 9+            | Gestor de paquetes de Node  |

| Git            | Última        | Control de versiones        |

| Navegador      | Chrome / Edge | Ver el dashboard            |



\---



\## 8.3 Estructura de Carpetas



```

domovida-backend/

├── backend/              # API FastAPI

│   ├── main.py

│   ├── database.py

│   ├── models.py

│   ├── schemas.py

│   ├── routers/

│   ├── simulate\_sensors.py

│   └── domovida.db

├── frontend/             # Dashboard React

│   ├── src/

│   ├── public/

│   ├── package.json

│   └── .env

├── docs/

│   └── evidencias\_OE1/   # Estas fichas

└── README.md









\## 8.4 Paso 1: Clonar el Repositorio



&#x20;  bash

git clone https://github.com/AndresVergara74/domovida-backend.git

cd domovida-backend









\## 8.5 Paso 2: Ejecutar el Backend



\*\*Terminal 1:\*\*



&#x20;  bash

cd backend

python -m pip install -r requirements.txt

python -m uvicorn main:app --reload





\*\*Salida esperada:\*\*



```

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

INFO:     Started reloader process \[xxxxx] using WatchFiles

INFO:     Application startup complete.

```



\*\*Verificación:\*\* Abrir en el navegador `http://localhost:8000/docs` y ver los 4 endpoints.







\## 8.6 Paso 3: Ejecutar el Simulador de Sensores



\*\*Terminal 2:\*\*



&#x20;  bash

cd backend

python simulate\_sensors.py





\*\*Salida esperada:\*\*





🏠 DOMOVIDA - SIMULADOR DE SENSORES IoT

📡 Backend: http://localhost:8000/api/sensor-data

⏱️  Intervalo: 5 segundos



📊 Ciclo #1 - 21:33:07

✅ acelerometro\_dormitorio      | tipo: acelerometro

✅ pir\_living                   | tipo: pir

✅ gas\_cocina                   | tipo: gas











\## 8.7 Paso 4: Ejecutar el Frontend



\*\*Terminal 3:\*\*



&#x20;  bash

cd frontend

npm install

npm run dev





\*\*Salida esperada:\*\*





VITE v8.2.2  ready in 523 ms

➜  Local:   http://localhost:5173/





\*\*Verificación:\*\* Abrir en el navegador `http://localhost:5173/` y ver el dashboard.







\## 8.8 Resumen Visual



```

┌──────────────────────┐

│   Terminal 1         │

│   Backend FastAPI    │

│   Puerto: 8000       │

└──────────┬───────────┘

&#x20;          │

&#x20;          │ HTTP POST /api/sensor-data

&#x20;          │

┌──────────▼───────────┐

│   Terminal 2         │

│   Simulador Sensores │

│   Envía cada 5s      │

└──────────────────────┘



┌──────────────────────┐

│   Terminal 3         │

│   Frontend React     │

│   Puerto: 5173       │

└──────────┬───────────┘

&#x20;          │

&#x20;          │ HTTP GET /api/eventos

&#x20;          │ HTTP GET /api/alertas/\*

&#x20;          │

&#x20;          ▼

&#x20;   \[Navegador Web]

&#x20;   http://localhost:5173









\## 8.9 Comandos de Git



\### Ver estado del repositorio



&#x20;  bash

git status





\### Agregar cambios



&#x20;  bash

git add .





\### Hacer commit



&#x20;  bash

git commit -m "mensaje descriptivo"





\### Subir a GitHub



&#x20;  bash

git push





\### Ver historial



&#x20;  bash

git log --oneline









\## 8.10 Comandos Útiles Adicionales



\### Verificar la base de datos SQLite3



&#x20;  bash

ls backend/domovida.db





\### Consultar cantidad de eventos



Abrir en el navegador:



http://localhost:8000/api/eventos





\### Ver documentación interactiva de la API





http://localhost:8000/docs





\### Ver todas las alertas activas





http://localhost:8000/api/alertas/activas





\### Ver estado de inactividad





http://localhost:8000/api/alertas/inactividad









\## 8.11 Solución de Problemas Comunes



\### Error: `Could not import module "main"`



\*\*Causa:\*\* Estás ejecutando uvicorn desde la carpeta incorrecta.



\*\*Solución:\*\* Asegúrate de estar en la carpeta `backend`:

&#x20;  bash

cd backend

python -m uvicorn main:app --reload





\### Error: CORS bloqueado en el navegador



\*\*Causa:\*\* El frontend y el backend están en puertos diferentes.



\*\*Solución:\*\* Verificar que `main.py` incluya los orígenes correctos:

&#x20;  python

allow\_origins=\["http://localhost:5173", "http://localhost:3000"]





\### Error: `sensores.filter is not a function`



\*\*Causa:\*\* El endpoint `/api/alertas/inactividad` no devuelve un array.



\*\*Solución:\*\* Verificar que el router devuelva una lista `resultado` (no un objeto con `sensores\_inactivos`).



\### Error: No se ven datos en el dashboard



\*\*Causa:\*\* El simulador no está corriendo o el backend está caído.



\*\*Solución:\*\*

1\. Verificar que las 3 terminales estén activas

2\. Revisar que el backend responda en `http://localhost:8000/api/eventos`

3\. Recargar el dashboard con `F5`







\## 8.12 Orden de Inicio Recomendado



Para un arranque limpio del sistema:



1\. \*\*Terminal 1:\*\* Backend (uvicorn)

2\. \*\*Terminal 2:\*\* Simulador de sensores

3\. \*\*Terminal 3:\*\* Frontend (npm run dev)

4\. \*\*Navegador:\*\* Abrir `http://localhost:5173/`



En 10 segundos, el dashboard empezará a mostrar datos en tiempo real.







\## 8.13 Estado de Validación



| Comando                               | Estado       |

|---------------------------------------|------------ -|

| `python -m uvicorn main:app --reload` | ✅ Funciona  |

| `python simulate\_sensors.py`          | ✅ Funciona  |

| `npm run dev`                         | ✅ Funciona  |

| `git add .`                           | ✅ Funciona  |

| `git commit -m "..."`                 | ✅ Funciona  |

| `git push`                            | ✅ Funciona  |







\## 8.14 Próximos Comandos (Objetivo 2 — AWS)



&#x20;  bash

\# Futuro: Despliegue en AWS

aws ec2 run-instances ...

aws rds create-db-instance ...

aws s3 mb s3://domovida-backups ...





\*(Se documentará cuando se implemente el Objetivo 2)\*




