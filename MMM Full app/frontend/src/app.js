// app.js — Application entry point
// Bootstrap the entire 9-step UTC Channel Attribution Platform

(function boot() {
  'use strict';

  // ── Initialize toast system
  toast.init();

  // ── Initialize app state
  appState.init();

  // ── Register all 9 screens with the router
  router.register('screen-1', () => {
    // Login is handled separately (overlay)
    return '';
  });

  router.register('screen-2', () => {
    const html = renderDataSource();
    setTimeout(initDataSource, 50);
    return html;
  });

  router.register('screen-3', () => {
    const html = renderDataReport();
    setTimeout(initDataReport, 50);
    return html;
  });

  router.register('screen-4', () => {
    const html = renderConfigure();
    setTimeout(initConfigure, 50);
    return html;
  });

  router.register('screen-5', () => {
    const html = renderSchema();
    setTimeout(initSchema, 50);
    return html;
  });

  router.register('screen-6', () => {
    const html = renderDashboard();
    setTimeout(initDashboard, 80);
    return html;
  });

  router.register('screen-7', () => {
    const html = renderBuilder();
    setTimeout(initBuilder, 50);
    return html;
  });

  router.register('screen-8', () => {
    const html = renderComparison();
    setTimeout(initComparison, 80);
    return html;
  });

  router.register('screen-9', () => {
    const html = renderExport();
    setTimeout(initExport, 50);
    return html;
  });

  // ── Render login screen first
  renderLogin();

  // ── Render stepper
  stepper.render(1);

  // ── Render sidebar
  sidebar.render();

  window.signOut = async function () {
    const shell = document.getElementById('shell');
    const login = document.getElementById('screen-login');

    // Tell the API (best-effort)
    try { await api.logout(); } catch (_) { }

    if (shell) shell.classList.add('hidden');
    if (login) {
      login.style.display = 'flex';
      login.style.opacity = '1';
      login.style.transition = 'none';
    }

    appState.user = null;
    appState.currentStep = 1;
    router.current = null;

    renderLogin();
    toast.show('Signed out successfully', 'info');
  };

  // ── Mode toggle handlers — global delegation for all mode toggles
  document.addEventListener('click', (e) => {
    const modeBtn = e.target.closest('.mode-toggle .mode-btn');
    if (modeBtn) {
      const toggle = modeBtn.closest('.mode-toggle');
      // Don't handle if already handled by specific init functions
      if (toggle.id === 'cmp-mode' || toggle.id === 'exp-format') return;
      toggle.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      modeBtn.classList.add('active');
    }
  });

  console.log('%c✓ UTC Channel Attribution Platform loaded', 'color: #FFB162; font-weight: 700; font-size: 14px;');
  console.log(`%c  API endpoint: ${API_BASE_URL}`, 'color: #4A6B8A; font-size: 11px;');

  // Ping backend health
  api.health().then(h => {
    const ds = h.databricks_connection === 'ok' ? '🟢 Databricks connected' : '🟠 Databricks unreachable — using mock data';
    console.log(`%c  ${ds}`, 'color: #4A6B8A; font-size: 11px;');
  }).catch(() => {
    console.warn('%c  ⚠ Backend unreachable — running in MOCK mode', 'color: #E59A4B; font-size: 11px;');
  });

})();
