"""
Router de interoperabilidad HL7 FHIR R4 para DomoVida.

Expone los eventos de los sensores como recursos FHIR R4 `Observation`
y al adulto mayor monitoreado como recurso `Patient` seudonimizado, para que
un sistema clínico (por ejemplo, la ficha de un CESFAM) pueda consultarlos
con un estándar internacional.

Privacidad (Ley N° 21.719):
- El paciente se identifica solo con un seudónimo (Patient/domovida-p001).
- No se incluyen nombre, RUT ni dirección (minimización de datos):
  el recurso Patient solo contiene el seudónimo y datos no identificatorios.

Terminologías usadas:
- SNOMED CT 1912002 "Fall (event)" para caídas.
- LOINC 8867-4 "Heart rate" y 59408-5 "Oxygen saturation" para el sensor cardíaco.
- Catálogo propio de DomoVida para gas, humo, apertura, movimiento y botón de pánico.
"""
from datetime import timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Evento

router = APIRouter()

FHIR_JSON = "application/fhir+json"
SISTEMA_LOCAL = "https://github.com/AndresVergara74/domovida-backend/fhir/CodeSystem/evento-sensor"
PACIENTE_ID = "domovida-p001"
PACIENTE_SEUDONIMO = {"reference": f"Patient/{PACIENTE_ID}", "display": "Adulto mayor (seudonimizado)"}
SISTEMA_SEUDONIMOS = "https://github.com/AndresVergara74/domovida-backend/fhir/NamingSystem/seudonimo-paciente"

# Código principal de cada tipo de sensor
CODIGOS = {
    "acelerometro": {"system": "http://snomed.info/sct", "code": "1912002", "display": "Fall (event)"},
    "cardiovascular": {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"},
    "gas": {"system": SISTEMA_LOCAL, "code": "gas", "display": "Concentración de gas en el ambiente"},
    "humo": {"system": SISTEMA_LOCAL, "code": "humo", "display": "Nivel de humo en el ambiente"},
    "apertura": {"system": SISTEMA_LOCAL, "code": "apertura", "display": "Apertura de puerta o ventana"},
    "pir": {"system": SISTEMA_LOCAL, "code": "movimiento", "display": "Movimiento e inactividad"},
    "boton_panico": {"system": SISTEMA_LOCAL, "code": "boton-panico", "display": "Activación del botón de pánico"},
}

INTERPRETACION = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
CATEGORIA = "http://terminology.hl7.org/CodeSystem/observation-category"
CRITICOS = {"acelerometro", "cardiovascular", "boton_panico", "gas", "humo"}


def _cantidad(valor, unidad, codigo_ucum):
    return {"value": valor, "unit": unidad, "system": "http://unitsofmeasure.org", "code": codigo_ucum}


def evento_a_observation(ev: Evento) -> dict:
    """Convierte un evento de DomoVida en un recurso FHIR R4 Observation."""
    valor = ev.valor or {}
    codigo = CODIGOS.get(ev.tipo, {"system": SISTEMA_LOCAL, "code": ev.tipo, "display": ev.tipo})
    fecha = ev.timestamp
    if fecha is not None and fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)

    obs = {
        "resourceType": "Observation",
        "id": f"evento-{ev.id}",
        "status": "final",
        "category": [{
            "coding": [{
                "system": CATEGORIA,
                "code": "vital-signs" if ev.tipo == "cardiovascular" else "activity",
            }]
        }],
        "code": {"coding": [codigo], "text": codigo["display"]},
        "subject": PACIENTE_SEUDONIMO,
        "device": {"display": f"Sensor {ev.sensor_id} ({ev.habitacion})"},
        "interpretation": [{
            "coding": [{
                "system": INTERPRETACION,
                "code": ("AA" if ev.tipo in CRITICOS else "A") if ev.alerta else "N",
            }]
        }],
    }
    if fecha is not None:
        obs["effectiveDateTime"] = fecha.isoformat()

    # Valor principal según el tipo de sensor
    if ev.tipo == "cardiovascular" and "bpm" in valor:
        obs["valueQuantity"] = _cantidad(valor["bpm"], "beats/minute", "/min")
        if "spo2" in valor:
            obs["component"] = [{
                "code": {"coding": [{"system": "http://loinc.org", "code": "59408-5",
                                     "display": "Oxygen saturation in Arterial blood by Pulse oximetry"}]},
                "valueQuantity": _cantidad(valor["spo2"], "%", "%"),
            }]
    elif ev.tipo == "gas" and "nivel_ppm" in valor:
        obs["valueQuantity"] = _cantidad(valor["nivel_ppm"], "ppm", "[ppm]")
    elif ev.tipo == "humo" and "nivel" in valor:
        obs["valueQuantity"] = _cantidad(valor["nivel"], "ppm", "[ppm]")
    elif ev.tipo == "acelerometro" and "magnitud" in valor:
        obs["valueQuantity"] = _cantidad(valor["magnitud"], "m/s2", "m/s2")
    elif ev.tipo == "apertura":
        obs["valueBoolean"] = bool(valor.get("abierto"))
    elif ev.tipo == "boton_panico":
        obs["valueBoolean"] = bool(valor.get("activado"))
    elif ev.tipo == "pir" and "minutos_inactivo" in valor:
        obs["valueQuantity"] = _cantidad(valor["minutos_inactivo"], "min", "min")

    if ev.alerta:
        obs["note"] = [{"text": "Evento marcado como alerta por las reglas de umbral de DomoVida."}]
    return obs


@router.get("/fhir/Observation/{evento_id}")
def obtener_observation(evento_id: int, db: Session = Depends(get_db)):
    """Devuelve un evento como recurso FHIR R4 Observation."""
    ev = db.query(Evento).filter(Evento.id == evento_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Observation no encontrada")
    return JSONResponse(content=evento_a_observation(ev), media_type=FHIR_JSON)


@router.get("/fhir/Observation")
def buscar_observations(
    alerta: Optional[bool] = Query(None, description="true = solo eventos con alerta"),
    patient: Optional[str] = Query(None, description="Paciente: domovida-p001 o Patient/domovida-p001"),
    _count: int = Query(20, ge=1, le=100, alias="_count"),
    db: Session = Depends(get_db),
):
    """Devuelve las últimas observaciones como un Bundle FHIR de tipo searchset."""
    if patient is not None and patient.split("/")[-1] != PACIENTE_ID:
        # El prototipo monitorea un solo hogar: otro paciente no tiene observaciones
        return JSONResponse(content={"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []},
                            media_type=FHIR_JSON)
    q = db.query(Evento)
    if alerta is not None:
        q = q.filter(Evento.alerta == alerta)
    eventos = q.order_by(Evento.timestamp.desc()).limit(_count).all()
    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(eventos),
        "entry": [
            {"fullUrl": f"Observation/evento-{ev.id}", "resource": evento_a_observation(ev)}
            for ev in eventos
        ],
    }
    return JSONResponse(content=bundle, media_type=FHIR_JSON)


# ============================================================
# RECURSO PATIENT (seudonimizado)
# ============================================================

def paciente_seudonimizado() -> dict:
    """Recurso FHIR R4 Patient del adulto mayor monitoreado.

    Solo contiene el seudónimo: sin nombre, RUT, fecha de nacimiento ni dirección.
    La correspondencia entre el seudónimo y la persona real queda fuera del
    sistema (en el consentimiento firmado que custodia el cuidador).
    """
    return {
        "resourceType": "Patient",
        "id": PACIENTE_ID,
        "meta": {"security": [{
            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationValue",
            "code": "PSEUDED",
            "display": "pseudonymized",
        }]},
        "text": {
            "status": "generated",
            "div": '<div xmlns="http://www.w3.org/1999/xhtml">Adulto mayor monitoreado por DomoVida '
                   '(identidad seudonimizada según la Ley N° 21.719).</div>',
        },
        "identifier": [{
            "use": "secondary",
            "type": {"text": "Seudónimo DomoVida"},
            "system": SISTEMA_SEUDONIMOS,
            "value": PACIENTE_ID,
        }],
        "active": True,
        "managingOrganization": {"display": "DomoVida (prototipo académico, Duoc UC)"},
    }


@router.get("/fhir/Patient/{paciente_id}")
def obtener_patient(paciente_id: str):
    """Devuelve el recurso FHIR R4 Patient seudonimizado."""
    if paciente_id != PACIENTE_ID:
        raise HTTPException(status_code=404, detail="Patient no encontrado")
    return JSONResponse(content=paciente_seudonimizado(), media_type=FHIR_JSON)


@router.get("/fhir/Patient")
def buscar_patients():
    """Bundle searchset con los pacientes (el prototipo monitorea un solo hogar)."""
    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [{"fullUrl": f"Patient/{PACIENTE_ID}", "resource": paciente_seudonimizado()}],
    }
    return JSONResponse(content=bundle, media_type=FHIR_JSON)
