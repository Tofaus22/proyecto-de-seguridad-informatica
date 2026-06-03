# Escáner Web Educativo v2.0 🛡️

Herramienta educativa y modular en Python diseñada para realizar análisis de seguridad web de forma **pasiva**. 

Este escáner **no explota vulnerabilidades**, no realiza ataques de fuerza bruta y no interactúa agresivamente con los servidores. Se limita a analizar las cabeceras HTTP, el contenido de la respuesta y las configuraciones públicas con fines puramente educativos y de auditoría preventiva.

---

## ✨ Características Principales

- **Dashboard Web Interactivo:** Interfaz gráfica moderna estilo *glassmorphism* construida con Flask, Vanilla JS y CSS.
- **Módulos de Seguridad (11 Checks):** Arquitectura modular extensible para evaluar múltiples vectores de seguridad pasivos.
- **Guías Educativas:** Cada hallazgo incluye una explicación detallada del problema y guías de mitigación (con ejemplos de código).
- **Exportación Profesional:** Generación de reportes de auditoría en formato **PDF** y **JSON**.
- **Historial de Análisis:** Guarda el registro de todos los escaneos realizados con una barra de búsqueda integrada.
- **Preparado para Producción:** Incluye `Procfile` y dependencias (Gunicorn) para desplegar fácilmente en la nube (Render, Railway, etc.).

---

## 🔍 ¿Qué revisa?

| Check | Descripción | Puntos |
|-------|-------------|--------|
| 🔒 **HTTPS** | Valida si el sitio usa conexión segura forzada. | 15 |
| 📜 **Certificado SSL** | Verifica el emisor, expiración, versión y protocolo TLS. | 15 |
| 🛡️ **Cabeceras HTTP** | Analiza 8 cabeceras clave (HSTS, X-Frame-Options, CSP, etc.). | 15 |
| 🍪 **Cookies** | Audita atributos `Secure`, `HttpOnly` y `SameSite`. | 10 |
| 📝 **Protección CSRF** | Búsqueda heurística de tokens Anti-CSRF en formularios. | 5 |
| 🔀 **Contenido Mixto** | Detección de recursos inseguros (HTTP) cargados bajo HTTPS. | 10 |
| 🔧 **Tecnologías** | Identificación de versiones de software, servidores y lenguajes expuestos. | 10 |
| 🤖 **robots.txt** | Análisis de exposición de directorios sensibles en la indexación web. | 5 |
| 📧 **Registros DNS** | Verificación de protección contra suplantación de identidad (SPF y DMARC). | 5 |
| 🗣️ **Comentarios HTML** | Extracción de comentarios de desarrolladores que pueden fugar información. | 5 |
| 📄 **security.txt** | Búsqueda de políticas de reporte de vulnerabilidades (RFC 9116). | 5 |

**Puntaje total: 0 - 100**

---

## ⚙️ Requisitos

- Python 3.10+
- [Git](https://git-scm.com/) (Opcional, para despliegue)

---

## 🚀 Instalación y Uso Local

1. **Clonar y preparar entorno:**
   ```bash
   git clone https://github.com/Tofaus22/proyecto-de-seguridad-informatica.git
   cd proyecto-de-seguridad-informatica
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lanzar el Dashboard Web (Recomendado):**
   ```bash
   python main.py --web
   ```
   *Abre tu navegador en `http://127.0.0.1:5000`*

### Uso Avanzado por Terminal (CLI)

```bash
# Escaneo simple por terminal
python main.py https://example.com

# Escaneo por lotes
python main.py --batch links.txt

# Escaneo con salida en JSON
python main.py https://example.com -o json

# Dashboard web en un puerto específico
python main.py --web --port 8080
```

---

## ☁️ Despliegue en Internet (Render)

El repositorio ya cuenta con el entorno listo para ser alojado gratuitamente en [Render](https://render.com/).

1. Sube tus cambios a tu repositorio de GitHub.
2. Crea una cuenta en Render e inicia sesión con GitHub.
3. Haz clic en **New +** y selecciona **Web Service**.
4. Conecta tu repositorio `proyecto-de-seguridad-informatica`.
5. Configura los siguientes parámetros:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn web.app:app`
   - **Plan:** `Free ($0)`
6. Haz clic en **Create Web Service**. ¡Listo! Tendrás una URL pública para compartir tu proyecto.

---

## 📂 Estructura del Código

```text
proyecto-de-seguridad-informatica/
├── escaner/                  # Core del escáner
│   ├── checks/               # Módulos de verificación (11 scripts separados)
│   ├── scanner.py            # Orquestador y registro de puntajes
│   ├── report.py             # Generador de reportes en texto/JSON
│   └── history.py            # Gestión del historial (persistencia local)
├── web/                      # Backend y Frontend Web
│   ├── app.py                # Servidor Flask e interfaz API
│   ├── templates/            # Plantillas HTML
│   └── static/               # Estilos avanzados (CSS) y lógica UI (JS)
├── main.py                   # Punto de entrada y parser de argumentos
├── Procfile                  # Configuración para servidores PaaS
└── requirements.txt          # Dependencias (incluye gunicorn)
```

---

## ⚠️ Aviso Legal / Nota Educativa

La detección de vulnerabilidades como CSRF es **heurística** e intencionalmente simplificada (busca tokens ocultos, etiquetas meta y variables que contengan `csrf` en el código fuente). Esta herramienta es una Prueba de Concepto (PoC) para facilitar el aprendizaje en clases de ciberseguridad y **no** sustituye una auditoría de seguridad profesional exhaustiva.
