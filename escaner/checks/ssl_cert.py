"""Verificacion del certificado SSL."""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

SSL_SCORE = 15


def check_ssl_certificate(url: str) -> dict:
    """Verifica el certificado SSL del sitio.

    Revisa: emisor, fecha de expiracion, dias restantes, protocolo.

    Args:
        url: URL del sitio a verificar.

    Returns:
        Dict con resultados del check.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname or parsed.scheme != "https":
        return {
            "name": "Certificado SSL",
            "passed": False,
            "score": 0,
            "max_score": SSL_SCORE,
            "detail": "El sitio no usa HTTPS, no hay certificado que verificar",
            "icon": "📜",
            "items": [],
        }

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                protocol_version = ssock.version()

        if not cert:
            return {
                "name": "Certificado SSL",
                "passed": False,
                "score": 0,
                "max_score": SSL_SCORE,
                "detail": "No se pudo obtener el certificado",
                "icon": "📜",
                "items": [],
            }

        # Extraer info del certificado
        subject = dict(x[0] for x in cert.get("subject", ()))
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        not_after_str = cert.get("notAfter", "")
        not_before_str = cert.get("notBefore", "")

        # Calcular dias restantes
        not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_remaining = (not_after - now).days

        # Verificar si es autofirmado
        is_self_signed = subject == issuer

        # Calcular puntaje
        score = 0
        if days_remaining > 30:
            score += 7  # Certificado vigente con margen
        elif days_remaining > 0:
            score += 3  # Certificado vigente pero proximo a expirar
        # Si expirado: 0 puntos

        if not is_self_signed:
            score += 5  # No es autofirmado

        if protocol_version and "TLSv1.2" in protocol_version or "TLSv1.3" in protocol_version:
            score += 3  # Protocolo moderno

        common_name = subject.get("commonName", "desconocido")
        issuer_org = issuer.get("organizationName", issuer.get("commonName", "desconocido"))

        items = [
            {"label": "Dominio (CN)", "value": common_name},
            {"label": "Emisor", "value": issuer_org},
            {"label": "Valido hasta", "value": not_after_str},
            {"label": "Dias restantes", "value": str(days_remaining)},
            {"label": "Autofirmado", "value": "Si" if is_self_signed else "No"},
            {"label": "Protocolo", "value": protocol_version or "desconocido"},
        ]

        if days_remaining <= 0:
            detail = f"Certificado EXPIRADO hace {abs(days_remaining)} dias"
            passed = False
        elif days_remaining <= 30:
            detail = f"Certificado expira en {days_remaining} dias — renovar pronto"
            passed = True
        else:
            detail = f"Certificado valido por {days_remaining} dias mas"
            passed = True

        return {
            "name": "Certificado SSL",
            "passed": passed,
            "score": min(score, SSL_SCORE),
            "max_score": SSL_SCORE,
            "detail": detail,
            "icon": "📜",
            "items": items,
        }

    except Exception as error:
        return {
            "name": "Certificado SSL",
            "passed": False,
            "score": 0,
            "max_score": SSL_SCORE,
            "detail": f"Error al verificar certificado: {error}",
            "icon": "📜",
            "items": [],
        }
