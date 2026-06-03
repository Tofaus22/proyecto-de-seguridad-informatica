"""Verificacion y analisis del archivo robots.txt."""

from __future__ import annotations

from urllib.parse import urlparse
import requests

ROBOTS_SCORE = 5

# Palabras clave sospechosas o sensibles a buscar en las reglas de desautorizacion
SENSITIVE_KEYWORDS = [
    "admin", "backup", "respaldo", "config", "secret", "private", "privado",
    "db", "database", "base-de-datos", "mysql", "postgres", "test", "prueba",
    "login", "root", "api", "credential", "credencial", "key", "clave"
]


def check_robots_txt(url: str) -> dict:
    """Verifica si existe el archivo robots.txt y analiza rutas expuestas.

    Args:
        url: URL final o base del sitio analizado.

    Returns:
        Dict con resultados del check.
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_url}/robots.txt"

    items = []
    has_robots = False
    score = 0
    detail = ""

    try:
        response = requests.get(
            robots_url,
            timeout=8,
            headers={"User-Agent": "EscanerEducativo/2.0"},
            allow_redirects=True
        )

        if response.status_code == 200:
            has_robots = True
            lines = response.text.splitlines()
            exposed_paths = []

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if ":" in line:
                    parts = line.split(":", 1)
                    directive = parts[0].strip().lower()
                    value = parts[1].strip()

                    if directive == "disallow" and value:
                        # Limpiar path
                        path_clean = value.lower()
                        # Verificar si contiene palabras sensibles
                        matched_words = [word for word in SENSITIVE_KEYWORDS if word in path_clean]

                        if matched_words:
                            exposed_paths.append({
                                "path": value,
                                "matched": matched_words
                            })
                            items.append({
                                "directive": "Disallow",
                                "value": value,
                                "risk": "medio",
                                "reason": f"Expone ruta con: {', '.join(matched_words)}"
                            })
                        else:
                            items.append({
                                "directive": "Disallow",
                                "value": value,
                                "risk": "bajo",
                                "reason": "Ruta estandar"
                            })

            if exposed_paths:
                score = ROBOTS_SCORE - min(5, len(exposed_paths) * 2)
                detail = f"robots.txt expone {len(exposed_paths)} ruta(s) potencialmente sensible(s)"
            else:
                score = ROBOTS_SCORE
                detail = "robots.txt presente y configurado de forma segura"

        else:
            # Archivo no existe o devuelve error (404, 403, etc.)
            score = ROBOTS_SCORE // 2  # 5 puntos
            detail = f"No se encontro el archivo robots.txt (HTTP {response.status_code})"

    except Exception as error:
        score = 0
        detail = f"Error al verificar robots.txt: {error}"

    return {
        "name": "Archivo robots.txt",
        "passed": has_robots and score >= ROBOTS_SCORE * 0.7,
        "score": score,
        "max_score": ROBOTS_SCORE,
        "detail": detail,
        "icon": "🤖",
        "items": items[:10],  # Limitar a los primeros 10 para no saturar
    }
