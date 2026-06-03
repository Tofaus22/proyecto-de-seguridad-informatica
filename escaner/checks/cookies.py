"""Verificacion de seguridad de cookies."""

from __future__ import annotations

COOKIES_SCORE = 10


def check_cookies(response_cookies: list[dict]) -> dict:
    """Verifica atributos de seguridad en las cookies.

    Ahora revisa Secure, HttpOnly y SameSite (expandido vs original).

    Args:
        response_cookies: Lista de dicts con info de cada cookie.

    Returns:
        Dict con resultados del check.
    """
    if not response_cookies:
        return {
            "name": "Cookies",
            "passed": True,
            "score": COOKIES_SCORE,
            "max_score": COOKIES_SCORE,
            "detail": "No se detectaron cookies en la respuesta",
            "icon": "🍪",
            "items": [],
        }

    items = []
    total_attrs = 0
    present_attrs = 0

    for cookie in response_cookies:
        name = cookie.get("name", "desconocida")
        secure = cookie.get("secure", False)
        httponly = cookie.get("httponly", False)
        samesite = cookie.get("samesite", "")

        attrs = {
            "Secure": secure,
            "HttpOnly": httponly,
            "SameSite": bool(samesite),
        }

        total_attrs += len(attrs)
        present_attrs += sum(1 for v in attrs.values() if v)

        items.append({
            "name": name,
            "secure": secure,
            "httponly": httponly,
            "samesite": samesite if samesite else "No definido",
            "attrs_ok": sum(1 for v in attrs.values() if v),
            "attrs_total": len(attrs),
        })

    score = round((present_attrs / total_attrs) * COOKIES_SCORE) if total_attrs > 0 else 0
    secure_count = sum(1 for item in items if item["attrs_ok"] == item["attrs_total"])

    return {
        "name": "Cookies",
        "passed": score >= COOKIES_SCORE * 0.6,
        "score": score,
        "max_score": COOKIES_SCORE,
        "detail": f"{secure_count}/{len(items)} cookies completamente seguras",
        "icon": "🍪",
        "items": items,
    }
