/**
 * FIFA WC 2026 Smart Stadium AI Command Center - Client Logic
 * ============================================================
 * Premium UI with structured JSON rendering, color-coded badges,
 * loading spinners, and graceful offline/fallback handling.
 */

// ─── Environment Configuration ───
const PROD_API_URL = "https://fifas-ai.onrender.com";

const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocalhost ? "http://localhost:8000/api" : `${PROD_API_URL}/api`;

// ─── DOM Elements ───────────────────────────────────────────
const els = {
    stadiumSelect: document.getElementById('stadium-select'),
    langSelect: document.getElementById('language-select'),
    tabs: document.querySelectorAll('.tab-btn'),
    panels: document.querySelectorAll('.panel'),
    chat: {
        input: document.getElementById('chat-input'),
        btn: document.getElementById('chat-send'),
        messages: document.getElementById('chat-messages')
    },
    toast: document.getElementById('error-toast'),
    errorMsg: document.getElementById('error-message'),
    closeToast: document.getElementById('close-toast')
};

// ─── Structured JSON → Polished HTML Renderer ───────────────
function renderStructuredData(data) {
    if (!data || typeof data !== 'object') return `<p>${data}</p>`;
    
    let html = '<div class="structured-output">';
    for (const [key, value] of Object.entries(data)) {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const badgeClass = getSeverityBadge(key, value);
        
        if (Array.isArray(value)) {
            html += `<div class="data-field">
                <span class="field-label">${label}</span>
                <ul class="action-list">${value.map(v => `<li>${v}</li>`).join('')}</ul>
            </div>`;
        } else if (typeof value === 'object' && value !== null) {
            html += `<div class="data-field">
                <span class="field-label">${label}</span>
                ${renderStructuredData(value)}
            </div>`;
        } else {
            html += `<div class="data-field">
                <span class="field-label">${label}</span>
                ${badgeClass 
                    ? `<span class="badge ${badgeClass}">${value}</span>` 
                    : `<span class="field-value">${value}</span>`}
            </div>`;
        }
    }
    html += '</div>';
    return html;
}

function getSeverityBadge(key, value) {
    const k = key.toLowerCase();
    const v = String(value).toLowerCase();
    if (k.includes('priority') || k.includes('severity') || k.includes('level') || k.includes('risk') || k.includes('status') || k.includes('niveau') || k.includes('gravedad')) {
        if (v.includes('critical') || v.includes('emergency') || v.includes('high') || v.includes('severe') || v.includes('alta') || v.includes('critique') || v.includes('critico')) return 'badge-red';
        if (v.includes('medium') || v.includes('moderate') || v.includes('elevated') || v.includes('warning') || v.includes('media') || v.includes('moyen')) return 'badge-yellow';
        if (v.includes('low') || v.includes('normal') || v.includes('stable') || v.includes('clear') || v.includes('good') || v.includes('baja') || v.includes('faible')) return 'badge-green';
    }
    return null;
}

// ─── Fallback Protocols Renderer ────────────────────────────
function renderFallbackMessage(result) {
    let html = `<div class="fallback-container">
        <div class="fallback-header">${result.response || 'AI temporarily unavailable.'}</div>`;
    
    if (result.cached_protocols) {
        html += '<div class="cached-protocols"><h4>📋 Cached Safety Protocols</h4>';
        for (const [key, val] of Object.entries(result.cached_protocols)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            html += `<div class="protocol-item"><strong>${label}:</strong> ${val}</div>`;
        }
        html += '</div>';
    }
    html += '</div>';
    return html;
}

// ─── Loading Spinner HTML ───────────────────────────────────
function spinnerHTML(text) {
    return `<div class="loading-state"><div class="spinner"></div><span>${text}</span></div>`;
}

// ─── Button State Management ────────────────────────────────
function setBtnLoading(btn, loading) {
    btn.disabled = loading;
    if (loading) {
        btn.dataset.originalText = btn.textContent;
        btn.innerHTML = `<span class="spinner-inline"></span> Processing...`;
    } else {
        btn.textContent = btn.dataset.originalText || btn.textContent;
    }
}

// ─── Initialize ─────────────────────────────────────────────
async function init() {
    await fetchStadiums();
    await fetchLanguages();
    setupEventListeners();
}

async function fetchStadiums() {
    try {
        const res = await fetch(`${API_BASE}/stadiums`);
        if (!res.ok) throw new Error("Backend offline");
        const data = await res.json();
        els.stadiumSelect.innerHTML = data.stadiums.map(s => 
            `<option value="${s.id}">${s.name} (${s.country})</option>`
        ).join('');
    } catch (e) {
        showError("Backend unavailable. Using offline fallback mode.");
        els.stadiumSelect.innerHTML = `<option value="metlife">MetLife Stadium (Offline Mode)</option>`;
    }
}

async function fetchLanguages() {
    try {
        const res = await fetch(`${API_BASE}/languages`);
        if (!res.ok) throw new Error("Backend offline");
        const langs = await res.json();
        els.langSelect.innerHTML = Object.entries(langs).map(([code, name]) => 
            `<option value="${code}">${name}</option>`
        ).join('');
    } catch (e) {
        els.langSelect.innerHTML = `<option value="en">English (Offline Mode)</option>`;
    }
}

// ─── Event Listeners ────────────────────────────────────────
function setupEventListeners() {
    els.tabs.forEach(tab => tab.addEventListener('click', () => switchTab(tab)));
    els.closeToast.addEventListener('click', () => els.toast.classList.add('hidden'));

    els.chat.btn.addEventListener('click', sendChatMessage);
    els.chat.input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    
    // Form Events
    document.getElementById('zone-north').addEventListener('input', e => {
        document.getElementById('val-north').textContent = e.target.value + '%';
    });
    document.getElementById('zone-south').addEventListener('input', e => {
        document.getElementById('val-south').textContent = e.target.value + '%';
    });
    
    els.stadiumSelect.addEventListener('change', renderStadiumMap);
    els.langSelect.addEventListener('change', applyLocalization);

    document.getElementById('a11y-btn').addEventListener('click', handleA11y);
    document.getElementById('crowd-btn').addEventListener('click', handleCrowd);
    document.getElementById('incident-btn').addEventListener('click', handleIncident);
    document.getElementById('briefing-btn').addEventListener('click', handleBriefing);
    
    document.querySelectorAll('.map-zone').forEach(btn => {
        btn.addEventListener('click', handleStadiumModel);
    });
}

function switchTab(clickedTab) {
    els.tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
    els.panels.forEach(p => p.classList.remove('active'));
    clickedTab.classList.add('active');
    clickedTab.setAttribute('aria-selected', 'true');
    document.getElementById(clickedTab.getAttribute('aria-controls')).classList.add('active');
}

// ─── Core API Call with Error Interceptor ───────────────────
async function apiCall(endpoint, payload) {
    try {
        // Inject language globally into every request payload
        payload.language = els.langSelect.value;
        
        const res = await fetch(`${API_BASE}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        // Save successful interactions to local history
        if (res.ok && data.status !== 'error') {
            saveToHistory(endpoint, payload, data);
        }
        
        if (!res.ok) throw new Error(data.detail || 'API Error');
        return data;
    } catch (e) {
        if (e.message.includes('Failed to fetch') || e.message.includes('NetworkError')) {
            showError("Cannot reach the AI Command Center. Please verify the backend is running.");
        } else {
            showError(e.message);
        }
        return { status: 'error', response: e.message };
    }
}

function showError(msg) {
    els.errorMsg.textContent = msg;
    els.toast.classList.remove('hidden');
    setTimeout(() => els.toast.classList.add('hidden'), 6000);
}

// ─── Smart Result Renderer (decides formatting) ─────────────
function renderResult(resBox, result) {
    if (result.status === 'success' && result.data) {
        resBox.innerHTML = renderStructuredData(result.data);
    } else if (result.status === 'success' && result.response) {
        resBox.innerHTML = `<div class="field-value">${result.response}</div>`;
    } else if (result.type === 'rate_limit') {
        resBox.innerHTML = `<div class="fallback-container">
            <div class="fallback-header" style="color:var(--accent-yellow)">⏳ System Busy</div>
            <p>${result.message}</p>
        </div>`;
    } else if (result.status === 'fallback') {
        resBox.innerHTML = renderFallbackMessage(result);
    } else {
        resBox.innerHTML = `<div class="error-inline">⚠️ ${result.response || 'Service temporarily unavailable. Please try again.'}</div>`;
    }
    resBox.classList.remove('hidden');
}

// ═══════════════════════════ FEATURES ════════════════════════

// F1: Concierge Chat
async function sendChatMessage() {
    const text = els.chat.input.value.trim();
    if (!text) return;
    
    appendMessage(text, 'user-message');
    els.chat.input.value = '';
    els.chat.input.disabled = true;
    setBtnLoading(els.chat.btn, true);
    
    const loadingId = appendMessage("Thinking...", 'ai-message loading');

    try {
        const result = await apiCall('chat', {
            message: text,
            language: els.langSelect.value,
            stadium_id: els.stadiumSelect.value
        });

        document.getElementById(loadingId).remove();
        
        if (result.type === 'rate_limit') {
            appendMessage(`System Busy: ${result.message}`, 'ai-message fallback-msg');
        } else if (result.status === 'fallback') {
            appendMessage(result.response, 'ai-message fallback-msg');
        } else if (result.status !== 'error') {
            appendMessage(result.response, 'ai-message');
        } else {
            appendMessage('Service temporarily unavailable. Please try again.', 'ai-message fallback-msg');
        }
    } finally {
        els.chat.input.disabled = false;
        setBtnLoading(els.chat.btn, false);
        els.chat.input.focus();
    }
}

function appendMessage(text, className) {
    const id = 'msg-' + Date.now();
    const div = document.createElement('div');
    div.className = `message ${className}`;
    div.id = id;
    div.textContent = text;
    els.chat.messages.appendChild(div);
    els.chat.messages.scrollTop = els.chat.messages.scrollHeight;
    return id;
}

// F3: Accessibility Navigator
async function handleA11y() {
    const btn = document.getElementById('a11y-btn');
    const resBox = document.getElementById('a11y-result');
    setBtnLoading(btn, true);
    resBox.innerHTML = spinnerHTML("Generating accessible route...");
    resBox.classList.remove('hidden');

    try {
        const result = await apiCall('accessible-route', {
            disability_type: document.getElementById('a11y-type').value,
            destination: document.getElementById('a11y-dest').value || 'Nearest seat',
            stadium_id: els.stadiumSelect.value
        });
        renderResult(resBox, result);
    } finally {
        setBtnLoading(btn, false);
    }
}

// F2: Crowd Intelligence
async function handleCrowd() {
    const btn = document.getElementById('crowd-btn');
    const resBox = document.getElementById('crowd-result');
    setBtnLoading(btn, true);
    resBox.innerHTML = spinnerHTML("Analyzing crowd density...");
    resBox.classList.remove('hidden');

    try {
        const result = await apiCall('crowd-analysis', {
            zone_data: {
                "North": parseInt(document.getElementById('zone-north').value),
                "South": parseInt(document.getElementById('zone-south').value)
            },
            stadium_id: els.stadiumSelect.value
        });
        renderResult(resBox, result);
    } finally {
        setBtnLoading(btn, false);
    }
}

// F6: Incident Response
async function handleIncident() {
    const btn = document.getElementById('incident-btn');
    const resBox = document.getElementById('incident-result');
    setBtnLoading(btn, true);
    resBox.innerHTML = spinnerHTML("Generating incident protocol...");
    resBox.classList.remove('hidden');

    try {
        const result = await apiCall('incident-response', {
            incident_type: document.getElementById('inc-type').value,
            location: document.getElementById('inc-loc').value,
            severity: document.getElementById('inc-sev').value,
            stadium_id: els.stadiumSelect.value
        });
        renderResult(resBox, result);
    } finally {
        setBtnLoading(btn, false);
    }
}

// F8: Match Briefing
async function handleBriefing() {
    const btn = document.getElementById('briefing-btn');
    const resBox = document.getElementById('briefing-result');
    setBtnLoading(btn, true);
    resBox.innerHTML = spinnerHTML("Compiling match-day briefing...");
    resBox.classList.remove('hidden');

    try {
        const result = await apiCall('match-briefing', {
            match_info: document.getElementById('brf-match').value,
            weather: document.getElementById('brf-weather').value,
            expected_attendance: parseInt(document.getElementById('brf-att').value),
            stadium_id: els.stadiumSelect.value
        });
        renderResult(resBox, result);
    } finally {
        setBtnLoading(btn, false);
    }
}

// F9: Generative Stadium Model (Interactive Map)
async function handleStadiumModel(e) {
    const btn = e.currentTarget;
    const zone = btn.getAttribute('data-zone');
    const resBox = document.getElementById('stadium-model-result');
    
    const allBtns = document.querySelectorAll('.map-zone');
    allBtns.forEach(b => b.disabled = true);
    btn.classList.add('zone-active');
    
    resBox.innerHTML = spinnerHTML(`Generating intelligence for <b>${zone}</b>...`);
    resBox.classList.remove('hidden');

    try {
        const result = await apiCall('generative-stadium', {
            seat_section: zone,
            stadium_id: els.stadiumSelect.value
        });
        renderResult(resBox, result);
    } finally {
        allBtns.forEach(b => b.disabled = false);
        btn.classList.remove('zone-active');
    }
}

// ─── Dynamic Stadium Views ──────────────────────────────────
const STADIUM_LAYOUTS = {
    metlife: {
        gates: [ {id: "Gate A (North)", label: "🚪 Gate A"}, {id: "Gate B (East)", label: "🚪 Gate B"}, {id: "Gate C (South)", label: "🚪 Gate C"}, {id: "Gate D (West)", label: "🚪 Gate D"} ],
        food: [ {id: "North Concourse Food Court", label: "🍔 North Concessions"}, {id: "South Concourse Food Court", label: "🍕 South Concessions"}, {id: "East VIP Lounge", label: "🥂 East VIP Lounge"} ],
        seats: [ {id: "Block 101, Lower North", label: "Block 101"}, {id: "Block 102, Lower North", label: "Block 102"}, {id: "Block 201, Upper South", label: "Block 201"}, {id: "Block 202, Upper South", label: "Block 202"}, {id: "Block 301, East Wing", label: "Block 301"} ]
    },
    azteca: {
        gates: [ {id: "Puerta 1 (North)", label: "🚪 Puerta 1"}, {id: "Puerta 3 (South)", label: "🚪 Puerta 3"}, {id: "Puerta 5 (East)", label: "🚪 Puerta 5"}, {id: "Puerta 6 (West)", label: "🚪 Puerta 6"} ],
        food: [ {id: "North Concourse Food Court", label: "🌮 North Food"}, {id: "South Food Court", label: "🌯 South Food"} ],
        seats: [ {id: "Section 10, Lower North", label: "Sec 10"}, {id: "Section 25, Lower South", label: "Sec 25"}, {id: "Section 101, East Wing", label: "Sec 101"} ]
    },
    bmo: {
        gates: [ {id: "Gate 1 (North)", label: "🚪 Gate 1"}, {id: "Gate 3 (South)", label: "🚪 Gate 3"}, {id: "Gate 5 (East)", label: "🚪 Gate 5"} ],
        food: [ {id: "Main Concourse Food", label: "🌭 Main Concourse"}, {id: "VIP Lounge", label: "🥂 VIP Lounge"} ],
        seats: [ {id: "Section 104", label: "Sec 104"}, {id: "Section 106", label: "Sec 106"}, {id: "Section 114", label: "Sec 114"} ]
    }
};

function renderStadiumMap() {
    const mapContainer = document.querySelector('.stadium-map');
    if (!mapContainer) return;
    
    const layout = STADIUM_LAYOUTS[els.stadiumSelect.value] || STADIUM_LAYOUTS['metlife'];
    
    let html = `
        <div class="map-label" data-i18n="lbl_gates">── Entry Gates ──</div>
        <div class="map-row">
            ${layout.gates.map(g => `<button class="map-zone gate-zone" data-zone="${g.id}">${g.label}</button>`).join('')}
        </div>
        <div class="map-arrow">↓</div>
        <div class="map-label" data-i18n="lbl_food">── Concessions & Food ──</div>
        <div class="map-row">
            ${layout.food.map(f => `<button class="map-zone food-zone" data-zone="${f.id}">${f.label}</button>`).join('')}
        </div>
        <div class="map-arrow">↓</div>
        <div class="map-label" data-i18n="lbl_seats">── Seating Sections ──</div>
        <div class="map-row">
            ${layout.seats.map(s => `<button class="map-zone seat-zone" data-zone="${s.id}">${s.label}</button>`).join('')}
        </div>
    `;
    
    mapContainer.innerHTML = html;
    
    // Bind events
    document.querySelectorAll('.map-zone').forEach(btn => {
        btn.addEventListener('click', handleStadiumModel);
    });
    
    // Reactively localize newly generated map labels
    applyLocalization();
}

// ─── Global Language Localization ─────────────────────────────
const TRANSLATIONS = {
    en: {
        tab_fan: "🧑 Fan Mode",
        tab_ops: "👷 Operations Mode",
        tab_history: "📜 History Log",
        f1_title: "F1: Multilingual Fan Concierge",
        f3_title: "F3: Accessibility Navigator",
        f2_title: "F2: Crowd Intelligence",
        f6_title: "F6: Incident Advisor",
        f8_title: "F8: Match Briefing",
        lbl_gates: "── Entry Gates ──",
        lbl_food: "── Concessions & Food ──",
        lbl_seats: "── Seating Sections ──",
        btn_a11y: "Generate Route",
        btn_crowd: "Analyze Flow",
        btn_incident: "Generate Protocol",
        btn_briefing: "Generate Briefing",
        app_title: "🏆 FIFA WC 2026 AI Command Center",
        lbl_stadium: "🏟️ Stadium",
        lbl_lang: "🌐 Language"
    },
    es: {
        tab_fan: "🧑 Modo Fan",
        tab_ops: "👷 Modo Operaciones",
        tab_history: "📜 Historial",
        f1_title: "F1: Conserje Multilingüe",
        f3_title: "F3: Navegador de Accesibilidad",
        f2_title: "F2: Inteligencia de Multitudes",
        f6_title: "F6: Asesor de Incidentes",
        f8_title: "F8: Resumen del Partido",
        lbl_gates: "── Puertas de Entrada ──",
        lbl_food: "── Concesiones y Comida ──",
        lbl_seats: "── Secciones de Asientos ──",
        btn_a11y: "Generar Ruta",
        btn_crowd: "Analizar Flujo",
        btn_incident: "Generar Protocolo",
        btn_briefing: "Generar Resumen",
        app_title: "🏆 Centro de Mando IA FIFA",
        lbl_stadium: "🏟️ Estadio",
        lbl_lang: "🌐 Idioma"
    },
    fr: {
        tab_fan: "🧑 Mode Supporter",
        tab_ops: "👷 Mode Opérations",
        tab_history: "📜 Historique",
        f1_title: "F1: Concierge Multilingue",
        f3_title: "F3: Navigateur d'Accessibilité",
        f2_title: "F2: Intelligence des Foules",
        f6_title: "F6: Conseiller en Incidents",
        f8_title: "F8: Résumé du Match",
        lbl_gates: "── Portes d'Entrée ──",
        lbl_food: "── Concessions et Nourriture ──",
        lbl_seats: "── Sections de Sièges ──",
        btn_a11y: "Générer l'Itinéraire",
        btn_crowd: "Analyser le Flux",
        btn_incident: "Générer le Protocole",
        btn_briefing: "Générer le Résumé",
        app_title: "🏆 Centre de Commandement IA",
        lbl_stadium: "🏟️ Stade",
        lbl_lang: "🌐 Langue"
    },
    ar: {
        tab_fan: "🧑 وضع المشجع",
        tab_ops: "👷 وضع العمليات",
        tab_history: "📜 سجل التاريخ",
        f1_title: "F1: مساعد المشجع متعدد اللغات",
        f3_title: "F3: متصفح إمكانية الوصول",
        f2_title: "F2: ذكاء الحشود",
        f6_title: "F6: مستشار الحوادث",
        f8_title: "F8: ملخص المباراة",
        lbl_gates: "── بوابات الدخول ──",
        lbl_food: "── الامتيازات والطعام ──",
        lbl_seats: "── أقسام الجلوس ──",
        btn_a11y: "إنشاء مسار",
        btn_crowd: "تحليل التدفق",
        btn_incident: "إنشاء بروتوكول",
        btn_briefing: "إنشاء ملخص",
        app_title: "🏆 مركز قيادة الذكاء الاصطناعي",
        lbl_stadium: "🏟️ الملعب",
        lbl_lang: "🌐 اللغة"
    }
};

function applyLocalization() {
    const lang = els.langSelect.value;
    const dict = TRANSLATIONS[lang] || TRANSLATIONS['en'];
    
    // Translate static elements
    const elementsToTranslate = {
        'tab-fan': dict.tab_fan,
        'tab-ops': dict.tab_ops,
        'tab-history': dict.tab_history,
        'a11y-btn': dict.btn_a11y,
        'crowd-btn': dict.btn_crowd,
        'incident-btn': dict.btn_incident,
        'briefing-btn': dict.btn_briefing
    };
    
    for (const [id, text] of Object.entries(elementsToTranslate)) {
        const el = document.getElementById(id);
        if (el && !el.disabled) el.textContent = text;
        else if (el && el.disabled) el.dataset.originalText = text; // Update text for when it unspins
    }
    
    // Translate headers
    const headers = document.querySelectorAll('h2');
    headers.forEach(h2 => {
        if (h2.textContent.includes('F1:')) h2.textContent = dict.f1_title;
        else if (h2.textContent.includes('F3:')) h2.textContent = dict.f3_title;
        else if (h2.textContent.includes('F2:')) h2.textContent = dict.f2_title;
        else if (h2.textContent.includes('F6:')) h2.textContent = dict.f6_title;
        else if (h2.textContent.includes('F8:')) h2.textContent = dict.f8_title;
    });
    
    // Translate map labels if rendered
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.textContent = dict[key];
    });
}

// ─── Local History System ───────────────────────────────────
const HISTORY_KEY = 'wc_history';

function saveToHistory(endpoint, payload, result) {
    try {
        let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        
        // Don't save full raw zone arrays to save space
        const summaryPayload = { ...payload };
        if (summaryPayload.zone_data) summaryPayload.zone_data = "Simulated density mapped";
        
        history.unshift({
            timestamp: new Date().toISOString(),
            endpoint: endpoint,
            payload: summaryPayload,
            result: result
        });
        
        // Keep only last 50 items to stay strictly under 10MB limit
        if (history.length > 50) history = history.slice(0, 50);
        
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        renderHistory();
    } catch (e) {
        console.error("Local history save failed:", e);
    }
}

function renderHistory() {
    const container = document.getElementById('history-container');
    if (!container) return;
    
    let history = [];
    try {
        history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch(e) {}
    
    if (history.length === 0) {
        container.innerHTML = '<div class="empty-state">No history recorded yet. Use the features to generate intelligence.</div>';
        return;
    }
    
    let html = '';
    history.forEach((item, idx) => {
        const date = new Date(item.timestamp).toLocaleString();
        html += `
            <div class="history-item">
                <div class="history-header">
                    <span class="badge" style="background:var(--accent-blue);color:#000;">${item.endpoint.toUpperCase()}</span>
                    <span class="history-time">${date}</span>
                </div>
                <div class="history-body">
                    <strong>Query:</strong> <pre style="background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:4px;margin-bottom:0.5rem;font-size:0.8rem;">${JSON.stringify(item.payload, null, 2)}</pre>
                    <strong>Response:</strong>
                    <div style="margin-top:0.5rem;font-size:0.9rem;">
                        ${item.result.data ? renderStructuredData(item.result.data) : (item.result.response || 'System Busy')}
                    </div>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

document.getElementById('clear-history-btn')?.addEventListener('click', () => {
    localStorage.removeItem(HISTORY_KEY);
    renderHistory();
    showToast("Local history cleared.");
});

// ─── Boot ───────────────────────────────────────────────────
init().then(() => {
    // Ensuring map and localization run explicitly AFTER APIs complete
    renderStadiumMap();
    applyLocalization();
});
renderHistory();
