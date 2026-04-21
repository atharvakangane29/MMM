// frontend/src/api.js
// ─────────────────────────────────────────────────────────────────────────────
//  Centralized API client
//  All fetch calls go through here.  No hardcoded URLs anywhere else.
//  Uses API_BASE_URL from config.js (loaded first in index.html).
// ─────────────────────────────────────────────────────────────────────────────

const api = (() => {
  'use strict';

  // ── Token management ───────────────────────────────────────────────────────
  function getToken() { return sessionStorage.getItem('mmm_token') || ''; }
  function setToken(t) { sessionStorage.setItem('mmm_token', t); }
  function clearToken() { sessionStorage.removeItem('mmm_token'); }

  // ── Core fetch wrapper ─────────────────────────────────────────────────────
  async function _fetch(path, options = {}) {
    const token = getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

    if (res.status === 401) {
      clearToken();
      // Redirect to login
      if (typeof signOut === 'function') signOut();
      throw new Error('Session expired. Please log in again.');
    }

    if (!res.ok) {
      let errMsg = `HTTP ${res.status}`;
      try {
        const body = await res.json();
        errMsg = body?.error?.message || body?.detail || errMsg;
      } catch (_) {}
      throw new Error(errMsg);
    }

    // For binary responses (CSV/PDF) return the Response object directly
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/pdf') || ct.includes('text/csv')) {
      return res;
    }

    return res.json();
  }

  // ── Auth ───────────────────────────────────────────────────────────────────
  async function login(email, password) {
    const data = await _fetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    return data;
  }

  async function logout() {
    try { await _fetch('/auth/logout', { method: 'POST' }); } catch (_) {}
    clearToken();
  }

  async function getMe() {
    return _fetch('/auth/me');
  }

  // ── Databricks metadata ────────────────────────────────────────────────────
  async function getCatalogs() {
    return _fetch('/databricks/catalogs');
  }

  async function getSchemas(catalog) {
    return _fetch(`/databricks/schemas?catalog=${encodeURIComponent(catalog)}`);
  }

  async function getTables(catalog, schema) {
    return _fetch(`/databricks/tables?catalog=${encodeURIComponent(catalog)}&schema=${encodeURIComponent(schema)}`);
  }

  async function validateTable(catalog, schema, table) {
    return _fetch('/databricks/validate-table', {
      method: 'POST',
      body: JSON.stringify({ catalog, schema, table }),
    });
  }

  // ── Data quality ───────────────────────────────────────────────────────────
  async function getDataReport(catalog, schema, table) {
    return _fetch(`/data/report?catalog=${encodeURIComponent(catalog)}&schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`);
  }

  async function getTablePreview(catalog, schema, table, limit = 5) {
    return _fetch(`/data/preview?catalog=${encodeURIComponent(catalog)}&schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}&limit=${limit}`);
  }

  // ── Scenarios ──────────────────────────────────────────────────────────────
  async function runScenario(payload) {
    return _fetch('/scenarios/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async function listScenarios(params = {}) {
    const q = new URLSearchParams(params).toString();
    return _fetch(`/scenarios${q ? '?' + q : ''}`);
  }

  async function getScenario(scenarioId) {
    return _fetch(`/scenarios/${scenarioId}`);
  }

  async function getScenarioStatus(scenarioId) {
    return _fetch(`/scenarios/${scenarioId}/status`);
  }

  async function getScenarioResults(scenarioId) {
    return _fetch(`/scenarios/${scenarioId}/results`);
  }

  async function deleteScenario(scenarioId) {
    return _fetch(`/scenarios/${scenarioId}`, { method: 'DELETE' });
  }

  // ── Comparison ─────────────────────────────────────────────────────────────
  async function compareScenarios(scenarioIds, dimensionOverride, segmentFilter) {
    return _fetch('/compare', {
      method: 'POST',
      body: JSON.stringify({
        scenario_ids: scenarioIds,
        comparison_dimension: dimensionOverride || null,
        hcp_segment_filter: segmentFilter || 'all_hcps',
      }),
    });
  }

  // ── Export ─────────────────────────────────────────────────────────────────
  async function exportScenario(scenarioId, format = 'csv') {
    const res = await _fetch(`/export/${scenarioId}?format=${format}`);
    // res is a raw Response (binary)
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scenario_${scenarioId}_report.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // ── Health ─────────────────────────────────────────────────────────────────
  async function health() {
    return _fetch('/health');
  }

  // ── Polling helper ─────────────────────────────────────────────────────────
  /**
   * Poll a scenario's status every `intervalMs` until SUCCESS or FAILED.
   * Calls onUpdate(statusData) on each poll.
   * Calls onComplete(scenarioId) when SUCCESS.
   * Calls onError(errorMessage) when FAILED.
   * Returns a stop() function to cancel polling.
   */
  function pollStatus(scenarioId, { onUpdate, onComplete, onError, intervalMs = 5000 } = {}) {
    let timer = null;

    async function tick() {
      try {
        const data = await getScenarioStatus(scenarioId);
        if (onUpdate) onUpdate(data);

        if (data.status === 'SUCCESS') {
          clearInterval(timer);
          if (onComplete) onComplete(scenarioId);
        } else if (data.status === 'FAILED') {
          clearInterval(timer);
          if (onError) onError(data.message || 'Job failed on Databricks.');
        }
      } catch (err) {
        // Network blip — keep polling
        console.warn('[polling]', err.message);
      }
    }

    timer = setInterval(tick, intervalMs);
    tick(); // immediate first poll

    return { stop: () => clearInterval(timer) };
  }

  // ── Public interface ───────────────────────────────────────────────────────
  return {
    // token
    getToken, setToken, clearToken,
    // auth
    login, logout, getMe,
    // databricks
    getCatalogs, getSchemas, getTables, validateTable,
    // data
    getDataReport, getTablePreview,
    // scenarios
    runScenario, listScenarios, getScenario,
    getScenarioStatus, getScenarioResults, deleteScenario,
    // compare
    compareScenarios,
    // export
    exportScenario,
    // health
    health,
    // util
    pollStatus,
  };
})();
