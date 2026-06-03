"""Punto de entrada principal del Escaner Web Educativo.

Uso:
    python main.py https://ejemplo.com          # Escaneo simple
    python main.py --batch links.txt            # Escaneo por lotes
    python main.py --web                        # Lanzar dashboard web
    python main.py https://ejemplo.com -o json  # Salida en JSON
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Agregar directorio raiz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configurar encoding UTF-8 para stdout/stderr si estan disponibles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from escaner.scanner import scan_site
from escaner.report import format_text_report, format_json_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="escaner-web",
        description="Escaner Web Educativo — Analisis pasivo de seguridad web",
        epilog="Ejemplo: python main.py https://example.com",
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL del sitio a analizar",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Lanzar el dashboard web interactivo",
    )
    parser.add_argument(
        "--batch",
        type=str,
        metavar="ARCHIVO",
        help="Archivo con URLs para escaneo por lotes (una por linea)",
    )
    parser.add_argument(
        "-o", "--output",
        choices=["text", "json"],
        default="text",
        help="Formato de salida (default: text)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto para el dashboard web (default: 5000)",
    )
    return parser.parse_args()


def format_result(result: dict, output_format: str) -> str:
    if output_format == "json":
        return format_json_report(result)
    return format_text_report(result)


def scan_single(url: str, output_format: str) -> None:
    print(f"\n[*] Analizando: {url}\n")
    result = scan_site(url)

    if result.get("error"):
        print(f"[ERROR] {result['error']}")
        return

    print(format_result(result, output_format))


def scan_batch(filepath: str, output_format: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] Archivo no encontrado: {filepath}")
        return

    urls = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not urls:
        print("[ERROR] El archivo no contiene URLs.")
        return

    print(f"\n[BATCH] Escaneo por lotes: {len(urls)} sitios\n")
    print("=" * 60)

    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Analizando: {url}")
        print("-" * 40)

        result = scan_site(url)
        if result.get("error"):
            print(f"[ERROR] {result['error']}")
        else:
            print(format_result(result, output_format))

        print()

    print("=" * 60)
    print(f"[OK] Escaneo por lotes completado: {len(urls)} sitios analizados.")


def launch_web(port: int) -> None:
    try:
        from web.app import run_dashboard
        run_dashboard(port=port, debug=True)
    except ImportError as e:
        print(f"[ERROR] Error al importar el modulo web: {e}")
        print("Asegurate de tener Flask instalado: pip install flask")


def main() -> None:
    args = parse_args()

    if args.web:
        launch_web(args.port)
        return

    if args.batch:
        scan_batch(args.batch, args.output)
        return

    if args.url:
        scan_single(args.url, args.output)
        return

    # Si no se proporciona nada, mostrar ayuda
    print("[*] Escaner Web Educativo v2.0\n")
    print("Modos de uso:")
    print("  python main.py https://ejemplo.com    -> Escaneo simple")
    print("  python main.py --batch links.txt      -> Escaneo por lotes")
    print("  python main.py --web                  -> Dashboard web\n")
    print("Usa --help para ver todas las opciones.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEscaneo cancelado por el usuario.")
    except Exception as error:
        print(f"\n[ERROR] Error inesperado: {error}")
