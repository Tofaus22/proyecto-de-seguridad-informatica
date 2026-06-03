"""Generacion de reportes en diferentes formatos."""

from __future__ import annotations

import json


def format_text_report(result: dict) -> str:
    """Genera un reporte en texto plano legible."""
    lines: list[str] = []

    def title(text: str) -> None:
        if lines:
            lines.append("")
        lines.append(text)
        lines.append("-" * len(text))

    url_info = result.get("url_info", {})
    title("Resumen general")
    lines.append(f"URL solicitada : {url_info.get('requested', 'N/A')}")
    lines.append(f"URL final      : {url_info.get('final', 'N/A')}")
    lines.append(f"Estado HTTP    : {url_info.get('status_code', 'N/A')}")

    for check in result.get("checks", []):
        icon = "✅" if check["passed"] else "⚠️"
        title(f"{check['name']}")
        lines.append(f"{icon} {check['detail']} ({check['score']}/{check['max_score']})")

        for item in check.get("items", []):
            if "header" in item:
                status = "✅" if item["present"] else "⚠️"
                val = f" = {item['value']}" if item.get("value") else ""
                lines.append(f"  {status} {item['header']}{val}")
            elif "name" in item and "secure" in item:
                status = "✅" if item.get("attrs_ok", 0) == item.get("attrs_total", 0) else "⚠️"
                lines.append(f"  {status} Cookie: {item['name']}")
            elif "form_number" in item:
                status = "✅" if item["protected"] else "⚠️"
                lines.append(f"  {status} Formulario #{item['form_number']}: {item['reason']}")
            elif "directive" in item:
                status = "⚠️" if item.get("risk") == "medio" else "ℹ️"
                lines.append(f"  {status} {item['directive']}: {item['value']} — {item['reason']}")
            elif item.get("category") == "DNS TXT":
                status = "✅" if item["present"] else "⚠️"
                lines.append(f"  {status} {item['name']}: {item['value']}")
            elif "comment_number" in item:
                lines.append(f"  ⚠️ Comentario #{item['comment_number']}: {item['text']} (Encontrado: '{item['matched']}')")
            elif "label" in item:
                lines.append(f"  {item['label']}: {item['value']}")
            elif "tag" in item:
                lines.append(f"  ⚠️ <{item['tag']}> carga: {item['url']}")
            elif "source" in item:
                risk_icon = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}.get(item.get("risk", ""), "⚪")
                lines.append(f"  {risk_icon} {item['category']}: {item['value']}")

    title("Puntaje de seguridad")
    lines.append(f"Puntaje estimado: {result['total_score']}/{result['max_score']}")

    return "\n".join(lines)


def format_json_report(result: dict) -> str:
    """Genera un reporte en formato JSON."""
    return json.dumps(result, ensure_ascii=False, indent=2)
