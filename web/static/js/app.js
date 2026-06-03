/**
 * Escaner Web Dashboard — Frontend Logic
 */

let currentResult = null;

const MITIGATION_GUIDES = {
    "HTTPS": {
        title: "🔒 Solución: Forzar HTTPS",
        desc: "Redirecciona todo el tráfico HTTP a HTTPS usando una redirección 301 (permanente) en tu servidor web.",
        code: "# En Nginx (nginx.conf):\nserver {\n    listen 80;\n    server_name tu-dominio.com;\n    return 301 https://$host$request_uri;\n}"
    },
    "Certificado SSL": {
        title: "📜 Solución: Instalar/Renovar Certificado SSL",
        desc: "Utiliza una Entidad de Certificación de confianza. Let's Encrypt ofrece certificados gratuitos con renovación automática.",
        code: "# Instalar con Certbot en Apache/Nginx:\nsudo apt install certbot python3-certbot-nginx\nsudo certbot --nginx -d tu-dominio.com"
    },
    "Cabeceras de Seguridad": {
        title: "🛡️ Solución: Configurar Cabeceras HTTP",
        desc: "Agrega las cabeceras de seguridad recomendadas en tu servidor para proteger a tus usuarios contra ataques comunes.",
        code: "# En Nginx:\nadd_header Content-Security-Policy \"default-src 'self'\";\nadd_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\";\nadd_header X-Frame-Options \"DENY\";\nadd_header X-Content-Type-Options \"nosniff\";"
    },
    "Cookies": {
        title: "🍪 Solución: Asegurar Atributos de Cookies",
        desc: "Establece los atributos HttpOnly, Secure y SameSite en todas las cookies de sesión y autenticación.",
        code: "// En Node.js/Express:\nres.cookie('session_id', 'valor_secreto', {\n    httpOnly: true,\n    secure: true,\n    sameSite: 'lax'\n});"
    },
    "Proteccion CSRF": {
        title: "📝 Solución: Implementar Anti-CSRF Tokens",
        desc: "Asegura todos los formularios de modificación (POST/PUT) inyectando tokens CSRF únicos de sesión y validándolos en el backend.",
        code: "<!-- Ejemplo en formulario HTML -->\n<input type=\"hidden\" name=\"csrf_token\" value=\"token_criptografico_unico\" />"
    },
    "Contenido Mixto": {
        title: "🔀 Solución: Enlaces de Recursos Seguros",
        desc: "Cambia todas las URLs absolutas HTTP en scripts, imágenes y enlaces a HTTPS, o bien utiliza rutas relativas.",
        code: "<!-- Cambiar esto: -->\n<script src=\"http://cdn.ejemplo.com/library.js\"></script>\n<!-- Por esto: -->\n<script src=\"https://cdn.ejemplo.com/library.js\"></script>"
    },
    "Tecnologias Expuestas": {
        title: "🔧 Solución: Ocultar Huellas del Servidor",
        desc: "Deshabilita las firmas del servidor y cabeceras que delaten versiones exactas para mitigar ataques dirigidos.",
        code: "# En nginx.conf:\nserver_tokens off;\n\n# En php.ini:\nexpose_php = Off"
    },
    "Archivo robots.txt": {
        title: "🤖 Solución: Evitar Exposición en robots.txt",
        desc: "No incluyas rutas administrativas o privadas secretas en robots.txt (ya que es público). En su lugar, protégelas con autenticación.",
        code: "# En lugar de Disallow: /secreto/,\n# restringe el acceso desde la configuración del servidor con contraseñas."
    },
    "Políticas DNS (Correo)": {
        title: "✉️ Solución: Configurar SPF y DMARC",
        desc: "Añade registros DNS de tipo TXT para validar los servidores emisores autorizados y el comportamiento ante correos no autenticados.",
        code: "# Registro TXT de tu dominio para SPF:\nv=spf1 include:spf.protection.outlook.com ~all\n\n# Registro TXT en _dmarc.tu-dominio.com para DMARC:\nv=DMARC1; p=quarantine; pct=100"
    },
    "Comentarios HTML": {
        title: "💬 Solución: Remover Comentarios en Producción",
        desc: "Configura tu compilador o minificador de HTML para remover automáticamente todos los comentarios antes del despliegue.",
        code: "# Usando Webpack, Vite, o minificadores de HTML en tu flujo de compilación:\nhtmlMinifier.minify(html, { removeComments: true });"
    },
    "Archivo security.txt": {
        title: "📜 Solución: Crear security.txt",
        desc: "Añade un archivo de texto en /.well-known/security.txt que ayude a investigadores a reportar vulnerabilidades de manera ética.",
        code: "# Contenido de /.well-known/security.txt:\nContact: https://tu-dominio.com/reportar-vulnerabilidad\nExpires: 2027-01-01T00:00:00.000Z"
    }
};

// ===== DOM ELEMENTS =====
const urlInput = document.getElementById('url-input');
const scanBtn = document.getElementById('scan-btn');
const errorMsg = document.getElementById('error-msg');
const scanSection = document.getElementById('scan-section');
const loadingSection = document.getElementById('loading-section');
const loadingUrl = document.getElementById('loading-url');
const loadingSteps = document.getElementById('loading-steps');
const resultsSection = document.getElementById('results-section');
const checksGrid = document.getElementById('checks-grid');
const historyList = document.getElementById('history-list');
const historyEmpty = document.getElementById('history-empty');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    loadHistory();

    urlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') startScan();
    });
});

// ===== PARTICLES =====
function createParticles() {
    const container = document.getElementById('particles');
    const count = 20;
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = (Math.random() * 10) + 's';
        particle.style.opacity = Math.random() * 0.4 + 0.1;
        container.appendChild(particle);
    }
}

// ===== URL VALIDATION =====
function validateUrl(url) {
    if (!url || !url.trim()) return false;
    // Allow URLs without protocol
    const withProtocol = url.match(/^https?:\/\//) ? url : 'https://' + url;
    try {
        new URL(withProtocol);
        return true;
    } catch {
        return false;
    }
}

// ===== SCAN =====
async function startScan() {
    const url = urlInput.value.trim();

    // Validate
    if (!validateUrl(url)) {
        showError('Por favor, ingresa una URL válida (ej: https://example.com)');
        return;
    }

    hideError();
    showLoading(url);

    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });

        const result = await response.json();

        if (result.error) {
            hideLoading();
            showError('Error: ' + result.error);
            return;
        }

        // Complete loading animation
        await completeLoadingSteps();
        hideLoading();
        showResults(result);
        loadHistory();

    } catch (err) {
        hideLoading();
        showError('Error de conexión: No se pudo contactar al servidor.');
    }
}

// ===== LOADING ANIMATION =====
let loadingInterval = null;

function showLoading(url) {
    scanSection.querySelector('.scan-card').style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    loadingUrl.textContent = url;

    // Reset steps
    const steps = loadingSteps.querySelectorAll('.step');
    steps.forEach(s => { s.classList.remove('active', 'done'); });
    steps[0].classList.add('active');

    // Auto-advance steps
    let current = 0;
    loadingInterval = setInterval(() => {
        if (current < steps.length - 1) {
            steps[current].classList.remove('active');
            steps[current].classList.add('done');
            current++;
            steps[current].classList.add('active');
        }
    }, 800);
}

async function completeLoadingSteps() {
    clearInterval(loadingInterval);
    const steps = loadingSteps.querySelectorAll('.step');
    steps.forEach(s => {
        s.classList.remove('active');
        s.classList.add('done');
    });
    await sleep(400);
}

function hideLoading() {
    clearInterval(loadingInterval);
    loadingSection.style.display = 'none';
    scanSection.querySelector('.scan-card').style.display = 'block';
}

// ===== RESULTS =====
function showResults(result) {
    currentResult = result;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Animate gauge
    const score = result.total_score;
    const maxScore = result.max_score;
    const pct = score / maxScore;
    animateGauge(score, maxScore, pct);

    // Score description
    const scoreLabel = document.getElementById('score-label');
    const scoreDesc = document.getElementById('score-description');
    const urlInfo = document.getElementById('url-info');

    if (pct >= 0.8) {
        scoreLabel.textContent = '🛡️ Seguridad Alta';
        scoreDesc.textContent = 'El sitio cumple con la mayoría de buenas prácticas de seguridad analizadas.';
    } else if (pct >= 0.5) {
        scoreLabel.textContent = '⚡ Seguridad Moderada';
        scoreDesc.textContent = 'El sitio tiene una seguridad aceptable pero hay áreas de mejora.';
    } else {
        scoreLabel.textContent = '⚠️ Seguridad Baja';
        scoreDesc.textContent = 'Se detectaron múltiples áreas de mejora en la seguridad del sitio.';
    }

    // URL info
    const info = result.url_info || {};
    urlInfo.innerHTML = `
        <div class="url-info-item">
            <span class="label">URL solicitada</span>
            <span class="value">${escapeHtml(info.requested || '')}</span>
        </div>
        <div class="url-info-item">
            <span class="label">URL final</span>
            <span class="value">${escapeHtml(info.final || '')}</span>
        </div>
        <div class="url-info-item">
            <span class="label">Estado HTTP</span>
            <span class="value">${info.status_code || 'N/A'}</span>
        </div>
    `;

    // Check cards
    checksGrid.innerHTML = '';
    (result.checks || []).forEach((check, i) => {
        const card = createCheckCard(check, i);
        checksGrid.appendChild(card);
    });
}

function animateGauge(score, maxScore, pct) {
    const gaugeFill = document.getElementById('gauge-fill');
    const scoreNumber = document.getElementById('score-number');
    const scoreMax = document.getElementById('score-max');

    // Circumference = 2 * PI * r (r=85)
    const circumference = 2 * Math.PI * 85;
    const offset = circumference * (1 - pct);

    // Color based on score
    let color;
    if (pct >= 0.8) color = 'var(--success)';
    else if (pct >= 0.5) color = 'var(--warning)';
    else color = 'var(--danger)';

    gaugeFill.style.stroke = color;
    gaugeFill.style.filter = `drop-shadow(0 0 12px ${color})`;

    // Animate
    requestAnimationFrame(() => {
        gaugeFill.style.strokeDashoffset = offset;
    });

    scoreMax.textContent = `/${maxScore}`;

    // Count up animation
    let current = 0;
    const duration = 1500;
    const startTime = performance.now();

    function updateCounter(time) {
        const elapsed = time - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // Ease out cubic
        current = Math.round(eased * score);
        scoreNumber.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    requestAnimationFrame(updateCounter);
}

function createCheckCard(check, index) {
    const card = document.createElement('div');
    const scorePct = check.max_score > 0 ? check.score / check.max_score : 0;
    let status;
    if (scorePct >= 0.8) status = 'passed';
    else if (scorePct >= 0.4) status = 'failed';
    else status = 'critical';

    card.className = `check-card ${status}`;
    card.style.animationDelay = `${index * 0.1}s`;

    let itemsHtml = '';
    if (check.items && check.items.length > 0) {
        itemsHtml = '<div class="check-items">';
        const maxItems = 6;
        const items = check.items.slice(0, maxItems);

        items.forEach(item => {
            if (item.header !== undefined) {
                // Security headers
                const dotClass = item.present ? 'ok' : 'warn';
                const val = item.value ? `: ${escapeHtml(item.value.substring(0, 40))}` : '';
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">${escapeHtml(item.header)}</span>
                        <span class="check-item-value">${item.present ? 'Presente' : 'Ausente'}</span>
                    </div>`;
            } else if (item.name !== undefined && item.secure !== undefined) {
                // Cookies
                const dotClass = item.attrs_ok === item.attrs_total ? 'ok' : (item.attrs_ok > 0 ? 'warn' : 'bad');
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">${escapeHtml(item.name)}</span>
                        <span class="check-item-value">${item.attrs_ok}/${item.attrs_total} attrs</span>
                    </div>`;
            } else if (item.form_number !== undefined) {
                // CSRF
                const dotClass = item.protected ? 'ok' : 'warn';
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">Form #${item.form_number} (${escapeHtml(item.method)})</span>
                        <span class="check-item-value">${item.protected ? 'Protegido' : 'Sin CSRF'}</span>
                    </div>`;
            } else if (item.label !== undefined) {
                // SSL certificate or security.txt
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ok"></span>
                        <span class="check-item-text">${escapeHtml(item.label)}</span>
                        <span class="check-item-value">${escapeHtml(String(item.value).substring(0, 30))}</span>
                    </div>`;
            } else if (item.tag !== undefined) {
                // Mixed content
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot bad"></span>
                        <span class="check-item-text">&lt;${escapeHtml(item.tag)}&gt;</span>
                        <span class="check-item-value">${escapeHtml(item.url.substring(0, 40))}</span>
                    </div>`;
            } else if (item.source !== undefined) {
                // Tech detection
                const riskColors = { alto: 'bad', medio: 'warn', bajo: 'ok' };
                const dotClass = riskColors[item.risk] || 'ok';
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">${escapeHtml(item.category)}</span>
                        <span class="check-item-value">${escapeHtml(String(item.value).substring(0, 30))}</span>
                    </div>`;
            } else if (item.directive !== undefined) {
                // Robots.txt
                const dotClass = item.risk === 'medio' ? 'warn' : 'ok';
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">${escapeHtml(item.directive)}: ${escapeHtml(item.value)}</span>
                        <span class="check-item-value">${escapeHtml(item.reason)}</span>
                    </div>`;
            } else if (item.category === 'DNS TXT') {
                // DNS SPF/DMARC
                const dotClass = item.present ? 'ok' : 'warn';
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot ${dotClass}"></span>
                        <span class="check-item-text">${escapeHtml(item.name)}</span>
                        <span class="check-item-value">${escapeHtml(item.value)}</span>
                    </div>`;
            } else if (item.comment_number !== undefined) {
                // HTML comments
                itemsHtml += `
                    <div class="check-item">
                        <span class="status-dot warn"></span>
                        <span class="check-item-text">Comentario #${item.comment_number}: ${escapeHtml(item.text)}</span>
                        <span class="check-item-value">Exposed: ${escapeHtml(item.matched)}</span>
                    </div>`;
            }
        });

        if (check.items.length > maxItems) {
            itemsHtml += `<div class="check-item" style="justify-content:center;color:var(--text-muted);">+${check.items.length - maxItems} más</div>`;
        }

        itemsHtml += '</div>';
    }

    // mitigation info
    let mitigationHtml = '';
    const guide = MITIGATION_GUIDES[check.name];
    if (guide) {
        mitigationHtml = `
            <div class="mitigation-guide">
                <div class="mitigation-title">${guide.title}</div>
                <div>${guide.desc}</div>
                <pre class="mitigation-code">${escapeHtml(guide.code)}</pre>
            </div>
        `;
    }

    card.innerHTML = `
        <div class="check-header">
            <div class="check-title">
                <span class="check-icon">${check.icon || '🔍'}</span>
                <span class="check-name">${escapeHtml(check.name)}</span>
            </div>
            <span class="check-score">${check.score}/${check.max_score}</span>
        </div>
        <div class="check-detail">${escapeHtml(check.detail)}</div>
        ${itemsHtml}
        ${mitigationHtml}
    `;

    // Click handler to expand mitigation guide
    card.addEventListener('click', (e) => {
        // Prevent toggle if clicking on text fields or code
        if (e.target.closest('.check-item') || e.target.closest('.mitigation-code')) return;
        card.classList.toggle('expanded');
    });

    return card;
}

// ===== HISTORY =====
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();

        if (!history || history.length === 0) {
            historyEmpty.style.display = 'block';
            clearHistoryBtn.style.display = 'none';
            return;
        }

        historyEmpty.style.display = 'none';
        clearHistoryBtn.style.display = 'block';

        // Keep only the entries, remove old content
        const entries = historyList.querySelectorAll('.history-entry');
        entries.forEach(e => e.remove());

        history.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'history-entry';
            div.onclick = () => {
                urlInput.value = entry.url;
                scanSection.querySelector('.scan-card').style.display = 'block';
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };

            const score = entry.score || 0;
            const maxScore = entry.max_score || 100;
            const pct = maxScore > 0 ? score / maxScore : 0;
            let badgeClass;
            if (pct >= 0.8) badgeClass = 'good';
            else if (pct >= 0.5) badgeClass = 'ok';
            else badgeClass = 'bad';

            div.innerHTML = `
                <div class="history-entry-info">
                    <div class="history-score-badge ${badgeClass}">${score}</div>
                    <span class="history-url">${escapeHtml(entry.url)}</span>
                </div>
                <span class="history-date">${escapeHtml(entry.timestamp)}</span>
            `;

            historyList.appendChild(div);
        });

        filterHistory(); // Apply search text if any
    } catch {
        // Silently fail
    }
}

async function clearHistory() {
    try {
        await fetch('/api/history', { method: 'DELETE' });
        const entries = historyList.querySelectorAll('.history-entry');
        entries.forEach(e => e.remove());
        historyEmpty.style.display = 'block';
        clearHistoryBtn.style.display = 'none';
    } catch {
        // Silently fail
    }
}

// ===== RESET =====
function resetScan() {
    resultsSection.style.display = 'none';
    scanSection.querySelector('.scan-card').style.display = 'block';
    urlInput.value = '';
    urlInput.focus();

    // Reset gauge
    const gaugeFill = document.getElementById('gauge-fill');
    gaugeFill.style.strokeDashoffset = 534;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== UTILS =====
function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}

function hideError() {
    errorMsg.style.display = 'none';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ===== HISTORY FILTER & EXPORTS =====
function filterHistory() {
    const searchVal = (document.getElementById('history-search')?.value || '').trim().toLowerCase();
    const entries = historyList.querySelectorAll('.history-entry');
    
    entries.forEach(entry => {
        const url = (entry.querySelector('.history-url')?.textContent || '').toLowerCase();
        if (url.includes(searchVal)) {
            entry.style.display = 'flex';
        } else {
            entry.style.display = 'none';
        }
    });
}

function exportPDF() {
    window.print();
}

function exportJSON() {
    if (!currentResult) return;
    const jsonStr = JSON.stringify(currentResult, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const downloadAnchor = document.createElement('a');
    
    // Clean URL filename
    let cleanUrl = currentResult.url_info.requested
        .replace(/^https?:\/\//i, '')
        .replace(/[^a-z0-9]/gi, '_')
        .toLowerCase();
        
    downloadAnchor.setAttribute("href", url);
    downloadAnchor.setAttribute("download", `reporte_seguridad_${cleanUrl}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    URL.revokeObjectURL(url);
}
