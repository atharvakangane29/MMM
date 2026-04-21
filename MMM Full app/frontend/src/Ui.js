// js/ui.js — Toast, Router, Stepper, Sidebar, Running Drawer

// ── TOAST ──
const toast = {
  container: null,
  init() {
    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  },
  show(msg, type = 'success', duration = 3500) {
    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span class="toast-icon">${icons[type]||'•'}</span><span>${msg}</span>`;
    this.container.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(8px)';
      el.style.transition = '0.3s ease';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }
};

// ── ROUTER ──
const router = {
  screens: {},
  current: null,

  register(id, fn) { this.screens[id] = fn; },

  go(step) {
    const id = `screen-${step}`;
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;

    // Update body layout visibility
    document.getElementById('shell')?.classList.toggle('hidden', step === 1);

    if (this.current === id) return;
    this.current = id;

    mainContent.innerHTML = '';
    mainContent.classList.add('fade-in');
    setTimeout(() => mainContent.classList.remove('fade-in'), 300);

    const fn = this.screens[id];
    if (fn) {
      const content = fn();
      if (typeof content === 'string') {
        mainContent.innerHTML = content;
      } else if (content instanceof HTMLElement) {
        mainContent.appendChild(content);
      }
    }
  }
};

// ── STEPPER ──
const stepper = {
  steps: [
    { n:1, label:'Login' },
    { n:2, label:'Data Source' },
    { n:3, label:'Data Report' },
    { n:4, label:'Configure' },
    { n:5, label:'Schema & KPIs' },
    { n:6, label:'Dashboard' },
    { n:7, label:'Builder' },
    { n:8, label:'Compare' },
    { n:9, label:'Export' }
  ],

  render(currentStep) {
    const bar = document.getElementById('stepper-bar');
    if (!bar) return;
    bar.innerHTML = '';
    this.steps.forEach((s, i) => {
      const completed = s.n < currentStep;
      const active = s.n === currentStep;
      const locked = s.n >= 6 && !MOCK.scenarios.some(sc => sc.status === 'SUCCESS');

      const item = document.createElement('div');
      item.className = `step-item ${completed?'completed':''} ${active?'active':''} ${(!completed&&!active&&!locked)?'upcoming':''} ${locked&&!active?'locked':''}`;
      item.innerHTML = `
        <div class="step-inner">
          <div class="step-dot">${completed ? '✓' : s.n}</div>
          <span class="step-label">${s.label}</span>
        </div>
      `;
      if (!locked || completed || active) {
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
          if (s.n !== currentStep) {
            appState.setStep(s.n);
            this.render(s.n);
          }
        });
      }
      bar.appendChild(item);

      if (i < this.steps.length - 1) {
        const conn = document.createElement('div');
        conn.className = 'step-connector';
        bar.appendChild(conn);
      }
    });
  },

  update(step) { this.render(step); }
};

// ── SIDEBAR ──
const sidebar = {
  render() {
    const list = document.getElementById('sidebar-scenarios');
    if (!list) return;
    list.innerHTML = '';

    const scenarios = Array.from(appState.scenarios.values());
    if (!scenarios.length) {
      list.innerHTML = `<div class="empty-state" style="padding:24px 12px">
        <div class="empty-state-icon">📊</div>
        <div class="empty-state-title" style="font-size:13px">No scenarios yet</div>
        <div class="empty-state-desc" style="font-size:11px">Run your first attribution model to see results</div>
      </div>`;
      return;
    }

    scenarios.forEach(sc => {
      const card = document.createElement('div');
      card.className = `scenario-card ${appState.activeScenarioId === sc.id ? 'active' : ''}`;

      const productClass = sc.product.toLowerCase();
      const isPinned = appState.isPinned(sc.id);

      let statusBadge = `<span class="status-badge ${sc.status.toLowerCase()}">
        <span class="status-dot"></span>${sc.status}
      </span>`;

      let progressBar = '';
      if (sc.status === 'RUNNING') {
        progressBar = `<div class="progress-wrap" style="margin-top:6px">
          <div class="progress-fill" id="progress-${sc.id}" style="width:${sc.progress||30}%"></div>
        </div>`;
      }

      card.innerHTML = `
        <div class="scenario-card-header">
          <span class="scenario-product-pill ${productClass}">${sc.product}</span>
          <button class="pin-btn ${isPinned ? 'pinned' : ''}" data-id="${sc.id}" title="${isPinned ? 'Unpin from comparison' : 'Pin for comparison'}">
            ${isPinned ? '📌' : '📌'}
          </button>
        </div>
        <div class="scenario-name" style="margin-top:4px">${sc.name}</div>
        <div class="scenario-meta">${sc.level} · ${sc.segment} · ${sc.start} – ${sc.end}</div>
        ${progressBar}
        <div class="scenario-footer">
          ${statusBadge}
          <span style="font-size:9px;color:var(--oatmeal)">${sc.created.split('·')[0].trim()}</span>
        </div>`;

      card.addEventListener('click', (e) => {
        if (e.target.closest('.pin-btn')) return;
        appState.activeScenarioId = sc.id;
        if (sc.status === 'SUCCESS' && appState.currentStep >= 6) {
          router.go(6);
          stepper.update(6);
          appState.currentStep = 6;
        } else if (sc.status === 'SUCCESS') {
          appState.setStep(6);
        } else {
          appState.setStep(7);
        }
        this.render();
      });

      card.querySelector('.pin-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        appState.togglePin(sc.id);
        this.render();
        updateFooter();
      });

      list.appendChild(card);
    });
    updateFooter();
  }
};

function updateFooter() {
  const count = appState.comparisonSet.length;
  const hint = document.getElementById('comparison-hint');
  if (hint) {
    if (count >= 2) {
      hint.innerHTML = `<strong style="color:var(--amber)">${count}</strong> scenarios pinned · <a onclick="appState.setStep(8);stepper.update(8)">Compare →</a>`;
    } else if (count === 1) {
      hint.textContent = '1 scenario pinned — pin 1 more to compare';
    } else {
      hint.textContent = 'Pin scenarios to compare side-by-side';
    }
  }
}

// ── RUNNING DRAWER ──
const runningDrawer = {
  show(name, progress = 0, elapsed = '00:00', message = 'Queued...') {
    const d = document.getElementById('running-drawer');
    if (!d) return;
    d.querySelector('#drawer-scenario-name').textContent = name;
    d.querySelector('#drawer-message').textContent = message;
    d.querySelector('#drawer-elapsed').textContent = `Elapsed: ${elapsed}`;
    d.querySelector('#drawer-progress').style.width = progress + '%';
    d.classList.add('visible');
  },
  hide() {
    const d = document.getElementById('running-drawer');
    if (d) d.classList.remove('visible');
  },
  update(progress, message, elapsed) {
    const d = document.getElementById('running-drawer');
    if (!d) return;
    d.querySelector('#drawer-progress').style.width = progress + '%';
    d.querySelector('#drawer-message').textContent = message;
    d.querySelector('#drawer-elapsed').textContent = `Elapsed: ${elapsed}`;
  }
};

// ── SIMULATE JOB ──
function simulateJob(scenario, onComplete) {
  let progress = 0;
  let elapsed = 0;
  const messages = [
    'Loading HCP universe table...',
    'Building longitudinal journey sequences...',
    'Computing Markov transition matrices...',
    'Applying removal effect algorithm...',
    'Normalising attribution percentages...',
    'Computing segment breakdowns...',
    'Writing results to Delta Lake...',
    'Finalising output...'
  ];

  runningDrawer.show(scenario.name, 0, '00:00', messages[0]);

  const interval = setInterval(() => {
    elapsed += 5;
    progress += Math.random() * 15 + 5;
    if (progress > 98) progress = 99;

    const msgIdx = Math.min(Math.floor(progress / 13), messages.length - 1);
    const mins = Math.floor(elapsed / 60).toString().padStart(2,'0');
    const secs = (elapsed % 60).toString().padStart(2,'0');
    runningDrawer.update(progress, messages[msgIdx], `${mins}:${secs}`);

    // Update scenario card progress
    const fill = document.getElementById(`progress-${scenario.id}`);
    if (fill) fill.style.width = progress + '%';

    if (progress >= 99) {
      clearInterval(interval);
      setTimeout(() => {
        runningDrawer.hide();
        scenario.status = 'SUCCESS';
        scenario.completed = new Date().toLocaleDateString('en-US', { month:'short', day:'2-digit', year:'numeric' }) + ' · ' + new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit' });

        // Add mock results
        if (!MOCK.results[scenario.id]) {
          MOCK.results[scenario.id] = { ...MOCK.results['scen-001'] };
        }

        appState.scenarios.set(scenario.id, scenario);
        sidebar.render();
        toast.show(`"${scenario.name}" completed! Results ready.`, 'success');
        onComplete && onComplete(scenario);
      }, 800);
    }
  }, 400);

  appState.pollingTimers.set(scenario.id, interval);
}