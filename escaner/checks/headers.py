"""Verificacion de cabeceras de seguridad HTTP."""

from __future__ import annotations

from typing import Any


# Cabeceras con su peso en el puntaje y descripcion educativa
SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "weight": 5,
        "description": "Controla que recursos puede cargar la pagina",
    },
    "Strict-Transport-Security": {
        "weight": 5,
        "description": "Fuerza conexiones HTTPS en visitas futuras",
    },
    "X-Frame-Options": {
        "weight": 3,
        "description": "Previene que el sitio sea embebido en iframes (clickjacking)",
    },
    "X-Content-Type-Options": {
        "weight": 3,
        "description": "Previene MIME sniffing del navegador",
    },
    "Referrer-Policy": {
        "weight": 2,
        "description": "Controla que informacion de referencia se envia",
    },
    "Permissions-Policy": {
        "weight": 2,
        "description": "Controla acceso a APIs del navegador (camara, microfono, etc.)",
    },
    "X-XSS-Protection": {
        "weight": 1,
        "description": "Proteccion XSS legacy del navegador",
    },
    "Cache-Control": {
        "weight": 1,
        "description": "Controla el almacenamiento en cache (puede exponer datos sensibles)",
    },
}

MAX_HEADER_SCORE = sum(h["weight"] for h in SECURITY_HEADERS.values())

# Normalizamos a 20 puntos del total
HEADER_TOTAL = 20


def check_security_headers(response_headers: dict[str, Any]) -> dict:
    """Verifica la presencia de cabeceras de seguridad.

    Args:
        response_headers: Headers de la respuesta HTTP.

    Returns:
        Dict con resultados del check.
    """
    items = []
    raw_score = 0

    for header_name, info in SECURITY_HEADERS.items():
        present = header_name in response_headers
        value = response_headers.get(header_name, "")
        items.append({
            "header": header_name,
            "present": present,
            "value": str(value) if present else "",
            "description": info["description"],
            "weight": info["weight"],
        })
        if present:
            raw_score += info["weight"]

    # Normalizar puntaje a la escala del total asignado
    normalized_score = round((raw_score / MAX_HEADER_SCORE) * HEADER_TOTAL) if MAX_HEADER_SCORE > 0 else 0
    present_count = sum(1 for item in items if item["present"])

    return {
        "name": "Cabeceras de Seguridad",
        "passed": present_count >= len(SECURITY_HEADERS) // 2,
        "score": normalized_score,
        "max_score": HEADER_TOTAL,
        "detail": f"{present_count}/{len(SECURITY_HEADERS)} cabeceras presentes",
        "icon": "🛡️",
        "items": items,
    }
