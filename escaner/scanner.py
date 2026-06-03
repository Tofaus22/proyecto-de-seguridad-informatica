"""Orquestador principal del escaner de seguridad."""

from __future__ import annotations

from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

from escaner.checks import (
    check_cookies,
    check_forms_for_csrf,
    check_https,
    check_mixed_content,
    check_security_headers,
    check_ssl_certificate,
    detect_technologies,
    check_robots_txt,
    check_dns_mail_security,
    check_html_comments,
    check_security_txt,
)
from escaner.history import append_scan_result

TIMEOUT_SECONDS = 10
MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB


def normalize_url(url: str) -> str:
    """Agrega https:// si el usuario no incluye un esquema."""
    url = url.strip()
    if not urlparse(url).scheme:
        return f"https://{url}"
    return url


def _extract_cookies(response: requests.Response) -> list[dict]:
    """Extrae info de cookies en formato estructurado."""
    cookies = []
    for cookie in response.cookies:
        cookie_dict = {
            "name": cookie.name,
            "secure": bool(cookie.secure),
            "httponly": cookie.has_nonstandard_attr("httponly") or cookie.has_nonstandard_attr("HttpOnly"),
            "samesite": "",
        }
        # Intentar extraer SameSite
        for attr in ("samesite", "SameSite"):
            val = cookie.get_nonstandard_attr(attr)
            if val:
                cookie_dict["samesite"] = val
                break
        cookies.append(cookie_dict)
    return cookies


def scan_site(url: str) -> dict:
    """Ejecuta todos los checks de seguridad sobre un sitio web.

    Args:
        url: URL del sitio a analizar.

    Returns:
        Dict con todos los resultados estructurados.
    """
    normalized_url = normalize_url(url)

    try:
        response = requests.get(
            normalized_url,
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": "EscanerEducativo/2.0"},
            allow_redirects=True,
            stream=True,
        )

        # Limitar tamaño de respuesta
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_RESPONSE_SIZE:
            return _error_result(
                normalized_url,
                f"Respuesta demasiado grande ({int(content_length) // 1024 // 1024} MB)"
            )

        html = response.text

    except RequestException as error:
        return _error_result(normalized_url, str(error))

    # Ejecutar todos los checks
    final_url = response.url
    response_headers = response.headers
    cookie_list = _extract_cookies(response)

    checks = [
        check_https(final_url),
        check_ssl_certificate(final_url),
        check_security_headers(response_headers),
        check_cookies(cookie_list),
        check_forms_for_csrf(html),
        check_mixed_content(html, final_url),
        detect_technologies(response_headers, html),
        check_robots_txt(final_url),
        check_dns_mail_security(final_url),
        check_html_comments(html),
        check_security_txt(final_url),
    ]

    total_score = sum(c["score"] for c in checks)
    max_score = sum(c["max_score"] for c in checks)

    result = {
        "url_info": {
            "requested": normalized_url,
            "final": final_url,
            "status_code": response.status_code,
        },
        "checks": checks,
        "total_score": total_score,
        "max_score": max_score,
        "error": None,
    }

    # Guardar en historial
    try:
        append_scan_result(normalized_url, result)
    except OSError:
        pass  # No fallar si no se puede escribir el historial

    return result


def _error_result(url: str, detail: str) -> dict:
    """Genera un resultado de error."""
    result = {
        "url_info": {
            "requested": url,
            "final": None,
            "status_code": None,
        },
        "checks": [],
        "total_score": 0,
        "max_score": 100,
        "error": detail,
    }
    try:
        append_scan_result(url, result)
    except OSError:
        pass
    return result
