\# Ficha 5: Base de Datos



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 5.1 Descripción General



DomoVida utiliza una \*\*arquitectura de persistencia híbrida\*\* que combina una base de datos local (Edge) con una base de datos en la nube. Esta estrategia garantiza continuidad operativa incluso ante fallas de conectividad, y prepara al sistema para escalar a cientos de hogares.



\---



\## 5.2 Arquitectura Híbrida



┌──────────────────────────────────────────────────┐

│ CAPA LOCAL (Edge Computing)                      │

│                                                  │

│ SQLite3 → backend/domovida.db                    │

│ • Persistencia rápida                            │

│ • Sin dependencia de internet                    │

│ • Resiliencia ante fallas de red                 │

└──────────────────────────────────────────────────┘

↕

(sincronización futura)

↕

┌──────────────────────────────────────────────────┐

│ CAPA NUBE (Escalabilidad)                        │

│                                                  │

│ PostgreSQL → AWS RDS                             │

│ • Análisis agregado de múltiples hogares         │

│ • Backups automáticos                            │

│ • Machine Learning distribuido                   │

└──────────────────────────────────────────────────┘





\---



\## 5.3 Tecnología Actual: SQLite3



\*\*Ubicación:\*\* `backend/domovida.db`



\*\*Ventajas para el prototipo académico:\*\*

\- Sin instalación adicional (incluido en Python)

\- Sin configuración de servidor

\- Persistencia en un solo archivo

\- Ideal para pruebas y desarrollo

\- Cumple con el principio de Edge Computing



\*\*Conexión (SQLAlchemy):\*\*



```python

from sqlalchemy import create\_engine

from sqlalchemy.orm import sessionmaker



DATABASE\_URL = "sqlite:///./domovida.db"

engine = create\_engine(DATABASE\_URL, connect\_args={"check\_same\_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



\## 5.4 Modelo de Datos



\## 5.4.1 Tabla eventos

Columna	Tipo	Descripción

id	Integer (PK)	Identificador único

sensor\_id	String (index)	ID del sensor (ej: acelerometro\_dormitorio)

tipo	String (index)	Tipo de sensor (ej: acelerometro)

habitacion	String (nullable)	Ubicación (ej: dormitorio)

valor	JSON	Datos específicos del sensor

alerta	Boolean	True si es una alerta crítica

timestamp	DateTime	Fecha y hora del evento



Definición en SQLAlchemy:



from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON

from datetime import datetime

from database import Base



class Evento(Base):

&#x20;   \_\_tablename\_\_ = "eventos"



&#x20;   id = Column(Integer, primary\_key=True, index=True)

&#x20;   sensor\_id = Column(String, index=True)

&#x20;   tipo = Column(String, index=True)

&#x20;   habitacion = Column(String, nullable=True)

&#x20;   valor = Column(JSON)

&#x20;   alerta = Column(Boolean, default=False)

&#x20;   timestamp = Column(DateTime, default=datetime.utcnow)



\##  5.5 Ejemplo de Registro



{

&#x20; "id": 951,

&#x20; "sensor\_id": "acelerometro\_dormitorio",

&#x20; "tipo": "acelerometro",

&#x20; "habitacion": "dormitorio",

&#x20; "valor": {

&#x20;   "ax": -2.35,

&#x20;   "ay": 6.74,

&#x20;   "az": 25.55,

&#x20;   "magnitud": 26.53

&#x20; },

&#x20; "alerta": true,

&#x20; "timestamp": "2026-09-18T17:41:23.827444"

}



\## 5.6 Consultas Típicas



Obtener últimos eventos



SELECT \* FROM eventos

ORDER BY timestamp DESC

LIMIT 50;



Contar alertas activas (últimas 24h)



SELECT COUNT(\*) FROM eventos

WHERE alerta = 1

AND timestamp >= datetime('now', '-24 hours');



Sensores PIR con inactividad



SELECT DISTINCT sensor\_id, habitacion

FROM eventos

WHERE tipo = 'pir'

GROUP BY sensor\_id;



\## 5.7 Seudonimización y Privacidad



En conformidad con la Ley N° 21.719 sobre protección de datos personales:



✅ No se almacenan RUT ni nombres en la base operativa



✅ Los sensores se identifican por códigos (ej: acelerometro\_dormitorio)



✅ Los valores numéricos no permiten identificar personas



✅ Los datos son anonimizados por diseño



Futuro: Implementar capa adicional de seudonimización con hashing para los sensor\_id.



\## 5.8 Estado Actual



Aspecto	                                Estado

Base de datos SQLite3	                  ✅ Funcionando

Tabla eventos	                          ✅ Creada

Registros almacenados	                  ✅ +965 eventos

Seudonimización básica	                ✅ Implementada

Migración a PostgreSQL (AWS RDS)	      🔜 Objetivo 2

Sincronización híbrida	                🔜 Futuro



\## 5.9 Comandos Útiles



Ver el archivo de base de datos



ls backend/domovida.db


Abrir la base de datos con SQLite (si está instalado)



sqlite3 backend/domovida.db

.tables

SELECT COUNT(\*) FROM eventos;

.quit



\## 5.10 Próximas Mejoras



🔜 Migrar a PostgreSQL en AWS RDS



🔜 Implementar Supabase como alternativa de nube



🔜 Crear índices compuestos para consultas más rápidas



🔜 Implementar backups automáticos a S3



🔜 Crear tabla de usuarios para control de acceso



🔜 Añadir tabla de configuración de sensores por hogar



🔜 Implementar cifrado a nivel de columna para datos sensibles





