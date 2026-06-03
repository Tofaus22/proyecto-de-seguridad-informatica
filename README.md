# Escáner Web Educativo v2.0

Herramienta educativa en Python para hacer una revisión pasiva de seguridad sobre sitios web.

Este escáner **no explota vulnerabilidades**, no hace fuerza bruta y no realiza acciones agresivas. Solo revisa elementos visibles en la respuesta del sitio para fines educativos.

## ¿Qué revisa?

| Check | Descripción | Puntos |
|-------|-------------|--------|
| 🔒 HTTPS | Si el sitio usa conexión segura | 25 |
| 📜 Certificado SSL | Emisor, expiración, protocolo TLS | 15 |
| 🛡️ Cabeceras de seguridad | 8 cabeceras HTTP de seguridad | 20 |
| 🍪 Cookies | Atributos Secure, HttpOnly, SameSite | 15 |
| 📝 Protección CSRF | Tokens en formularios HTML | 10 |
| 🔀 Contenido mixto | Recursos HTTP en páginas HTTPS | 10 |
| 🔧 Tecnologías expuestas | Versiones de software visibles | 5 |

**Puntaje total: 0 - 100**

## Requisitos

- Python 3.10+
- requests
- beautifulsoup4
- flask

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Dashboard Web (recomendado)

```bash
python main.py --web
```

Abre tu navegador en `http://127.0.0.1:5000` para usar el dashboard interactivo.

### Escaneo por terminal

```bash
python main.py https://example.com
```

### Escaneo por lotes

```bash
python main.py --batch links.txt
```

### Opciones avanzadas

```bash
python main.py https://example.com -o json    # Salida en JSON
python main.py --web --port 8080              # Dashboard en puerto 8080
python main.py --help                         # Ver todas las opciones
```

## Estructura del proyecto

```
proyecto de seguridad/
├── escaner/                  # Paquete principal
│   ├── checks/               # Módulos de verificación
│   │   ├── https.py           # Verificación HTTPS
│   │   ├── headers.py         # Cabeceras de seguridad (8)
│   │   ├── cookies.py         # Análisis de cookies
│   │   ├── csrf.py            # Detección CSRF
│   │   ├── ssl_cert.py        # Certificado SSL
│   │   ├── tech_detect.py     # Detección de tecnologías
│   │   └── mixed_content.py   # Contenido mixto
│   ├── scanner.py             # Orquestador principal
│   ├── report.py              # Generador de reportes
│   └── history.py             # Gestión del historial
├── web/                       # Dashboard web
│   ├── app.py                 # Servidor Flask
│   ├── templates/             # Plantillas HTML
│   └── static/                # CSS y JavaScript
├── main.py                    # Punto de entrada CLI
├── requirements.txt           # Dependencias
└── escaner_web.py             # Script original (referencia)
```

## Nota

La detección de CSRF es intencionalmente heurística. Busca tokens hidden, meta tags y la palabra `csrf` dentro de formularios HTML. Esto sirve para explicar la idea en clase, pero no reemplaza una auditoría real.
