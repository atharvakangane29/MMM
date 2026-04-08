// js/screens.js — All 9 screen renderers

// ── SCREEN 1: LOGIN ──
function renderLogin() {
  const screen = document.getElementById('screen-login');
  screen.innerHTML = `
    <div class="login-card">
      <div class="login-logo-wrap">
        <div class="login-logo">
          <img src="assets/img/logo.png" alt="Circulants Logo" style="width: 50px; height: auto;">
        </div>
        <div>
          <div style="font-size:9px;color:var(--blue-mid);font-weight:600;letter-spacing:0.08em">Circulants</div>
        </div>
      </div>
      <div class="login-title">Channel Attribution Platform</div>
      <div class="login-sub"> Internal Analytics</div>
      <div class="login-sep"></div>
      <div class="login-error-banner" id="login-error">Invalid email or password. Please try again.</div>
      <div class="form-group">
        <label class="form-label">Email Address</label>
        <input type="email" class="form-input" id="login-email" placeholder="analyst@utc.com" value="jane.smith@utc.com">
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <div style="position:relative">
          <input type="password" class="form-input" id="login-password" placeholder="••••••••" value="password123">
          <button id="pw-toggle" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:var(--blue-mid);font-size:13px">👁</button>
        </div>
      </div>
      <button class="btn btn-primary btn-full btn-xl" id="login-btn">
        <span id="login-btn-text">Sign In to Platform</span>
      </button>
      <div style="text-align:center;margin-top:10px">
        <a href="#" style="font-size:12px;color:var(--blue-mid);text-decoration:none">Forgot password?</a>
      </div>
    </div>`;

  document.getElementById('pw-toggle').addEventListener('click', () => {
    const pw = document.getElementById('login-password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
  });

  document.getElementById('login-btn').addEventListener('click', () => {
    const email = document.getElementById('login-email').value;
    const pw = document.getElementById('login-password').value;
    const btn = document.getElementById('login-btn');
    const errBanner = document.getElementById('login-error');

    if (!email.includes('@')) {
      document.getElementById('login-email').classList.add('error');
      return;
    }

    if (pw.length < 6) {
      errBanner.classList.add('show');
      screen.querySelector('.login-card').style.animation = 'shake 0.4s ease';
      return;
    }

    btn.innerHTML = '<span style="display:inline-block;width:16px;height:16px;border:2px solid rgba(27,38,50,0.3);border-top-color:var(--truffle);border-radius:50%;animation:spin 0.6s linear infinite"></span> Signing in…';
    btn.disabled = true;

    setTimeout(() => {
      screen.style.opacity = '0';
      screen.style.transition = '0.4s ease';
      setTimeout(() => {
        screen.style.display = 'none';
        document.getElementById('shell').classList.remove('hidden');
        appState.user = MOCK.user;
        appState.setStep(2);
        stepper.update(2);
        toast.show(`Welcome back, ${MOCK.user.name}!`, 'success');
      }, 400);
    }, 1200);
  });

  document.getElementById('login-email').addEventListener('input', () => {
    document.getElementById('login-email').classList.remove('error');
  });
}

// ── SCREEN 2: DATA SOURCE ──
function renderDataSource() {
  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Data Source</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Connect to your Databricks workspace and select the MMM results table</p>
        </div>
      </div>
      <div class="grid-2-3" style="align-items:start">
        <div class="card">
          <div class="section-heading">Workspace Connection</div>
          <div class="form-group">
            <label class="form-label">Databricks Host</label>
            <input type="text" class="form-input" value="https://adb-123456789.azuredatabricks.net" readonly>
          </div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <span class="connection-badge connected"><span class="connection-dot"></span> Connected</span>
            <span style="font-size:11px;color:var(--blue-mid)">Workspace reachable · SDK v0.28</span>
          </div>
          <div class="sep"></div>
          <div class="section-heading">Browse Data</div>
          <div class="form-group">
            <label class="form-label">Catalog</label>
            <select class="form-input" id="ds-catalog">
              <option value="">Select catalog…</option>
              ${MOCK.catalogs.map(c => `<option value="${c}" ${c === 'hive_metastore' ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Schema</label>
            <select class="form-input" id="ds-schema">
              <option value="">Select schema…</option>
              ${(MOCK.schemas['hive_metastore'] || []).map(s => `<option value="${s}" ${s === 'utc_attribution' ? 'selected' : ''}>${s}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Table</label>
            <select class="form-input" id="ds-table">
              <option value="">Select table…</option>
              ${(MOCK.tables['utc_attribution'] || []).map(t => `<option value="${t.name}" ${t.name === 'mmm_scenario_results' ? 'selected' : ''}>${t.name} (${t.row_count} rows)</option>`).join('')}
            </select>
          </div>
          <button class="btn btn-primary btn-full" id="ds-validate-btn">Validate & Preview</button>
          <div id="ds-validation-result" style="margin-top:12px"></div>
          <button class="btn btn-primary btn-full btn-lg hidden" id="ds-continue-btn" style="margin-top:12px">Continue to Data Report →</button>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-lg">Table Preview</div>
            <span id="ds-preview-meta" style="font-size:11px;color:var(--blue-mid)">Select a table to preview</span>
          </div>
          <div id="ds-preview-content">
            <div class="empty-state" style="padding:40px 16px">
              <div class="empty-state-icon">🗃️</div>
              <div class="empty-state-title">No table selected</div>
              <div class="empty-state-desc">Select a catalog, schema, and table to see a preview</div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

function initDataSource() {
  const validateBtn = document.getElementById('ds-validate-btn');
  const continueBtn = document.getElementById('ds-continue-btn');
  const resultDiv = document.getElementById('ds-validation-result');

  validateBtn?.addEventListener('click', () => {
    const table = document.getElementById('ds-table').value;
    if (!table) { toast.show('Please select a table first', 'info'); return; }

    validateBtn.innerHTML = '<span style="display:inline-block;width:14px;height:14px;border:2px solid rgba(27,38,50,0.2);border-top-color:var(--truffle);border-radius:50%;animation:spin 0.6s linear infinite"></span> Validating…';
    validateBtn.disabled = true;

    setTimeout(() => {
      validateBtn.innerHTML = 'Validate & Preview';
      validateBtn.disabled = false;

      if (table === 'mmm_scenario_results') {
        resultDiv.innerHTML = `<div class="callout amber">
          <span class="callout-icon">✓</span> <strong>Table validated</strong> — 73 columns · 377 rows detected. Schema matches expected MMM output format.
        </div>`;

        // Show preview
        const cols = Object.keys(MOCK.previewRows[0]);
        document.getElementById('ds-preview-meta').textContent = '377 rows · 73 columns · Last modified Apr 03, 2026';
        document.getElementById('ds-preview-content').innerHTML = `
          <div class="preview-table-wrap">
            <table class="preview-table">
              <thead><tr>${cols.slice(0, 7).map(c => `<th>${c}</th>`).join('')}<th>…</th></tr></thead>
              <tbody>
                ${MOCK.previewRows.map(row => `<tr>${cols.slice(0, 7).map(c => `<td>${row[c]}</td>`).join('')}<td style="color:var(--oatmeal)">…</td></tr>`).join('')}
              </tbody>
            </table>
          </div>`;

        continueBtn.classList.remove('hidden');
        appState.connection = { catalog: 'hive_metastore', schema: 'utc_attribution', table };
      } else {
        resultDiv.innerHTML = `<div class="callout flame">
          <span class="callout-icon">✕</span> <strong>Schema mismatch</strong> — Missing columns: Attribution_Pct_0_2_Years, no_of_hcp_0_2_Years. Expected 73, found 68.
        </div>`;
      }
    }, 1200);
  });

  continueBtn?.addEventListener('click', () => {
    appState.setStep(3);
    stepper.update(3);
  });
}

// ── SCREEN 3: DATA REPORT ──
function renderDataReport() {
  const d = MOCK.dataReport;
  const completenessColor = d.overview.completeness >= 95 ? 'var(--blue)' : d.overview.completeness >= 80 ? 'var(--amber)' : 'var(--flame)';

  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Data Quality Report</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Automated completeness, date coverage, and null analysis</p>
        </div>
        <div class="page-header-actions">
          <button class="btn btn-outline btn-sm">↻ Refresh</button>
          <span style="font-size:11px;color:var(--blue-mid);align-self:center">Last scanned: Apr 03, 2026 · 10:28 AM</span>
        </div>
      </div>

      <div class="dq-health-grid stagger">
        ${[
      { label: 'Total Rows', value: d.overview.total_rows, sub: 'mmm_scenario_results' },
      { label: 'Total Columns', value: d.overview.total_cols, sub: '73-column schema' },
      { label: 'Date Range', value: d.overview.date_range, sub: 'Observation window', big: false },
      { label: 'Completeness', value: d.overview.completeness + '%', sub: 'Schema fill rate', color: completenessColor },
      { label: 'Unique Scenarios', value: d.overview.unique_scenarios, sub: 'Distinct run IDs' }
    ].map(k => `<div class="dq-card">
          <div class="dq-label">${k.label}</div>
          <div class="dq-value" style="${k.color ? 'color:' + k.color : ''};font-size:${k.big === false ? '15px' : '20px'}">${k.value}</div>
          <div class="dq-sub">${k.sub}</div>
        </div>`).join('')}
      </div>

      <div class="card" style="margin-bottom:16px">
        <div class="card-header">
          <div class="card-title-lg">Date Coverage Timeline</div>
          <span style="font-size:11px;color:var(--flame)">⚠ 2 months with no data (Jun 2023, Jan 2024)</span>
        </div>
        <div id="dq-coverage-chart"></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-lg">Column Null Rate Analysis</div>
          <span style="font-size:11px;color:var(--blue-mid)">${d.columns.length} columns</span>
        </div>
        <div class="filter-chips" id="dq-filters">
          ${['All', 'Attribution %', 'HCP Counts', 'Touchpoints', 'Prescribers', 'Run Config'].map((f, i) => `<button class="chip ${i === 0 ? 'active' : ''}" data-filter="${f}">${f}</button>`).join('')}
        </div>
        <div class="data-table-wrap" id="dq-table-wrap">
          ${renderDQTable(d.columns, 'All')}
        </div>
        <div class="callout" style="margin-top:12px">
          <span class="callout-icon">ℹ️</span> Partial nulls in segment-specific columns are expected behaviour. A Cluster-level run will have nulls for LOB and Competitor Drug columns — this is by design.
        </div>
      </div>

      <div style="display:flex;gap:10px;justify-content:space-between;margin-top:16px;align-items:center">
        <a href="#" class="btn btn-ghost" onclick="appState.setStep(2);stepper.update(2);return false">← Back to Data Source</a>
        <button class="btn btn-primary btn-lg" onclick="appState.setStep(4);stepper.update(4)">Proceed to Configure Scenario →</button>
      </div>
    </div>`;
}

function renderDQTable(columns, filter) {
  const filtered = filter === 'All' ? columns : columns.filter(c => c.group === filter);
  const statusIcons = { clean: '✓', partial: '⚠', missing: '✗' };
  const statusColors = { clean: 'var(--blue)', partial: 'var(--amber)', missing: 'var(--flame)' };

  return `<table class="data-table">
    <thead><tr><th>Group</th><th>Column</th><th>Type</th><th>Null Rate</th><th>Status</th><th>Note</th></tr></thead>
    <tbody>
      ${filtered.map(c => `<tr>
        <td style="font-size:11px;color:var(--blue-mid)">${c.group}</td>
        <td class="mono" style="font-size:11px;font-weight:600">${c.column}</td>
        <td class="mono" style="font-size:10px;color:var(--blue-mid)">${c.type}</td>
        <td>
          <div class="inline-bar-wrap">
            <div class="inline-bar-track" style="min-width:40px">
              <div class="inline-bar-fill" style="width:${c.null_rate}%;background:${c.null_rate === 0 ? 'var(--amber)' : c.null_rate > 50 ? 'var(--flame)' : '#E59A4B'}"></div>
            </div>
            <span style="font-size:11px;font-weight:600">${c.null_rate}%</span>
          </div>
        </td>
        <td><span style="font-size:11px;font-weight:700;color:${statusColors[c.status]}">${statusIcons[c.status]} ${c.status.charAt(0).toUpperCase() + c.status.slice(1)}</span></td>
        <td style="font-size:10px;color:var(--blue-mid)">${c.note || '—'}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

function initDataReport() {
  setTimeout(() => {
    const coverageEl = document.getElementById('dq-coverage-chart');
    if (coverageEl) charts.coverage(coverageEl, MOCK.dataReport.coverage);
  }, 50);

  document.querySelectorAll('#dq-filters .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#dq-filters .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      document.getElementById('dq-table-wrap').innerHTML = renderDQTable(MOCK.dataReport.columns, chip.dataset.filter);
    });
  });
}

// ── SCREEN 4: CONFIGURE ──
function renderConfigure() {
  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Configure Scenario</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Set hyperparameters and trigger the Markov chain attribution model on Databricks</p>
        </div>
      </div>
      <div class="grid-2-1" style="align-items:start">
        <div class="card">
          <div class="section-heading">Scenario Identity</div>
          <div class="form-group">
            <label class="form-label">Scenario Name <span style="color:var(--flame)">*</span></label>
            <input type="text" class="form-input" id="cfg-name" placeholder="e.g. Q4 TYVASO — Cluster Baseline">
          </div>
          <div class="sep"></div>
          <div class="section-heading">Hyperparameters</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Start Date</label>
              <input type="date" class="form-input" id="cfg-start" value="2023-01-01">
            </div>
            <div class="form-group">
              <label class="form-label">End Date</label>
              <input type="date" class="form-input" id="cfg-end" value="2025-03-31">
            </div>
          </div>
          <div id="cfg-date-warn" class="hidden">
            <div style="font-size:11px;color:var(--amber);margin-top:-8px;margin-bottom:8px">⚠ Date range is less than 12 months — model accuracy may be reduced</div>
          </div>

          <div class="form-group">
            <label class="form-label">Product</label>
            <div class="pill-selector" id="cfg-product">
              ${['ALL', 'TYVASO', 'REMODULIN', 'ORENITRAM', 'TREPROSTINIL'].map(p => `<button class="pill-option ${p === 'TYVASO' ? 'selected' : ''}" data-val="${p}">${p}</button>`).join('')}
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Attribution Level</label>
            <div class="card-selector cols-3" id="cfg-level">
              <div class="card-option selected" data-val="touchpoint">
                <div class="card-option-icon">🎯</div>
                <div class="card-option-title">Touchpoint</div>
                <div class="card-option-desc">Most granular — individual call types per HCP</div>
              </div>
              <div class="card-option" data-val="channel">
                <div class="card-option-icon">📡</div>
                <div class="card-option-title">Channel</div>
                <div class="card-option-desc">Grouped by modality (Live, Virtual, Email)</div>
              </div>
              <div class="card-option" data-val="team">
                <div class="card-option-icon">👥</div>
                <div class="card-option-title">Team</div>
                <div class="card-option-desc">Grouped by sales team (SALES, MDD, MSL…)</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">HCP Segment</label>
            <div class="card-selector cols-4" id="cfg-segment" style="grid-template-columns:repeat(2,1fr)">
              <div class="card-option selected" data-val="cluster">
                <div class="card-option-icon">🏆</div>
                <div class="card-option-title">Cluster</div>
                <div class="card-option-desc">High Performer → Unresponsive performance tiers</div>
              </div>
              <div class="card-option" data-val="lob">
                <div class="card-option-icon">📅</div>
                <div class="card-option-title">Length of Business</div>
                <div class="card-option-desc">0–2 / 2–10 / 10+ years since first referral</div>
              </div>
              <div class="card-option" data-val="competitor_drug">
                <div class="card-option-icon">💊</div>
                <div class="card-option-title">Competitor Drug</div>
                <div class="card-option-desc">Writes vs Does Not Write competitor</div>
              </div>
              <div class="card-option" data-val="all_hcps">
                <div class="card-option-icon">👁</div>
                <div class="card-option-title">All HCPs</div>
                <div class="card-option-desc">Full universe — no segment filter applied</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Notes (optional)</label>
            <textarea class="form-input" id="cfg-notes" rows="2" placeholder="Analyst notes for this scenario…" style="resize:vertical"></textarea>
          </div>

          <button class="btn btn-primary btn-full btn-xl" id="cfg-run-btn" disabled>
            ▶ Run Attribution Model
          </button>
        </div>

        <div>
          <div class="config-summary-card">
            <div class="config-summary-header">SCENARIO CONFIGURATION</div>
            <div class="config-summary-body">
              <div class="config-row"><span class="config-key">Name</span><span class="config-val" id="cfg-sum-name" style="color:var(--oatmeal);font-style:italic">Not set</span></div>
              <div class="config-row"><span class="config-key">Product</span><span class="config-val" id="cfg-sum-product">TYVASO</span></div>
              <div class="config-row"><span class="config-key">Date Range</span><span class="config-val" id="cfg-sum-dates">Jan 2023 → Mar 2025</span></div>
              <div class="config-row"><span class="config-key">Duration</span><span class="config-val" id="cfg-sum-duration">27 months</span></div>
              <div class="config-row"><span class="config-key">Level</span><span class="config-val" id="cfg-sum-level">Touchpoint</span></div>
              <div class="config-row"><span class="config-key">Segment</span><span class="config-val" id="cfg-sum-segment">Cluster</span></div>
            </div>
            <div style="padding:0 16px 14px">
              <div class="config-runtime">⏱ Estimated runtime: <strong>~60–90 seconds</strong></div>
              <div class="config-runtime" style="margin-top:6px">📊 Matching rows: <strong>377</strong></div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

function initConfigure() {
  function updateSummary() {
    const name = document.getElementById('cfg-name')?.value;
    const product = document.querySelector('#cfg-product .selected')?.dataset.val;
    const level = document.querySelector('#cfg-level .selected')?.dataset.val;
    const segment = document.querySelector('#cfg-segment .selected')?.dataset.val;
    const start = document.getElementById('cfg-start')?.value;
    const end = document.getElementById('cfg-end')?.value;
    const btn = document.getElementById('cfg-run-btn');

    if (name) {
      document.getElementById('cfg-sum-name').textContent = name;
      document.getElementById('cfg-sum-name').style.cssText = 'color:var(--blue);font-style:normal';
    } else {
      document.getElementById('cfg-sum-name').textContent = 'Not set';
      document.getElementById('cfg-sum-name').style.cssText = 'color:var(--oatmeal);font-style:italic';
    }
    if (product) document.getElementById('cfg-sum-product').textContent = product;
    if (level) document.getElementById('cfg-sum-level').textContent = level.charAt(0).toUpperCase() + level.slice(1);
    if (segment) document.getElementById('cfg-sum-segment').textContent = segment.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    if (start && end) {
      const s = new Date(start); const e = new Date(end);
      const months = Math.round((e - s) / (1000 * 60 * 60 * 24 * 30.4));
      document.getElementById('cfg-sum-dates').textContent = `${start} → ${end}`;
      document.getElementById('cfg-sum-duration').textContent = `${months} months`;
      document.getElementById('cfg-date-warn').classList.toggle('hidden', months >= 12);
    }
    btn.disabled = !name || !product || !level || !segment;
  }

  ['cfg-name', 'cfg-start', 'cfg-end', 'cfg-notes'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', updateSummary);
  });

  document.querySelectorAll('#cfg-product .pill-option').forEach(p => {
    p.addEventListener('click', () => {
      document.querySelectorAll('#cfg-product .pill-option').forEach(o => o.classList.remove('selected'));
      p.classList.add('selected');
      updateSummary();
    });
  });

  ['cfg-level', 'cfg-segment'].forEach(groupId => {
    document.querySelectorAll(`#${groupId} .card-option`).forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll(`#${groupId} .card-option`).forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        updateSummary();
      });
    });
  });

  document.getElementById('cfg-run-btn')?.addEventListener('click', () => {
    const name = document.getElementById('cfg-name').value;
    const product = document.querySelector('#cfg-product .selected').dataset.val;
    const level = document.querySelector('#cfg-level .selected').dataset.val;
    const segment = document.querySelector('#cfg-segment .selected').dataset.val;

    const newScenario = {
      id: 'scen-' + Date.now(),
      name,
      product,
      level: level.charAt(0).toUpperCase() + level.slice(1),
      segment: segment.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      start: document.getElementById('cfg-start').value,
      end: document.getElementById('cfg-end').value,
      status: 'RUNNING',
      created: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }) + ' · ' + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      completed: null,
      pinned: false,
      progress: 0,
      notes: document.getElementById('cfg-notes').value
    };

    appState.addScenario(newScenario);
    appState.activeScenarioId = newScenario.id;

    appState.setStep(5);
    stepper.update(5);

    setTimeout(() => {
      simulateJob(newScenario, (completed) => {
        toast.show(`"${completed.name}" is ready! Click to view results.`, 'success');
        appState.activeScenarioId = completed.id;
      });
    }, 300);
  });
}

// ── SCREEN 5: SCHEMA & KPIs ──
function renderSchema() {
  const u = MOCK.universeKPIs;
  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Data Schema &amp; Universe KPIs</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Explore the 73-column schema and HCP universe while your model runs</p>
        </div>
        <div id="running-status-widget">
          ${renderRunningWidget()}
        </div>
      </div>
      <div class="grid-2" style="align-items:start">
        <div>
          <div class="card" style="margin-bottom:16px">
            <div class="card-header">
              <div class="card-title-lg">Schema Explorer</div>
              <span class="mono" style="font-size:11px;color:var(--blue-mid)">73 columns</span>
            </div>
            <input type="text" class="form-input" id="schema-search" placeholder="Search columns…" style="margin-bottom:12px">
            <div class="filter-chips" id="schema-filters">
              ${['All', 'Attribution %', 'HCP Counts', 'Touchpoints', 'Prescribers', 'Run Config'].map((f, i) => `<button class="chip ${i === 0 ? 'active' : ''}" data-filter="${f}">${f}</button>`).join('')}
            </div>
            <div id="schema-table-wrap" style="max-height:340px;overflow-y:auto">
              ${renderSchemaTable(MOCK.schemaColumns, 'All', '')}
            </div>
          </div>
        </div>
        <div>
          <div class="grid-2" style="margin-bottom:16px">
            ${[
      { label: 'Total HCPs in Universe', val: u.total_hcps.toLocaleString(), sub: 'hcp360_universe table', icon: '👥' },
      { label: 'Total Referrals', val: u.total_referrals.toLocaleString(), sub: 'Observation period', icon: '📋' },
      { label: 'Marketing Teams', val: u.marketing_teams, sub: 'SALES·MDD·MSL·RNS·SPK PGM·EMAIL', icon: '🏢' },
      { label: 'Total Touchpoints', val: u.total_touchpoints.toLocaleString(), sub: 'All HCP interactions', icon: '📞' },
      { label: 'HCP Prescribers', val: u.prescribers.toLocaleString(), sub: 'Converters in period', icon: '✍️' },
      { label: 'Date Coverage', val: '27 months', sub: u.date_coverage, icon: '📅' }
    ].map(k => `<div class="kpi-card" style="padding:14px 16px">
              <div class="kpi-label" style="display:flex;align-items:center;gap:4px"><span>${k.icon}</span>${k.label}</div>
              <div class="kpi-value" style="font-size:22px">${k.val}</div>
              <div class="kpi-sub">${k.sub}</div>
            </div>`).join('')}
          </div>
          <div class="card">
            <div class="card-header"><div class="card-title-lg">Team Coverage Breakdown</div></div>
            <div style="overflow-x:auto">
              <table class="team-table">
                <thead><tr><th>Team</th><th>HCPs Reached</th><th>Touchpoints</th><th>Est. Attribution</th></tr></thead>
                <tbody>
                  ${u.teams.map(t => `<tr>
                    <td><span class="team-dot" style="background:${t.color}"></span><strong>${t.name}</strong></td>
                    <td>${t.hcps} <span style="color:var(--oatmeal)">(${t.hcp_pct})</span></td>
                    <td>${t.touchpoints} <span style="color:var(--oatmeal)">(${t.tp_pct})</span></td>
                    <td><strong style="color:var(--blue)">${t.attribution}</strong></td>
                  </tr>`).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

function renderRunningWidget() {
  const running = MOCK.scenarios.find(s => s.status === 'RUNNING');
  if (running) {
    return `<div class="running-widget">
      <span style="color:var(--blue-mid)">⏱</span>
      <span style="font-size:12px;font-weight:600;color:var(--blue)">${running.name}</span>
      <span class="status-badge running"><span class="status-dot"></span>RUNNING</span>
      <div class="progress-wrap" style="width:80px"><div class="progress-fill" style="width:${running.progress || 30}%"></div></div>
    </div>`;
  }
  return `<button class="running-widget ready" onclick="appState.setStep(6);stepper.update(6)">
    <span style="color:var(--amber)">✓</span>
    <span style="font-size:12px;font-weight:600;color:var(--blue)">Results ready</span>
    <span class="btn btn-primary btn-sm">View Dashboard →</span>
  </button>`;
}

function renderSchemaTable(columns, filter, search) {
  const filtered = columns.filter(c => {
    const matchFilter = filter === 'All' || c.cat === filter;
    const matchSearch = !search || c.name.toLowerCase().includes(search.toLowerCase()) || c.desc.toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  const catClass = { 'Attribution %': 'cat-attribution', 'HCP Counts': 'cat-hcp', 'Touchpoints': 'cat-touchpoints', 'Prescribers': 'cat-prescribers', 'Run Config': 'cat-runconfig' };

  return `<table class="data-table">
    <thead><tr><th>Column</th><th>Type</th><th>Category</th><th>Description</th></tr></thead>
    <tbody>
      ${filtered.map(c => `<tr class="schema-row" onclick="this.nextElementSibling?.classList.toggle('hidden')">
        <td class="mono" style="font-size:11px;font-weight:600">${c.name}</td>
        <td class="mono" style="font-size:10px;color:var(--blue-mid)">${c.type}</td>
        <td><span class="schema-category-pill ${catClass[c.cat] || ''}">${c.cat}</span></td>
        <td style="font-size:11px;color:var(--blue-mid)">${c.desc.slice(0, 50)}${c.desc.length > 50 ? '…' : ''}</td>
      </tr>
      <tr class="hidden"><td colspan="4" class="schema-detail">${c.desc}</td></tr>`).join('')}
    </tbody>
  </table>`;
}

function initSchema() {
  document.getElementById('schema-search')?.addEventListener('input', (e) => {
    const search = e.target.value;
    const filter = document.querySelector('#schema-filters .chip.active')?.dataset.filter || 'All';
    document.getElementById('schema-table-wrap').innerHTML = renderSchemaTable(MOCK.schemaColumns, filter, search);
  });

  document.querySelectorAll('#schema-filters .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#schema-filters .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const search = document.getElementById('schema-search')?.value || '';
      document.getElementById('schema-table-wrap').innerHTML = renderSchemaTable(MOCK.schemaColumns, chip.dataset.filter, search);
    });
  });
}

// ── SCREEN 6: DASHBOARD ──
function renderDashboard() {
  const scen = appState.getActiveScenario();
  const results = appState.getActiveResult();

  if (!results) {
    return `<div class="empty-state" style="height:60vh">
      <div class="empty-state-icon">📊</div>
      <div class="empty-state-title">No results available</div>
      <div class="empty-state-desc">Select a completed scenario from the sidebar or run a new one</div>
      <button class="btn btn-primary" style="margin-top:16px" onclick="appState.setStep(4)">+ New Scenario</button>
    </div>`;
  }

  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>${scen?.name || 'Results Dashboard'}</h1>
          <div class="meta-pills">
            <span class="meta-pill product">${scen?.product || 'TYVASO'}</span>
            <span class="meta-pill">${scen?.level || 'Touchpoint'}</span>
            <span class="meta-pill">${scen?.segment || 'Cluster'}</span>
            <span class="meta-pill">${scen?.start || '2023-01-01'} – ${scen?.end || '2025-03-31'}</span>
            ${scen?.completed ? `<span class="meta-pill">✓ ${scen.completed}</span>` : ''}
          </div>
        </div>
        <div class="page-header-actions">
          <button class="btn btn-outline btn-sm" onclick="appState.togglePin(appState.activeScenarioId);sidebar.render();toast.show('Scenario ${appState.isPinned(appState.activeScenarioId) ? 'removed from' : 'added to'} comparison','success')">
            📌 ${appState.isPinned(appState.activeScenarioId) ? 'Pinned' : 'Add to Compare'}
          </button>
          <button class="btn btn-outline btn-sm" onclick="appState.setStep(9);stepper.update(9)">Export Report</button>
        </div>
      </div>

      <div class="kpi-grid stagger">
        ${[
      { label: 'Total HCPs in Universe', val: results.summary_kpis.total_hcps },
      { label: 'Total Referrals', val: results.summary_kpis.total_referrals },
      { label: 'Total Touchpoints', val: results.summary_kpis.total_touchpoints },
      { label: 'Total Prescribers', val: results.summary_kpis.total_prescribers }
    ].map(k => `<div class="kpi-card">
          <div class="kpi-label">${k.label}</div>
          <div class="kpi-value">${k.val}</div>
        </div>`).join('')}
      </div>

      <div class="grid-2-3" style="margin-bottom:16px;align-items:start">
        <div class="card">
          <div class="card-header"><div class="card-title-lg">Team Attribution</div></div>
          <div id="team-donut"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title-lg">Channel Attribution</div>
            <span style="font-size:11px;color:var(--blue-mid)">${results.channels.length} channels</span>
          </div>
          <div id="channel-table"></div>
        </div>
      </div>

      <div class="card" style="margin-bottom:16px">
        <div class="card-header">
          <div class="card-title-lg">Marketing Touchpoint Flow → Referral Conversion</div>
          <span style="font-size:11px;color:var(--blue-mid)">Markov Chain Attribution · Sankey Diagram</span>
        </div>
        <p style="font-size:11px;color:var(--blue-mid);margin-bottom:12px">Band width represents attribution proportion. Hover over flows for details.</p>
        <div id="sankey-chart"></div>
      </div>

      <div class="grid-2" style="margin-bottom:16px;align-items:start">
        <div class="card">
          <div class="card-header">
            <div class="card-title-lg">HCP Segment Movement</div>
            <span style="font-size:11px;color:var(--blue-mid)">Jan 2023 → Mar 2025</span>
          </div>
          <p style="font-size:11px;color:var(--blue-mid);margin-bottom:10px">Count of HCPs in each performance tier by month</p>
          <div id="journey-chart"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title-lg">Segment Attribution Heatmap</div>
            <span style="font-size:11px;color:var(--blue-mid)">Channel × Segment matrix</span>
          </div>
          <div id="heatmap-chart"></div>
        </div>
      </div>
    </div>`;
}

function initDashboard() {
  const results = appState.getActiveResult();
  if (!results) return;

  setTimeout(() => {
    const donutEl = document.getElementById('team-donut');
    if (donutEl) charts.donut(donutEl, results.team_summary);

    const channelEl = document.getElementById('channel-table');
    if (channelEl) charts.channelBars(channelEl, results.channels);

    const sankeyEl = document.getElementById('sankey-chart');
    if (sankeyEl) charts.sankey(sankeyEl);

    const journeyEl = document.getElementById('journey-chart');
    if (journeyEl) charts.journey(journeyEl);

    const heatmapEl = document.getElementById('heatmap-chart');
    if (heatmapEl) charts.heatmap(heatmapEl, results.heatmap);
  }, 50);
}

// ── SCREEN 7: SCENARIO BUILDER ──
function renderBuilder() {
  const scenarios = Array.from(appState.scenarios.values());
  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Scenario Builder</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Manage, clone, and monitor all attribution runs</p>
        </div>
        <div class="page-header-actions">
          <button class="btn btn-primary" onclick="appState.setStep(4);stepper.update(4)">+ New Scenario</button>
        </div>
      </div>
      <div class="grid-1-2" style="align-items:start">
        <div>
          <div class="card" style="padding:12px">
            <div class="card-header" style="margin-bottom:10px">
              <div class="card-title-lg">Scenario Library</div>
              <span style="font-size:11px;color:var(--blue-mid)">${scenarios.length} runs</span>
            </div>
            <div class="filter-chips" id="builder-filters">
              ${['All', 'SUCCESS', 'RUNNING', 'FAILED'].map((f, i) => `<button class="chip ${i === 0 ? 'active' : ''}" data-filter="${f}">${f}</button>`).join('')}
            </div>
            <div id="builder-list">
              ${renderBuilderList(scenarios, 'All')}
            </div>
          </div>
        </div>
        <div id="builder-detail">
          ${renderBuilderDetail(MOCK.scenarios[0])}
        </div>
      </div>
    </div>`;
}

function renderBuilderList(scenarios, filter) {
  const filtered = filter === 'All' ? scenarios : scenarios.filter(s => s.status === filter);
  const teamColors = { TYVASO: '#FFB162', REMODULIN: '#2C3B4D', ORENITRAM: '#4A6B8A', TREPROSTINIL: '#7FA3C0', ALL: '#C9C1B1' };

  return filtered.map(sc => {
    const color = teamColors[sc.product] || '#C9C1B1';
    const isPinned = appState.isPinned(sc.id);
    return `<div class="scenario-card ${sc.id === appState.activeScenarioId ? 'active' : ''}" data-id="${sc.id}" style="cursor:pointer;margin-bottom:6px">
      <div style="display:flex;align-items:flex-start;gap:6px">
        <span class="scenario-product-pill ${sc.product.toLowerCase()}">${sc.product}</span>
        <div style="flex:1">
          <div style="font-size:13px;font-weight:700;color:var(--blue)">${sc.name}</div>
          <div style="font-size:11px;color:var(--blue-mid);margin-top:2px">${sc.level} · ${sc.segment} · ${sc.start}–${sc.end}</div>
          <div style="font-size:10px;color:var(--oatmeal);margin-top:2px">${sc.created}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">
          <span class="status-badge ${sc.status.toLowerCase()}"><span class="status-dot"></span>${sc.status}</span>
          <button class="pin-btn ${isPinned ? 'pinned' : ''}" data-pin="${sc.id}" onclick="event.stopPropagation();appState.togglePin('${sc.id}');sidebar.render();document.getElementById('builder-list').innerHTML=renderBuilderList(Array.from(appState.scenarios.values()),document.querySelector('#builder-filters .chip.active')?.dataset.filter||'All')">
            ${isPinned ? '📌' : '📌'}
          </button>
        </div>
      </div>
      ${sc.status === 'RUNNING' ? `<div class="progress-wrap" style="margin-top:8px"><div class="progress-fill" style="width:${sc.progress || 30}%"></div></div>` : ''}
    </div>`;
  }).join('') || `<div class="empty-state" style="padding:24px"><div class="empty-state-icon">🔍</div><div class="empty-state-desc">No scenarios match this filter</div></div>`;
}

function renderBuilderDetail(sc) {
  if (!sc) return `<div class="card"><div class="empty-state"><div class="empty-state-icon">👆</div><div class="empty-state-title">Select a scenario</div></div></div>`;

  const results = MOCK.results[sc.id];
  const timeline = [
    { label: 'Queued', time: sc.created.split('·')[1]?.trim() || '10:30:00', state: 'done' },
    { label: 'Running on Databricks', time: '+0:12', state: sc.status !== 'QUEUED' ? 'done' : 'current' },
    { label: 'Writing to Delta Lake', time: '+1:10', state: sc.status === 'SUCCESS' ? 'done' : sc.status === 'RUNNING' ? 'current' : 'pending' },
    { label: sc.status === 'FAILED' ? 'Job Failed' : 'Completed', time: sc.completed?.split('·')[1]?.trim() || '—', state: sc.status === 'SUCCESS' ? 'done' : sc.status === 'FAILED' ? 'done' : 'pending' }
  ];

  return `<div class="card slide-up">
    <div class="card-header">
      <div class="card-title-lg" style="font-size:16px">${sc.name}</div>
      <span class="status-badge ${sc.status.toLowerCase()}"><span class="status-dot"></span>${sc.status}</span>
    </div>

    <div class="grid-2" style="margin-bottom:14px">
      ${[
      { label: 'Product', val: sc.product },
      { label: 'Level', val: sc.level },
      { label: 'Segment', val: sc.segment },
      { label: 'Date Range', val: `${sc.start} – ${sc.end}` }
    ].map(r => `<div class="detail-chip">
        <div class="detail-chip-label">${r.label}</div>
        <div style="font-size:13px;font-weight:600;color:var(--blue)">${r.val}</div>
      </div>`).join('')}
    </div>

    ${results ? `<div class="detail-kpi-chips">
      ${[
        { label: 'Total Referrals', val: results.summary_kpis.total_referrals },
        { label: 'Top Channel', val: results.channels[0]?.channel + ' ' + results.channels[0]?.pct + '%' },
        { label: 'Top Team', val: results.team_summary[0]?.team + ' ' + results.team_summary[0]?.pct + '%' }
      ].map(k => `<div class="detail-chip">
        <div class="detail-chip-label">${k.label}</div>
        <div class="detail-chip-val">${k.val}</div>
      </div>`).join('')}
    </div>` : ''}

    <div class="sep"></div>
    <div class="section-heading">Status Timeline</div>
    <div class="status-timeline">
      ${timeline.map(t => `<div class="timeline-item ${t.state}">
        <div class="timeline-dot">${t.state === 'done' ? '✓' : t.state === 'current' ? '●' : '○'}</div>
        <div class="timeline-text">
          <div class="timeline-label">${t.label}</div>
          <div class="timeline-time">${t.time}</div>
        </div>
      </div>`).join('')}
    </div>

    ${sc.notes ? `<div class="callout" style="margin-top:10px"><strong>Note:</strong> ${sc.notes}</div>` : ''}

    <div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap">
      ${sc.status === 'SUCCESS' ? `<button class="btn btn-primary" onclick="appState.activeScenarioId='${sc.id}';appState.setStep(6);stepper.update(6)">View Full Dashboard →</button>` : ''}
      <button class="btn btn-outline" onclick="cloneScenario('${sc.id}')">Clone Scenario</button>
      <button class="btn btn-danger btn-sm">Delete</button>
    </div>
  </div>`;
}

function cloneScenario(id) {
  const sc = appState.scenarios.get(id);
  if (!sc) return;
  appState.setStep(4);
  stepper.update(4);
  toast.show(`Cloning "${sc.name}" — form pre-filled`, 'info');
  setTimeout(() => {
    const nameEl = document.getElementById('cfg-name');
    if (nameEl) {
      nameEl.value = `Copy of ${sc.name}`;
      nameEl.dispatchEvent(new Event('input'));
    }
  }, 100);
}

function initBuilder() {
  document.querySelectorAll('#builder-filters .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#builder-filters .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      document.getElementById('builder-list').innerHTML = renderBuilderList(Array.from(appState.scenarios.values()), chip.dataset.filter);
      rebindBuilderClicks();
    });
  });

  rebindBuilderClicks();
}

function rebindBuilderClicks() {
  document.querySelectorAll('#builder-list .scenario-card').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('.pin-btn')) return;
      const id = card.dataset.id;
      appState.activeScenarioId = id;
      const sc = appState.scenarios.get(id);
      document.getElementById('builder-detail').innerHTML = renderBuilderDetail(sc);
      document.querySelectorAll('#builder-list .scenario-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
    });
  });
}

// ── SCREEN 8: COMPARISON ──
function renderComparison() {
  const pinned = appState.comparisonSet;
  const hasEnough = pinned.length >= 2;

  const scA = appState.scenarios.get(pinned[0]);
  const scB = appState.scenarios.get(pinned[1]);
  const resA = scA ? (MOCK.results[scA.id] || MOCK.results['scen-001']) : null;
  const resB = scB ? (MOCK.results[scB.id] || MOCK.results['scen-002']) : null;

  if (!hasEnough) {
    return `<div class="slide-up">
      <div class="page-header"><div class="page-header-left"><h1>Scenario Comparison</h1></div></div>
      <div class="empty-state" style="height:60vh">
        <div class="empty-state-icon">📌</div>
        <div class="empty-state-title">Pin at least 2 scenarios to compare</div>
        <div class="empty-state-desc">Click the 📌 pin icon on any scenario card in the sidebar, or go to the Scenario Builder</div>
        <button class="btn btn-primary" style="margin-top:16px" onclick="appState.setStep(7);stepper.update(7)">Go to Scenario Builder →</button>
      </div>
    </div>`;
  }

  const scAWithName = { ...resA, scenario_name: scA?.name, ...resA?.team_summary && {} };
  const scBWithName = { ...resB, scenario_name: scB?.name, ...resB?.team_summary && {} };

  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Scenario Comparison</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">${pinned.length} scenarios selected</p>
        </div>
        <div class="page-header-actions">
          <button class="btn btn-outline btn-sm" onclick="appState.setStep(9);stepper.update(9)">Export Comparison →</button>
        </div>
      </div>

      <div class="compare-bar">
        <div class="compare-bar-section">
          <span class="compare-bar-label">Comparing:</span>
          <select class="compare-select" id="cmp-scen-a">
            ${Array.from(appState.scenarios.values()).filter(s => s.status === 'SUCCESS').map(s => `<option value="${s.id}" ${s.id === pinned[0] ? 'selected' : ''}>${s.name}</option>`).join('')}
          </select>
          <span style="font-size:11px;color:var(--blue-mid);font-weight:600">vs</span>
          <select class="compare-select" id="cmp-scen-b">
            ${Array.from(appState.scenarios.values()).filter(s => s.status === 'SUCCESS').map(s => `<option value="${s.id}" ${s.id === pinned[1] ? 'selected' : ''}>${s.name}</option>`).join('')}
          </select>
        </div>
        <div class="compare-bar-section" style="margin-left:auto">
          <span class="compare-bar-label">Mode:</span>
          <div class="mode-toggle" id="cmp-mode">
            <button class="mode-btn active" data-mode="side-by-side">Side-by-Side</button>
            <button class="mode-btn" data-mode="delta">Delta View</button>
            <button class="mode-btn" data-mode="waterfall">Waterfall</button>
          </div>
        </div>
      </div>

      <div class="insight-card">
        <div class="insight-title">💡 Key Insight — Auto-Generated</div>
        <ul class="insight-bullets">
          <li>SALES attribution is <strong>7pp higher</strong> for ${scA?.name?.split('—')[0]?.trim() || 'Scenario A'} (59% vs 52%) — likely driven by TYVASO's stronger field force engagement</li>
          <li>MDD team is <strong>4pp more effective</strong> for ${scB?.name?.split('—')[0]?.trim() || 'Scenario B'} (21% vs 17%) — specialist engagement stronger for IV/SC route</li>
          <li>Speaker Programs perform <strong>equally</strong> across both products (5% vs 5%) — channel agnostic to product</li>
        </ul>
        <div class="insight-rec">💡 Recommendation: ${scB?.product || 'REMODULIN'} strategy should emphasise MDD team engagement. Consider reallocating SALES budget towards MDD for this product.</div>
      </div>

      <div class="card" style="margin-bottom:16px">
        <div class="card-header">
          <div class="card-title-lg">Attribution Comparison</div>
          <div style="display:flex;align-items:center;gap:10px">
            <div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:12px;border-radius:2px;background:#FFB162"></div><span style="font-size:11px">${scA?.name || 'Scenario A'}</span></div>
            <div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:12px;border-radius:2px;background:#4A6B8A"></div><span style="font-size:11px">${scB?.name || 'Scenario B'}</span></div>
          </div>
        </div>
        <div id="cmp-chart"></div>
      </div>

      <div class="card">
        <div class="card-header"><div class="card-title-lg">Delta Analysis</div><span style="font-size:11px;color:var(--blue-mid)">B − A difference in percentage points</span></div>
        <div id="cmp-delta"></div>
      </div>
    </div>`;
}

function initComparison() {
  const pinned = appState.comparisonSet;
  if (pinned.length < 2) return;

  function updateCharts() {
    const idA = document.getElementById('cmp-scen-a')?.value || pinned[0];
    const idB = document.getElementById('cmp-scen-b')?.value || pinned[1];
    const resA = MOCK.results[idA] || MOCK.results['scen-001'];
    const resB = MOCK.results[idB] || MOCK.results['scen-002'];
    const scA = appState.scenarios.get(idA);
    const scB = appState.scenarios.get(idB);
    const mode = document.querySelector('#cmp-mode .mode-btn.active')?.dataset.mode || 'side-by-side';

    const cmpChart = document.getElementById('cmp-chart');
    const cmpDelta = document.getElementById('cmp-delta');

    if (mode === 'waterfall') {
      if (cmpChart) charts.waterfall(cmpChart, [
        { ...resA, name: scA?.name || 'Scenario A' },
        { ...resB, name: scB?.name || 'Scenario B' }
      ]);
      if (cmpDelta) cmpDelta.innerHTML = '<div style="color:var(--blue-mid);font-size:12px;padding:10px">Waterfall mode — see chart above for delta breakdown</div>';
    } else {
      const aChannels = resA.team_summary.map(t => ({ channel: t.team, team: t.team, pct: t.pct }));
      const bChannels = resB.team_summary.map(t => ({ channel: t.team, team: t.team, pct: t.pct }));
      const scAData = { channels: aChannels, scenario_name: scA?.name || 'Scenario A' };
      const scBData = { channels: bChannels, scenario_name: scB?.name || 'Scenario B' };

      if (cmpChart) {
        if (mode === 'side-by-side') charts.comparisonBars(cmpChart, scAData, scBData, 'side-by-side');
      }
      if (cmpDelta) charts.comparisonBars(cmpDelta, scAData, scBData, 'delta');
    }
  }

  document.querySelectorAll('#cmp-mode .mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#cmp-mode .mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateCharts();
    });
  });

  ['cmp-scen-a', 'cmp-scen-b'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', updateCharts);
  });

  setTimeout(updateCharts, 50);
}

// ── SCREEN 9: EXPORT ──
function renderExport() {
  const sections = [
    { id: 'cover', name: 'Cover Page', desc: 'UTC logo, title, analyst name, date, confidentiality', checked: true },
    { id: 'summary', name: 'Executive Summary', desc: 'Auto-generated 3-bullet insight narrative', checked: true },
    { id: 'dataqual', name: 'Data Quality Summary', desc: 'Completeness score, date range, null highlights', checked: true },
    { id: 'config', name: 'Scenario Configuration', desc: 'Parameters table per scenario', checked: true },
    { id: 'kpis', name: 'Universe KPIs', desc: '6 marketing KPI cards from HCP360', checked: true },
    { id: 'team', name: 'Team Attribution', desc: 'Donut chart + attribution data table', checked: true },
    { id: 'channels', name: 'Channel Attribution', desc: 'Bar table with inline bars, all channels', checked: true },
    { id: 'heatmap', name: 'Segment Heatmap', desc: 'Channel × segment attribution matrix', checked: true },
    { id: 'sankey', name: 'Sankey Flow Diagram', desc: 'Full marketing touchpoint flow chart', checked: true },
    { id: 'journey', name: 'HCP Journey Chart', desc: 'Segment movement & timeline chart', checked: true },
    { id: 'compare', name: 'Scenario Comparison', desc: 'Delta analysis & grouped bar chart', checked: false },
    { id: 'appendix', name: 'Data Appendix', desc: 'Full 73-column raw results (large)', checked: false }
  ];

  return `
    <div class="slide-up">
      <div class="page-header">
        <div class="page-header-left">
          <h1>Export Executive Report</h1>
          <p style="font-size:13px;color:var(--blue-mid);margin-top:4px">Build a customisable PDF or Excel report for stakeholders</p>
        </div>
      </div>
      <div class="grid-2-1" style="align-items:start">
        <div>
          <div class="card" style="margin-bottom:14px">
            <div class="section-heading">Report Identity</div>
            <div class="form-group">
              <label class="form-label">Report Title</label>
              <input type="text" class="form-input" id="exp-title" value="UTC Channel Attribution — Q4 2025 Analysis">
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Prepared For</label>
                <input type="text" class="form-input" value="Commercial Strategy Team">
              </div>
              <div class="form-group">
                <label class="form-label">Prepared By</label>
                <input type="text" class="form-input" value="${MOCK.user.name}">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Date</label>
                <input type="date" class="form-input" value="2026-04-03">
              </div>
              <div class="form-group">
                <label class="form-label">Confidentiality</label>
                <select class="form-input">
                  <option>Internal</option>
                  <option selected>Confidential</option>
                  <option>Restricted</option>
                </select>
              </div>
            </div>
          </div>

          <div class="card" style="margin-bottom:14px">
            <div class="section-heading">Scenario Selection</div>
            <div style="display:flex;gap:10px;margin-bottom:12px">
              <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px">
                <input type="radio" name="exp-mode" value="single"> Single Scenario
              </label>
              <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px">
                <input type="radio" name="exp-mode" value="comparison" checked> Comparison Report
              </label>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px" id="exp-scenarios">
              ${appState.comparisonSet.map(id => {
    const sc = appState.scenarios.get(id);
    return sc ? `<span class="meta-pill product" style="display:flex;align-items:center;gap:5px">${sc.name} <span onclick="this.parentElement.remove()" style="cursor:pointer;opacity:0.6;hover:opacity:1">×</span></span>` : '';
  }).join('')}
            </div>
          </div>

          <div class="card" style="margin-bottom:14px">
            <div class="section-heading">Content Sections</div>
            <div class="export-section-list" id="exp-sections">
              ${sections.map(s => `<div class="export-section-item ${s.checked ? 'checked' : ''}" data-section="${s.id}">
                <div class="export-checkbox"><span class="export-checkbox-check">✓</span></div>
                <div style="flex:1">
                  <div class="export-section-name">${s.name}</div>
                  <div class="export-section-desc">${s.desc}</div>
                </div>
              </div>`).join('')}
            </div>
          </div>

          <div class="card" style="margin-bottom:14px">
            <div class="section-heading">Format</div>
            <div class="mode-toggle" id="exp-format" style="display:inline-flex">
              <button class="mode-btn active" data-fmt="pdf">PDF Report</button>
              <button class="mode-btn" data-fmt="excel">Excel Workbook</button>
              <button class="mode-btn" data-fmt="both">Both</button>
            </div>
            <div style="margin-top:10px;display:flex;gap:8px">
              <div class="mode-toggle">
                <button class="mode-btn active">A4</button>
                <button class="mode-btn">Letter</button>
              </div>
              <div class="mode-toggle">
                <button class="mode-btn active">Branded</button>
                <button class="mode-btn">B&W Print</button>
              </div>
            </div>
          </div>

          <div id="exp-result" style="margin-bottom:14px"></div>
          <button class="btn btn-primary btn-full btn-xl" id="exp-generate-btn">Generate Report</button>
        </div>

        <div>
          <div class="card" style="position:sticky;top:0">
            <div class="card-header">
              <div class="card-title-lg">Live Preview</div>
              <span style="font-size:11px;color:var(--blue-mid)" id="exp-pagecount">~10 pages</span>
            </div>
            <div class="preview-pages" id="exp-preview">
              <div class="preview-page" style="padding:0;overflow:hidden">
                <div class="preview-page-cover">
                  <div style="width:24px;height:24px;background:var(--amber);border-radius:4px;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--truffle)">UTC</div>
                  <div class="preview-page-title" id="exp-preview-title">UTC Channel Attribution — Q4 2025 Analysis</div>
                  <div class="preview-page-subtitle">Prepared by ${MOCK.user.name} · Apr 03, 2026</div>
                  <div class="preview-page-subtitle" style="margin-top:4px">CONFIDENTIAL</div>
                </div>
              </div>
              <div class="preview-page">
                <div style="height:8px;background:var(--amber);border-radius:2px;width:60%;margin-bottom:6px"></div>
                <div style="height:4px;background:var(--sand);border-radius:2px;width:90%;margin-bottom:3px"></div>
                <div style="height:4px;background:var(--sand);border-radius:2px;width:75%;margin-bottom:8px"></div>
                <div style="display:flex;gap:4px;margin-bottom:6px">
                  ${[59, 17, 10, 5, 5, 3].map(v => `<div style="flex:${v};height:20px;background:var(--amber);border-radius:2px;opacity:${0.4 + v / 100}"></div>`).join('')}
                </div>
                <div style="height:4px;background:var(--sand);border-radius:2px;width:85%"></div>
              </div>
              <div class="preview-page">
                <div style="height:6px;background:var(--blue);border-radius:2px;width:40%;margin-bottom:6px"></div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:6px">
                  ${[1, 2, 3, 4].map(_ => `<div style="height:14px;background:var(--palladian);border:1px solid var(--sand);border-radius:2px"></div>`).join('')}
                </div>
                <div style="height:4px;background:var(--sand);border-radius:2px;width:100%;margin-bottom:2px"></div>
                <div style="height:4px;background:var(--sand);border-radius:2px;width:80%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

function initExport() {
  document.querySelectorAll('.export-section-item').forEach(item => {
    item.addEventListener('click', () => {
      item.classList.toggle('checked');
      updatePageCount();
    });
  });

  document.querySelectorAll('#exp-format .mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#exp-format .mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  document.getElementById('exp-title')?.addEventListener('input', (e) => {
    document.getElementById('exp-preview-title').textContent = e.target.value;
  });

  document.getElementById('exp-generate-btn')?.addEventListener('click', () => {
    const btn = document.getElementById('exp-generate-btn');
    btn.innerHTML = '<span style="display:inline-block;width:16px;height:16px;border:2px solid rgba(27,38,50,0.2);border-top-color:var(--truffle);border-radius:50%;animation:spin 0.6s linear infinite;vertical-align:middle;margin-right:6px"></span>Building your report…';
    btn.disabled = true;

    setTimeout(() => {
      btn.innerHTML = '▶ Generate Report';
      btn.disabled = false;
      document.getElementById('exp-result').innerHTML = `
        <div class="callout amber">
          <strong>✓ Report ready!</strong>
          <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
            <button class="btn btn-primary" onclick="toast.show('Downloading UTC_Attribution_Report_2026-04-03.pdf…','success')">⬇ Download PDF</button>
            <button class="btn btn-outline" onclick="toast.show('Downloading UTC_Attribution_Report_2026-04-03.xlsx…','success')">⬇ Download Excel</button>
          </div>
        </div>`;
      toast.show('Report generated successfully!', 'success');
    }, 2500);
  });

  updatePageCount();
}

function updatePageCount() {
  const checked = document.querySelectorAll('.export-section-item.checked').length;
  const estimate = checked + 1;
  const pc = document.getElementById('exp-pagecount');
  if (pc) pc.textContent = `~${estimate} pages`;
}