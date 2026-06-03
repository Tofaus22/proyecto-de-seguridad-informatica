"""Verificacion de politicas de correo antisuplantacion (SPF y DMARC) via DNS."""

from __future__ import annotations

from urllib.parse import urlparse
import requests

DNS_MAIL_SCORE = 15


def check_dns_mail_security(url: str) -> dict:
    """Verifica la presencia de registros SPF y DMARC utilizando la API DoH de Google.

    Args:
        url: URL del sitio a verificar.

    Returns:
        Dict con los resultados.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.path

    # Limpiar hostname de www. si es necesario, o mantenerlo
    if hostname.startswith("www."):
        domain = hostname[4:]
    else:
        domain = hostname

    items = []
    has_spf = False
    has_dmarc = False
    spf_record = ""
    dmarc_record = ""

    # 1. Consultar registro SPF (en los registros TXT del dominio raiz o hostname)
    try:
        response_spf = requests.get(
            "https://dns.google/resolve",
            params={"name": domain, "type": "TXT"},
            timeout=8
        )
        if response_spf.status_code == 200:
            data = response_spf.json()
            if "Answer" in data:
                for answer in data["Answer"]:
                    txt_data = answer.get("data", "")
                    # Limpiar comillas
                    txt_data_clean = txt_data.replace('"', '').strip()
                    if txt_data_clean.lower().startswith("v=spf1"):
                        has_spf = True
                        spf_record = txt_data_clean
                        break
    except Exception:
        pass

    # 2. Consultar registro DMARC (en los registros TXT de _dmarc.{dominio})
    try:
        response_dmarc = requests.get(
            "https://dns.google/resolve",
            params={"name": f"_dmarc.{domain}", "type": "TXT"},
            timeout=8
        )
        if response_dmarc.status_code == 200:
            data = response_dmarc.json()
            if "Answer" in data:
                for answer in data["Answer"]:
                    txt_data = answer.get("data", "")
                    txt_data_clean = txt_data.replace('"', '').strip()
                    if txt_data_clean.lower().startswith("v=dmarc1"):
                        has_dmarc = True
                        dmarc_record = txt_data_clean
                        break
    except Exception:
        pass

    # Calcular puntaje
    score = 0
    if has_spf:
        score += 7
        items.append({
            "name": "Registro SPF",
            "present": True,
            "value": spf_record,
            "category": "DNS TXT",
            "risk": "bajo"
        })
    else:
        items.append({
            "name": "Registro SPF",
            "present": False,
            "value": "Ausente o no encontrado",
            "category": "DNS TXT",
            "risk": "medio"
        })

    if has_dmarc:
        score += 8
        items.append({
            "name": "Registro DMARC",
            "present": True,
            "value": dmarc_record,
            "category": "DNS TXT",
            "risk": "bajo"
        })
    else:
        items.append({
            "name": "Registro DMARC",
            "present": False,
            "value": "Ausente o no encontrado",
            "category": "DNS TXT",
            "risk": "medio"
        })

    # Generar detalle educativo
    if has_spf and has_dmarc:
        detail = "Políticas SPF y DMARC configuradas correctamente en DNS"
        passed = True
    elif has_spf:
        detail = "SPF presente, pero DMARC está ausente (riesgo de spoofing)"
        passed = False
    elif has_dmarc:
        detail = "DMARC presente, pero SPF está ausente (configuración incompleta)"
        passed = False
    else:
        detail = "Sin protección de correo en DNS (SPF y DMARC ausentes)"
        passed = False

    return {
        "name": "Políticas DNS (Correo)",
        "passed": passed,
        "score": score,
        "max_score": DNS_MAIL_SCORE,
        "detail": detail,
        "icon": "✉️",
        "items": items,
    }
