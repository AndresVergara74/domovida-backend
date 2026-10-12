#!/usr/bin/env bash
# DomoVida - Reintento automatico para crear la VM Ampere A1 (Always Free) en Oracle Cloud Santiago.
# Corre en la VM E2.1.Micro actual. Intenta crear la instancia cada INTERVALO segundos
# hasta que haya capacidad; al lograrlo avisa por ntfy y se detiene.
# Requisitos: OCI CLI en ~/oci-venv y configuracion en ~/.oci/config (llave de API fuera del repositorio).
# Variables opcionales: NTFY_TOPIC, OCPUS, MEMORIA_GB, INTERVALO.
set -u

OCI="$HOME/oci-venv/bin/oci"
NOMBRE="domovida-ampere"
SHAPE="VM.Standard.A1.Flex"
OCPUS="${OCPUS:-2}"
MEMORIA_GB="${MEMORIA_GB:-12}"
SUBRED_NOMBRE="subnet-20261011-1419"
INTERVALO="${INTERVALO:-300}"
NTFY_TOPIC="${NTFY_TOPIC:-}"
DIR="$HOME/ampere"
LOG="$DIR/intentos.log"
mkdir -p "$DIR"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }
avisar() {
  [ -n "$NTFY_TOPIC" ] && curl -s -H "Title: $1" -H "Priority: high" -d "$2" "https://ntfy.sh/$NTFY_TOPIC" >/dev/null
}

TENANCY=$(grep '^tenancy=' "$HOME/.oci/config" | head -1 | cut -d= -f2 | tr -d ' \r')
[ -z "$TENANCY" ] && { log "ERROR: no se encontro tenancy en ~/.oci/config"; exit 1; }

AD=$($OCI iam availability-domain list --query 'data[0].name' --raw-output) || { log "ERROR: no se pudo leer la zona (revisar llave de API)"; exit 1; }
SUBRED=$($OCI network subnet list --compartment-id "$TENANCY" --all \
  --query "data[?\"display-name\"=='$SUBRED_NOMBRE'] | [0].id" --raw-output)
IMAGEN=$($OCI compute image list --compartment-id "$TENANCY" --operating-system "Canonical Ubuntu" \
  --operating-system-version "22.04" --shape "$SHAPE" --sort-by TIMECREATED --sort-order DESC --all \
  --query "data[?!contains(\"display-name\",'Minimal')] | [0].id" --raw-output)
LLAVE_SSH="$HOME/.ssh/authorized_keys"

for v in AD SUBRED IMAGEN; do
  [ -z "${!v}" ] || [ "${!v}" = "null" ] && { log "ERROR: no se pudo obtener $v"; exit 1; }
done
log "Inicio: $SHAPE ${OCPUS} OCPU / ${MEMORIA_GB} GB, cada ${INTERVALO}s. Zona $AD"
log "Imagen: $IMAGEN"

intento=0
errores=0
while true; do
  # Evitar duplicados: si ya existe una instancia con este nombre (no terminada), terminar.
  existe=$($OCI compute instance list --compartment-id "$TENANCY" --all \
    --query "data[?\"display-name\"=='$NOMBRE' && \"lifecycle-state\"!='TERMINATED'] | [0].\"lifecycle-state\"" \
    --raw-output 2>/dev/null)
  if [ -n "$existe" ] && [ "$existe" != "null" ]; then
    log "La instancia $NOMBRE ya existe (estado $existe). Fin del reintento."
    avisar "DomoVida: Ampere lista" "La VM $NOMBRE existe en Oracle Santiago (estado $existe)."
    exit 0
  fi

  intento=$((intento + 1))
  salida=$($OCI compute instance launch \
    --availability-domain "$AD" --compartment-id "$TENANCY" \
    --shape "$SHAPE" --shape-config "{\"ocpus\": $OCPUS, \"memoryInGBs\": $MEMORIA_GB}" \
    --image-id "$IMAGEN" --subnet-id "$SUBRED" --assign-public-ip true \
    --display-name "$NOMBRE" --ssh-authorized-keys-file "$LLAVE_SSH" 2>&1)
  codigo=$?

  if [ $codigo -eq 0 ]; then
    log "Intento $intento: CREADA."
    avisar "DomoVida: Ampere creada" "Se creo $NOMBRE ($OCPUS OCPU, $MEMORIA_GB GB) en Oracle Santiago tras $intento intentos."
    exit 0
  elif echo "$salida" | grep -qiE "out of (host )?capacity|InternalError"; then
    log "Intento $intento: sin capacidad."
  elif echo "$salida" | grep -qiE "TooManyRequests|429"; then
    log "Intento $intento: demasiadas solicitudes, se espera el doble."
    sleep "$INTERVALO"
  else
    errores=$((errores + 1))
    log "Intento $intento: error inesperado ($errores seguidos): $(echo "$salida" | tr '\n' ' ' | cut -c1-400)"
    if [ $errores -ge 5 ]; then
      avisar "DomoVida: reintento Ampere detenido" "5 errores seguidos. Revisar ~/ampere/intentos.log"
      exit 2
    fi
    sleep "$INTERVALO"; continue
  fi
  errores=0
  sleep "$INTERVALO"
done
