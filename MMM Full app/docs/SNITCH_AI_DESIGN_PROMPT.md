# UI/UX Design Prompt — UTC Channel Attribution MMM Platform
## Full 9-Screen Wireflow for Team Showcase

> **For:** Snitch AI (or any UI/UX workflow tool)
> **Output requested:** Full clickable wireflow covering all 9 screens, all interaction states, all transitions
> **Audience:** United Therapeutics internal commercial analytics team
> **Purpose:** Team walkthrough / stakeholder showcase of the full analyst journey

---

## Brand & Visual Language

Design a **professional pharma analytics dashboard** — data-dense, authoritative, and precise. The aesthetic is a premium internal BI tool: not a consumer app, not a generic SaaS template. Think a high-end financial terminal with warm, grounded tones.

### Color Palette — use exactly these tokens, no substitutions

```
--palladian: #EEE9DF   →  page backgrounds, full-screen backgrounds
--oatmeal:   #C9C1B1   →  borders, dividers, inactive sidebar items, disabled states
--blue:      #2C3B4D   →  primary body text, table data, all headings
--truffle:   #1B2632   →  top navbar, section headers, dark surfaces
--amber:     #FFB162   →  primary CTA button, selected/active state, chart highlight (SALES)
--flame:     #A35139   →  error/failed state, negative deltas, critical badges
--blue-mid:  #4A6B8A   →  secondary labels, axis text, chart legends, metadata
--blue-lt:   #7FA3C0   →  chart lines, low-severity indicators, inactive tab text
--sand:      #D8D0C4   →  table row borders, card section dividers
--card:      #F7F4EF   →  card backgrounds, form inputs, sidebar panels
```

### Typography
- Headings: Inter or DM Sans, weight 600–700
- Body / table data: Inter, weight 400–500
- Labels / axes: Inter, 11–12px, uppercase with letter-spacing
- KPI numbers: tabular lining numerals, weight 700, large scale

### Density
Data-dense — this is an analyst tool. Cards: 16–20px padding. Table rows: 10–12px vertical padding. Border radius: 8px cards, 4px inputs, 999px pills/badges.

---

## Persistent Shell Elements (appear on every screen after login)

### Top Navbar (52px, `--truffle` bg)
- Left: UTC wordmark in white
- Center: "Channel Attribution Platform" in `--palladian`, weight 500
- Right: notification bell + user avatar circle + logout icon

### Left Sidebar (240px, `--card` bg, `--sand` right border)
- `+ New Scenario` button at top — full width, `--amber` bg, `--truffle` text, weight 600
- Scrollable scenario history list below
- Bottom: settings gear + docs link

### Horizontal Step Stepper (pinned below navbar, visible on Steps 2–9)
Nine numbered circles connected by a progress line:
```
① Login  ──  ② Data Source  ──  ③ Data Report  ──  ④ Configure  ──  ⑤ Schema  ──  ⑥ Dashboard  ──  ⑦ Builder  ──  ⑧ Compare  ──  ⑨ Export
```
- Completed: `--amber` filled circle + ✓ icon
- Active: `--blue` filled circle, bold label, slight shadow
- Upcoming: `--oatmeal` circle, `--blue-mid` label, dimmed
- Clicking a completed step navigates back to it

---

## SCREEN 1 — Login

**Full-page, no sidebar, no stepper.**
Page background: `--palladian`.

**Login card** (centered, 420px wide, `--card` bg, `--sand` border, 12px radius, subtle shadow):
- UTC logo / wordmark (top of card, centered)
- Heading: "Channel Attribution Platform" — `--blue`, weight 700, 22px
- Subheading: "United Therapeutics · Internal Analytics" — `--blue-mid`, 13px
- Divider line `--sand`
- Email field — `--card` bg input, `--sand` border, `--blue` text, `--blue-mid` placeholder
- Password field — same styling + show/hide eye icon right side
- `Sign In` button — full width, `--amber` bg, `--truffle` text, 48px height, weight 700
- "Forgot password?" — centered link below button, `--blue-mid`, 12px
- Footer (bottom of card): "Powered by Databricks · ISO-27001 BSI Certified" — `--oatmeal`, 11px

**States to show:**
- Default / empty
- Validation error: email field outlined in `--flame` + inline error "Please enter a valid email"
- Failed auth: `--flame` bg banner top of card "Invalid email or password" + card shake
- Loading: button shows spinner + "Signing in…", disabled

**Flow arrow:** Sign In success → Screen 2

---

## SCREEN 2 — Data Source Selection

**Stepper:** Step 2 active. Step 1 complete (✓).
**Layout:** Two panels inside main content area (`--palladian` bg).

**Left Panel (60%, `--card` bg, `--sand` border, 8px radius, 24px padding):**

Section "WORKSPACE":
- Databricks Host URL — read-only input (`--oatmeal` bg)
- Connection badge: `● Connected` (`--amber` dot) or `● Disconnected` (`--flame`)

Section "SELECT DATA SOURCE" — Three cascading dropdowns:
1. **Catalog** — "Select catalog…" → options: `hive_metastore`, `main`, `utc_prod`
2. **Schema** — "Select schema…" → options: `utc_attribution`, `mmm_results`
3. **Table** — "Select table…" → options: `mmm_scenario_results`, `result`

`Validate & Preview` button (`--amber`) — appears after all 3 selected.

Validation result banner:
- ✓ `--amber` left border: "Table validated — 73 columns · 377 rows · Schema matches MMM output"
- ✗ `--flame` left border: "Schema mismatch — missing 25 expected columns"

`Continue to Data Report →` — `--amber`, full width, bottom. Disabled until validated.

**Right Panel (40%, `--card` bg):**
"Table Preview" header. Mini scrollable data table (5 rows × 10 columns). `--truffle` header, `--sand` borders.

**Flow arrow:** Continue → Screen 3

---

## SCREEN 3 — Data Report

**Stepper:** Step 3 active. Steps 1–2 complete.
**Layout:** Full content area, 3 stacked sections.

**Page Header:**
"Data Quality Report" — `--blue`, weight 700. Right: Refresh button + "Last scanned" timestamp.

**Section A — 5 Health Summary Cards:**
```
Total Rows: 377  |  Total Cols: 73  |  Date Range: Jan 2023–Mar 2025  |  Completeness: 94.2%  |  Unique Scenarios: 3
```
All `--card` bg, `--sand` border. Completeness: >95% `--blue`, 80–95% `--amber`, <80% `--flame`.

**Section B — Date Coverage Timeline:**
Horizontal bar chart (80px tall). Bars in `--amber`. Gap months in `--flame` with "⚠ No data" annotation.

**Section C — Column Null Rate Table:**
Filter chips: `[ All ] [ Attribution % ] [ HCP Counts ] [ Touchpoints ] [ Prescribers ]`

```
Group             Column                            Null Rate   Status
Attribution %     Attribution_Pct_High_Performer    0.0%        ✓ Clean   (--blue)
                  Attribution_Pct_All_HCPs          41.3%       ⚠ Partial (--amber)
HCP Counts        no_of_hcp_High_Performer          0.0%        ✓ Clean
Touchpoints       total_touchpoints_All_HCPs        41.3%       ⚠ Partial
```

Callout: "ℹ️ Partial nulls are expected — segment-specific columns are null outside their configured scope."

Decision gate:
- `Proceed to Configure Scenario →` (`--amber`)
- `← Back to Data Source` (text link)

**Flow arrow:** Proceed → Screen 4

---

## SCREEN 4 — Configure Scenario (Hyperparameters)

**Stepper:** Step 4 active. Steps 1–3 complete.
**Layout:** Two columns. Left (55%) form. Right (45%) live summary.

**Left — Form (`--card` bg card, 24px padding):**

Scenario Name — required text input, placeholder "e.g. Q4 TYVASO — Cluster Baseline"

**5 Hyperparameters:**

1+2. Date pickers side-by-side: Start Date · End Date. Warning if <12 months.

3. Product pills:
```
[ ALL ]   [ TYVASO ]   [ REMODULIN ]   [ ORENITRAM ]   [ TREPROSTINIL ]
```
Selected: `--amber` bg, `--truffle` text. Unselected: `--card` bg, `--oatmeal` border.

4. Attribution Level — 3 card selectors:
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  🎯 Touchpoint   │  │  📡 Channel      │  │  👥 Team         │
│  Most granular   │  │  Grouped by      │  │  Grouped by      │
│  individual call │  │  modality type   │  │  sales team      │
│  type per HCP    │  │  (Live, Virtual) │  │  (SALES, MDD…)   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```
Selected: `--amber` 2px border. Unselected: `--sand` border.

5. HCP Segment — 4 card selectors (2×2 grid):
```
┌─────────────────┐  ┌─────────────────┐
│  🏆 Cluster     │  │  📅 Length of   │
│  High Performer │  │  Business (LOB) │
│  → Unresponsive │  │  0–2/2–10/10+yr │
└─────────────────┘  └─────────────────┘
┌─────────────────┐  ┌─────────────────┐
│  💊 Competitor  │  │  👁 All HCPs    │
│  Drug           │  │  No segment     │
│  Writes vs Not  │  │  filter         │
└─────────────────┘  └─────────────────┘
```

Optional notes textarea (2 rows).

Submit button: `▶ Run Attribution Model` — full width, 52px, `--amber` bg, `--truffle` text, weight 700. Disabled until all 5 params + name filled.

**Right — Live Configuration Summary (sticky card):**
```
┌─────────────────────────────────────┐
│  SCENARIO CONFIGURATION             │
│─────────────────────────────────────│
│  Name         Q4 TYVASO — Cluster   │
│  Product      [TYVASO amber pill]   │
│  Date Range   Jan 2023 → Mar 2025   │
│               (27 months)           │
│  Level        Touchpoint            │
│  Segment      Cluster               │
│─────────────────────────────────────│
│  Estimated Runtime                  │
│  ⏱  ~60–90 seconds                 │
│─────────────────────────────────────│
│  Rows matching params               │
│  📊  377 rows                       │
└─────────────────────────────────────┘
```

**Post-submit state:**
Button → spinner. Bottom drawer slides up (200px, `--truffle` bg, white text):
```
⏱  "Q4 TYVASO — Cluster" is running on Databricks
████████████████░░░░░░░░░░░░░░░  45%   Computing transition matrices…
Elapsed: 00:42   Estimated remaining: ~00:30
```
Progress bar: `--oatmeal` track, `--amber` fill.

**Flow arrow:** Run + drawer → Screen 5 (model runs in background)

---

## SCREEN 5 — Data Schema & Universe KPIs

**Stepper:** Step 5 active. Steps 1–4 complete.
**Running status widget top-right:**
```
⏱ Q4 TYVASO — Cluster   RUNNING   █████████░░  78%
```
On SUCCESS → `✓ Results ready — View Dashboard →` (`--amber` bg button).

**Layout:** Two columns. Left (50%): Schema Explorer. Right (50%): Universe KPIs.

**Left — Schema Explorer (`--card` bg):**
Search bar + filter chips: `[ All ] [ Attribution % ] [ HCP Counts ] [ Touchpoints ] [ Prescribers ] [ Run Config ]`
Active chip: `--amber` bg. Inactive: `--card` bg `--oatmeal` border.

Column table:
```
Column Name                          Type       Category          Description
scenario_id                          STRING     Run Config        UUID for this run
Channel                              STRING     Dimension         Channel/touchpoint name
Attribution_Pct_High_Performer       DOUBLE     Attribution %     Attribution for High Performers
no_of_hcp_High_Performer             BIGINT     HCP Counts        HCPs reached in segment
total_touchpoints_High_Performer     BIGINT     Touchpoints       Touchpoint volume
no_of_prescribers_High_Performer     BIGINT     Prescribers       Converted HCPs
…  (73 columns total)
```
Category pill: Attribution % = `--amber`, HCP Counts = `--blue-mid`, Touchpoints = `--blue-lt`, Prescribers = `--blue`, Run Config = `--oatmeal`.
Click row → expands to show full description + example value.

**Right — Universe KPIs (`--card` bg):**

2×3 KPI card grid:
```
┌─────────────────────┐  ┌─────────────────────┐
│ TOTAL HCPs          │  │ TOTAL REFERRALS      │
│ IN UNIVERSE         │  │ (Obs. Period)        │
│   13,354            │  │   11,138             │
└─────────────────────┘  └─────────────────────┘
┌─────────────────────┐  ┌─────────────────────┐
│ MARKETING TEAMS     │  │ TOTAL TOUCHPOINTS    │
│   6                 │  │   90,777             │
│ SALES·MDD·MSL       │  │                      │
│ RNS·SPK PGM·EMAIL   │  │                      │
└─────────────────────┘  └─────────────────────┘
┌─────────────────────┐  ┌─────────────────────┐
│ HCP PRESCRIBERS     │  │ DATE COVERAGE        │
│ (Converters)        │  │  Jan 2023–Mar 2025   │
│   2,701             │  │  27 months           │
└─────────────────────┘  └─────────────────────┘
```

Team Breakdown mini-table:
```
Team      HCPs Reached     Touchpoints     Attribution
SALES     11,209 (84%)     73,219 (81%)    ~59%
MDD        1,477 (11%)      6,981  (8%)    ~17%
MSL        1,601 (12%)      4,301  (5%)    ~10%
RNS          727  (5%)      1,568  (2%)     ~5%
SPK PGM    1,852 (14%)      2,411  (3%)     ~5%
EMAIL        930  (7%)      2,297  (3%)     ~3%
```

**Flow arrow:** Status widget SUCCESS button → Screen 6

---

## SCREEN 6 — Results Dashboard

**Stepper:** Step 6 active. Steps 1–5 complete.
**This is the richest screen — the primary analytical view.**
**Layout:** Full content area, 6 sections stacked.

**Section A — Page Header:**
Scenario name: "Q4 TYVASO — Cluster Segment" — `--blue`, weight 700, 26px
Metadata pills: `[TYVASO]` amber · `[Touchpoint]` blue-mid · `[Cluster]` blue-mid · `[Jan 2023–Mar 2025]` blue-mid
Right: `📌 Add to Compare` (outline amber) · `Export PDF` · `Export Excel`

**Section B — 4 KPI Cards:**
Total HCPs: 1,534 · Total Referrals: 11,138 · Total Touchpoints: 90,777 · Total Prescribers: 2,701

**Section C — Team Donut (40%) + Channel Table (60%):**

Donut chart colors:
- SALES 59% → `--amber` (#FFB162)
- MDD 17% → `--blue` (#2C3B4D)
- MSL 10% → `--blue-mid` (#4A6B8A)
- RNS 5% → `--blue-lt` (#7FA3C0)
- SPK PGM 5% → `--oatmeal` (#C9C1B1)
- EMAIL 3% → `--sand` (#D8D0C4)

Channel table (`--truffle` header, `--sand` borders):
```
Channel               Attribution %       HCPs    Touchpoints  Prescribers
SALES_Live_Call       ████████████  41%   1,209    73,219       2,108
MDD_Live_Call         ███           10%     477     6,981         721
MSL_Live_Call         ██             8%     447     4,301         647
SALES_Virtual_Call    █▌             6%     892    12,400         890
MDD_PhoneEmail_Call   █▌             5%     280     3,200         312
Speaker_Pgm_Live      █▌             5%     625     2,411         454
MSL_Virtual_Call      █              3%     290     2,100         280
Email_Clicked         █              3%     320     2,297         225
```
Bar: `--oatmeal` track, `--amber` fill. Row hover: `--palladian` bg + `--amber` left border 3px.

**Section D — Sankey Flow Diagram ⭐ (full width, 400px, `--card` bg):**

Title: "Marketing Touchpoint Flow → Referral Conversion"
4-layer D3 Sankey (horizontal left-to-right):

```
Layer 1 (Team)    Layer 2 (Modality)      Layer 3 (Segment)        Layer 4 (Outcome)

                  ┌── Live Call ──────── High Performer ──────────► ✓ Conversion
SALES ───────────►│                      Moderate Performer ──────► ✓ Conversion
                  └── Virtual Call ───── Average Performer ───────► ✓ Conversion
                                         Low Performer ─────────────► ✗ No Convert
MDD ─────────────►── Live Call ──────────────────────────────────────► ✓ Conversion
                  └── Phone/Email ────────────────────────────────────► ✗ No Convert
MSL ─────────────►── Live Call ─────────────────────────────────────► ✓ Conversion
SPK PGM ─────────►── Live Spk Pgm ─────────────────────────────────► ✓ Conversion
EMAIL ───────────►── Email Clicked ─────────────────────────────────► ✗ No Convert
```

Band thickness = attribution proportion.
Band colors: `--amber` (high ≥30%), `--blue-mid` (10–29%), `--blue-lt` (<10%).

Hover state: highlighted band + `--truffle` tooltip: "SALES → Live Call: 41% attribution · 6,571 referrals · 73,219 touchpoints"
Click node: filters channel table above.

**Section E — HCP Vertical Movement / Journey Chart ⭐ (full width, `--card` bg):**

Title: "HCP Segment Movement & Journey"
Subtitle: "How HCPs shifted between performance clusters over the observation period"

**Part 1 — Alluvial Migration Chart (300px):**
Shows HCP flows from period start to period end:
```
JAN 2023 (Start)                               MAR 2025 (End)

High Performer  ─────────────────────────────── High Performer
                              ╲
Moderate Performer  ──────────────────────────── Moderate Performer
Average Performer  ─────────────────────────────── Average Performer
Low Performer  ──────────────────────────────────── Low Performer (some ↑)
Near Sleeping  ────────────────────────────────────── Near Sleeping
Sleeping  ──────────────────────────────────────────── Sleeping (some ↑ some ↓)
Unresponsive  ────────────────────────────────────────── Unresponsive
```
Upward flow: `--amber`. Stable: `--blue-lt`. Downward: `--flame`.

**Part 2 — Segment Count Timeline (200px):**
Multi-line chart (ApexCharts). One line per segment. X axis = months. Y axis = HCP count.
- High Performer: `--amber` · Moderate: `--blue` · Average: `--blue-mid` · Low: `--blue-lt` · Near Sleeping/Sleeping: `--oatmeal` · Unresponsive: `--sand`
Hover crosshair: tooltip with all segment counts for that month.

Click segment label → filters channel table to that segment's columns.

**Section F — Segment Heatmap (full width, `--card` bg):**
Channel × Segment matrix. Cell bg: `--palladian` (low) → `--blue-lt` (mid) → `--truffle` (high). `--truffle` header row.

---

## SCREEN 7 — Scenario Builder

**Stepper:** Step 7 active. Steps 1–6 complete.
**Layout:** Two panels. Left (35%): Scenario Library. Right (65%): detail/editor.

**Left Panel — Scenario Library:**
Header + `+ New Scenario` (`--amber` small button).
Filter/sort: "Sort by: Newest" + `[ All ] [ SUCCESS ] [ RUNNING ] [ FAILED ]` pills.

5 scenario cards (show these examples):
```
┌───────────────────────────────────────────────────┐
│ [TYVASO]  Q4 TYVASO — Cluster Segment       [···] │
│ Touchpoint · Cluster · Jan 2023 – Mar 2025        │
│ Apr 03 2026 · 10:31 AM                            │
│ ───────────────────── SUCCESS  [📌 Pinned]         │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│ [REMODULIN]  REMODULIN All HCPs — Team Level [···]│
│ Team · All HCPs · Jan 2023 – Mar 2025             │
│ Apr 02 2026 · 14:22 PM                            │
│ ───────────────────── SUCCESS  [📌 Pinned]         │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│ [ORENITRAM]  ORENITRAM LOB Analysis         [···] │
│ Channel · LOB · Jan 2023 – Mar 2025               │
│ Apr 03 2026 · 11:05 AM                            │
│ ██████████░░░░░░ RUNNING  (pulse animation)        │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│ [TREPROSTINIL]  Competitor Analysis         [···] │
│ Touchpoint · Competitor Drug · Jan–Mar 2025       │
│ Apr 01 2026 · 09:18 AM                            │
│ ───────────────────── SUCCESS                      │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│ [TYVASO]  Channel Level Q1                  [···] │
│ Channel · Cluster · Q1 2025                       │
│ Mar 31 2026 · 16:44 PM                            │
│ ───────────────────── FAILED (--flame badge)       │
└───────────────────────────────────────────────────┘
```

Below list: "2 scenarios pinned for comparison" + `Go to Comparison →` link (`--amber` text).

**Right Panel — 3 states (show all 3 as separate frames):**

State A (Scenario Selected):
- Parameter summary grid
- Status timeline: `QUEUED 10:30:00 → RUNNING 10:30:12 → SUCCESS 10:31:42`
- Quick chips: Total Referrals: 11,138 · Top Channel: SALES_Live_Call 41% · Top Team: SALES 59%
- Buttons: `View Full Dashboard →` (`--amber`) · `Clone Scenario` (outline) · `Delete` (`--flame` text)

State B (New Scenario): Same form as Screen 4 inline.
State C (Clone): Screen 4 form pre-filled, "Cloned from: Q4 TYVASO" callout.

**Flow arrows:**
- `View Full Dashboard →` → Screen 6
- `Go to Comparison →` → Screen 8

---

## SCREEN 8 — Scenario Comparison Engine

**Stepper:** Step 8 active. All previous complete.
**Layout:** Full width. Top: control bar. Middle: chart + insight. Below: delta table. Right rail: pinned cards.

**Comparison Control Bar (`--card` bg, `--sand` border, 48px):**
```
│ Comparing: [Q4 TYVASO Cluster ▾]  vs  [REMODULIN All HCPs ▾]  [+ Add]  │
│ View by: [Team] [Channel] [Touchpoint]  Segment: [All HCPs ▾]           │
│ Mode: [Side-by-Side] [Overlay] [Waterfall] [Delta Only]  [Export →]     │
```
Active mode pills: `--amber` bg. Inactive: `--card` `--oatmeal` border.

**Main Chart — Side-by-Side (default):**
Grouped bar chart. X axis: SALES, MDD, MSL, RNS, SPK PGM, EMAIL. Y axis: Attribution %.
- Scenario A bars: `--amber` (#FFB162)
- Scenario B bars: `--blue-mid` (#4A6B8A)
- Chart bg: `--card`. Gridlines: `--sand`. Axis: `--blue-mid`.

Bar values (approximate from real data):
```
         SALES  MDD   MSL   RNS   SPK PGM  EMAIL
TYVASO:   59%   17%   10%    5%     5%       3%
REMODULIN: 52%  21%   12%    4%     5%       4%
```

Hover tooltip: `--truffle` bg, white text, shows both values + delta.

**Auto-Generated Insight Callout (`--card` bg, `--amber` left border 4px):**
```
💡 Key Insight

Comparing Q4 TYVASO Cluster vs REMODULIN All HCPs:
• SALES attribution is 7pp higher for TYVASO (59% vs 52%).
• MDD team is 4pp more effective for REMODULIN (21% vs 17%).
• Speaker Programs perform equally for both products (5%).

Recommendation: REMODULIN strategy should emphasise MDD team engagement.
```

**Delta Table:**
```
Channel              Scenario A   Scenario B   Δ pp      Δ Relative
SALES_Live_Call         59%          52%       +7pp ▲    +13%    (amber bold)
MDD_Live_Call           17%          21%       -4pp ▼    -19%    (flame bold)
MSL_Live_Call           10%          12%       -2pp ▼    -17%
Speaker_Pgm_Live         5%           5%        0pp       0%     (blue-mid)
RNS_Live_Call            5%           4%       +1pp ▲    +25%
Email_Clicked            3%           4%       -1pp ▼    -25%
```

**Right Rail (280px, `--card` bg, `--sand` left border):**
"PINNED SCENARIOS" (`--blue-mid` uppercase) + 2 mini-cards. Active in comparison: card gets 2px border in their scenario color.

**Alternate Waterfall state (show as second frame):**
Single bar chart. Delta bars: above baseline = `--amber`, below = `--flame`. Net total bar far right.

**Flow arrow:** `Export →` → Screen 9

---

## SCREEN 9 — Export Executive Report

**Stepper:** Step 9 active. All steps complete.
**Layout:** Two panels. Left (55%): Report Builder. Right (45%): Live Preview.

**Left Panel (`--card` bg, 24px padding):**

Section "REPORT IDENTITY":
- Report Title: "Channel Attribution Analysis — Q4 TYVASO"
- Prepared For: "Commercial Strategy Team"
- Prepared By: pre-filled user name
- Date: "Apr 03, 2026"

Section "SCENARIO SELECTION":
Radio buttons: `○ Single Scenario`  `● Comparison Report`
Two pills showing pinned scenarios: `[Q4 TYVASO ×]  [REMODULIN ×]`

Section "CONTENT SECTIONS" (checkboxes):
```
☑  Cover Page                    UTC logo, title, analyst, date
☑  Executive Summary             3-bullet auto-generated insight
☑  Data Quality Summary          Completeness %, date range
☑  Scenario Configuration        Parameters table per scenario
☑  Universe Overview KPIs        6 marketing KPI cards
☑  Team Attribution              Donut chart + attribution table
☑  Channel Attribution           Bar table with inline bars
☑  Segment Heatmap               Channel × segment matrix
☑  Sankey Flow Diagram            Static image
☑  HCP Journey Chart              Static image
☐  Scenario Comparison            (enabled in Comparison mode)
☐  Data Appendix                  Full 73-column raw results
```
Checked: `--amber` checkbox. Unchecked: `--oatmeal` border.

Section "FORMAT":
`[ PDF Report ]  [ Excel Workbook ]` toggle pills.
PDF options: `[A4]  [Letter]` · `[Branded]  [Print-Friendly B&W]`

"Estimated: ~9 pages" — updates dynamically as sections toggle.

`Generate Report` button — full width, `--amber`, 52px.

Post-generate state:
```
✓ Report ready
[⬇ Download PDF]   [⬇ Download Excel]
```

**Right Panel — Live Preview:**
CSS-scaled (0.45) miniature pages:
- Page 1: Cover — UTC logo, title centered, "Prepared for: Commercial Strategy Team", date
- Page 2: Executive Summary — mini KPI chips + small donut thumbnail
- Page 3: Channel Table — mini bar table

`--palladian` / `--card` / `--truffle` palette applied inside preview. `--sand` border per page. "Page X of ~9" counter.

---

## Interaction Flow Connections

```
Screen 1 (Login)
  └─ ✓ Sign In ────────────────────────────────────────► Screen 2

Screen 2 (Data Source)
  └─ ✓ Validated + Continue ──────────────────────────► Screen 3

Screen 3 (Data Report)
  └─ ✓ Proceed to Configure ──────────────────────────► Screen 4

Screen 4 (Configure Scenario)
  └─ ▶ Run Attribution Model ─── triggers job ─────────► Screen 5
       [bottom drawer slides up]                        [model running in BG]

Screen 5 (Schema & KPIs)
  └─ ✓ "Results ready →" widget ──────────────────────► Screen 6

Screen 6 (Results Dashboard)
  ├─ 📌 Add to Compare ──────────────────────────────► pins to sidebar (stays on Screen 6)
  ├─ Sidebar: + New Scenario ─────────────────────────► Screen 7
  └─ Stepper: Step 7 ─────────────────────────────────► Screen 7

Screen 7 (Scenario Builder)
  ├─ View Full Dashboard → ───────────────────────────► Screen 6
  ├─ Clone Scenario ──────────────────────────────────► Screen 7 (clone form state)
  └─ Go to Comparison → ──────────────────────────────► Screen 8

Screen 8 (Comparison)
  └─ Export → ────────────────────────────────────────► Screen 9

Screen 9 (Export)
  └─ ✓ Download PDF / Excel ──────────────────────────► file download (stays on Screen 9)

Any screen (stepper click on completed step)
  └─ ────────────────────────────────────────────────► that step's screen
```

---

## Loading / Empty States

| State | Screen | Description |
|---|---|---|
| Sidebar empty | 6–9 | Centered illustration + "No scenarios yet — Run your first attribution model" + CTA |
| Schema loading | 5 | Column rows shimmer: `--oatmeal`→`--sand` pulsing skeleton bars |
| Dashboard loading | 6 | KPI cards + chart areas replaced by pulsing skeleton blocks |
| Model RUNNING | 4 | Bottom drawer slide-up with animated `--amber` progress bar |
| Chart rendering | 6 | Chart containers show `--oatmeal` spinner centered |
| Comparison empty | 8 | "Pin at least 2 scenarios to compare" + arrow graphic pointing to sidebar |
| Export generating | 9 | Button spinner + "Building your report…" |

---

## Deliverables Requested from Snitch AI

1. **All 9 screens** at 1440×900 viewport — with sidebar and stepper visible on screens 2–9
2. **Alternate states** per screen (empty, loading, error, success, hover, active, post-submit)
3. **Annotated flow arrows** connecting all screens with trigger labels
4. **Component close-ups:** scenario sidebar card (SUCCESS/RUNNING/FAILED badge states) · attribution table row (hover + default) · delta badge (positive + negative) · form selection cards (selected + unselected) · stepper circles (complete/active/upcoming)
5. **Color annotation layer** on each screen labelling which token is applied to which element
6. **Clickable prototype** connecting the full linear journey: Login → Data Source → Data Report → Configure → Schema/KPIs → Dashboard → Builder → Comparison → Export
7. **Three chart close-ups:** Sankey diagram (hover state) · HCP Journey alluvial chart (both sub-charts) · Comparison waterfall chart (delta mode)
