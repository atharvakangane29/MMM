# FRONTEND_GUIDE.md — Component Map & Implementation Guide

## UTC Channel Attribution MMM Platform

**Stack:** Vanilla JS · Tailwind CSS · ApexCharts · Chart.js · jsPDF · SheetJS

---

## 1. Page Map (9-Step Flow)

```
Step 1  /login                  — Authentication
Step 2  /setup/data-source      — Databricks catalog + table selection
Step 3  /setup/data-report      — Automated data quality report
Step 4  /setup/configure        — Hyperparameter config + scenario naming
Step 5  /setup/schema           — Data schema explorer + marketing KPIs
Step 6  /dashboard              — Results: KPI cards + Sankey + HCP Journey
Step 7  /scenarios              — Multi-scenario builder + management
Step 8  /compare                — Scenario comparison engine
Step 9  /export                 — Executive report builder + download
```

See `USER_FLOW.md` for the full specification of every screen and state.

---

## 2. Global State Manager (`js/state.js`)

The app has **no framework**. All shared data lives in a single `appState` object that persists across all 9 steps.

```javascript
// js/state.js
const appState = {
  // Step 1 — Auth
  user: null,                   // { name, email, role, token }

  // Step 2 — Data connection
  connection: {
    catalog: null,              // e.g. "hive_metastore"
    schema: null,               // e.g. "utc_attribution"
    resultsTable: null,         // e.g. "mmm_scenario_results"
    hcpTable: null              // e.g. "hcp360_universe"
  },

  // Step 3 — Data report
  dataReport: null,             // full report object from /data/report

  // Step 4 — Current scenario being configured
  pendingScenario: null,        // params before job is submitted

  // Steps 5–9 — Core data
  scenarios: new Map(),         // scenario_id → full result object
  scenarioMeta: new Map(),      // scenario_id → { name, status, params, created_at }
  activeScenarioId: null,       // currently displayed scenario

  // Step 8 — Comparison
  comparisonSet: [],            // array of scenario_ids (max 4)
  comparisonDimension: 'team',  // 'team' | 'channel' | 'touchpoint'
  comparisonSegment: 'all_hcps',
  comparisonMetric: 'attribution_pct', // 'attribution_pct' | 'hcp_count' | 'touchpoints' | etc.

  // Step 9 — Export options
  exportOptions: {
    title: 'UTC Channel Attribution Report',
    preparedBy: '',
    confidentiality: 'Confidential',
    format: 'pdf',
    sections: {}
  },

  // Polling
  pollingTimers: new Map(),     // scenario_id → setInterval ID

  // Navigation
  currentStep: 1,

  // Methods
  setUser(user) { this.user = user; saveToSession('user', user); },
  setConnection(conn) { this.connection = conn; },
  setDataReport(report) { this.dataReport = report; },
  setActiveScenario(id) { this.activeScenarioId = id; this.renderDashboard(); },

  addScenarioResult(id, data) {
    this.scenarios.set(id, data);
    this.renderDashboard();
    this.updateComparisonIfPinned(id);
  },

  pinToCompare(id) {
    if (this.comparisonSet.length >= 4) return;
    if (!this.comparisonSet.includes(id)) {
      this.comparisonSet.push(id);
      this.renderComparison();
    }
  },

  unpinFromCompare(id) {
    this.comparisonSet = this.comparisonSet.filter(s => s !== id);
    this.renderComparison();
  },

  startPolling(scenarioId) {
    const timer = setInterval(() => polling.checkStatus(scenarioId), 5000);
    this.pollingTimers.set(scenarioId, timer);
  },

  stopPolling(scenarioId) {
    clearInterval(this.pollingTimers.get(scenarioId));
    this.pollingTimers.delete(scenarioId);
  },

  renderDashboard() { /* triggers charts.js + sankey.js refresh */ },
  renderComparison() { /* triggers comparison.js refresh */ },

  navigate(step) {
    this.currentStep = step;
    router.go(step);
  }
};
```

---

## 3. API Client (`js/api.js`)

Thin wrappers around `fetch()` for all backend endpoints.

```javascript
// js/api.js
const BASE_URL = '/api/v1';

const api = {
  async runScenario(params) {
    const res = await fetch(`${BASE_URL}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  },

  async getStatus(scenarioId) {
    const res = await fetch(`${BASE_URL}/scenarios/${scenarioId}/status`);
    return res.json();
  },

  async getResults(scenarioId) {
    const res = await fetch(`${BASE_URL}/scenarios/${scenarioId}/results`);
    if (!res.ok) throw await res.json();
    return res.json();
  },

  async listScenarios(page = 1, filters = {}) {
    const params = new URLSearchParams({ page, ...filters });
    const res = await fetch(`${BASE_URL}/scenarios?${params}`);
    return res.json();
  },

  async compareScenarios(scenarioIds, dimension = 'team', segment = 'all_hcps') {
    const res = await fetch(`${BASE_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_ids: scenarioIds,
        comparison_dimension: dimension,
        hcp_segment_filter: segment
      })
    });
    return res.json();
  },

  getExportUrl(scenarioId, format = 'csv') {
    return `${BASE_URL}/export/${scenarioId}?format=${format}`;
  }
};
```

---

## 4. Polling Logic (`js/polling.js`)

```javascript
// js/polling.js
const polling = {
  async checkStatus(scenarioId) {
    const { status, progress_pct, message } = await api.getStatus(scenarioId);

    // Update progress bar
    const bar = document.querySelector(`#progress-${scenarioId}`);
    if (bar) {
      bar.style.width = `${progress_pct}%`;
      bar.setAttribute('aria-valuenow', progress_pct);
    }

    const label = document.querySelector(`#status-label-${scenarioId}`);
    if (label) label.textContent = message || status;

    if (status === 'SUCCESS') {
      appState.stopPolling(scenarioId);
      const results = await api.getResults(scenarioId);
      appState.addScenarioResult(scenarioId, results);
      showToast(`Scenario "${results.scenario_name}" is ready!`, 'success');
    }

    if (status === 'FAILED') {
      appState.stopPolling(scenarioId);
      showToast(`Scenario run failed: ${message}`, 'error');
    }
  }
};
```

---

## 5. Scenario Builder Page (`pages/scenario-builder.html`)

### Form Fields

| Field | HTML Element | Values |
|---|---|---|
| Scenario Name | `<input type="text">` | Free text |
| Product | `<select>` | TYVASO, REMODULIN, ORENITRAM, TREPROSTINIL, ALL |
| Start Date | `<input type="date">` | Min: 2020-01-01 |
| End Date | `<input type="date">` | Must be > start_date |
| Attribution Level | `<radio group>` | Touchpoint / Channel / Team |
| HCP Segment | `<radio group>` | Cluster / LOB / Competitor Drug / All HCPs |
| Notes | `<textarea>` | Optional |

### Submission Flow

```javascript
document.getElementById('run-btn').addEventListener('click', async () => {
  const params = {
    scenario_name: document.getElementById('scenario-name').value,
    product: document.getElementById('product').value,
    start_date: document.getElementById('start-date').value,
    end_date: document.getElementById('end-date').value,
    attribution_level: document.querySelector('[name="attribution-level"]:checked').value,
    hcp_segment: document.querySelector('[name="hcp-segment"]:checked').value,
    notes: document.getElementById('notes').value
  };

  try {
    const { scenario_id, scenario_name } = await api.runScenario(params);
    appState.scenarioMeta.set(scenario_id, { name: scenario_name, status: 'QUEUED' });
    addScenarioToSidebar(scenario_id, scenario_name);
    showProgressBar(scenario_id);
    appState.startPolling(scenario_id);
  } catch (err) {
    showToast(err.error?.message || 'Failed to start run.', 'error');
  }
});
```

---

## 6. KPI Dashboard (`pages/dashboard.html`)

Rendered when a scenario reaches SUCCESS state.

### KPI Cards (top row)

Four summary stat cards:

| KPI | Source Field | Format |
|---|---|---|
| Total HCPs in Universe | `summary_kpis.total_hcps_in_universe` | Number with comma |
| Total Referrals | `summary_kpis.total_referrals` | Number with comma |
| Total Touchpoints | `summary_kpis.total_touchpoints` | Number with comma |
| Total Prescribers | `summary_kpis.total_prescribers` | Number with comma |

### Team Attribution Donut (ApexCharts)

```javascript
// Donut chart — team-level attribution
function renderTeamDonut(teamSummary) {
  const options = {
    chart: { type: 'donut', height: 350 },
    series: Object.values(teamSummary).map(t => Math.round(t.attribution_pct * 100)),
    labels: Object.keys(teamSummary),
    colors: ['#2563EB','#7C3AED','#059669','#D97706','#DC2626','#6B7280'],
    legend: { position: 'bottom' },
    plotOptions: {
      pie: { donut: { labels: { show: true, total: { show: true, label: 'Attribution' } } } }
    }
  };
  new ApexCharts(document.querySelector('#team-donut'), options).render();
}
```

### Channel Attribution Bar Table

A hybrid component: a sortable HTML table with an inline horizontal bar in each row showing the attribution percentage. Columns:

| Column | Description |
|---|---|
| Channel | Channel/touchpoint name |
| Attribution % | Horizontal bar + number |
| HCPs Reached | Count |
| Touchpoints | Count |
| Prescribers | Count |
| Efficiency | `touchpoints_to_prescribers / touchpoints` ratio |

Sortable by clicking column headers (vanilla JS sort on the `channel_attribution` array).

### Segment Heatmap (Chart.js)

A matrix chart showing attribution % per (channel × segment):
- **X axis**: HCP segments (High Performer → Unresponsive)
- **Y axis**: Channels
- **Cell color**: Blue gradient (light = low %, dark = high %)

```javascript
function renderSegmentHeatmap(channelAttribution) {
  const segments = [
    'high_performer','moderate_performer','average_performer',
    'low_performer','near_sleeping','sleeping','unresponsive'
  ];
  const channels = channelAttribution.map(c => c.channel);
  const data = [];

  channelAttribution.forEach((ch, y) => {
    segments.forEach((seg, x) => {
      data.push({ x, y, v: ch.attribution_pct[seg] || 0 });
    });
  });

  // Render as Chart.js matrix plugin or custom canvas draw
}
```

---

## 7. Sankey Chart — Marketing Flow (`js/sankey.js`)

**Library:** D3.js with `d3-sankey` plugin (or `Chart.js` with sankey plugin)  
**Location:** Step 6 Dashboard, Tab 2

### Node Structure

```
Left tier    Middle tier          Right tier         Terminal
─────────    ─────────────────    ──────────────     ────────────────
SALES        SALES_Live_Call   →  High Performer  →  Converted
MDD          SALES_Virtual     →  Moderate        →  Not Converted
MSL          MDD_Live_Call     →  Average
RNS          MDD_Phone_Email   →  Low Performer
SPK PGM      MSL_Live_Call     →  Near Sleeping
EMAIL        Speaker_Prog_Live →  Sleeping
             Email_Clicked     →  Unresponsive
```

When attribution level = Team, the middle tier is collapsed — left and right tiers connect directly.

### Color Assignment

```javascript
// js/sankey.js
const NODE_COLORS = {
  // Source nodes (teams)
  'SALES':          '#FFB162',   // --amber
  'MDD':            '#2C3B4D',   // --blue
  'MSL':            '#4A6B8A',   // --blue-mid
  'RNS':            '#7FA3C0',   // --blue-lt
  'SPK PGM':        '#C9C1B1',   // --oatmeal
  'EMAIL':          '#D8D0C4',   // --sand

  // Segment nodes (right tier)
  'High Performer': '#FFB162',   // --amber (high value)
  'Moderate Performer': '#4A6B8A',
  'Average Performer':  '#7FA3C0',
  'Low Performer':      '#C9C1B1',
  'Near Sleeping':      '#D8D0C4',
  'Sleeping':           '#A35139', // --flame
  'Unresponsive':       '#1B2632', // --truffle

  // Terminal
  'Converted':      '#FFB162',
  'Not Converted':  '#C9C1B1'
};

// Link opacity
const LINK_OPACITY = 0.45; // fills are semi-transparent, colored by source
```

### Tooltip on hover

```javascript
// On link hover:
tooltip.html(`
  <strong>${link.source.name} → ${link.target.name}</strong><br/>
  Attribution: ${(link.value * 100).toFixed(1)}%<br/>
  HCPs Reached: ${link.hcp_count.toLocaleString()}<br/>
  Touchpoints: ${link.touchpoints.toLocaleString()}
`);
```

### Filter/View toggles

```javascript
// Above chart — toggle what link WIDTH represents:
const VIEW_MODES = {
  'attribution_pct': 'Attribution %',
  'referral_volume': 'Referral Volume',
  'touchpoints':     'Total Touchpoints'
};
```

---

## 8. HCP Journey Chart — Vertical Movement (`js/sankey.js`)

**Purpose:** Show HCP migration between performance tiers over time.  
**Chart type:** Time-series alluvial / bump chart (D3.js)  
**Location:** Step 6 Dashboard, Tab 3

### Layout

```
Y axis (tiers, top = best):     Time →   Q1 2023   Q2 2023   Q3 2023 … Q4 2025
────────────────────────────────────────────────────────────────────────────────
High Performer           ████ ─── ████████ ─────────── ██████████
Moderate Performer      ██████── ████─────────────────── ████████
Average Performer       ██████─────── ████──────────────── ████
Low Performer            ████─────────────── ████──────── ████
Near Sleeping            ████──────────────────── ████───
Sleeping                 ████──────────────────────────── ██
Unresponsive             ████───────────────────────────────── ██
```

- **Band width** = number of HCPs in that tier at that time period
- **Upward flows** (tier improving): `--blue-lt` tinted arrows/curves
- **Downward flows** (tier degrading): `--flame` tinted curves

### Data structure expected

```javascript
// From API results
const journeyData = {
  time_periods: ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', ...],
  segments: ['High Performer', 'Moderate', 'Average', 'Low', 'Near Sleeping', 'Sleeping', 'Unresponsive'],
  counts: {
    // segment → array of counts per time period
    'High Performer': [512, 525, 540, 559, ...],
    'Moderate Performer': [198, 205, 215, 226, ...],
    // ...
  },
  flows: [
    // transitions between periods
    { from: 'Low Performer', to: 'Average Performer', period: '2023-Q2→Q3', count: 23, primary_channel: 'SALES_Live_Call' },
    // ...
  ]
};
```

### Summary Table below chart

```javascript
// Rendered below the chart — net movement per segment
function renderJourneySummary(journeyData) {
  const columns = ['Segment', 'Start Count', 'End Count', 'Net Change', 'Direction', 'Primary Channel'];
  // Direction: amber ▲ for positive, flame ▼ for negative, neutral — for flat
}
```

---

## 9. Comparison Engine (`pages/comparison.html`, `js/comparison.js`)

### Pinning Scenarios

Each row in the sidebar scenario list has a **pin button** (📌). Clicking it calls `appState.pinToCompare(id)`.

Up to 4 scenarios can be pinned simultaneously.

### Comparison View Modes

Toggle between:
- **Side-by-Side** — grouped bar chart (channels on X, bars per scenario)
- **Overlay** — area/line chart with shaded areas per scenario
- **Delta View** — shows only the difference between two selected scenarios

### Grouped Bar Chart (ApexCharts)

```javascript
function renderComparisonChart(compareData, mode = 'side-by-side') {
  const channels = compareData.scenarios[0].channels.map(c => c.channel);

  const series = compareData.scenarios.map(scenario => ({
    name: scenario.scenario_name,
    data: scenario.channels.map(c => Math.round(c.attribution_pct * 100))
  }));

  const options = {
    chart: { type: mode === 'overlay' ? 'area' : 'bar', height: 400 },
    series,
    xaxis: { categories: channels },
    yaxis: { title: { text: 'Attribution %' }, max: 100 },
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth' },
    fill: { opacity: mode === 'overlay' ? 0.4 : 1 },
    legend: { position: 'top' },
    colors: ['#2563EB','#DC2626','#059669','#D97706']
  };

  new ApexCharts(document.querySelector('#comparison-chart'), options).render();
}
```

### Delta Table

When exactly 2 scenarios are compared, shows a delta table:

| Channel | Scenario A | Scenario B | Δ Absolute | Δ Relative |
|---|---|---|---|---|
| SALES_Live_Call | 41% | 31% | +10pp | +32% |
| MDD_Live_Call | 10% | 16% | -6pp | -38% |

Rows coloured green (positive delta for A) or red (negative delta for A).

---

### Waterfall Chart (new in Step 8)

Shows budget/attribution decomposition. Library: ApexCharts `bar` chart in waterfall mode.

```javascript
function renderWaterfallChart(compareData) {
  // Series: [Total, -SALES, -MDD, -MSL, -RNS, -SPK PGM, -EMAIL, =Residual]
  const options = {
    chart: { type: 'bar' },
    plotOptions: { bar: { columnWidth: '60%' } },
    colors: [
      ({ value }) => value >= 0 ? 'var(--amber)' : 'var(--flame)'
    ],
    xaxis: { categories: ['Total', 'SALES', 'MDD', 'MSL', 'RNS', 'SPK PGM', 'EMAIL'] }
  };
}
```

### Metric toggle

Switch what all comparison charts display:

```javascript
const METRIC_OPTIONS = [
  { value: 'attribution_pct',            label: 'Attribution %' },
  { value: 'hcp_count',                  label: 'HCPs Reached' },
  { value: 'touchpoints',                label: 'Total Touchpoints' },
  { value: 'prescribers',                label: 'Prescribers' },
  { value: 'touchpoints_per_prescriber', label: 'Touchpoints / Prescriber' }
];
```

---

## 10. Export Builder (`pages/export.html`, `js/export.js`)

The export builder (Step 9) is a **dedicated full-page UI**, not just a button. It uses a two-panel layout:

**Left panel — options form:**

```html
<!-- Report Identity -->
<input id="report-title" value="UTC Channel Attribution Report" />
<input id="prepared-by" placeholder="Your name" />
<input type="date" id="report-date" />
<select id="confidentiality">
  <option>Internal</option>
  <option selected>Confidential</option>
  <option>Restricted</option>
</select>

<!-- Section checkboxes -->
<label><input type="checkbox" checked id="sec-exec-summary" /> Executive Summary</label>
<label><input type="checkbox" checked id="sec-data-quality" /> Data Quality Summary</label>
<label><input type="checkbox" checked id="sec-kpis" /> KPI Summary</label>
<label><input type="checkbox" checked id="sec-sankey" /> Sankey Chart</label>
<label><input type="checkbox" checked id="sec-journey" /> HCP Journey Chart</label>
<label><input type="checkbox" checked id="sec-comparison" /> Scenario Comparison</label>
<label><input type="checkbox" id="sec-raw-data" /> Raw Data Appendix</label>

<!-- Format -->
<div class="toggle-group">
  <button class="active">PDF</button>
  <button>Excel</button>
  <button>Both</button>
</div>
```

**Right panel — live preview:**

```javascript
// js/export.js
function updatePreview() {
  // Collect checked sections
  const sections = [...document.querySelectorAll('[id^="sec-"]:checked')]
    .map(el => el.id.replace('sec-', ''));

  // Estimate page count
  const PAGE_WEIGHTS = {
    'exec-summary': 0.5, 'data-quality': 1, 'kpis': 1,
    'sankey': 1, 'journey': 1, 'comparison': 1, 'raw-data': 3
  };
  const estimated = sections.reduce((acc, s) => acc + (PAGE_WEIGHTS[s] || 1), 1);
  document.getElementById('page-count').textContent = `~${Math.ceil(estimated)} pages`;
}

async function downloadReport() {
  const payload = buildExportPayload();   // collects all form state
  const response = await api.exportReport(payload);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `UTC_Attribution_Report_${today()}.pdf`;
  a.click();
}
```

**PDF structure (generated server-side via FastAPI + WeasyPrint or ReportLab):**

```
Page 1  — Cover:          UTC logo, report title, scenario names, date, confidentiality
Page 2  — Data Quality:   Overview KPIs, completeness score, date range summary
Page 3  — Data Universe:  Marketing KPIs, team/channel coverage map
Page 4  — KPI Dashboard:  4 stat cards, team donut, channel attribution table
Page 5  — Sankey Chart:   Full-width flow diagram + 3 insight callouts
Page 6  — HCP Journey:    Vertical movement chart + summary table
Page 7  — Comparison:     Grouped bar chart, waterfall, delta table (if 2+ scenarios)
Page N  — Appendix:       Raw 73-column data table (if selected, large)
```

---

## 11. Step Progress Stepper (`js/stepper.js`)

Shown at the top of all setup screens (Steps 1–5). Horizontal step indicator.

```html
<nav class="stepper">
  <div class="step completed">
    <span class="step-dot">✓</span>
    <span class="step-label">Login</span>
  </div>
  <div class="step active">
    <span class="step-dot">2</span>
    <span class="step-label">Data Source</span>
  </div>
  <div class="step upcoming">
    <span class="step-dot">3</span>
    <span class="step-label">Data Report</span>
  </div>
  <!-- steps 4, 5 ... -->
</nav>
```

```css
.step-dot {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.step.completed .step-dot { background: var(--amber); color: var(--truffle); }
.step.active .step-dot    { background: var(--blue);  color: white; }
.step.upcoming .step-dot  { background: var(--oatmeal); color: var(--blue-mid); }
.step-label { font-size: 11px; color: var(--blue-mid); margin-top: 4px; }
.step.active .step-label  { color: var(--blue); font-weight: 600; }
.step-connector { flex: 1; height: 2px; background: var(--sand); margin: 0 4px; align-self: center; }
```

---

## 12. Design System & Color Palette

### CSS Custom Properties (define in `:root`)

```css
:root {
  --palladian: #EEE9DF;   /* page background, screen backgrounds */
  --oatmeal:   #C9C1B1;   /* borders, dividers, inactive elements */
  --blue:      #2C3B4D;   /* primary text, table text, strong UI elements */
  --truffle:   #1B2632;   /* header background, dark surfaces, critical text */
  --amber:     #FFB162;   /* primary action colour, selected state, highlights */
  --flame:     #A35139;   /* critical/error state, high-severity anomalies */
  --blue-mid:  #4A6B8A;   /* secondary text, labels, axes */
  --blue-lt:   #7FA3C0;   /* low-severity indicators, chart lines */
  --sand:      #D8D0C4;   /* table borders, card dividers */
  --card:      #F7F4EF;   /* card backgrounds, inputs */
}
```

### Token Usage Map

| Token | Hex | Used For |
|---|---|---|
| `--palladian` | `#EEE9DF` | `<body>` background, full-page backgrounds |
| `--card` | `#F7F4EF` | KPI cards, form inputs, sidebar panels |
| `--truffle` | `#1B2632` | Top navbar, dark header bar |
| `--blue` | `#2C3B4D` | Primary body text, table content, headings |
| `--blue-mid` | `#4A6B8A` | Labels, axis text, secondary metadata |
| `--blue-lt` | `#7FA3C0` | Chart lines, low-severity badges, inactive tabs |
| `--oatmeal` | `#C9C1B1` | Borders, dividers, inactive sidebar items |
| `--sand` | `#D8D0C4` | Table row borders, card section dividers |
| `--amber` | `#FFB162` | Primary CTA button, selected pills, highlights |
| `--flame` | `#A35139` | Error states, FAILED badge, negative delta |

### Chart Color Assignments

```javascript
// charts.js — consistent channel/team color mapping
const TEAM_COLORS = {
  'SALES':   '#FFB162',   // amber  — highest share, dominant
  'MDD':     '#2C3B4D',   // blue   — second tier
  'MSL':     '#4A6B8A',   // blue-mid
  'RNS':     '#7FA3C0',   // blue-lt
  'SPK PGM': '#C9C1B1',   // oatmeal
  'EMAIL':   '#D8D0C4',   // sand
};

const STATUS_COLORS = {
  SUCCESS: '#FFB162',   // amber
  RUNNING: '#4A6B8A',   // blue-mid
  QUEUED:  '#C9C1B1',   // oatmeal
  FAILED:  '#A35139',   // flame
};

const SEGMENT_HEATMAP = {
  // Blue gradient from palladian (low) → truffle (high)
  low:    '#EEE9DF',
  mid:    '#7FA3C0',
  high:   '#1B2632',
};
```

### Component Styles

**App shell / Navbar**
```css
.navbar {
  background: var(--truffle);
  color: #fff;
  border-bottom: 1px solid var(--blue);
}
```

**Sidebar**
```css
.sidebar {
  background: var(--card);
  border-right: 1px solid var(--sand);
}
.sidebar-item.active {
  background: var(--amber);
  color: var(--truffle);
  font-weight: 600;
}
.sidebar-item:hover {
  background: var(--oatmeal);
}
```

**KPI Card**
```html
<div style="background: var(--card);
            border: 1px solid var(--sand);
            border-radius: 12px;
            padding: 1.5rem;">
  <p style="color: var(--blue-mid); font-size: 0.75rem; text-transform: uppercase;">
    Total Referrals
  </p>
  <p style="color: var(--blue); font-size: 2rem; font-weight: 700;">
    11,138
  </p>
</div>
```

**Primary Button (Run Scenario)**
```html
<button style="background: var(--amber);
               color: var(--truffle);
               border: none;
               border-radius: 8px;
               padding: 0.6rem 1.5rem;
               font-weight: 600;
               cursor: pointer;">
  Run Attribution
</button>
```

**Status Badge**
```html
<!-- SUCCESS -->
<span style="background: #FFF3E0; color: var(--amber);
             border: 1px solid var(--amber);
             padding: 2px 10px; border-radius: 999px; font-size: 0.75rem;">
  SUCCESS
</span>

<!-- FAILED -->
<span style="background: #F9EBE8; color: var(--flame);
             border: 1px solid var(--flame);
             padding: 2px 10px; border-radius: 999px; font-size: 0.75rem;">
  FAILED
</span>

<!-- RUNNING -->
<span style="background: #EAF0F6; color: var(--blue-mid);
             border: 1px solid var(--blue-mid);
             padding: 2px 10px; border-radius: 999px; font-size: 0.75rem;">
  RUNNING
</span>
```

**Progress Bar**
```html
<div style="width: 100%; background: var(--oatmeal); border-radius: 999px; height: 6px;">
  <div id="progress-{scenarioId}"
       style="background: var(--amber); height: 6px; border-radius: 999px;
              width: 0%; transition: width 0.4s ease;">
  </div>
</div>
```

**Table**
```css
.data-table {
  background: var(--card);
  border: 1px solid var(--sand);
  border-radius: 8px;
  border-collapse: collapse;
  width: 100%;
}
.data-table th {
  background: var(--truffle);
  color: var(--palladian);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.75rem 1rem;
}
.data-table td {
  color: var(--blue);
  border-bottom: 1px solid var(--sand);
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
}
.data-table tr:hover td {
  background: var(--palladian);
}
```

**Inline Attribution Bar (inside table cell)**
```html
<td>
  <div style="display: flex; align-items: center; gap: 8px;">
    <div style="flex: 1; background: var(--oatmeal); border-radius: 999px; height: 6px;">
      <div style="background: var(--amber); height: 6px; border-radius: 999px; width: 41%;"></div>
    </div>
    <span style="color: var(--blue); font-weight: 600; min-width: 40px;">41%</span>
  </div>
</td>
```

**Delta Badge (comparison table)**
```html
<!-- Positive delta: amber highlight -->
<span style="color: var(--amber); font-weight: 700;">+10pp</span>

<!-- Negative delta: flame -->
<span style="color: var(--flame); font-weight: 700;">-6pp</span>
```

---

## 10. Toast Notifications

```javascript
function showToast(message, type = 'info') {
  const colours = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500'
  };
  const toast = document.createElement('div');
  toast.className = `fixed bottom-4 right-4 ${colours[type]} text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
```
