# USER_FLOW.md — Canonical 9-Step User Journey

## UTC Channel Attribution MMM Platform

> **This is the single source of truth for the user experience.** Every screen, decision point, validation rule, state, and transition is defined here. All other docs (ARCHITECTURE, API, FRONTEND_GUIDE) are implementations of this flow.

---

## Flow Overview

```
  ①           ②              ③             ④              ⑤
LOGIN  →  DATA SOURCE  →  DATA REPORT  →  CONFIGURE  →  SCHEMA &
                                          SCENARIO       UNIVERSE KPIs
                                                              │
  ⑨           ⑧              ⑦             ⑥              ◄──┘
EXPORT  ←  COMPARISON  ←  SCENARIO    ←  RESULTS
REPORT                    BUILDER        DASHBOARD
```

Steps ①–③ are **one-time setup** per workspace connection (cached in session).
Steps ④–⑨ repeat for every new analysis session or scenario.
Steps ⑦–⑨ can be revisited non-linearly from the persistent left sidebar.

---

## Step 1 — Login

### Purpose
Authenticate the analyst before accessing any Databricks data or running models.

### Screen Layout
Full-page centered login card on `--palladian` background. Card uses `--card` background, `--sand` border, 12px radius, 420px wide.

### Elements
- UTC logo / wordmark at top of card
- Heading: "Channel Attribution Platform" in `--blue`, weight 700
- Subheading: "United Therapeutics · Internal Analytics" in `--blue-mid`
- Email input field
- Password input field (with show/hide toggle)
- `Sign In` button — full width, `--amber` bg, `--truffle` text, weight 700
- "Forgot password?" link below button in `--blue-mid`
- Footer: "Powered by Databricks · ISO-27001 Certified" in `--oatmeal` small

### Validation Rules
- Email must be valid format; shows inline error in `--flame` if not
- Password required; min 8 characters
- On failed auth: shake animation on card + error banner "Invalid email or password" in `--flame` bg

### Success Behaviour
- JWT stored in `sessionStorage` (not localStorage — session only)
- Redirect to Step 2 (Data Source) if no workspace is cached
- Redirect to Step 5 (Schema & KPIs) if workspace + table already configured in session

### API Call
```
POST /api/v1/auth/login
```

---

## Step 2 — Data Source Selection

### Purpose
Connect to the correct Databricks workspace. Select catalog → schema → table containing the MMM results. Validate that the selected table has the expected schema before allowing the analyst to proceed.

### Screen Layout
Stepper header at top (shows all 9 steps; Step 2 is active). Main content: two-panel layout. Left panel (60%): selection form. Right panel (40%): live table preview.

### Stepper Component
A horizontal progress stepper pinned below the navbar, always visible. Steps shown as numbered circles connected by a line:

```
① Login  ──  ② Data Source  ──  ③ Data Report  ──  ④ Configure  ──  ⑤ Schema  ──  ⑥ Dashboard  ──  ⑦ Builder  ──  ⑧ Compare  ──  ⑨ Export
  ✓              ACTIVE              ○                 ○               ○              ○               ○              ○             ○
```
- Completed: `--amber` filled circle with ✓
- Active: `--blue` filled circle with step number, bold label
- Upcoming: `--oatmeal` circle, `--blue-mid` label

### Left Panel — Selection Form

**Section: Workspace**
- Databricks Host URL — pre-filled from env, read-only
- Connection status badge: `● Connected` in `--amber` or `● Disconnected` in `--flame`

**Section: Browse Data — Three cascading dropdowns**

1. **Catalog** dropdown — loads on page open via `GET /api/v1/databricks/catalogs`
   - Options: e.g., `hive_metastore`, `main`, `utc_prod`

2. **Schema** dropdown — loads after catalog selected
   - Options: e.g., `utc_attribution`, `mmm_results`, `dbo`

3. **Table** dropdown — loads after schema selected
   - Options: e.g., `mmm_scenario_results`, `result`, `attribution_output`

After all three selected: `Validate & Preview` button (`--amber` bg, `--truffle` text).

**Validation Result Banner:**
- ✓ "Table validated — 73 columns, 377 rows detected. Schema matches expected MMM output."
- ✗ Flame banner: "Schema mismatch — missing columns: [Attribution_Pct_High_Performer…]. Expected 73, found 48."

### Right Panel — Table Preview
Once validated: scrollable data preview (first 5 rows, first 10 columns). Row count badge: "377 rows · 73 columns".

### Continue Button
`Continue to Data Report →` — enabled only after successful validation.

### API Calls
```
GET  /api/v1/databricks/catalogs
GET  /api/v1/databricks/schemas?catalog={catalog}
GET  /api/v1/databricks/tables?catalog={catalog}&schema={schema}
POST /api/v1/databricks/validate-table
GET  /api/v1/data/preview?catalog={c}&schema={s}&table={t}&rows=5
```

---

## Step 3 — Data Report

### Purpose
Surface data quality before running any model — completeness, date coverage, and null rates per column — so the analyst can decide whether to proceed or investigate upstream.

### Screen Layout
Full main content area. Header: "Data Quality Report" with a `Refresh` button and "Last scanned: {timestamp}" in `--blue-mid`. Three sections stacked vertically.

### Section A — Summary Health Cards (5 cards, top row)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ TOTAL ROWS   │  │ TOTAL COLS   │  │ DATE RANGE   │  │ COMPLETENESS │  │ UNIQUE       │
│    377       │  │     73       │  │ Jan 2023     │  │   94.2%      │  │ SCENARIOS    │
│              │  │              │  │ – Mar 2025   │  │ (amber/flame)│  │      3       │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```
Completeness %: < 80% → `--flame`, 80–95% → `--amber`, > 95% → `--blue`.

### Section B — Date Coverage Timeline

Horizontal bar chart (full width, 80px tall). X axis = months. Bars = record count per month in `--amber`. Gaps (zero-record months) highlighted in `--flame` with tooltip "No data — Jan 2024".

### Section C — Column Null Rate Table

Full-width table grouped by column category:
```
Group            Column                              Null Rate  Status
Attribution %    Attribution_Pct_High_Performer      0.0%       ✓ Clean
                 Attribution_Pct_All_HCPs            41.3%      ⚠ Partial
                 Attribution_Pct_0_2_Years           68.2%      ⚠ Partial
HCP Counts       no_of_hcp_High_Performer            0.0%       ✓ Clean
Touchpoints      total_touchpoints_All_HCPs          41.3%      ⚠ Partial
```
Status: `✓ Clean` (`--blue`), `⚠ Partial` (`--amber`), `✗ Missing` (`--flame`).

Explanatory callout:
> "ℹ️ Partial nulls in segment-specific columns are expected. A Cluster-level run will have nulls for LOB and Competitor Drug columns, and vice versa."

### Decision Gate
- `Proceed to Configure Scenario →` (`--amber`, full width)
- `← Back to Data Source` (text link)

### API Call
```
GET /api/v1/data/report?catalog={c}&schema={s}&table={t}
```

---

## Step 4 — Configure Scenario (Hyperparameters)

### Purpose
Name this scenario and set the 5 hyperparameters that control what the Markov chain model computes. The primary action that triggers the Databricks job.

### Screen Layout
Two-column layout. Left (55%): configuration form. Right (45%): live "Configuration Summary" card that updates as the analyst fills the form.

### Form — Left Column

**Section: Identity**
- Scenario Name — required text input. Placeholder: "e.g. Q4 TYVASO — Cluster Baseline"

**Section: 5 Hyperparameters**

1. **Start Date** — date picker. Min: `2020-01-01`. Default: `2023-01-01`. Warning if < 12 months range selected.

2. **End Date** — date picker. Must be > Start Date. Default: `2025-03-31`. Inline `--flame` error if end < start.

3. **Product** — visual pill group (not dropdown):
   ```
   [ ALL ]  [ TYVASO ]  [ REMODULIN ]  [ ORENITRAM ]  [ TREPROSTINIL ]
   ```
   Selected: `--amber` bg, `--truffle` text, weight 700. Unselected: `--card` bg, `--oatmeal` border, `--blue-mid` text.

4. **Attribution Level** — 3 card-style selectors:
   ```
   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
   │  🎯 Touchpoint   │  │  📡 Channel      │  │  👥 Team         │
   │  Most granular   │  │  Grouped by      │  │  Grouped by      │
   │  individual call │  │  modality type   │  │  sales team      │
   │  type per HCP    │  │  (Live, Virtual) │  │  (SALES, MDD…)   │
   └──────────────────┘  └──────────────────┘  └──────────────────┘
   ```
   Selected: `--amber` border (2px), `--card` bg. Unselected: `--sand` border.

5. **HCP Segment** — 4 card-style selectors:
   ```
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │  🏆 Cluster     │  │  📅 Length of   │  │  💊 Competitor  │  │  👁 All HCPs    │
   │  High Performer │  │  Business (LOB) │  │  Drug           │  │  Full universe  │
   │  → Unresponsive │  │  0–2 / 2–10 /   │  │  Writes vs      │  │  no segment     │
   │                 │  │  10+ Years      │  │  Does not write │  │  filter         │
   └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
   ```

**Optional Notes** — textarea, 2 rows.

### Live Configuration Summary — Right Column

Sticky card (`--card` bg, `--sand` border, `--truffle` top border 3px) updating in real-time:

```
┌─────────────────────────────────────┐
│  SCENARIO CONFIGURATION SUMMARY     │
│─────────────────────────────────────│
│  Name       Q4 TYVASO — Cluster     │
│  Product    TYVASO                  │
│  Date Range Jan 2023 → Mar 2025     │
│             (27 months)             │
│  Level      Touchpoint              │
│  Segment    Cluster                 │
│─────────────────────────────────────│
│  Estimated Databricks Runtime       │
│  ⏱  ~60–90 seconds                 │
│─────────────────────────────────────│
│  Rows matching these params         │
│  📊  377 rows                       │
└─────────────────────────────────────┘
```

### Submit Button
`▶ Run Attribution Model` — large, full-width, `--amber` bg, `--truffle` text, weight 700, 52px height. Disabled until all 5 params + name are filled.

### Post-Submit State
- Button → spinner + "Submitting to Databricks…"
- Bottom drawer slides up (200px):
  ```
  Scenario "Q4 TYVASO — Cluster" is running
  ████████████░░░░░░░░░░░░  45% — Computing transition matrices…
  Elapsed: 00:42   Estimated remaining: ~00:30
  ```
- User can navigate away — job continues. Scenario appears in sidebar with RUNNING pulse badge.
- Auto-advance to Step 5 after successful job trigger.

### API Call
```
POST /api/v1/scenarios/run
```

---

## Step 5 — Data Schema & Universe KPIs

### Purpose
Show the analyst what data they're working with — the 73-column schema with business definitions, and universe-level marketing KPIs from HCP360. **This screen is shown while the model runs in the background** (status widget top-right).

### Screen Layout
Two-column layout. Left (50%): schema explorer. Right (50%): marketing universe KPIs. Running status widget pinned top-right of page.

### Left — Schema Explorer

Searchable, filterable column reference table.

Filter chips: `[ All ]  [ Attribution % ]  [ HCP Counts ]  [ Touchpoints ]  [ Prescribers ]  [ Run Config ]`

Column table with: Column Name · Type · Category (color-coded pill) · Description. Clicking a row expands to show full description + example value. "73 columns" chip.

### Right — Marketing Universe KPIs

**2×3 KPI card grid:**
```
┌────────────────────┐  ┌────────────────────┐
│ TOTAL HCPs         │  │ TOTAL REFERRALS     │
│ IN UNIVERSE        │  │ Observation Period  │
│   13,354           │  │    11,138           │
└────────────────────┘  └────────────────────┘
┌────────────────────┐  ┌────────────────────┐
│ MARKETING TEAMS    │  │ TOTAL TOUCHPOINTS   │
│      6             │  │    90,777           │
│ SALES·MDD·MSL      │  │                     │
│ RNS·SPK PGM·EMAIL  │  │                     │
└────────────────────┘  └────────────────────┘
┌────────────────────┐  ┌────────────────────┐
│ HCP PRESCRIBERS    │  │ DATE RANGE          │
│ (Converters)       │  │ COVERAGE            │
│    2,701           │  │  Jan 2023           │
│                    │  │  → Mar 2025 (27mo)  │
└────────────────────┘  └────────────────────┘
```

**Team Breakdown mini-table:**
```
Team      HCPs Reached    Touchpoints    Attribution (prelim)
SALES     11,209 (84%)    73,219 (81%)   ~59%
MDD        1,477 (11%)     6,981  (8%)   ~17%
MSL        1,601 (12%)     4,301  (5%)   ~10%
RNS          727  (5%)     1,568  (2%)    ~5%
SPK PGM    1,852 (14%)     2,411  (3%)    ~5%
EMAIL        930  (7%)     2,297  (3%)    ~3%
```
"~" indicates cached preliminary values before the running scenario completes.

**Running Status Widget** (top-right corner, persistent):
```
⏱ Q4 TYVASO — Cluster  RUNNING  ████████░░  72%
```
On SUCCESS: becomes `✓ Ready — View Results →` amber CTA button.

### API Calls
```
GET /api/v1/data/schema?catalog={c}&schema={s}&table={t}
GET /api/v1/data/universe-kpis
GET /api/v1/scenarios/{id}/status   (polled every 5s)
```

---

## Step 6 — Results Dashboard

### Purpose
The primary analytical view. Full attribution results for the selected scenario: KPI summary cards, team donut, channel table, Sankey flow diagram, and HCP vertical movement/journey chart.

### Section A — Page Header
Scenario name, metadata pills (Product · Level · Segment · Date Range · Completed), action buttons: `+ Add to Compare` · `Export PDF` · `Export Excel`.

### Section B — 4 Summary KPI Cards
Total HCPs · Total Referrals · Total Touchpoints · Total Prescribers. (`--card` bg, `--sand` border.)

### Section C — Team Donut + Channel Table (side-by-side)

**Left: Team Attribution Donut** (ApexCharts, 40% width)
- SALES 59% → `--amber` · MDD 17% → `--blue` · MSL 10% → `--blue-mid` · RNS 5% → `--blue-lt` · SPK PGM 5% → `--oatmeal` · EMAIL 3% → `--sand`

**Right: Channel Attribution Table** (60% width)
Columns: Channel · Attribution % (inline bar) · HCPs Reached · Touchpoints · Prescribers. Top 8 channels with "Show all 16" expand.

### Section D — Sankey Flow Diagram ⭐

**Title:** "Marketing Touchpoint Flow → Referral Conversion"

A D3-based Sankey diagram, 4-layer, full width, 400px height:

```
Layer 1       Layer 2         Layer 3            Layer 4
(Team)        (Channel Type)  (HCP Segment)      (Outcome)

              ┌─Live Call──────────────────────────► Conversion ✓
SALES ───────►│
              └─Virtual Call ─────────────────────► Conversion ✓

MDD ─────────►──Live Call ────► High Performer ───► Conversion ✓
                              ► Moderate Perf. ───► Conversion ✓
MSL ─────────►──Live Call ────► Low Performer  ───► No Convert ✗

SPK PGM ─────►──Live (Spk)────────────────────────► Conversion ✓
              └─Virtual (Spk)─────────────────────► No Convert ✗

EMAIL ───────►──Email Clicked ─────────────────────► No Convert ✗
```

Flow band width = proportion of attribution. Colors: `--amber` (high), `--blue-mid` (medium), `--blue-lt` (low).

Interactivity: hover on any band → tooltip showing "SALES → Live Call: 73,219 touchpoints → 6,571 attributed referrals (59%)". Click a node → filters channel table to that path.

### Section E — HCP Vertical Movement / Journey Chart ⭐

**Title:** "HCP Segment Movement & Journey"

Two stacked sub-charts:

**Part 1 — Alluvial Migration Chart (300px):** Shows how HCPs flowed between segments from observation start to end.
- Flow colors: upward movement (improvement) = `--amber`, stable = `--blue-lt`, downward = `--flame`

```
Period Start (Jan 2023)          Period End (Mar 2025)

High Performer    ──────────────── High Performer
Moderate Performer ─────────╲──── Moderate Performer
Average Performer ────────────╲── Average Performer
Low Performer     ─────────────── Low Performer (some upgrade ↑)
Near Sleeping     ──────────────── Near Sleeping
Sleeping          ─────────────── Sleeping (some upgrade ↑, some drop ↓)
Unresponsive      ──────────────── Unresponsive
```

**Part 2 — Segment Count Timeline (200px):** Multi-line chart showing HCP count per segment month-over-month. One line per segment using team color palette.

Interactivity: click a segment label → filters channel table to show only that segment's attribution columns.

### Section F — Segment Heatmap (full width)
Channel × Segment matrix. Cell color: `--palladian` (low) → `--truffle` (high). (Full spec in FRONTEND_GUIDE.md)

### API Calls
```
GET /api/v1/scenarios/{id}/results
GET /api/v1/scenarios/{id}/sankey-data
GET /api/v1/scenarios/{id}/hcp-journey
```

---

## Step 7 — Scenario Builder

### Purpose
Manage multiple scenario runs from one place. Create new runs, clone existing ones with tweaked parameters, monitor status, and organise before comparison.

### Screen Layout
Two panels. Left (35%): scenario library list. Right (65%): selected scenario details or new scenario form.

### Left Panel — Scenario Library

Title: "Scenario Library" + `+ New Scenario` button (`--amber`).

Each scenario card:
```
┌───────────────────────────────────────────────────┐
│ [TYVASO]  Q4 TYVASO — Cluster Segment       [···] │
│ Touchpoint · Cluster · Jan 2023 – Mar 2025        │
│ Apr 03 2026 · 10:31 AM                            │
│ ████████████████████████ SUCCESS   [📌 Compare]   │
└───────────────────────────────────────────────────┘
```
- `[···]` menu: Clone · Rename · Delete
- `[Compare]` outline when not pinned, filled `--amber` when pinned (max 4)
- RUNNING cards show live animated progress bar

Filter/sort bar: sort by Date · Product · Status. Checkboxes for bulk delete.

### Right Panel
- **Scenario selected:** full parameter summary, status timeline (`QUEUED → RUNNING → SUCCESS` with timestamps), quick KPI chips, `View Full Dashboard →` and `Clone Scenario` buttons.
- **"New Scenario" clicked:** same form as Step 4, inline within the panel.
- **"Clone" clicked:** Step 4 form pre-filled with parent params, default name "Copy of [name]".

### API Calls
```
GET    /api/v1/scenarios
POST   /api/v1/scenarios/run
POST   /api/v1/scenarios/{id}/clone
DELETE /api/v1/scenarios/{id}
```

---

## Step 8 — Scenario Comparison

### Purpose
Place 2–4 scenarios side-by-side to understand how changing product, date range, level, or segment changes attribution. Includes delta analysis and auto-generated insight summary.

### Comparison Control Bar
```
│ Comparing: [Q4 TYVASO Cluster ▾] vs [REMODULIN All HCPs ▾]  + Add scenario  │
│ View by: [Team] [Channel] [Touchpoint]    Segment: [All HCPs ▾]              │
│ Mode: [Side-by-Side] [Overlay] [Waterfall] [Delta Only]        [Export →]    │
```
`--card` bg bar with `--sand` border.

### Chart Modes

**Side-by-Side:** Grouped bars. Scenario A = `--amber`, B = `--blue-mid`, C = `--blue-lt`, D = `--oatmeal`.

**Overlay:** Area chart at 40% opacity. Same colors.

**Waterfall:** Cumulative delta from A→B. Above baseline = `--amber` (B is higher), below = `--flame` (B is lower). Net total bar at right.

**Delta Only:** Hides chart, expands delta table full-width.

### Auto-Generated Insight Summary

Callout box (`--card` bg, `--amber` left border 4px):
```
💡 Key Insight — formula-generated

Comparing Q4 TYVASO Cluster vs. REMODULIN All HCPs:
• SALES Live Call attribution is 10pp higher for TYVASO (41%) vs REMODULIN (31%).
• MDD Live Call is 6pp higher for REMODULIN (16% vs 10%).
• Speaker Programs are 3pp more impactful for REMODULIN.

Recommendation: REMODULIN strategy should lean more on MDD and Speaker Programs.
```

### Delta Table
Columns: Channel · Scenario A % · Scenario B % · Δ pp · Δ Relative %. Positive delta: `--amber` bold + ▲. Negative delta: `--flame` bold + ▼.

### API Call
```
POST /api/v1/compare
```

---

## Step 9 — Export Executive Report

### Purpose
Generate a publication-quality report for stakeholders. Two formats: PDF (presentations) and Excel (further analysis).

### Screen Layout
Two-panel. Left (55%): report builder options. Right (45%): live report preview.

### Left Panel — Report Builder

**Report Identity:** Title · Prepared For · Prepared By (pre-filled) · Date (pre-filled)

**Scenario Selection:** Radio: `Single Scenario` or `Comparison Report` + relevant dropdowns.

**Content Sections** (checkboxes):
```
☑ Cover Page                    (logo, title, date, prepared by)
☑ Executive Summary             (auto-generated 3-bullet insight)
☑ Data Quality Summary          (completeness %, date range from Step 3)
☑ Scenario Configuration        (parameters table)
☑ Universe Overview KPIs        (6 marketing KPIs from Step 5)
☑ Team Attribution              (donut chart + data table)
☑ Channel Attribution           (bar table with inline bars)
☑ Segment Heatmap               (channel × segment matrix)
☑ Sankey Flow Diagram           (as static image)
☑ HCP Journey Chart             (as static image)
☐ Scenario Comparison           (enabled when Comparison mode selected)
☐ Data Appendix                 (full raw 73-column result table)
```

**Format Toggle:** `[ PDF Report ]  [ Excel Workbook ]`

**Generate Button:** `Generate Report` (`--amber`, full width). Shows spinner while building. On complete: download links appear.

### Right Panel — Live Preview
CSS-scaled miniature preview of first 3 report pages. Updates in real-time as sections are checked. Dynamic page count: "~8 pages".

### API Call
```
POST /api/v1/export/report
```

**Request body:**
```json
{
  "report_title": "Channel Attribution Analysis — Q4 TYVASO",
  "prepared_for": "Commercial Strategy Team",
  "scenario_ids": ["uuid-1"],
  "mode": "single",
  "format": "pdf",
  "sections": {
    "cover_page": true,
    "executive_summary": true,
    "data_quality": true,
    "scenario_config": true,
    "universe_kpis": true,
    "team_attribution": true,
    "channel_attribution": true,
    "segment_heatmap": true,
    "sankey_diagram": true,
    "hcp_journey": true,
    "comparison": false,
    "data_appendix": false
  },
  "pdf_options": { "page_size": "A4", "color_scheme": "branded" }
}
```

---

## Navigation Rules

### Linear (first run)
Steps 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 in order. Each "Continue" button activates only when required actions are complete.

### Non-linear (returning user)
Once a workspace/table is configured, the user can jump to any step from the stepper or sidebar. Completed steps show ✓ checkmarks.

### Back Navigation
Every step has a `← Back` text link. State is preserved (form values, selections) when going back.

### Session Persistence
- Auth token: `sessionStorage` (cleared on tab close)
- Workspace config (catalog/schema/table): `sessionStorage`
- Scenario result cache: `sessionStorage` keyed by `scenario_id`
- Pinned comparison set: `sessionStorage`

### Guard Rails
- Steps 5–9 are locked (stepper circles dimmed) until at least one scenario is in SUCCESS state
- Comparison (Step 8) shows empty state "Pin at least 2 scenarios to compare" if < 2 pinned
- Export (Step 9) locked until at least 1 SUCCESS scenario exists

---

## Error States Reference

| Error | Location | Display |
|---|---|---|
| Invalid credentials | Step 1 | Card shake animation + `--flame` banner |
| Databricks unreachable | Step 2 | `● Disconnected` badge + "Check workspace URL" |
| Schema mismatch | Step 2 | `--flame` banner listing missing columns |
| Low completeness (< 80%) | Step 3 | Warning card with `--flame` border |
| Date range < 3 months | Step 4 | Inline `--amber` warning below date pickers |
| Job failed | Steps 4–5 | Bottom drawer turns `--flame`: "Run failed — view Databricks logs" |
| No SUCCESS scenarios | Steps 6–9 | Locked state with explanation + CTA to Step 4 |
| Export timeout | Step 9 | Toast: "Report is taking longer than expected. We'll notify you when ready." |
