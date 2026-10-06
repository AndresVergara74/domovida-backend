# DomoVida · Diagramas de diseño

Diagramas del proyecto según la Guía de apoyo del estudiante (secciones 6.1 Arquitectura, 6.2 Modelo de datos, 6.3 UML mínimo, 6.5 Requisitos no funcionales en el diseño y 7.5 Pruebas de rendimiento). Actualizados al 6 de octubre de 2026.

Cada diagrama está en dos formatos: el código **Mermaid** (`.mmd`), que GitHub muestra como imagen en esta página y se puede editar como texto, y una imagen **PNG** para insertar en informes y presentaciones.

| N° | Diagrama | Sección de la guía | Archivos |
|---|---|---|---|
| 1 | Arquitectura de componentes | 6.1 y 6.3 | `01_componentes.mmd` · `.png` |
| 2 | Despliegue (infraestructura) | 6.1 | `02_despliegue.mmd` · `.png` |
| 3 | Secuencia del flujo crítico | 6.3 | `03_secuencia_flujo_critico.mmd` · `.png` |
| 4 | Casos de uso | 6.3 | `04_casos_de_uso.mmd` · `.png` |
| 5 | Modelo de datos (entidad-relación) | 6.2 | `05_modelo_datos.mmd` · `.png` |
| 6 | Flujo de datos personales y seguridad | 6.5 | `06_datos_personales_seguridad.mmd` · `.png` |
| 7 | Gráfico de latencia PR-01 / PR-01b | 7.5 | `07_latencia_pr01.png` · `07_latencia.py` |

---

## 1. Arquitectura de componentes

**Qué representa:** las partes del sistema y cómo se comunican. Los sensores del hogar envían lecturas a la API FastAPI; la API aplica seguridad, reglas de detección y alertas, guarda en Supabase (o en SQLite sin internet) y avisa al panel por WebSocket y al celular por ntfy.

**Decisiones de diseño que muestra:** una API única como punto de entrada (*API-first*) con la seguridad en la puerta de entrada (clave de API para sensores y sesión para el cuidador); separación entre las salidas en tiempo real (WebSocket), push (ntfy) e interoperabilidad (FHIR); persistencia doble nube/borde. Los componentes punteados (Raspberry Pi con MQTT y sistema clínico) son trabajo futuro: hoy los sensores son simulados.

```mermaid
flowchart TB
  subgraph HOGAR["Hogar (borde)"]
    direction LR
    SIM["Simulador de 8 sensores<br/>simulate_sensors.py"]
    RPI["Raspberry Pi + MQTT<br/>(futuro)"]:::futuro
  end
  subgraph PANEL["Panel del cuidador · React + Vite (Vercel)"]
    direction LR
    APP["Vista general, historial,<br/>sensores y mapa"]
    LOGIN["Inicio de sesión<br/>LoginCuidador.tsx"]
    CONS["Consentimiento<br/>Consentimiento.tsx"]
  end
  subgraph API["API FastAPI (Render) · backend/"]
    direction LR
    SEG["Seguridad<br/>seguridad.py · auth_cuidador.py"]
    REG["Reglas y alertas<br/>sensor_router · reglas_puerta · alerta_router"]
    WS["Tiempo real<br/>websocket_manager"]
    NOT["Notificaciones<br/>notifier"]
    FHIR["Interoperabilidad<br/>fhir_router"]
  end
  subgraph DATOS["Datos y servicios externos"]
    direction LR
    SUPA[("Supabase PostgreSQL<br/>RLS + triggers")]
    SQL[("SQLite<br/>modo borde")]
    AUTH["Supabase Auth"]
    NTFY["ntfy.sh → celular"]
    CLIN["Sistema clínico<br/>(futuro)"]:::futuro
  end
  SIM -- "HTTPS + X-API-Key" --> SEG
  RPI -.-> SEG
  APP -- "REST + Bearer token" --> SEG
  SEG --> REG
  REG --> WS
  REG --> NOT
  WS -- "WebSocket" --> APP
  LOGIN -- "correo y contraseña" --> AUTH
  SEG -- "valida el token" --> AUTH
  REG -- "SQLAlchemy" --> SUPA
  REG -. "sin internet" .-> SQL
  FHIR --> SUPA
  NOT --> NTFY
  CLIN -. "HL7 FHIR R4" .-> FHIR
  classDef futuro stroke-dasharray: 5 5,fill:#f2f2f2,color:#52514e
```

## 2. Despliegue (infraestructura)

**Qué representa:** dónde corre cada parte. El panel está en Vercel, la API en Render (Oregón, EE. UU.), la base de datos y la autenticación en Supabase (São Paulo, Brasil), y un entorno de prueba con Docker en AWS EC2 (Virginia, EE. UU.).

**Decisión de diseño que muestra:** explica el hallazgo principal de rendimiento. Con la API y la base de datos en continentes distintos, la alerta tarda 1.577 ms en promedio (PR-01); con ambas en la misma máquina, 216 ms (PR-01b). Por eso se planificó un despliegue en Oracle Cloud Santiago, hoy postergado por falta de capacidad gratuita en la región.

```mermaid
flowchart TB
  subgraph CL["Chile"]
    NAV["Navegador del cuidador"]
    CEL["Celular del cuidador<br/>app ntfy"]
    subgraph CASA["Hogar del adulto mayor"]
      SIM["Simulador de sensores<br/>(prototipo)"]
      BORDE["Modo borde: backend + SQLite<br/>+ panel local (sin internet)"]
    end
    ORA["Oracle Cloud Santiago<br/>(planificado: sin capacidad gratuita)"]:::futuro
  end
  subgraph US["EE. UU."]
    VER["Vercel CDN<br/>panel React"]
    REN["Render · Oregón<br/>API FastAPI (plan gratuito)<br/><b>PR-01: alerta en 1.577 ms</b><br/>(API en EE. UU., base en Brasil)"]:::medido
    subgraph AWS["AWS EC2 · us-east-1 (entorno de prueba)"]
      DC["Docker Compose<br/>backend + frontend + SQLite<br/><b>PR-01b: alerta en 216 ms</b><br/>(API y base en la misma máquina)"]:::medido
    end
  end
  subgraph BR["Brasil"]
    SUP[("Supabase · São Paulo<br/>PostgreSQL + Auth")]
  end
  NTFY["ntfy.sh<br/>servicio de avisos"]

  NAV -- "HTTPS" --> VER
  NAV -- "REST + WebSocket" --> REN
  SIM -- "HTTPS + X-API-Key" --> REN
  REN -- "Session Pooler, puerto 6543" --> SUP
  NAV -- "inicio de sesión" --> SUP
  REN --> NTFY --> CEL
  NAV -. "comparación" .-> DC
  classDef futuro stroke-dasharray: 5 5,fill:#f2f2f2,color:#52514e
  classDef medido fill:#fff8e1,stroke:#eda100,color:#0b0b0b
```

## 3. Secuencia del flujo crítico

**Qué representa:** el recorrido completo de una caída, en orden: la lectura del sensor (con su clave), la detección, el registro en la base, el trigger que crea la alerta, el aviso por WebSocket y por ntfy, y la atención del cuidador con su sesión.

**Decisiones de diseño que muestra:** el WebSocket se envía **antes** que ntfy y ntfy en segundo plano, lo que redujo la latencia en 17 % (commit 1c8c203); la alerta se crea con un trigger en la base de datos, no con un segundo INSERT desde Python; el token del cuidador se valida contra Supabase Auth en cada atención y su correo queda registrado.

```mermaid
sequenceDiagram
  autonumber
  participant S as Sensor (acelerómetro)
  participant A as API FastAPI
  participant B as Supabase PostgreSQL
  participant W as WebSocket
  participant P as Panel del cuidador
  participant N as ntfy.sh
  participant C as Celular del cuidador
  participant U as Supabase Auth
  S->>A: POST /api/sensor-data + X-API-Key (Z > 17 m/s²)
  alt clave ausente o incorrecta
    A-->>S: 401 No autorizado
  else clave válida
    A->>A: Reglas de umbral: caída detectada
    A->>B: INSERT evento (alerta = true)
    B->>B: Trigger crear_alerta_automatica (severidad crítica)
    A-->>S: 201 Creado
    A->>W: Notificar alerta (primero)
    W->>P: Alerta en tiempo real (216 ms en EC2 · 1.577 ms en Render)
    A-)N: Aviso push en segundo plano
    N-)C: «CAÍDA DETECTADA» (30/30 en PR-02)
  end
  Note over P: El cuidador presiona «Atender»
  opt sin sesión vigente
    P->>U: Correo y contraseña
    U-->>P: Token de acceso (1 hora)
  end
  P->>A: PATCH /api/alertas/{id}/resolver + Bearer token
  A->>U: GET /auth/v1/user (valida el token)
  U-->>A: Correo del cuidador
  A->>B: UPDATE resuelto = true, resuelto_por = correo
  A-->>P: 200 OK
  P->>P: Muestra «Atendida HH:MM»
```

## 4. Casos de uso

**Qué representa:** qué puede hacer cada actor (cuidador, adulto mayor, sensor, equipo de salud y personal técnico), con la historia de usuario del Product Backlog que corresponde a cada caso.

**Decisiones de diseño que muestra:** atender una alerta **incluye** iniciar sesión (HU-14); aceptar el consentimiento **incluye** la seudonimización (HU-08); una lectura de sensor desencadena las alertas de caída, gas, humo o puerta. El diagrama usa la notación de casos de uso adaptada a Mermaid (actores en círculos y casos en óvalos).

```mermaid
flowchart LR
  CUI(("Cuidador"))
  ADU(("Adulto mayor"))
  SEN(("Sensor IoT"))
  SAL(("Equipo de salud"))
  TEC(("Personal técnico"))
  subgraph SIS["Sistema DomoVida"]
    UC1(["Recibir alerta de caída en el panel · HU-01"])
    UC2(["Recibir aviso push en el celular · HU-02"])
    UC3(["Registrar eventos sin internet · HU-03"])
    UC4(["Alertar gas, humo y puerta · HU-04, HU-16"])
    UC5(["Consultar inactividad · HU-05"])
    UC6(["Atender una alerta · HU-06"])
    UC14(["Iniciar sesión · HU-14"])
    UC7(["Aceptar consentimiento informado · HU-07"])
    UC9(["Ver sensores en el mapa del hogar · HU-09"])
    UC10(["Filtrar el historial · HU-10"])
    UC13(["Enviar lecturas con clave de API · HU-13"])
    UC15(["Consultar datos en HL7 FHIR · HU-15"])
    UC8(["Seudonimizar datos y aplicar RLS · HU-08"])
    UC11(["Desplegar con Docker · HU-11"])
  end
  SEN --- UC13
  UC13 -. "incluye" .-> UC3
  UC13 -. "desencadena" .-> UC1
  UC13 -. "desencadena" .-> UC4
  CUI --- UC1
  CUI --- UC2
  CUI --- UC5
  CUI --- UC6
  UC6 -. "incluye" .-> UC14
  CUI --- UC9
  CUI --- UC10
  ADU --- UC7
  UC7 -. "incluye" .-> UC8
  SAL --- UC15
  TEC --- UC8
  TEC --- UC11
```

## 5. Modelo de datos (entidad-relación)

**Qué representa:** las tres tablas de Supabase/PostgreSQL con sus columnas reales (consultadas en `information_schema` el 06-10-2026) y sus relaciones.

**Decisiones de diseño que muestra:** `alertas.evento_id` es clave foránea de `eventos.id`, y cada alerta la crea el trigger `crear_alerta_automatica` con su severidad; `eventos.sync_status` lo marca el trigger `marcar_como_sincronizado`; la relación entre `sensores` y `eventos` es lógica (por `sensor_id`), sin clave foránea, para que un sensor nuevo pueda enviar datos antes de registrarse. Ninguna tabla guarda nombre ni RUT.

**Observación de diseño:** las columnas de atención (`resuelto`, `resuelto_en`, `resuelto_por`) existen en `eventos` y en `alertas`, pero la API actualiza solo las de `eventos`. Es una redundancia que conviene resolver (registro de pruebas, ajuste 17).

```mermaid
erDiagram
  SENSORES ||--o{ EVENTOS : "registra (vínculo lógico por sensor_id)"
  EVENTOS ||--o| ALERTAS : "genera (trigger crear_alerta_automatica)"
  SENSORES {
    integer id PK
    varchar sensor_id UK "ej. acelerometro_dormitorio"
    varchar tipo
    varchar habitacion
    boolean activo
    timestamp creado_en
  }
  EVENTOS {
    integer id PK
    varchar sensor_id "identifica al sensor"
    varchar tipo
    varchar habitacion
    json valor "lectura del sensor"
    boolean alerta
    timestamp timestamp
    varchar sync_status "trigger marcar_como_sincronizado"
    boolean resuelto
    timestamptz resuelto_en
    varchar resuelto_por "correo del cuidador (PS-01b)"
  }
  ALERTAS {
    integer id PK
    integer evento_id FK
    varchar tipo_alerta
    varchar nivel_severidad "critica o alta"
    jsonb payload_fhir
    boolean resuelto
    timestamptz resuelto_en
    varchar resuelto_por
    text notas_resolucion
    timestamptz creado_en
  }
```

## 6. Flujo de datos personales y seguridad

**Qué representa:** por dónde viajan los datos y qué control se aplica en cada punto, en tres zonas: el navegador del usuario, el hogar y la nube.

**Decisiones de diseño que muestra (privacidad por diseño, Ley N° 21.719):** el nombre y el RUT se seudonimizan en el navegador y no llegan a la base de datos; los sensores envían lecturas sin datos personales y con clave (PS-01); el cuidador se autentica con Supabase Auth y usa un token de 1 hora (PS-01b); RLS bloquea al rol anónimo (PI-03 y PI-03b); el aviso de ntfy no lleva datos sensibles; FHIR expone solo un seudónimo con la etiqueta PSEUDED (PI-05); los secretos viven en variables de entorno y nunca en GitHub.

```mermaid
flowchart TB
  subgraph NAVEG["1 · Navegador del usuario (los datos personales no salen de aquí)"]
    direction LR
    ADU(("Adulto mayor")) -- "nombre y RUT" --> CONS["Consentimiento informado<br/>2 casillas obligatorias"]
    CONS --> HASH["Seudonimización<br/>SHA-256 con sal (PU-03)"]
    HASH --> LS[("Se guardan solo iniciales<br/>y hash del RUT")]
    CUI(("Cuidador")) --> PANEL["Panel del cuidador"]
  end
  subgraph HOGAR["2 · Hogar"]
    SEN["Sensores<br/>lecturas sin datos personales"]
  end
  subgraph NUBE["3 · Nube (servicios de terceros)"]
    direction LR
    AUTHS["Supabase Auth<br/>contraseña cifrada"]
    API["API FastAPI"]
    DB[("Supabase PostgreSQL<br/>eventos sin nombre ni RUT<br/>RLS activo (PI-03, PI-03b)")]
    NT["ntfy.sh<br/>tópico seudonimizado,<br/>aviso sin datos sensibles"]
    FH["FHIR Patient/domovida-p001<br/>etiqueta PSEUDED (PI-05)"]
    ENV["Secretos en variables de entorno<br/>(Render y Vercel), nunca en GitHub"]:::secreto
  end
  X["Rol anónimo o cliente no autorizado"]:::bloqueo

  PANEL -- "correo y contraseña" --> AUTHS
  AUTHS -- "token de 1 hora" --> PANEL
  PANEL -- "HTTPS + Bearer token (PS-01b)" --> API
  SEN -- "HTTPS + X-API-Key (PS-01)" --> API
  ENV -.-> API
  API -- "rol dueño de la base" --> DB
  API --> NT
  API --> FH
  X -. "0 filas (RLS) · 401 sin clave o sesión" .-x DB
  classDef secreto fill:#fff8e1,stroke:#eda100,color:#0b0b0b
  classDef bloqueo fill:#fde8e8,stroke:#d03b3b,color:#0b0b0b
```

## 7. Gráfico de latencia PR-01 / PR-01b

**Qué representa:** el tiempo hasta que la alerta llega al panel en 30 caídas por escenario, con el promedio y el percentil 95, frente a la meta de 1.000 ms.

**Conclusión:** el ajuste del orden de las notificaciones bajó el promedio de 1.903 a 1.577 ms, pero solo la infraestructura con API y base de datos juntas (AWS EC2, 216 ms) cumple la meta. El gráfico se genera con `07_latencia.py` a partir de los datos de `registro_pruebas.md`.

![Latencia PR-01 y PR-01b](07_latencia_pr01.png)
