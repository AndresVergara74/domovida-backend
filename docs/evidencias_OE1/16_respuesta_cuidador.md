\# Ficha 16: Respuesta del Cuidador — Ciclo de Atención de Alertas



\*\*Proyecto:\*\* DomoVida — Plataforma IoT de Monitoreo Predictivo



\*\*Autor:\*\* Andrés Rodrigo Vergara Acevedo



\*\*Fecha:\*\* Septiembre 2026



\---



\## 16.1 Descripción General



DomoVida implementa un \*\*ciclo completo de respuesta del cuidador\*\* que permite no solo detectar alertas, sino también \*\*gestionarlas y cerrarlas\*\*. Esto transforma el sistema de un simple monitor pasivo a una \*\*herramienta de cuidado activa\*\*.



El flujo es:



```

\[Alerta detectada] → \[Cuidador notificado] → \[Cuidador atiende] → \[Alerta cerrada]

```



\---



\## 16.2 El Problema que Resuelve



\### Sin sistema de respuesta



\- ❌ Las alertas se acumulan sin control

\- ❌ No se sabe si fueron atendidas

\- ❌ No hay trazabilidad

\- ❌ El cuidador no tiene forma de "cerrar" una alerta

\- ❌ Después de unos días, hay cientos de alertas sin resolver



\### Con sistema de respuesta



\- ✅ Cada alerta se puede \*\*marcar como atendida\*\*

\- ✅ Se registra \*\*quién\*\* la atendió

\- ✅ Se registra \*\*cuándo\*\* se atendió

\- ✅ El contador de "alertas activas" refleja la realidad

\- ✅ El cuidador tiene \*\*control total\*\* sobre el sistema



\---



\## 16.3 Modelo de Datos



\### Tabla `eventos` (campos agregados)



```sql

ALTER TABLE eventos ADD COLUMN resuelto BOOLEAN DEFAULT FALSE;

ALTER TABLE eventos ADD COLUMN resuelto\_en TIMESTAMPTZ;

ALTER TABLE eventos ADD COLUMN resuelto\_por VARCHAR(100);

```



| Campo | Tipo | Descripción |

|-------|------|-------------|

| `resuelto` | BOOLEAN | `false` = activa, `true` = atendida |

| `resuelto\_en` | TIMESTAMPTZ | Cuándo se atendió |

| `resuelto\_por` | VARCHAR(100) | Quién la atendió |



\---



\## 16.4 Endpoint del Backend



\### PATCH `/api/alertas/{id}/resolver`



\*\*Descripción:\*\* Marca una alerta como resuelta (atendida por el cuidador).



\*\*Request Body:\*\*

```json

{

&#x20; "resuelto\_por": "Cuidador DomoVida"

}

```



\*\*Response (éxito):\*\*

```json

{

&#x20; "id": 14555,

&#x20; "resuelto": true,

&#x20; "resuelto\_en": "2026-09-26T04:54:24.308242+00:00",

&#x20; "resuelto\_por": "Cuidador DomoVida",

&#x20; "mensaje": "Alerta 14555 marcada como resuelta por Cuidador DomoVida"

}

```



\*\*Código fuente:\*\*



```python

@router.patch("/alertas/{alerta\_id}/resolver")

def resolver\_alerta(

&#x20;   alerta\_id: int,

&#x20;   datos: ResolverAlertaIn,

&#x20;   db: Session = Depends(get\_db),

):

&#x20;   """Marca una alerta como resuelta."""

&#x20;   alerta = (

&#x20;       db.query(Evento)

&#x20;       .filter(

&#x20;           Evento.id == alerta\_id,

&#x20;           Evento.alerta == True,

&#x20;           Evento.resuelto == False,

&#x20;       )

&#x20;       .first()

&#x20;   )



&#x20;   if not alerta:

&#x20;       raise HTTPException(status\_code=404, detail="Alerta no encontrada")



&#x20;   alerta.resuelto = True

&#x20;   alerta.resuelto\_en = datetime.utcnow()

&#x20;   alerta.resuelto\_por = datos.resuelto\_por



&#x20;   db.commit()

&#x20;   db.refresh(alerta)



&#x20;   return {

&#x20;       "id": alerta.id,

&#x20;       "resuelto": True,

&#x20;       "resuelto\_en": alerta.resuelto\_en.isoformat(),

&#x20;       "resuelto\_por": alerta.resuelto\_por,

&#x20;       "mensaje": f"Alerta {alerta\_id} marcada como resuelta por {datos.resuelto\_por}",

&#x20;   }

```



\---



\## 16.5 Frontend — Botón "Atender"



\### Implementación en `App.tsx`



```tsx

async function resolverAlerta(alertaId: number) {

&#x20; setResolviendoId(alertaId);



&#x20; try {

&#x20;   const response = await fetch(`${API\_URL}/api/alertas/${alertaId}/resolver`, {

&#x20;     method: "PATCH",

&#x20;     headers: { "Content-Type": "application/json" },

&#x20;     body: JSON.stringify({

&#x20;       resuelto\_por: "Cuidador DomoVida",

&#x20;     }),

&#x20;   });



&#x20;   if (!response.ok) throw new Error(`HTTP ${response.status}`);



&#x20;   setAlertasResueltas((prev) => new Set(prev).add(alertaId));



&#x20;   if (refrescar) await refrescar();

&#x20; } catch (error) {

&#x20;   console.error(`❌ Error al resolver alerta ${alertaId}:`, error);

&#x20;   alert("No se pudo marcar la alerta como atendida. Intenta de nuevo.");

&#x20; } finally {

&#x20;   setResolviendoId(null);

&#x20; }

}

```



\### Estados del botón



| Estado | Apariencia | Cuándo |

|--------|-----------|--------|

| Normal | `✓ Atender` (verde) | Alerta activa |

| Procesando | `Atendiendo...` (gris) | Mientras envía PATCH |

| Resuelta | `✓ Atendida` (verde claro) | Después de resolver |



\---



\## 16.6 Flujo Completo



\### Paso 1: Alerta detectada



El sensor envía un evento con `alerta=true`.



```

POST /api/sensor-data

{

&#x20; "sensor\_id": "acelerometro\_dormitorio",

&#x20; "tipo": "acelerometro",

&#x20; "alerta": true,

&#x20; ...

}

```



\### Paso 2: Trigger automático



El trigger PL/pgSQL crea una entrada en la tabla `alertas`.



\### Paso 3: Notificaciones



\- \*\*ntfy:\*\* Notificación push al teléfono del cuidador

\- \*\*WebSocket:\*\* Alerta en tiempo real en el dashboard

\- \*\*Dashboard:\*\* Notificación flotante + botón "✓ Atender"



\### Paso 4: Cuidador atiende



El cuidador hace clic en \*\*"✓ Atender"\*\*.



\### Paso 5: Backend actualiza



```

PATCH /api/alertas/{id}/resolver

{

&#x20; "resuelto\_por": "Cuidador DomoVida"

}

```



\### Paso 6: Registro en Supabase



```sql

UPDATE eventos

SET

&#x20; resuelto = TRUE,

&#x20; resuelto\_en = NOW(),

&#x20; resuelto\_por = 'Cuidador DomoVida'

WHERE id = 14555;

```



\### Paso 7: Frontend actualiza



\- El botón cambia a \*\*"✓ Atendida"\*\*

\- El contador de "Alertas activas" disminuye

\- La alerta desaparece de la lista al recargar



\---



\## 16.7 Evidencia de Funcionamiento



\### Prueba realizada



\*\*Fecha:\*\* 26 de septiembre de 2026, 04:54 AM



\*\*Alertas atendidas en esta sesión:\*\* 5



| id    | sensor\_id                 | tipo         | resuelto\_por      | resuelto\_en |

|-------|---------------------------|--------------|-------------------|-------------|

| 14555 | apertura\_puerta\_principal | apertura     | Cuidador DomoVida | 04:54:24    |

| 14563 | apertura\_puerta\_principal | apertura     | Cuidador DomoVida | 04:54:22    |

| 14651 | apertura\_puerta\_principal | apertura     | Cuidador DomoVida | 04:54:14    |

| 14667 | apertura\_puerta\_principal | apertura     | Cuidador DomoVida | 04:54:11    |

| 14670 | boton\_panico\_sala         | boton\_panico | Cuidador DomoVida | 04:54:07    |



\### Consulta de verificación



```sql

SELECT id, sensor\_id, tipo, alerta, resuelto, resuelto\_en, resuelto\_por

FROM eventos

WHERE alerta = TRUE

&#x20; AND resuelto = TRUE

ORDER BY resuelto\_en DESC

LIMIT 5;

```



\*\*Resultado:\*\* ✅ 5 filas con todos los datos correctos.



\---



\## 16.8 Ventajas del Sistema



| Ventaja | Descripción |

|---------|-------------|

| \*\*Trazabilidad\*\* | Se sabe quién atendió cada alerta |

| \*\*Timestamp\*\* | Se sabe exactamente cuándo |

| \*\*Control del cuidador\*\* | El cuidador tiene poder de decisión |

| \*\*Sin acumulación\*\* | Las alertas resueltas desaparecen del panel |

| \*\*Auditoría\*\* | Cada acción queda registrada en la base de datos |

| \*\*Métricas\*\* | Se puede medir el tiempo de respuesta |



\---



\## 16.9 Cumplimiento Normativo



| Norma | Cumplimiento |

|-------|--------------|

| Ley N° 21.719 | ✅ Registro de auditoría de acciones sobre datos personales |

| Ley N° 20.584 | ✅ Trazabilidad de atención clínica |

| Ley N° 19.628 | ✅ Protección de datos con registro de acceso |



\---



\## 16.10 Trabajo Futuro



🔜 \*\*Dashboard de métricas del cuidador:\*\* Tiempo promedio de respuesta



🔜 \*\*Notas de resolución:\*\* Campo para que el cuidador agregue observaciones



🔜 \*\*Múltiples cuidadores:\*\* Registro con autenticación JWT



🔜 \*\*Historial de resoluciones:\*\* Vista de todas las alertas atendidas



🔜 \*\*Alertas de escalamiento:\*\* Si no se atiende en X minutos, escalar a segundo cuidador



\---



\## 16.11 Conclusión



El sistema de \*\*respuesta del cuidador\*\* de DomoVida demuestra:



\- ✅ \*\*Madurez del proyecto:\*\* No es solo un monitor, es un sistema de gestión

\- ✅ \*\*Enfoque en el usuario:\*\* El cuidador tiene control total

\- ✅ \*\*Rigor técnico:\*\* Trazabilidad completa en la base de datos

\- ✅ \*\*Cumplimiento legal:\*\* Auditoría y protección de datos

\- ✅ \*\*Diferenciación:\*\* A diferencia de otras soluciones, DomoVida cierra el ciclo



Este logro constituye una \*\*evidencia clave\*\* para la defensa ante la comisión evaluadora y demuestra la madurez técnica del proyecto.

```



\---





