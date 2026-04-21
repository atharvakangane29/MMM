// js/state.js — Global app state
// Supports both real API results (appState.resultsCache) and MOCK fallback.

const appState = {
  user: null,
  currentStep: 1,
  connection: { catalog: null, schema: null, table: null },
  dataReport: null,        // real data report from GET /data/report
  pendingScenario: null,
  scenarios: new Map(),
  activeScenarioId: 'scen-001',
  comparisonSet: ['scen-001', 'scen-002'],
  pollingTimers: new Map(),
  exportOptions: { title: 'UTC Channel Attribution Report', format: 'pdf' },
  showAllChannels: false,
  resultsCache: {},        // scenario_id → full results object from API

  init() {
    // Preload mock scenarios as seed data (overwritten by real API data)
    MOCK.scenarios.forEach(s => this.scenarios.set(s.id, s));
  },

  setStep(n) {
    this.currentStep = n;
    if (typeof stepper !== 'undefined') stepper.update(n);
    if (typeof router !== 'undefined') router.go(n);
  },

  /**
   * Get results for the active scenario.
   * Priority: real API cache → MOCK fallback.
   */
  getActiveResult() {
    const realResult = this.resultsCache?.[this.activeScenarioId];
    if (realResult) {
      // Normalise real API shape to match what charts.js expects
      return _normaliseResults(realResult);
    }
    return MOCK.results[this.activeScenarioId] || null;
  },

  getActiveScenario() {
    return this.scenarios.get(this.activeScenarioId) || MOCK.scenarios[0];
  },

  addScenario(scenario) {
    this.scenarios.set(scenario.id, scenario);
    sidebar.render();
  },

  togglePin(id) {
    const idx = this.comparisonSet.indexOf(id);
    if (idx >= 0) {
      this.comparisonSet.splice(idx, 1);
    } else if (this.comparisonSet.length < 4) {
      this.comparisonSet.push(id);
    } else {
      toast.show('Maximum 4 scenarios can be pinned for comparison', 'info');
      return;
    }
    sidebar.render();
  },

  isPinned(id) { return this.comparisonSet.includes(id); },
};

/**
 * Transform the API's results shape into the shape the charts / screens expect.
 * This is the "adapter" that decouples the backend contract from the frontend internals.
 */
function _normaliseResults(apiResult) {
  if (!apiResult) return null;

  // team_summary: API gives { SALES: { attribution_pct, referrals_attributed } }
  // Charts expect: [{ team, pct, referrals, color }]
  const TEAM_COLORS = {
    SALES: '#FFB162', MDD: '#2C3B4D', MSL: '#4A6B8A',
    RNS: '#7FA3C0', 'SPK PGM': '#C9C1B1', EMAIL: '#D8D0C4', SPK_PGM: '#C9C1B1',
  };
  const team_summary = Object.entries(apiResult.team_level_summary || {}).map(([team, v]) => ({
    team,
    pct: Math.round((v.attribution_pct || 0) * 100),
    referrals: v.referrals_attributed || 0,
    color: TEAM_COLORS[team] || '#C9C1B1',
  }));

  // channels: API gives channel_attribution[] with attribution_pct object
  // Charts expect: [{ channel, team, pct, hcps, touchpoints, prescribers }]
  const channels = (apiResult.channel_attribution || []).map(ch => {
    const pct = ch.attribution_pct || {};
    const hcp = ch.hcp_counts || {};
    const tp = ch.touchpoint_counts || {};
    return {
      channel: ch.channel,
      team: ch.team,
      pct: Math.round((pct.all_hcps || pct.high_performer || 0) * 100),
      hcps: hcp.all_hcps || 0,
      touchpoints: tp.all_hcps || 0,
      prescribers: null,
    };
  });

  // heatmap
  const segKeys = ['high_performer', 'moderate_performer', 'average_performer',
    'low_performer', 'near_sleeping', 'sleeping', 'unresponsive'];
  const heatmap = {
    segments: ['High P.', 'Moderate P.', 'Average P.', 'Low P.', 'Near Sleep.', 'Sleeping', 'Unresponsive'],
    rows: channels.slice(0, 8).map(ch => {
      const src = (apiResult.channel_attribution || []).find(a => a.channel === ch.channel) || {};
      const pct = src.attribution_pct || {};
      return {
        channel: ch.channel,
        values: segKeys.map(k => Math.round((pct[k] || 0) * 100)),
      };
    }),
  };

  const kpis = apiResult.summary_kpis || {};
  return {
    summary_kpis: {
      total_hcps: (kpis.total_hcps_in_universe || 0).toLocaleString(),
      total_referrals: (kpis.total_referrals || 0).toLocaleString(),
      total_touchpoints: (kpis.total_touchpoints || 0).toLocaleString(),
      total_prescribers: (kpis.total_prescribers || 0).toLocaleString(),
    },
    team_summary,
    channels,
    heatmap,
  };
}