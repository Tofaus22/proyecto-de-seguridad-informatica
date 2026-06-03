"""Servidor web Flask para el dashboard del escaner."""

from __future__ import annotations

import sys
from pathlib import Path

# Agregar el directorio raiz al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request

from escaner.scanner import scan_site
from escaner.history import load_history, clear_history

app = Flask(__name__)


@app.route("/")
def index():
    """Pagina principal del dashboard."""
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    """Endpoint para ejecutar un escaneo.

    Recibe JSON: {"url": "https://example.com"}
    Devuelve JSON con los resultados del escaneo.
    """
    data = request.get_json(silent=True)
    if not data or not data.get("url"):
        return jsonify({"error": "Se requiere una URL para escanear"}), 400

    url = data["url"].strip()
    if not url:
        return jsonify({"error": "La URL no puede estar vacia"}), 400

    try:
        result = scan_site(url)
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": f"Error inesperado: {error}"}), 500


@app.route("/api/history")
def api_history():
    """Endpoint para obtener el historial de escaneos."""
    history = load_history()
    # Retornar los ultimos 50, mas recientes primero
    return jsonify(list(reversed(history[-50:])))


@app.route("/api/history", methods=["DELETE"])
def api_clear_history():
    """Endpoint para limpiar el historial."""
    clear_history()
    return jsonify({"message": "Historial limpiado"})


def run_dashboard(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """Inicia el servidor del dashboard."""
    print(f"\n[*] Escaner Web Dashboard")
    print(f"    Abre tu navegador en: http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard(debug=True)
