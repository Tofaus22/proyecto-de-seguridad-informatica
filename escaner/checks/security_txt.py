"""Verificacion de la presencia de security.txt (RFC 9116)."""

from __future__ import annotations

from urllib.parse import urlparse
import requests

SECURITY_TXT_SCORE = 5


def check_security_txt(url: str) -> dict:
    """Verifica si existe el archivo security.txt en la ruta estandar.

    Args:
        url: URL del sitio a verificar.

    Returns:
        Dict con resultados.
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    paths_to_try = [
        "/.well-known/security.txt",
        "/security.txt"
    ]

    has_security_txt = False
    found_url = ""
    contact_info = ""
    score = 0
    detail = ""
    items = []

    for path in paths_to_try:
        try:
            target_url = f"{base_url}{path}"
            response = requests.get(
                target_url,
                timeout=6,
                headers={"User-Agent": "EscanerEducativo/2.0"},
                allow_redirects=True
            )

            if response.status_code == 200:
                content = response.text.lower()
                if "contact:" in content:
                    has_security_txt = True
                    found_url = target_url
                    score = SECURITY_TXT_SCORE

                    # Intentar extraer la linea de contacto
                    for line in response.text.splitlines():
                        if line.strip().lower().startswith("contact:"):
                            contact_info = line.strip()
                            items.append({
                                "label": "Contacto",
                                "value": contact_info,
                                "present": True
                            })
                            break
                    break
        except Exception:
            pass

    if has_security_txt:
        detail = "Archivo security.txt presente con datos de contacto"
        passed = True
    else:
        detail = "No se encontro el archivo security.txt"
        passed = False
        score = 0

    return {
        "name": "Archivo security.txt",
        "passed": passed,
        "score": score,
        "max_score": SECURITY_TXT_SCORE,
        "detail": detail,
        "icon": "📜",
        "items": items,
    }
