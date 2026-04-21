# USER_FLOW.md — Canonical 9-Step User Journey

## UTC Channel Attribution MMM Platform

> **Design Philosophy:** Minimalist, progressive disclosure. Hide backend complexity. Rely on iconography, clear visual hierarchy, and clean data visualizations over text-heavy explanations.

---

## Global Navigation & Layout

**Collapsible Left Navigation Bar:**
A persistent sidebar on the left side of the screen. 
* **Expanded state:** Shows Icons + Text labels.
* **Collapsed state:** Shows Icons only to maximize screen real estate.
* **Menu Items:** * 🏠 Home / Project Hub
    * 🗄️ Data & Health
    * ⚙️ Active Scenario
    * 📊 Dashboard
    * ⚖️ Compare
    * 📜 Scenario History
    * 📥 Export

**Flow Connectors:**
Every screen utilizes prominent `← Back` and `Next Step →` buttons at the bottom right/left to create a seamless, guided linear flow, while the sidebar allows non-linear traversal for power users.

---

## Flow Overview

```text
  ①           ②              ③             ④              ⑤
LOGIN  →  PROJECT HUB  →  DATA SETUP   →  CONFIGURE  →  MODEL RUNS
         (New/History)    & HEALTH        SCENARIO       (Execution)
                                                              │
  ⑨           ⑧              ⑦             ⑥              ◄──┘
EXPORT  ←  COMPARISON  ←  RESULTS      ←  FILTERED
           VIEW           DASHBOARD       KPIs
```

---

## Step 1 — Login

### Purpose
Authenticate the user with a clean, distraction-free entry point.

### UI / Elements
* **Layout:** Centered login card on a clean, solid background.
* **Elements:** UTC Logo, Email input, Password input, large `Sign In` button.
* **Flow:** On success, user routes to Step 2.

---

## Step 2 — Project Hub (New vs. Existing)

### Purpose
Direct the user immediately to action without clutter. Ask: Are you starting fresh, or looking at past work?

### UI / Elements
* **Layout:** Two large, clickable visual cards side-by-side.
    * **Card A (New Project):** ➕ Icon. "Start New Analysis". Routes to Step 3.
    * **Card B (Existing Projects):** 📜 Icon. "Scenario History". Routes to the **Scenario History Page** (where all past runs are traversable in a clean, searchable grid).
* **Scenario History Page:** A clean table listing `Scenario Name`, `Product`, `Date`, and `Status`. Clicking a row jumps directly to Step 7 (Dashboard) for that run.

---

## Step 3 — Data Setup & Health

### Purpose
Combine data selection and quality assessment into a single, highly visual step. Hide the complexity of Databricks connections.

### UI / Elements
* **Top Bar (Selection):** 3 horizontal dropdowns (Catalog → Schema → Table). Once selected, the page populates instantly.
* **Visual KPIs (Basic Data):** Clean, large number widgets.
    * `Total Rows` | `Total Columns` | `Date Range`
* **Data Quality Report:** Minimalist visual indicators.
    * *Completeness:* A circular progress ring (e.g., 94% filled).
    * *Column Health:* Red/Yellow/Green dot indicators next to column categories (e.g., 🟢 Touchpoints, 🟡 HCP Counts). Avoid walls of text.
* **Flow:** `Next: Configure Scenario →`

---

## Step 4 — Configure Scenario

### Purpose
Set the parameters to filter the data. Designed as a clean form using visual toggles rather than long dropdowns.

### UI / Elements
* **Identity:** "Scenario Name" input.
* **Date Range:** Simple start/end date pickers.
* **Product Selection:** Visual pill-group toggles (e.g., `[ALL] [TYVASO] [REMODULIN]`).
* **Granularity & Segments:** Icon-based selection cards.
    * *Level:* `🎯 Touchpoint` | `📡 Channel` | `👥 Team`
    * *Segment:* `🏆 Cluster` | `📅 LOB` | `💊 Competitor` | `👁 All HCPs`
* **Flow:** `▶ Run Model` button.

---

## Step 5 — Model Runs

### Purpose
Show execution state. Keep the user engaged without showing terminal logs or complex backend steps.

### UI / Elements
* **Layout:** Centered, aesthetic loading animation (e.g., a pulsing data-flow graphic or continuous progress bar).
* **Text:** Minimal. "Applying filters and calculating Markov chains..."
* **Flow:** Auto-advances to Step 6 when the Databricks job returns a SUCCESS state.

---

## Step 6 — Filtered Data KPIs

### Purpose
Show the shape of the data *after* the Step 4 filters are applied, confirming to the user what universe they are about to analyze.

### UI / Elements
* **Layout:** A simple, clean summary dashboard (4 KPI blocks).
    * `Targeted HCPs` (Filtered count)
    * `Relevant Touchpoints` (Filtered count)
    * `Identified Prescribers` (Filtered count)
    * `Data Cutoff` (Start/End dates confirmed)
* **Flow:** `Next: View Full Dashboard →`

---

## Step 7 — Results Dashboard

### Purpose
The primary analytical view. Focus heavily on charts; avoid raw data tables unless expanded.

### UI / Elements
* **Top Bar:** Scenario name and quick-edit icon.
* **Visualizations:**
    * **Team Impact Donut:** Clean donut chart of team attribution %.
    * **Sankey Diagram:** Interactive flow chart showing Touchpoint → Conversion.
    * **Segment Heatmap:** Visual matrix of Channel vs. Segment impact.
* **Flow:** `← Back to Filters` or `Next: Compare Scenarios →`

---

## Step 8 — Comparison View

### Purpose
Place scenarios side-by-side to understand deltas visually.

### UI / Elements
* **Control Bar:** Select up to 4 scenarios from a dropdown to pin to the board.
* **Visualizations:** Side-by-side bar charts for Attribution %. 
* **Delta Highlights:** Use color coding (Green ▲ / Red ▼) to show percentage point differences between the baseline and the comparison models. Keep it visual.
* **Flow:** `Next: Export →`

---

## Step 9 — Export View

### Purpose
Generate a publication-quality report with minimal clicks.

### UI / Elements
* **Layout:** Two panels. Left: Simple checkbox toggles. Right: Live visual preview of the document.
* **Options:** * Report Type: `[ PDF Presentation ]` vs `[ Excel Raw Data ]`
    * Sections to include: Checkboxes for `Executive Summary`, `Sankey Chart`, `Dashboard Metrics`.
* **Flow:** Large `📥 Download` button.