// js/mock-data.js — Complete mock dataset for all 9 screens

const MOCK = {

  user: { name: 'Jane Smith', email: 'jane.smith@utc.com', role: 'analyst', initials: 'JS' },

  catalogs: ['hive_metastore', 'unity_catalog', 'mmm_dev'],
  schemas: { hive_metastore: ['utc_attribution', 'mmm_prod', 'mmm_staging'], unity_catalog: ['analytics', 'results'], mmm_dev: ['test_runs'] },
  tables: {
    utc_attribution: [
      { name: 'mmm_scenario_results', row_count: 377, column_count: 73, last_modified: '2026-04-03T14:05:34Z', size_bytes: 2400000 },
      { name: 'hcp360_universe', row_count: 13354, column_count: 45, last_modified: '2026-03-01T08:00:00Z', size_bytes: 8900000 }
    ],
    mmm_prod: [{ name: 'results_v2', row_count: 1200, column_count: 73, last_modified: '2026-04-01T10:00:00Z', size_bytes: 5100000 }],
    mmm_staging: [{ name: 'results_staging', row_count: 240, column_count: 68, last_modified: '2026-04-02T09:00:00Z', size_bytes: 900000 }]
  },

  previewRows: [
    { scenario_id:'3fa85f64', Channel:'SALES_Live_Call', Product:'TYVASO', Attribution_Pct_High_Performer:'0.3131', no_of_hcp_High_Performer:'559', total_touchpoints_High_Performer:'24035', run_segment:'Cluster Level', run_timestamp:'2026-04-03 10:31:42' },
    { scenario_id:'3fa85f64', Channel:'MDD_Live_Call',  Product:'TYVASO', Attribution_Pct_High_Performer:'0.1021', no_of_hcp_High_Performer:'280', total_touchpoints_High_Performer:'6981',  run_segment:'Cluster Level', run_timestamp:'2026-04-03 10:31:42' },
    { scenario_id:'3fa85f64', Channel:'MSL_Live_Call',  Product:'TYVASO', Attribution_Pct_High_Performer:'0.0891', no_of_hcp_High_Performer:'231', total_touchpoints_High_Performer:'4301',  run_segment:'Cluster Level', run_timestamp:'2026-04-03 10:31:42' },
    { scenario_id:'3fa85f64', Channel:'Email_Clicked',  Product:'TYVASO', Attribution_Pct_High_Performer:'0.0312', no_of_hcp_High_Performer:'320', total_touchpoints_High_Performer:'2297',  run_segment:'Cluster Level', run_timestamp:'2026-04-03 10:31:42' },
    { scenario_id:'3fa85f64', Channel:'Speaker_Pgm_Live',Product:'TYVASO',Attribution_Pct_High_Performer:'0.0544',no_of_hcp_High_Performer:'625', total_touchpoints_High_Performer:'2411',  run_segment:'Cluster Level', run_timestamp:'2026-04-03 10:31:42' }
  ],

  dataReport: {
    overview: { total_rows: 377, total_cols: 73, date_range: 'Jan 2023 – Mar 2025', completeness: 94.2, unique_scenarios: 12 },
    coverage: [
      { period:'Jan 23',count:18 },{ period:'Feb 23',count:22 },{ period:'Mar 23',count:19 },
      { period:'Apr 23',count:25 },{ period:'May 23',count:21 },{ period:'Jun 23',count:0  },
      { period:'Jul 23',count:28 },{ period:'Aug 23',count:26 },{ period:'Sep 23',count:30 },
      { period:'Oct 23',count:24 },{ period:'Nov 23',count:22 },{ period:'Dec 23',count:18 },
      { period:'Jan 24',count:0  },{ period:'Feb 24',count:20 },{ period:'Mar 24',count:25 },
      { period:'Apr 24',count:28 },{ period:'May 24',count:30 },{ period:'Jun 24',count:32 },
      { period:'Jul 24',count:29 },{ period:'Aug 24',count:27 },{ period:'Sep 24',count:31 },
      { period:'Oct 24',count:26 },{ period:'Nov 24',count:23 },{ period:'Dec 24',count:20 },
      { period:'Jan 25',count:22 },{ period:'Feb 25',count:24 },{ period:'Mar 25',count:26 }
    ],
    columns: [
      { group:'Attribution %', column:'Attribution_Pct_High_Performer', type:'DOUBLE', null_rate:0.00, status:'clean' },
      { group:'Attribution %', column:'Attribution_Pct_Moderate_Performer', type:'DOUBLE', null_rate:0.00, status:'clean' },
      { group:'Attribution %', column:'Attribution_Pct_Average_Performer', type:'DOUBLE', null_rate:0.00, status:'clean' },
      { group:'Attribution %', column:'Attribution_Pct_Low_Performer', type:'DOUBLE', null_rate:0.00, status:'clean' },
      { group:'Attribution %', column:'Attribution_Pct_All_HCPs', type:'STRING', null_rate:41.3, status:'partial', note:'Null when run_segment != "All HCPs"' },
      { group:'Attribution %', column:'Attribution_Pct_0_2_Years', type:'STRING', null_rate:68.2, status:'partial', note:'Null when run_segment != "LOB"' },
      { group:'Attribution %', column:'Attribution_Pct_2_10_Years', type:'STRING', null_rate:68.2, status:'partial', note:'Null when run_segment != "LOB"' },
      { group:'HCP Counts', column:'no_of_hcp_High_Performer', type:'BIGINT', null_rate:0.00, status:'clean' },
      { group:'HCP Counts', column:'no_of_hcp_Moderate_Performer', type:'BIGINT', null_rate:0.00, status:'clean' },
      { group:'HCP Counts', column:'no_of_hcp_All_HCPs', type:'STRING', null_rate:41.3, status:'partial', note:'Conditional null' },
      { group:'Touchpoints', column:'total_touchpoints_High_Performer', type:'BIGINT', null_rate:0.00, status:'clean' },
      { group:'Touchpoints', column:'total_touchpoints_All_HCPs', type:'STRING', null_rate:41.3, status:'partial' },
      { group:'Prescribers', column:'no_of_prescribers_High_Performer', type:'BIGINT', null_rate:0.00, status:'clean' },
      { group:'Prescribers', column:'no_of_prescribers_All_HCPs', type:'STRING', null_rate:41.3, status:'partial' },
      { group:'Run Config', column:'scenario_id', type:'STRING', null_rate:0.00, status:'clean' },
      { group:'Run Config', column:'run_product', type:'STRING', null_rate:0.00, status:'clean' },
      { group:'Run Config', column:'run_timestamp', type:'TIMESTAMP', null_rate:0.00, status:'clean' }
    ]
  },

  universeKPIs: {
    total_hcps: 13354, total_referrals: 11138, marketing_teams: 6,
    total_touchpoints: 90777, prescribers: 2701, date_coverage: 'Jan 2023 – Mar 2025',
    teams: [
      { name:'SALES', color:'#FFB162', hcps:'11,209', hcp_pct:'84%', touchpoints:'73,219', tp_pct:'81%', attribution:'~59%' },
      { name:'MDD',   color:'#2C3B4D', hcps: '1,477', hcp_pct:'11%', touchpoints: '6,981', tp_pct: '8%', attribution:'~17%' },
      { name:'MSL',   color:'#4A6B8A', hcps: '1,601', hcp_pct:'12%', touchpoints: '4,301', tp_pct: '5%', attribution:'~10%' },
      { name:'RNS',   color:'#7FA3C0', hcps:   '727', hcp_pct: '5%', touchpoints: '1,568', tp_pct: '2%', attribution: '~5%' },
      { name:'SPK PGM',color:'#C9C1B1',hcps: '1,852', hcp_pct:'14%', touchpoints: '2,411', tp_pct: '3%', attribution: '~5%' },
      { name:'EMAIL', color:'#D8D0C4', hcps:   '930', hcp_pct: '7%', touchpoints: '2,297', tp_pct: '3%', attribution: '~3%' }
    ]
  },

  scenarios: [
    {
      id: 'scen-001',
      name: 'Q4 TYVASO — Cluster Segment',
      product: 'TYVASO',
      level: 'Touchpoint',
      segment: 'Cluster',
      start: '2023-01-01', end: '2025-03-31',
      status: 'SUCCESS',
      created: 'Apr 03, 2026 · 10:30 AM',
      completed: 'Apr 03, 2026 · 10:31 AM',
      pinned: true,
      notes: 'Baseline run for Q4 planning'
    },
    {
      id: 'scen-002',
      name: 'REMODULIN All HCPs — Team Level',
      product: 'REMODULIN',
      level: 'Team',
      segment: 'All HCPs',
      start: '2023-01-01', end: '2025-03-31',
      status: 'SUCCESS',
      created: 'Apr 02, 2026 · 14:22 PM',
      completed: 'Apr 02, 2026 · 14:24 PM',
      pinned: true,
      notes: ''
    },
    {
      id: 'scen-003',
      name: 'ORENITRAM LOB Analysis',
      product: 'ORENITRAM',
      level: 'Channel',
      segment: 'LOB',
      start: '2023-01-01', end: '2025-03-31',
      status: 'RUNNING',
      created: 'Apr 03, 2026 · 11:05 AM',
      completed: null,
      pinned: false,
      progress: 65,
      notes: ''
    },
    {
      id: 'scen-004',
      name: 'TREPROSTINIL Competitor Analysis',
      product: 'TREPROSTINIL',
      level: 'Touchpoint',
      segment: 'Competitor Drug',
      start: '2023-01-01', end: '2025-03-31',
      status: 'SUCCESS',
      created: 'Apr 01, 2026 · 09:18 AM',
      completed: 'Apr 01, 2026 · 09:20 AM',
      pinned: false,
      notes: 'Comparing writers vs non-writers of competitor'
    },
    {
      id: 'scen-005',
      name: 'TYVASO Channel Level Q1 2025',
      product: 'TYVASO',
      level: 'Channel',
      segment: 'Cluster',
      start: '2025-01-01', end: '2025-03-31',
      status: 'FAILED',
      created: 'Mar 31, 2026 · 16:44 PM',
      completed: null,
      pinned: false,
      notes: ''
    }
  ],

  results: {
    'scen-001': {
      summary_kpis: { total_hcps: '1,534', total_referrals: '11,138', total_touchpoints: '90,777', total_prescribers: '2,701' },
      team_summary: [
        { team:'SALES',   pct:59, referrals:6571, color:'#FFB162' },
        { team:'MDD',     pct:17, referrals:1893, color:'#2C3B4D' },
        { team:'MSL',     pct:10, referrals:1114, color:'#4A6B8A' },
        { team:'RNS',     pct:5,  referrals:557,  color:'#7FA3C0' },
        { team:'SPK PGM', pct:5,  referrals:557,  color:'#C9C1B1' },
        { team:'EMAIL',   pct:3,  referrals:334,  color:'#D8D0C4' }
      ],
      channels: [
        { channel:'SALES_Live_Call',     team:'SALES',   pct:41, hcps:1209, touchpoints:73219, prescribers:2108 },
        { channel:'MDD_Live_Call',       team:'MDD',     pct:10, hcps:477,  touchpoints:6981,  prescribers:721  },
        { channel:'MSL_Live_Call',       team:'MSL',     pct:8,  hcps:447,  touchpoints:4301,  prescribers:647  },
        { channel:'SALES_Virtual_Call',  team:'SALES',   pct:6,  hcps:892,  touchpoints:12400, prescribers:890  },
        { channel:'MDD_PhoneEmail_Call', team:'MDD',     pct:5,  hcps:280,  touchpoints:3200,  prescribers:312  },
        { channel:'Speaker_Pgm_Live',    team:'SPK PGM', pct:5,  hcps:625,  touchpoints:2411,  prescribers:454  },
        { channel:'MSL_Virtual_Call',    team:'MSL',     pct:3,  hcps:290,  touchpoints:2100,  prescribers:280  },
        { channel:'Email_Clicked',       team:'EMAIL',   pct:3,  hcps:320,  touchpoints:2297,  prescribers:225  },
        { channel:'RNS_Live_Call',       team:'RNS',     pct:3,  hcps:280,  touchpoints:980,   prescribers:180  },
        { channel:'MDD_Virtual_Call',    team:'MDD',     pct:2,  hcps:220,  touchpoints:1800,  prescribers:160  },
        { channel:'MSL_PhoneEmail_Call', team:'MSL',     pct:2,  hcps:195,  touchpoints:1200,  prescribers:140  },
        { channel:'Speaker_Pgm_Virtual', team:'SPK PGM', pct:2,  hcps:410,  touchpoints:1800,  prescribers:320  },
        { channel:'RNS_Virtual_Call',    team:'RNS',     pct:2,  hcps:220,  touchpoints:588,   prescribers:120  },
        { channel:'RNS_PhoneEmail_Call', team:'RNS',     pct:1,  hcps:180,  touchpoints:420,   prescribers:90   },
        { channel:'MSL_Conference_Call', team:'MSL',     pct:1,  hcps:120,  touchpoints:300,   prescribers:80   },
        { channel:'MDD_Conference_Call', team:'MDD',     pct:0,  hcps:80,   touchpoints:200,   prescribers:40   }
      ],
      heatmap: {
        segments: ['High P.','Moderate P.','Average P.','Low P.','Near Sleep.','Sleeping','Unresponsive'],
        rows: [
          { channel:'SALES_Live_Call',    values:[34,33,27,47,31,33,33] },
          { channel:'MDD_Live_Call',      values:[12,10,8,15,9,10,11] },
          { channel:'MSL_Live_Call',      values:[9,8,7,10,7,8,9] },
          { channel:'SALES_Virtual_Call', values:[7,6,5,8,5,6,6] },
          { channel:'Speaker_Pgm_Live',   values:[6,5,5,7,5,5,5] },
          { channel:'Email_Clicked',      values:[3,3,4,3,4,3,3] }
        ]
      }
    },
    'scen-002': {
      summary_kpis: { total_hcps: '1,421', total_referrals: '9,842', total_touchpoints: '78,340', total_prescribers: '2,310' },
      team_summary: [
        { team:'SALES',   pct:52, referrals:5118, color:'#FFB162' },
        { team:'MDD',     pct:21, referrals:2067, color:'#2C3B4D' },
        { team:'MSL',     pct:12, referrals:1181, color:'#4A6B8A' },
        { team:'RNS',     pct:4,  referrals:394,  color:'#7FA3C0' },
        { team:'SPK PGM', pct:5,  referrals:492,  color:'#C9C1B1' },
        { team:'EMAIL',   pct:4,  referrals:394,  color:'#D8D0C4' }
      ],
      channels: [
        { channel:'SALES',   team:'SALES',   pct:52, hcps:1190, touchpoints:63350, prescribers:1840 },
        { channel:'MDD',     team:'MDD',     pct:21, hcps:920,  touchpoints:9800,  prescribers:760  },
        { channel:'MSL',     team:'MSL',     pct:12, hcps:690,  touchpoints:4900,  prescribers:430  },
        { channel:'SPK PGM', team:'SPK PGM', pct:5,  hcps:510,  touchpoints:2200,  prescribers:190  },
        { channel:'RNS',     team:'RNS',     pct:4,  hcps:380,  touchpoints:1200,  prescribers:140  },
        { channel:'EMAIL',   team:'EMAIL',   pct:4,  hcps:410,  touchpoints:2890,  prescribers:150  }
      ],
      heatmap: {
        segments: ['High P.','Moderate P.','Average P.','Low P.','Near Sleep.','Sleeping','Unresponsive'],
        rows: [
          { channel:'SALES',   values:[48,45,40,60,42,44,44] },
          { channel:'MDD',     values:[24,21,18,28,20,21,22] },
          { channel:'MSL',     values:[14,12,10,16,11,12,13] },
          { channel:'SPK PGM', values:[6,5,5,7,5,5,5] },
          { channel:'RNS',     values:[4,4,4,5,4,4,4] },
          { channel:'EMAIL',   values:[4,3,4,3,4,3,3] }
        ]
      }
    }
  },

  schemaColumns: [
    { name:'scenario_id', type:'STRING', cat:'Run Config', desc:'UUID identifying the scenario run' },
    { name:'run_product', type:'STRING', cat:'Run Config', desc:'Product parameter used for this run' },
    { name:'run_segment', type:'STRING', cat:'Run Config', desc:'HCP segment filter used' },
    { name:'run_level',   type:'STRING', cat:'Run Config', desc:'Attribution granularity: Touchpoint / Channel / Team' },
    { name:'run_start',   type:'DATE',   cat:'Run Config', desc:'Observation window start date' },
    { name:'run_end',     type:'DATE',   cat:'Run Config', desc:'Observation window end date' },
    { name:'run_timestamp', type:'TIMESTAMP', cat:'Run Config', desc:'When the model completed' },
    { name:'Product', type:'STRING', cat:'Run Config', desc:'Product being attributed' },
    { name:'Channel', type:'STRING', cat:'Run Config', desc:'The marketing channel / touchpoint / team' },
    { name:'Attribution_Pct_High_Performer',     type:'DOUBLE', cat:'Attribution %', desc:'Markov attribution share for High Performer HCPs (0.0–1.0)' },
    { name:'Attribution_Pct_Moderate_Performer', type:'DOUBLE', cat:'Attribution %', desc:'Attribution share for Moderate Performer HCPs' },
    { name:'Attribution_Pct_Average_Performer',  type:'DOUBLE', cat:'Attribution %', desc:'Attribution share for Average Performer HCPs' },
    { name:'Attribution_Pct_Low_Performer',      type:'DOUBLE', cat:'Attribution %', desc:'Attribution share for Low Performer HCPs' },
    { name:'Attribution_Pct_Near_Sleeping',      type:'DOUBLE', cat:'Attribution %', desc:'Attribution for HCPs with low recent engagement' },
    { name:'Attribution_Pct_Sleeping',           type:'DOUBLE', cat:'Attribution %', desc:'Attribution for HCPs with very low engagement' },
    { name:'Attribution_Pct_Unresponsive',       type:'DOUBLE', cat:'Attribution %', desc:'Attribution for HCPs with near-zero engagement' },
    { name:'Attribution_Pct_All_HCPs',           type:'STRING', cat:'Attribution %', desc:'Attribution for entire HCP universe — null when segment != All HCPs' },
    { name:'Attribution_Pct_does_not_writes',    type:'STRING', cat:'Attribution %', desc:'HCPs who do NOT prescribe competitor drugs' },
    { name:'Attribution_Pct_writes',             type:'STRING', cat:'Attribution %', desc:'HCPs who DO prescribe competitor drugs (Yutrepia, Uptravi, Winrevair)' },
    { name:'Attribution_Pct_0_2_Years',          type:'STRING', cat:'Attribution %', desc:'HCPs with 0–2 years since first referral (LOB segment)' },
    { name:'Attribution_Pct_2_10_Years',         type:'STRING', cat:'Attribution %', desc:'HCPs with 2–10 years since first referral' },
    { name:'Attribution_Pct_10_plus_Years',      type:'STRING', cat:'Attribution %', desc:'HCPs with 10+ years since first referral' },
    { name:'no_of_hcp_High_Performer',           type:'BIGINT', cat:'HCP Counts', desc:'Count of High Performer HCPs reached by this channel' },
    { name:'no_of_hcp_Moderate_Performer',       type:'BIGINT', cat:'HCP Counts', desc:'Count of Moderate Performer HCPs reached' },
    { name:'no_of_hcp_Average_Performer',        type:'BIGINT', cat:'HCP Counts', desc:'Count of Average Performer HCPs reached' },
    { name:'no_of_hcp_Low_Performer',            type:'BIGINT', cat:'HCP Counts', desc:'Count of Low Performer HCPs reached' },
    { name:'no_of_hcp_Near_Sleeping',            type:'BIGINT', cat:'HCP Counts', desc:'Count of Near Sleeping HCPs reached' },
    { name:'no_of_hcp_Sleeping',                 type:'BIGINT', cat:'HCP Counts', desc:'Count of Sleeping HCPs reached' },
    { name:'no_of_hcp_Unresponsive',             type:'BIGINT', cat:'HCP Counts', desc:'Count of Unresponsive HCPs reached' },
    { name:'no_of_hcp_All_HCPs',                 type:'STRING', cat:'HCP Counts', desc:'Total unique HCPs reached by this channel' },
    { name:'total_touchpoints_High_Performer',   type:'BIGINT', cat:'Touchpoints', desc:'Sum of touchpoints delivered to High Performer HCPs' },
    { name:'total_touchpoints_Moderate_Performer',type:'BIGINT',cat:'Touchpoints', desc:'Sum of touchpoints to Moderate Performer HCPs' },
    { name:'total_touchpoints_Average_Performer', type:'BIGINT',cat:'Touchpoints', desc:'Sum of touchpoints to Average Performer HCPs' },
    { name:'total_touchpoints_Low_Performer',    type:'BIGINT', cat:'Touchpoints', desc:'Sum of touchpoints to Low Performer HCPs' },
    { name:'total_touchpoints_All_HCPs',         type:'STRING', cat:'Touchpoints', desc:'Total touchpoints across all HCPs' },
    { name:'no_of_prescribers_High_Performer',   type:'BIGINT', cat:'Prescribers', desc:'Count of prescribers in High Performer segment' },
    { name:'no_of_prescribers_Moderate_Performer',type:'BIGINT',cat:'Prescribers', desc:'Count of prescribers in Moderate Performer segment' },
    { name:'no_of_prescribers_All_HCPs',         type:'STRING', cat:'Prescribers', desc:'Total prescribers across universe' },
    { name:'total_touchpoints_to_prescribers_High_Performer', type:'BIGINT', cat:'Prescribers', desc:'Touchpoints delivered to eventual High Performer prescribers — efficiency signal' },
    { name:'total_touchpoints_to_prescribers_All_HCPs',       type:'STRING', cat:'Prescribers', desc:'Total touchpoints to all eventual prescribers' }
  ],

  journeyData: {
    periods: ['Jan 23','Apr 23','Jul 23','Oct 23','Jan 24','Apr 24','Jul 24','Oct 24','Jan 25','Mar 25'],
    segments: [
      { name:'High Performer',    color:'#FFB162', counts:[490,512,525,540,552,559,565,570,578,582] },
      { name:'Moderate Performer',color:'#4A6B8A', counts:[198,205,210,215,220,226,228,232,235,238] },
      { name:'Average Performer', color:'#7FA3C0', counts:[255,260,258,264,265,264,268,268,270,272] },
      { name:'Low Performer',     color:'#C9C1B1', counts:[62,62,60,58,57,58,57,58,58,57]  },
      { name:'Near Sleeping',     color:'#D8D0C4', counts:[65,62,60,58,57,58,57,56,55,55]  },
      { name:'Sleeping',          color:'#A35139', counts:[135,132,130,128,126,128,127,126,125,124] },
      { name:'Unresponsive',      color:'#1B2632', counts:[210,208,207,205,204,205,203,202,200,200] }
    ]
  }
};
