\# Ficha 11: Triggers y Automatización en Supabase



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 11.1 Descripción General



DomoVida implementa dos \*\*triggers de PostgreSQL\*\* en Supabase que automatizan tareas críticas directamente en la base de datos. Esto reduce la carga del backend, garantiza la consistencia de los datos, y mejora el rendimiento general del sistema.



Los triggers están escritos en \*\*PL/pgSQL\*\*, el lenguaje procedimental de PostgreSQL.



\---



\## 11.2 Trigger #1: Actualizar `sync\_status` Automáticamente



\### ¿Qué hace?



Cuando se inserta un nuevo evento en la tabla `eventos`, este trigger actualiza automáticamente el campo `sync\_status` a `'synced'`, indicando que el dato ya está en la nube.



\### ¿Por qué es buena práctica?



| Beneficio          | Explicación                                                                                    |

|--------------------|------------------------------------------------------------------------------------------------|

| \*\*Automatización\*\* | Evita que el backend tenga que recordar actualizar este campo manualmente                      |

| \*\*Consistencia\*\*   | Garantiza que TODOS los eventos insertados directamente en Supabase tengan el estado correcto  |

| \*\*Trazabilidad\*\*   | Permite saber qué datos vienen de SQLite (Edge) y cuáles se insertaron directamente en la nube |

| \*\*Simplicidad\*\*    | El código Python queda más limpio y enfocado en la lógica de negocio                           |



\### Código SQL



```sql

\-- Función que ejecuta el trigger

CREATE OR REPLACE FUNCTION marcar\_como\_sincronizado()

RETURNS TRIGGER AS $$

BEGIN

&#x20;   NEW.sync\_status := 'synced';

&#x20;   RETURN NEW;

END;

$$ LANGUAGE plpgsql;



\-- Trigger que se ejecuta ANTES de cada INSERT

CREATE TRIGGER trigger\_sync\_eventos

BEFORE INSERT ON eventos

FOR EACH ROW

EXECUTE FUNCTION marcar\_como\_sincronizado();

```



\---



\## 11.3 Trigger #2: Crear Alerta Automáticamente



\### ¿Qué hace?



Cuando se inserta un evento con `alerta = TRUE`, este trigger crea automáticamente un registro en la tabla `alertas`, vinculando la alerta con el evento original.



\### ¿Por qué es buena práctica?



| Beneficio                           | Explicación |

|-------------------------------------|-------------|

| \*\*Automatización\*\*                  | Elimina la necesidad de que el backend haga dos INSERT (uno en eventos, otro en alertas)        |

| \*\*Integridad referencial\*\*          | Garantiza que SIEMPRE haya una alerta cuando un evento marca alerta=TRUE                        |

| \*\*Consistencia\*\*                    | Evita olvidos o errores del programador                                                         |

| \*\*Escalabilidad\*\*                   | Si en el futuro se insertan eventos desde otros sistemas (IoT directo, APIs externas),          |

|                                     |                                      el trigger garantiza que el comportamiento sea consistente |

| \*\*Rendimiento\*\*                     | Al ejecutarse en la base de datos (no en Python), el trigger es más rápido y no consume recursos|  |                                     |                                                                                     del backend |



\### Lógica de Severidad



El trigger asigna automáticamente el nivel de severidad según el tipo de evento:



| Tipo de Evento               | Severidad Asignada |

|------------------------------|--------------------|

| `acelerometro` (caída)       | \*\*crítica\*\*        |

| `cardiovascular` (infarto)   | \*\*crítica\*\*        |

| `boton\_panico`               | \*\*crítica\*\*        |

| `gas` (fuga)                 | \*\*crítica\*\*        |

| `humo`                       | \*\*crítica\*\*        |

| Otros                        | alta               |



\### Código SQL



```sql

CREATE OR REPLACE FUNCTION crear\_alerta\_automatica()

RETURNS TRIGGER AS $$

BEGIN

&#x20;   IF NEW.alerta = TRUE THEN

&#x20;       INSERT INTO alertas (

&#x20;           evento\_id,

&#x20;           tipo\_alerta,

&#x20;           nivel\_severidad,

&#x20;           payload\_fhir,

&#x20;           resuelto,

&#x20;           creado\_en

&#x20;       ) VALUES (

&#x20;           NEW.id,

&#x20;           NEW.tipo,

&#x20;           CASE 

&#x20;               WHEN NEW.tipo = 'acelerometro' THEN 'critica'

&#x20;               WHEN NEW.tipo = 'cardiovascular' THEN 'critica'

&#x20;               WHEN NEW.tipo = 'boton\_panico' THEN 'critica'

&#x20;               WHEN NEW.tipo = 'gas' THEN 'critica'

&#x20;               WHEN NEW.tipo = 'humo' THEN 'critica'

&#x20;               ELSE 'alta'

&#x20;           END,

&#x20;           NEW.valor,

&#x20;           FALSE,

&#x20;           NOW()

&#x20;       );

&#x20;   END IF;

&#x20;   RETURN NEW;

END;

$$ LANGUAGE plpgsql;



CREATE TRIGGER trigger\_crear\_alerta

AFTER INSERT ON eventos

FOR EACH ROW

EXECUTE FUNCTION crear\_alerta\_automatica();

```



\---



\## 11.4 Verificación de los Triggers



\### Consulta para listar triggers activos



```sql

SELECT 

&#x20;   trigger\_name,

&#x20;   event\_object\_table AS tabla,

&#x20;   event\_manipulation AS evento,

&#x20;   action\_timing AS momento,

&#x20;   action\_statement AS funcion

FROM information\_schema.triggers

WHERE event\_object\_schema = 'public'

ORDER BY event\_object\_table, trigger\_name;

```



\### Resultado obtenido



| trigger\_name           | tabla   | evento | momento | función                      |

|------------------------|---------|--------|---------|------------------------------|

| `trigger\_crear\_alerta` | eventos | INSERT | AFTER   | `crear\_alerta\_automatica()`  |

| `trigger\_sync\_eventos` | eventos | INSERT | BEFORE  | `marcar\_como\_sincronizado()` |



\---



\## 11.5 Prueba de Funcionamiento



\### Prueba del Trigger #2



\*\*Petición POST\*\* a `/api/sensor-data`:



```json

{

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

&#x20; "timestamp": "2026-09-23T22:15:00"

}

```



\*\*Resultado:\*\* `201 Created` ✅



\### Verificación en la tabla `alertas`



| alerta\_id | evento\_id | tipo\_alerta  | nivel\_severidad | resuelto | creado\_en           |

|-----------|-----------|--------------|-----------------|----------|---------------------|

| 1         | 3         | acelerometro | crítica         | false    | 2026-09-23 23:49:35 |



\*\*El trigger creó la alerta automáticamente.\*\* ✅



\---



\## 11.6 Ventajas de la Automatización en Base de Datos



| Ventaja               | Descripción                                                                                                 |

|-----------------------|-------------------------------------------------------------------------------------------------------------|

| \*\*Rendimiento\*\*       | Los triggers se ejecutan en el motor de PostgreSQL, que está optimizado para esto                           |

| \*\*Consistencia\*\*      | No importa qué aplicación inserte datos (FastAPI, otro backend, IoT directo), el comportamiento es el mismo |

| \*\*Seguridad\*\*         | Las reglas de negocio están en la base de datos, no en el código de aplicación                              |

| \*\*Mantenibilidad\*\*    | Cambiar una regla de negocio es cambiar un trigger, no todo el código Python                                |

| \*\*Auditoría\*\*         | Cada evento queda registrado con su alerta correspondiente, sin excepción                                   |



\---



\## 11.7 Cumplimiento Normativo



| Norma             | Cumplimiento                                                |

|-------------------|-------------------------------------------------------------|

| \*\*Ley N° 21.719\*\* | ✅ Los datos se almacenan cifrados (SSL) y con RLS activado |

| \*\*Ley N° 19.628\*\* | ✅ Protección de datos personales en la base de datos       |

| \*\*Ley N° 20.584\*\* | ✅ Confidencialidad de datos clínicos                       |



\---



\## 11.8 Próximas Mejoras



\- 🔜 Agregar \*\*trigger de auditoría\*\* (registrar cada cambio en las tablas).

\- 🔜 Implementar \*\*trigger de notificación\*\* (enviar push cuando se crea una alerta).

\- 🔜 Añadir \*\*trigger de sincronización inversa\*\* (Supabase → SQLite).

\- 🔜 Implementar \*\*funciones de estadísticas\*\* (calcular promedios, máximos, mínimos).



\---



\## 11.9 Conclusión



Los triggers de DomoVida demuestran que la \*\*automatización en base de datos\*\* es una práctica profesional que:



1\. \*\*Reduce la carga del backend\*\* (menos código Python).

2\. \*\*Garantiza la consistencia\*\* de los datos (siempre hay alerta cuando hay evento crítico).

3\. \*\*Mejora el rendimiento\*\* (PostgreSQL es más rápido que Python para estas tareas).

4\. \*\*Facilita el mantenimiento\*\* (las reglas de negocio están en un solo lugar).



Esta implementación está alineada con las \*\*buenas prácticas de ingeniería de software\*\* y demuestra un nivel avanzado de dominio de PostgreSQL y PL/pgSQL.

```







