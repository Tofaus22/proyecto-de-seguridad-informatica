"""Deteccion de proteccion CSRF en formularios HTML."""

from __future__ import annotations

from bs4 import BeautifulSoup

CSRF_SCORE = 5


def check_forms_for_csrf(html: str) -> dict:
    """Busca indicios de proteccion CSRF en formularios.

    Mejora vs original: busca tokens hidden, meta tags csrf, y la palabra csrf.

    Args:
        html: Contenido HTML de la pagina.

    Returns:
        Dict con resultados del check.
    """
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")

    if not forms:
        return {
            "name": "Proteccion CSRF",
            "passed": True,
            "score": CSRF_SCORE,
            "max_score": CSRF_SCORE,
            "detail": "No se encontraron formularios HTML",
            "icon": "📝",
            "items": [],
        }

    # Buscar meta tags csrf globales
    meta_csrf = soup.find("meta", attrs={"name": lambda x: x and "csrf" in x.lower()}) if soup.find("meta") else None

    items = []
    protected_count = 0

    for index, form in enumerate(forms, start=1):
        form_str = str(form).lower()
        method = (form.get("method") or "get").upper()

        # Heuristicas de deteccion
        has_csrf_word = "csrf" in form_str
        has_token_input = bool(form.find("input", attrs={
            "type": "hidden",
            "name": lambda x: x and any(
                word in x.lower()
                for word in ["csrf", "token", "_token", "authenticity"]
            ),
        }))
        has_meta_csrf = meta_csrf is not None

        is_protected = has_csrf_word or has_token_input or has_meta_csrf
        if is_protected:
            protected_count += 1

        reason = []
        if has_token_input:
            reason.append("Campo hidden con token")
        if has_csrf_word:
            reason.append("Referencia a 'csrf'")
        if has_meta_csrf:
            reason.append("Meta tag CSRF global")
        if not reason:
            reason.append("Sin proteccion detectada")

        items.append({
            "form_number": index,
            "method": method,
            "action": form.get("action", "(sin action)"),
            "protected": is_protected,
            "reason": ", ".join(reason),
        })

    score = round((protected_count / len(forms)) * CSRF_SCORE) if forms else 0

    return {
        "name": "Proteccion CSRF",
        "passed": protected_count >= len(forms) * 0.5,
        "score": score,
        "max_score": CSRF_SCORE,
        "detail": f"{protected_count}/{len(forms)} formularios con indicios de proteccion",
        "icon": "📝",
        "items": items,
    }
