"""
PS-01 (parte 2) · Autenticación del cuidador con Supabase Auth.

El panel inicia sesión con correo y contraseña en Supabase Auth y envía el
token de acceso en la cabecera
    Authorization: Bearer <token>
al marcar una alerta como atendida. El backend valida el token consultando a
Supabase Auth (GET /auth/v1/user) y registra el correo del cuidador en
`resuelto_por`, de modo que queda trazabilidad de quién atendió cada alerta.

Variables de entorno (Render):
    SUPABASE_URL       URL del proyecto, por ejemplo https://xxxx.supabase.co
    SUPABASE_ANON_KEY  clave pública (anon / publishable) del proyecto

Si no están definidas, la verificación queda desactivada (modo desarrollo o
modo borde sin internet, donde Supabase no es alcanzable) y se avisa en el log.
"""
import logging
import os
from typing import Optional

import requests
from fastapi import Header, HTTPException, status

logger = logging.getLogger("domovida.auth")
_aviso_mostrado = False


def config_auth():
    """Devuelve (url, clave_publica) o (None, None) si la autenticación está desactivada."""
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    clave = os.getenv("SUPABASE_ANON_KEY", "").strip()
    if url and clave:
        return url, clave
    return None, None


def auth_activa() -> bool:
    return config_auth()[0] is not None


def _no_autorizado(mensaje: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=mensaje,
        headers={"WWW-Authenticate": "Bearer"},
    )


def verificar_cuidador(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    """Dependencia de FastAPI. Devuelve el correo del cuidador autenticado,
    o None si la autenticación está desactivada."""
    global _aviso_mostrado
    url, clave = config_auth()
    if url is None:
        if not _aviso_mostrado:
            logger.warning("SUPABASE_URL/SUPABASE_ANON_KEY no definidas: resolver alertas no exige sesión")
            _aviso_mostrado = True
        return None

    if not authorization or not authorization.lower().startswith("bearer "):
        _no_autorizado("Inicia sesión como cuidador para atender alertas")
    token = authorization[7:].strip()
    if not token:
        _no_autorizado("Inicia sesión como cuidador para atender alertas")

    try:
        r = requests.get(
            f"{url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": clave},
            timeout=8,
        )
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="No se pudo verificar la sesión con Supabase")

    if r.status_code != 200:
        _no_autorizado("Sesión inválida o expirada; vuelve a iniciar sesión")
    return (r.json() or {}).get("email") or "cuidador"
