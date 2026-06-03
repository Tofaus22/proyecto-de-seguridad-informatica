"""Deteccion de contenido mixto (mixed content)."""

from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup

MIXED_CONTENT_SCORE = 10


# Etiquetas y atributos que cargan recursos externos
RESOURCE_TAGS = {
    "script": "src",
    "link": "href",
    "img": "src",
    "iframe": "src",
    "source": "src",
    "video": "src",
    "audio": "src",
    "object": "data",
    "embed": "src",
}


def check_mixed_content(html: str, page_url: str) -> dict:
    """Detecta recursos HTTP en paginas HTTPS.

    Cargar recursos por HTTP en una pagina HTTPS es un riesgo de seguridad
    conocido como 'mixed content'.

    Args:
        html: Contenido HTML de la pagina.
        page_url: URL de la pagina analizada.

    Returns:
        Dict con resultados del check.
    """
    is_https = urlparse(page_url).scheme == "https"

    if not is_https:
        return {
            "name": "Contenido Mixto",
            "passed": False,
            "score": 0,
            "max_score": MIXED_CONTENT_SCORE,
            "detail": "El sitio no usa HTTPS — no aplica verificacion de contenido mixto",
            "icon": "🔀",
            "items": [],
        }

    soup = BeautifulSoup(html, "html.parser")
    items = []
    insecure_count = 0
    total_external = 0

    for tag_name, attr_name in RESOURCE_TAGS.items():
        for tag in soup.find_all(tag_name):
            url = tag.get(attr_name, "")
            if not url or url.startswith("data:") or url.startswith("#"):
                continue

            parsed = urlparse(url)
            # Solo nos interesan URLs absolutas con esquema HTTP
            if parsed.scheme == "http":
                insecure_count += 1
                total_external += 1
                items.append({
                    "tag": tag_name,
                    "attribute": attr_name,
                    "url": url[:120],  # Truncar URLs muy largas
                    "secure": False,
                })
            elif parsed.scheme == "https":
                total_external += 1

    if insecure_count == 0:
        score = MIXED_CONTENT_SCORE
        detail = "No se detecto contenido mixto"
        passed = True
    else:
        score = max(0, MIXED_CONTENT_SCORE - (insecure_count * 2))
        detail = f"{insecure_count} recurso(s) cargados por HTTP inseguro"
        passed = False

    return {
        "name": "Contenido Mixto",
        "passed": passed,
        "score": score,
        "max_score": MIXED_CONTENT_SCORE,
        "detail": detail,
        "icon": "🔀",
        "items": items,
    }
