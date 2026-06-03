"""Escaner web educativo y pasivo.

Uso:
    python escaner_web.py https://ejemplo.com
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

if TYPE_CHECKING:
    from requests import Response
else:
    Response = Any

DEPENDENCIES_ERROR = None

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.exceptions import RequestException
except ModuleNotFoundError as error:
    requests = None
    BeautifulSoup = None
    RequestException = Exception
    DEPENDENCIES_ERROR = error


SECURITY_HEADERS = {
    "Content-Security-Policy": 15,
    "Strict-Transport-Security": 15,
    "X-Frame-Options": 15,
}

HTTPS_SCORE = 25
COOKIES_SCORE = 15
CSRF_SCORE = 15
TIMEOUT_SECONDS = 10
HISTORY_FILE = Path("historial.txt")


def normalize_url(url: str) -> str:
    """Agrega https:// si el usuario no incluye un esquema."""
    if not urlparse(url).scheme:
        return f"https://{url}"
    return url


def fetch_site(url: str) -> Response:
    """Hace una sola peticion GET para analizar el sitio de forma pasiva."""
    headers = {"User-Agent": "EscanerEducativo/1.0"}
    return requests.get(url, timeout=TIMEOUT_SECONDS, headers=headers, allow_redirects=True)


def check_https(final_url: str) -> tuple[bool, int]:
    uses_https = urlparse(final_url).scheme.lower() == "https"
    return uses_https, HTTPS_SCORE if uses_https else 0


def check_security_headers(response: Response) -> tuple[list[tuple[str, bool]], int]:
    results = []
    score = 0

    for header_name, header_score in SECURITY_HEADERS.items():
        present = header_name in response.headers
        results.append((header_name, present))
        if present:
            score += header_score

    return results, score


def check_cookies(response: Response) -> tuple[list[tuple[str, bool]], int]:
    cookies = []

    for cookie in response.cookies:
        cookies.append((cookie.name, bool(cookie.secure)))

    if not cookies:
        return [], COOKIES_SCORE

    secure_count = sum(1 for _, is_secure in cookies if is_secure)
    score = round((secure_count / len(cookies)) * COOKIES_SCORE)
    return cookies, score


def check_forms_for_csrf(html: str) -> tuple[list[tuple[int, bool]], int]:
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")

    if not forms:
        return [], CSRF_SCORE

    results = []
    csrf_matches = 0

    for index, form in enumerate(forms, start=1):
        has_csrf_hint = "csrf" in str(form).lower()
        results.append((index, has_csrf_hint))
        if has_csrf_hint:
            csrf_matches += 1

    score = round((csrf_matches / len(forms)) * CSRF_SCORE)
    return results, score


def append_title(lines: list[str], text: str) -> None:
    if lines:
        lines.append("")
    lines.append(text)
    lines.append("-" * len(text))


def format_status(ok: bool, label: str, detail: str) -> str:
    icon = "✅" if ok else "⚠️"
    return f"{icon} {label}: {detail}"


def append_history_entry(url: str, report: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 80
    history_entry = "\n".join(
        [
            separator,
            f"Fecha        : {timestamp}",
            f"URL analizada: {url}",
            separator,
            report,
            "",
        ]
    )
    HISTORY_FILE.open("a", encoding="utf-8").write(history_entry)


def analyze_site(url: str) -> str:
    normalized_url = normalize_url(url)
    lines: list[str] = []

    try:
        response = fetch_site(normalized_url)
    except RequestException as error:
        append_title(lines, "Error de analisis")
        lines.append("❌ No se pudo analizar el sitio.")
        lines.append(f"Detalle: {error}")
        report = "\n".join(lines)
        append_history_entry(normalized_url, report)
        return report

    response.raise_for_status()

    append_title(lines, "Resumen general")
    lines.append(f"URL solicitada : {normalized_url}")
    lines.append(f"URL final      : {response.url}")
    lines.append(f"Estado HTTP    : {response.status_code}")

    https_ok, https_score = check_https(response.url)
    header_results, header_score = check_security_headers(response)
    cookie_results, cookie_score = check_cookies(response)
    form_results, form_score = check_forms_for_csrf(response.text)

    total_score = https_score + header_score + cookie_score + form_score

    append_title(lines, "1. HTTPS")
    lines.append(
        format_status(
            https_ok,
            "Conexion segura",
            "El sitio usa HTTPS" if https_ok else "El sitio no usa HTTPS",
        )
    )

    append_title(lines, "2. Cabeceras de seguridad")
    for header_name, present in header_results:
        detail = "Presente" if present else "Ausente"
        lines.append(format_status(present, header_name, detail))

    append_title(lines, "3. Cookies")
    if not cookie_results:
        lines.append("ℹ️ No se detectaron cookies en la respuesta.")
    else:
        for cookie_name, is_secure in cookie_results:
            detail = "Incluye atributo Secure" if is_secure else "No incluye atributo Secure"
            lines.append(format_status(is_secure, f"Cookie {cookie_name}", detail))

    append_title(lines, "4. Formularios y CSRF")
    if not form_results:
        lines.append("ℹ️ No se encontraron formularios HTML.")
    else:
        for form_number, has_csrf_hint in form_results:
            detail = "Se encontro la palabra 'csrf'" if has_csrf_hint else "No se encontro ninguna pista de CSRF"
            lines.append(format_status(has_csrf_hint, f"Formulario #{form_number}", detail))

    append_title(lines, "5. Puntaje de seguridad")
    lines.append(f"Puntaje estimado: {total_score}/100")

    report = "\n".join(lines)
    append_history_entry(normalized_url, report)
    return report


def main() -> None:
    if DEPENDENCIES_ERROR is not None:
        print("❌ Faltan dependencias para ejecutar el escaner.")
        print("Instala primero: pip install requests beautifulsoup4")
        print(f"Detalle: no se encontro el modulo '{DEPENDENCIES_ERROR.name}'")
        return

    if len(sys.argv) < 2:
        print("Uso: python escaner_web.py https://ejemplo.com")
        return

    report = analyze_site(sys.argv[1])
    print(report)


if __name__ == "__main__":
    try:
        main()
    except RequestException as error:
        print("❌ Error HTTP durante el analisis.")
        print(f"Detalle: {error}")
    except Exception as error:
        print("❌ Ocurrio un error inesperado.")
        print(f"Detalle: {error}")