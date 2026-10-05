"""
PS-01 · Autenticación de los sensores con clave de API.

Los sensores (Raspberry Pi o simulador) deben enviar la cabecera
    X-API-Key: <clave>
en cada POST a /api/sensor-data. La clave se define en la variable de
entorno DOMOVIDA_API_KEY (en Render: Environment; en local: archivo .env).

Si DOMOVIDA_API_KEY no está definida, la verificación queda desactivada
(modo desarrollo / modo borde sin configurar) y se avisa en el log.
"""
import logging
import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

logger = logging.getLogger("domovida.seguridad")

NOMBRE_CABECERA = "X-API-Key"


def clave_configurada() -> Optional[str]:
    """Devuelve la clave definida en el entorno, o None si no hay."""
    clave = os.getenv("DOMOVIDA_API_KEY", "").strip()
    return clave or None


def clave_valida(recibida: Optional[str], esperada: Optional[str]) -> bool:
    """Compara en tiempo constante (evita ataques de temporización)."""
    if esperada is None:
        return True  # verificación desactivada
    if not recibida:
        return False
    return secrets.compare_digest(recibida.encode(), esperada.encode())


_aviso_mostrado = False


def verificar_clave_sensor(x_api_key: Optional[str] = Header(default=None)):
    """Dependencia de FastAPI: rechaza con 401 si la clave falta o es incorrecta."""
    global _aviso_mostrado
    esperada = clave_configurada()
    if esperada is None and not _aviso_mostrado:
        logger.warning("DOMOVIDA_API_KEY no definida: /api/sensor-data acepta datos sin clave")
        _aviso_mostrado = True
    if not clave_valida(x_api_key, esperada):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API ausente o inválida",
            headers={"WWW-Authenticate": NOMBRE_CABECERA},
        )
