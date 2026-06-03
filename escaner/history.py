"""Gestion del historial de escaneos."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "historial.json"


def append_scan_result(url: str, result: dict) -> None:
    """Agrega un resultado de escaneo al historial JSON.

    Fix vs original: usa 'with' para cerrar el archivo correctamente
    y ruta absoluta relativa al proyecto.
    """
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "score": result.get("total_score", 0),
        "max_score": result.get("max_score", 100),
        "status": "success" if not result.get("error") else "error",
    }

    history = load_history()
    history.append(entry)

    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history() -> list[dict]:
    """Carga el historial de escaneos desde el archivo JSON."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def clear_history() -> None:
    """Limpia el historial de escaneos."""
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump([], f)
