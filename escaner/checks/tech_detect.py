"""Deteccion de tecnologias del servidor."""

from __future__ import annotations

from typing import Any


# Headers que revelan tecnologias
TECH_HEADERS = {
    "Server": "Servidor web",
    "X-Powered-By": "Framework / Lenguaje",
    "X-Generator": "CMS / Generador",
    "X-AspNet-Version": "ASP.NET Version",
    "X-AspNetMvc-Version": "ASP.NET MVC Version",
    "X-Drupal-Cache": "Drupal CMS",
    "X-Varnish": "Varnish Cache",
    "X-Cache": "Sistema de cache",
    "Via": "Proxy / CDN",
    "CF-RAY": "Cloudflare CDN",
}

TECH_SCORE = 5


def detect_technologies(response_headers: dict[str, Any], html: str = "") -> dict:
    """Detecta tecnologias expuestas en headers y HTML.

    Exponer versiones de software es un riesgo de seguridad
    porque facilita ataques dirigidos.

    Args:
        response_headers: Headers de la respuesta HTTP.
        html: Contenido HTML (opcional).

    Returns:
        Dict con resultados del check.
    """
    items = []
    exposed_count = 0

    for header_name, category in TECH_HEADERS.items():
        if header_name in response_headers:
            value = str(response_headers[header_name])
            items.append({
                "source": "Header",
                "name": header_name,
                "category": category,
                "value": value,
                "risk": _assess_risk(header_name, value),
            })
            exposed_count += 1

    # Buscar meta generator en HTML
    if html:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and generator.get("content"):
            items.append({
                "source": "HTML Meta",
                "name": "generator",
                "category": "CMS / Framework",
                "value": generator["content"],
                "risk": "medio",
            })
            exposed_count += 1

    # Menos tecnologias expuestas = mejor puntaje
    if exposed_count == 0:
        score = TECH_SCORE
        detail = "No se detectaron tecnologias expuestas"
    elif exposed_count <= 2:
        score = TECH_SCORE - 1
        detail = f"{exposed_count} tecnologia(s) detectada(s)"
    elif exposed_count <= 4:
        score = TECH_SCORE - 2
        detail = f"{exposed_count} tecnologias expuestas"
    else:
        score = max(0, TECH_SCORE - 3)
        detail = f"{exposed_count} tecnologias expuestas — riesgo de informacion"

    return {
        "name": "Tecnologias Expuestas",
        "passed": exposed_count <= 2,
        "score": score,
        "max_score": TECH_SCORE,
        "detail": detail,
        "icon": "🔧",
        "items": items,
    }


def _assess_risk(header_name: str, value: str) -> str:
    """Evalua el riesgo de exponer un header de tecnologia."""
    # Si incluye numero de version, riesgo mas alto
    import re

    if re.search(r"\d+\.\d+", value):
        return "alto"
    if header_name in ("Server", "X-Powered-By"):
        return "medio"
    return "bajo"
