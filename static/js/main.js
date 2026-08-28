/* ═══════════════════════════════════════════════════════════════
   CyberShield — Main JavaScript
   ═══════════════════════════════════════════════════════════════ */

'use strict';

// ── Particle Background ───────────────────────────────────────────
(function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];
  const COUNT = 70;
  const COLORS = ['#00ffe0', '#00ff88', '#3b82f6', '#a855f7'];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function randBetween(a, b) { return a + Math.random() * (b - a); }

  function createParticle() {
    return {
      x:     randBetween(0, W),
      y:     randBetween(0, H),
      r:     randBetween(.6, 2.2),
      vx:    randBetween(-.25, .25),
      vy:    randBetween(-.4, -.1),
      alpha: randBetween(.2, .7),
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: COUNT }, createParticle);
  }

  function tick() {
    ctx.clearRect(0, 0, W, H);

    particles.forEach(p => {
      p.x  += p.vx;
      p.y  += p.vy;
      p.alpha -= .0008;

      if (p.y < -10 || p.alpha <= 0) {
        Object.assign(p, createParticle(), { y: H + 5, alpha: randBetween(.3, .7) });
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    });
    ctx.globalAlpha = 1;

    requestAnimationFrame(tick);
  }

  window.addEventListener('resize', resize);
  init();
  tick();
})();

// ── Navbar ────────────────────────────────────────────────────────
(function initNavbar() {
  const toggle = document.getElementById('nav-toggle');
  const navbar = document.getElementById('navbar');
  if (!toggle || !navbar) return;

  toggle.addEventListener('click', () => {
    navbar.classList.toggle('nav-open');
  });

  // Scroll shrink
  window.addEventListener('scroll', () => {
    navbar.style.background = window.scrollY > 20
      ? 'rgba(8,11,20,.95)'
      : 'rgba(8,11,20,.8)';
  }, { passive: true });
})();

// ── Utilities ─────────────────────────────────────────────────────
function togglePass(fieldId) {
  const inp = document.getElementById(fieldId);
  if (!inp) return;
  inp.type = inp.type === 'password' ? 'text' : 'password';
}

function filterHistory(query) {
  const rows = document.querySelectorAll('#history-table tbody tr');
  const q = query.toLowerCase();
  rows.forEach(row => {
    const search = row.dataset.search || '';
    row.style.display = search.includes(q) ? '' : 'none';
  });
}

// Auto-dismiss flash messages after 5 s
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
});

// ── Tab switcher ─────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => {
    t.classList.toggle('active', t.id === `tab-${name}`);
    t.setAttribute('aria-selected', t.id === `tab-${name}`);
  });
  document.querySelectorAll('.tab-panel').forEach(p => {
    p.classList.toggle('active', p.id === `panel-${name}`);
  });
  clearResult();
}

// ── Sample pills ──────────────────────────────────────────────────
function fillSample(type, value) {
  if (type === 'url') {
    const inp = document.getElementById('url-input');
    if (inp) { inp.value = value; inp.focus(); }
    switchTab('url');
  } else {
    const inp = document.getElementById('email-input');
    if (inp) { inp.value = value; inp.focus(); }
    switchTab('email');
  }
}

// ── Threat Gauge animation ────────────────────────────────────────
function animateGauge(pct) {
  const fill   = document.getElementById('gauge-fill');
  const needle = document.getElementById('gauge-needle');
  const label  = document.getElementById('gauge-pct');
  if (!fill || !needle || !label) return;

  const TRACK = 173;
  const targetOffset = TRACK - (TRACK * pct / 100);

  // Choose colour
  const color = pct >= 75 ? '#ff3c6e' : pct >= 45 ? '#ff9f1c' : '#00ff88';
  fill.style.transition = 'stroke-dashoffset 1s cubic-bezier(.4,0,.2,1), stroke .4s ease';
  fill.style.stroke = color;
  fill.style.strokeDashoffset = targetOffset;

  // Needle: maps 0% → -90deg, 100% → +90deg
  const deg = -90 + (pct / 100) * 180;
  needle.style.transition = 'transform 1s cubic-bezier(.4,0,.2,1)';
  needle.setAttribute('transform', `rotate(${deg})`);

  // Counter
  let current = 0;
  const step  = pct / 40;
  const timer = setInterval(() => {
    current = Math.min(current + step, pct);
    label.textContent = Math.round(current) + '%';
    if (current >= pct) clearInterval(timer);
  }, 25);
}

// ── Show result panel ─────────────────────────────────────────────
function showResult(data, type) {
  const panel    = document.getElementById('result-panel');
  const badge    = document.getElementById('result-badge');
  const riskEl   = document.getElementById('result-risk');
  const valueEl  = document.getElementById('result-value');
  const timeEl   = document.getElementById('result-time');
  const featWrap = document.getElementById('result-features');
  const featGrid = document.getElementById('features-grid');

  if (!panel) return;

  const label = data.label || '—';
  const risk  = data.risk_level || 'LOW';
  const pct   = data.confidence || 0;

  badge.textContent = label;
  badge.className   = `result-badge badge-${label.toLowerCase().replace(' ','')}`;

  riskEl.textContent = `${risk} RISK — ${pct}% confidence`;
  riskEl.className   = `result-risk risk-${risk.toLowerCase()}`;

  if (type === 'url') {
    valueEl.textContent = data.url || '';
  } else {
    valueEl.textContent = data.text_preview || '';
  }

  timeEl.textContent = data.scanned_at ? `Scanned at ${data.scanned_at}` : '';

  // Features breakdown (URL only)
  if (type === 'url' && data.features) {
    featGrid.innerHTML = '';
    const boolKeys = ['has_https','has_ip_address','is_shortened'];
    const fmt = (k, v) => {
      const isBool = boolKeys.includes(k);
      const displayVal = isBool ? (v ? 'Yes' : 'No') : v;
      const flagClass  = isBool && v ? 'f-flag-1' : isBool ? 'f-flag-0' : '';
      return `<div class="feature-chip ${flagClass}">
        <div class="f-name">${k.replace(/_/g,' ')}</div>
        <div class="f-val">${displayVal}</div>
      </div>`;
    };
    featGrid.innerHTML = Object.entries(data.features).map(([k,v]) => fmt(k,v)).join('');
    featWrap.classList.remove('hidden');
  } else {
    featWrap.classList.add('hidden');
  }

  panel.classList.remove('hidden');
  animateGauge(pct);

  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearResult() {
  const panel = document.getElementById('result-panel');
  if (panel) panel.classList.add('hidden');
}

// ── Scan URL ──────────────────────────────────────────────────────
async function scanURL() {
  const input = document.getElementById('url-input');
  const btn   = document.getElementById('btn-scan-url');
  const url   = input?.value.trim();

  if (!url) { shake(input); return; }

  setLoading(btn, true);
  clearResult();

  try {
    const res  = await fetch('/api/scan/url', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ url }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Scan failed.', 'error');
      return;
    }
    showResult(data, 'url');
  } catch (err) {
    showToast('Network error. Is the server running?', 'error');
  } finally {
    setLoading(btn, false);
  }
}

// ── Scan Email ────────────────────────────────────────────────────
async function scanEmail() {
  const input = document.getElementById('email-input');
  const btn   = document.getElementById('btn-scan-email');
  const text  = input?.value.trim();

  if (!text) { shake(input); return; }

  setLoading(btn, true);
  clearResult();

  try {
    const res  = await fetch('/api/scan/email', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ text }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Scan failed.', 'error');
      return;
    }
    showResult(data, 'email');
  } catch (err) {
    showToast('Network error. Is the server running?', 'error');
  } finally {
    setLoading(btn, false);
  }
}

// ── Load stats (for index page) ───────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();

    animateCount('stat-total',   data.total_scans || 0);
    animateCount('stat-flagged', data.malicious   || 0);

    const urlM = data.model_metrics?.url_model;
    const emM  = data.model_metrics?.email_model;

    const el = id => document.getElementById(id);

    if (urlM && el('stat-accuracy')) {
      el('stat-accuracy').textContent = (urlM.accuracy * 100).toFixed(1) + '%';
    }
    if (emM && el('stat-email-accuracy')) {
      el('stat-email-accuracy').textContent = (emM.accuracy * 100).toFixed(1) + '%';
    }
  } catch (_) { /* stats are non-critical */ }
}

// ── Load dashboard metrics ────────────────────────────────────────
async function loadDashboard() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();

    const urlM = data.model_metrics?.url_model;
    const emM  = data.model_metrics?.email_model;

    // Helper
    const setBar = (barId, valId, pct) => {
      const bar = document.getElementById(barId);
      const val = document.getElementById(valId);
      if (bar) bar.style.width = (pct * 100).toFixed(1) + '%';
      if (val) val.textContent = (pct * 100).toFixed(1) + '%';
    };

    if (urlM) {
      setBar('url-acc', 'url-acc-val', urlM.accuracy);
      setBar('url-pre', 'url-pre-val', urlM.precision);
      setBar('url-rec', 'url-rec-val', urlM.recall);
      setBar('url-f1',  'url-f1-val',  urlM.f1_score);

      const kpi = document.getElementById('kpi-accuracy');
      if (kpi) kpi.textContent = (urlM.f1_score * 100).toFixed(1) + '%';
    }

    if (emM) {
      setBar('em-acc', 'em-acc-val', emM.accuracy);
      setBar('em-pre', 'em-pre-val', emM.precision);
      setBar('em-rec', 'em-rec-val', emM.recall);
      setBar('em-f1',  'em-f1-val',  emM.f1_score);
    }

  } catch (_) { /* non-critical */ }
}

// ── UI helpers ────────────────────────────────────────────────────
function setLoading(btn, loading) {
  if (!btn) return;
  const text   = btn.querySelector('.btn-text');
  const loader = btn.querySelector('.btn-loader');
  btn.disabled = loading;
  if (text)   text.classList.toggle('hidden', loading);
  if (loader) loader.classList.toggle('hidden', !loading);
}

function shake(el) {
  if (!el) return;
  el.style.animation = 'none';
  el.offsetHeight;
  el.style.animation = 'shake .35s ease';
  setTimeout(() => el.style.animation = '', 350);
}

function animateCount(elId, target) {
  const el = document.getElementById(elId);
  if (!el) return;
  const num = el.querySelector('.stat-num') || el;
  let current = 0;
  const step  = Math.max(1, Math.ceil(target / 40));
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    num.textContent = current.toLocaleString();
    if (current >= target) clearInterval(timer);
  }, 30);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('flash-container')
    || (() => {
      const d = document.createElement('div');
      d.id = 'flash-container';
      d.className = 'flash-container';
      document.body.appendChild(d);
      return d;
    })();

  const div = document.createElement('div');
  div.className = `flash flash-${type}`;
  div.innerHTML = `<span>${message}</span><button class="flash-close" onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(div);

  setTimeout(() => {
    div.style.transition = 'opacity .4s ease';
    div.style.opacity = '0';
    setTimeout(() => div.remove(), 400);
  }, 4000);
}

// Enter key support for URL input
document.addEventListener('DOMContentLoaded', () => {
  const urlInput = document.getElementById('url-input');
  if (urlInput) {
    urlInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') scanURL();
    });
  }
});

// Inject shake keyframe
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
@keyframes shake {
  0%,100%{transform:translateX(0)}
  20%    {transform:translateX(-6px)}
  40%    {transform:translateX(6px)}
  60%    {transform:translateX(-4px)}
  80%    {transform:translateX(4px)}
}`;
document.head.appendChild(shakeStyle);
