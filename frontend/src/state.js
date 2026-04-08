// js/state.js — Global app state

const appState = {
  user: null,
  currentStep: 1,
  connection: { catalog: null, schema: null, table: null },
  dataReport: null,
  pendingScenario: null,
  scenarios: new Map(),
  activeScenarioId: 'scen-001',
  comparisonSet: ['scen-001', 'scen-002'],
  pollingTimers: new Map(),
  exportOptions: { title: 'UTC Channel Attribution Report', format: 'pdf' },
  showAllChannels: false,

  init() {
    // Preload mock scenarios
    MOCK.scenarios.forEach(s => this.scenarios.set(s.id, s));
  },

  setStep(n) {
    this.currentStep = n;
    if (typeof stepper !== 'undefined') stepper.update(n);
    if (typeof router !== 'undefined') router.go(n);
  },

  getActiveResult() {
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

  isPinned(id) { return this.comparisonSet.includes(id); }
};