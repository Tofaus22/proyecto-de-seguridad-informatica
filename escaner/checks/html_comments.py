"""Auditoria de comentarios HTML en busca de informacion sensible."""

from __future__ import annotations

import re
from bs4 import BeautifulSoup, Comment

COMMENTS_SCORE = 5

# Palabras clave que denotan anotaciones internas o secretos
SENSITIVE_KEYWORDS = [
    r"\btodo\b", r"\bfixme\b", r"\bpassword\b", r"\bcontrase[nñ]a\b",
    r"\bkey\b", r"\btoken\b", r"\bsecret\b", r"\badmin\b", r"\bapi\b",
    r"\bdb_\b", r"\bcredentials?\b", r"\bcredenciales?\b", r"\buser\b",
    r"\bpass\b"
]


def check_html_comments(html: str) -> dict:
    """Busca comentarios HTML y audita si exponen informacion de desarrollo o credenciales.

    Args:
        html: Contenido HTML de la pagina.

    Returns:
        Dict con los resultados.
    """
    soup = BeautifulSoup(html, "html.parser")
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    items = []
    sensitive_comments_count = 0

    # Compilar expresion regular para busqueda rapida
    pattern = re.compile("|".join(SENSITIVE_KEYWORDS), re.IGNORECASE)

    for i, comment in enumerate(comments, start=1):
        comment_text = comment.strip()
        if not comment_text:
            continue

        match = pattern.search(comment_text)
        if match:
            sensitive_comments_count += 1
            # Truncar comentarios muy largos
            short_text = comment_text[:100] + "..." if len(comment_text) > 100 else comment_text
            items.append({
                "comment_number": i,
                "text": short_text,
                "matched": match.group(0),
                "risk": "medio",
                "reason": "Contiene palabra clave de desarrollo o credencial"
            })

    # Calcular puntaje
    if not comments:
        score = COMMENTS_SCORE
        detail = "No se encontraron comentarios HTML en la pagina"
        passed = True
    elif sensitive_comments_count == 0:
        score = COMMENTS_SCORE
        detail = f"Se analizaron {len(comments)} comentarios HTML sin encontrar contenido sensible"
        passed = True
    else:
        score = max(0, COMMENTS_SCORE - (sensitive_comments_count * 2))
        detail = f"Se detectaron {sensitive_comments_count} comentario(s) HTML con informacion sensible"
        passed = False

    return {
        "name": "Comentarios HTML",
        "passed": passed,
        "score": score,
        "max_score": COMMENTS_SCORE,
        "detail": detail,
        "icon": "💬",
        "items": items[:10],  # Limitar a los 10 primeros
    }
