"""Verificacion de uso de HTTPS."""

from __future__ import annotations

from urllib.parse import urlparse


HTTPS_SCORE = 25


def check_https(final_url: str) -> dict:
    """Verifica si la URL final usa HTTPS.

    Retorna un dict con:
        - name: nombre del check
        - passed: bool
        - score: puntos obtenidos
        - max_score: puntos posibles
        - detail: descripcion del resultado
    """
    uses_https = urlparse(final_url).scheme.lower() == "https"
    return {
        "name": "HTTPS",
        "passed": uses_https,
        "score": HTTPS_SCORE if uses_https else 0,
        "max_score": HTTPS_SCORE,
        "detail": "El sitio usa HTTPS" if uses_https else "El sitio NO usa HTTPS",
        "icon": "🔒" if uses_https else "🔓",
    }
