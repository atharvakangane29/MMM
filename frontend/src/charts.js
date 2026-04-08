// js/charts.js — All chart rendering functions

const charts = {

  // ── DONUT CHART (SVG) ──
  donut(container, data, centerLabel = 'Attribution') {
    const size = 180;
    const cx = size / 2;
    const cy = size / 2;
    const r = 65;
    const ri = 42;
    const gap = 0.02;

    const total = data.reduce((s, d) => s + d.pct, 0);
    let angle = -Math.PI / 2;

    const paths = data.map(d => {
      const sweep = (d.pct / total) * (Math.PI * 2) - gap;
      const x1 = cx + r * Math.cos(angle);
      const y1 = cy + r * Math.sin(angle);
      const x2 = cx + r * Math.cos(angle + sweep);
      const y2 = cy + r * Math.sin(angle + sweep);
      const xi1 = cx + ri * Math.cos(angle);
      const yi1 = cy + ri * Math.sin(angle);
      const xi2 = cx + ri * Math.cos(angle + sweep);
      const yi2 = cy + ri * Math.sin(angle + sweep);
      const large = sweep > Math.PI ? 1 : 0;

      const path = `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} L ${xi2} ${yi2} A ${ri} ${ri} 0 ${large} 0 ${xi1} ${yi1} Z`;
      angle += sweep + gap;
      return `<path d="${path}" fill="${d.color}" opacity="0.92" class="donut-segment" data-label="${d.team}" data-val="${d.pct}%" style="cursor:pointer;transition:opacity 0.15s">
        <title>${d.team}: ${d.pct}%</title>
      </path>`;
    }).join('');

    container.innerHTML = `
      <div class="donut-chart">
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
          ${paths}
        </svg>
        <div class="donut-center">
          <div class="donut-center-val">${total}%</div>
          <div class="donut-center-label">${centerLabel}</div>
        </div>
      </div>
      <div class="chart-legend">
        ${data.map(d => `<div class="legend-item"><div class="legend-dot" style="background:${d.color}"></div>${d.team} <strong>${d.pct}%</strong></div>`).join('')}
      </div>`;

    // Hover effects
    container.querySelectorAll('.donut-segment').forEach(path => {
      path.addEventListener('mouseenter', () => path.style.opacity = '1');
      path.addEventListener('mouseleave', () => path.style.opacity = '0.92');
    });
  },

  // ── HORIZONTAL BAR CHART (Channel Attribution) ──
  channelBars(container, channels, showAll = false) {
    const visible = showAll ? channels : channels.slice(0, 8);
    const maxPct = Math.max(...channels.map(c => c.pct));

    const teamColors = { SALES:'#FFB162', MDD:'#2C3B4D', MSL:'#4A6B8A', 'SPK PGM':'#C9C1B1', RNS:'#7FA3C0', EMAIL:'#D8D0C4' };

    container.innerHTML = `
      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Channel</th>
              <th>Attribution %</th>
              <th>HCPs Reached</th>
              <th>Touchpoints</th>
              <th>Prescribers</th>
            </tr>
          </thead>
          <tbody>
            ${visible.map((c, i) => {
              const barWidth = (c.pct / maxPct) * 100;
              const color = teamColors[c.team] || '#7FA3C0';
              const isTop = i === 0;
              return `<tr class="${isTop ? 'highlight' : ''}">
                <td>
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${color};flex-shrink:0"></span>
                    <span style="font-weight:${isTop?700:400}">${c.channel}</span>
                  </div>
                </td>
                <td>
                  <div class="inline-bar-wrap">
                    <div class="inline-bar-track">
                      <div class="inline-bar-fill" style="width:0%;background:${color}" data-target="${barWidth}"></div>
                    </div>
                    <span class="inline-bar-val">${c.pct}%</span>
                  </div>
                </td>
                <td class="mono" style="font-size:12px">${c.hcps.toLocaleString()}</td>
                <td class="mono" style="font-size:12px">${c.touchpoints.toLocaleString()}</td>
                <td class="mono" style="font-size:12px">${c.prescribers.toLocaleString()}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
      ${!showAll && channels.length > 8 ? `<button class="btn btn-ghost btn-sm" style="margin-top:8px;width:100%" id="show-all-channels">Show all ${channels.length} channels ↓</button>` : ''}`;

    // Animate bars
    requestAnimationFrame(() => {
      container.querySelectorAll('.inline-bar-fill[data-target]').forEach(bar => {
        setTimeout(() => { bar.style.width = bar.dataset.target + '%'; }, 100);
      });
    });

    const showAllBtn = container.querySelector('#show-all-channels');
    if (showAllBtn) {
      showAllBtn.addEventListener('click', () => {
        this.channelBars(container, channels, true);
      });
    }
  },

  // ── HEATMAP ──
  heatmap(container, data) {
    const maxVal = Math.max(...data.rows.flatMap(r => r.values));
    const minVal = Math.min(...data.rows.flatMap(r => r.values));

    function getColor(val) {
      const t = (val - minVal) / (maxVal - minVal);
      if (t < 0.33) return `hsl(210,30%,${90 - t * 30}%)`;
      if (t < 0.66) return `hsl(210,45%,${77 - t * 25}%)`;
      return `hsl(210,55%,${60 - t * 30}%)`;
    }
    function getTextColor(val) {
      const t = (val - minVal) / (maxVal - minVal);
      return t > 0.6 ? '#fff' : 'var(--blue)';
    }

    container.innerHTML = `<div class="heatmap-wrap">
      <table class="heatmap-table">
        <thead>
          <tr>
            <th>Channel</th>
            ${data.segments.map(s => `<th>${s}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.rows.map(row => `<tr>
            <td>${row.channel}</td>
            ${row.values.map(v => `<td style="background:${getColor(v)};color:${getTextColor(v)}" title="${row.channel} — ${data.segments[row.values.indexOf(v)]||''}: ${v}%">${v}%</td>`).join('')}
          </tr>`).join('')}
        </tbody>
      </table>
    </div>`;
  },

  // ── SANKEY DIAGRAM (SVG Canvas) ──
  sankey(container) {
    const w = container.clientWidth || 700;
    const h = 380;

    const teamColors = {
      'SALES': '#FFB162', 'MDD': '#2C3B4D', 'MSL': '#4A6B8A',
      'RNS': '#7FA3C0', 'SPK PGM': '#C9C1B1', 'EMAIL': '#D8D0C4'
    };

    // Simplified SVG Sankey
    const nodes = {
      teams: [
        { id:'SALES', y:30, h:120, color:'#FFB162' },
        { id:'MDD',   y:165, h:45, color:'#2C3B4D' },
        { id:'MSL',   y:223, h:28, color:'#4A6B8A' },
        { id:'RNS',   y:263, h:15, color:'#7FA3C0' },
        { id:'SPK PGM',y:288,h:15, color:'#C9C1B1' },
        { id:'EMAIL', y:313, h:10, color:'#D8D0C4' }
      ],
      channels: [
        { id:'SALES Live',  y:20,  h:85,  color:'#FFB162' },
        { id:'SALES Virtual',y:115,h:30,  color:'#FFB162' },
        { id:'MDD Live',    y:158, h:28,  color:'#2C3B4D' },
        { id:'MDD Phone',   y:196, h:16,  color:'#2C3B4D' },
        { id:'MSL Live',    y:222, h:22,  color:'#4A6B8A' },
        { id:'Spk Pgm',     y:254, h:15,  color:'#C9C1B1' },
        { id:'Email',       y:278, h:10,  color:'#D8D0C4' }
      ],
      segments: [
        { id:'High Performer',    y:10,  h:70,  color:'#FFB162' },
        { id:'Moderate Performer',y:90,  h:40,  color:'#4A6B8A' },
        { id:'Average Performer', y:140, h:45,  color:'#7FA3C0' },
        { id:'Low Performer',     y:195, h:18,  color:'#C9C1B1' },
        { id:'Near Sleeping',     y:223, h:15,  color:'#D8D0C4' },
        { id:'Sleeping',          y:248, h:22,  color:'#A35139' },
        { id:'Unresponsive',      y:280, h:26,  color:'#1B2632' }
      ],
      outcomes: [
        { id:'Conversion ✓', y:40,  h:190, color:'#FFB162' },
        { id:'No Conversion',y:240, h:90,  color:'#C9C1B1' }
      ]
    };

    const x1 = 10, x2 = w * 0.28, x3 = w * 0.55, x4 = w * 0.78, x5 = w - 100;
    const nodeW = 12;

    // Helper to draw bezier link between two nodes
    function link(x1, y1, h1, x2, y2, h2, color, opacity = 0.35) {
      const cy = y1 + h1/2;
      const cy2 = y2 + h2/2;
      const cp = (x2 - x1) * 0.5;
      return `<path d="M${x1},${y1} C${x1+cp},${y1} ${x2-cp},${y2} ${x2},${y2} L${x2},${y2+h2} C${x2-cp},${y2+h2} ${x1+cp},${y1+h1} ${x1},${y1+h1} Z"
        fill="${color}" opacity="${opacity}" class="sankey-link-path" style="cursor:pointer;transition:opacity 0.15s">
        <title>${color}</title>
      </path>`;
    }

    // Draw node rects
    function nodeRects(nodeList, x) {
      return nodeList.map(n => `
        <rect x="${x}" y="${n.y}" width="${nodeW}" height="${n.h}" fill="${n.color}" rx="2"/>
        <text x="${x < w/2 ? x + nodeW + 5 : x - 5}" y="${n.y + n.h/2 + 4}"
          text-anchor="${x < w/2 ? 'start' : 'end'}"
          fill="var(--blue)" font-size="10" font-family="DM Sans, sans-serif" font-weight="600">${n.id}</text>
      `).join('');
    }

    const svgLinks = [
      // Teams → Channels
      link(x1+nodeW, 30,  120, x2, 20,  85,  '#FFB162', 0.4),
      link(x1+nodeW, 165, 45,  x2, 158, 28,  '#2C3B4D', 0.38),
      link(x1+nodeW, 165, 45,  x2, 196, 16,  '#2C3B4D', 0.28),
      link(x1+nodeW, 223, 28,  x2, 222, 22,  '#4A6B8A', 0.36),
      link(x1+nodeW, 288, 15,  x2, 254, 15,  '#C9C1B1', 0.4),
      link(x1+nodeW, 313, 10,  x2, 278, 10,  '#D8D0C4', 0.4),
      link(x1+nodeW, 30,  120, x2, 115, 30,  '#FFB162', 0.25),
      // Channels → Segments
      link(x2+nodeW, 20,  85,  x3, 10,  70,  '#FFB162', 0.38),
      link(x2+nodeW, 20,  85,  x3, 90,  40,  '#FFB162', 0.28),
      link(x2+nodeW, 115, 30,  x3, 140, 45,  '#FFB162', 0.25),
      link(x2+nodeW, 158, 28,  x3, 90,  40,  '#2C3B4D', 0.3),
      link(x2+nodeW, 196, 16,  x3, 195, 18,  '#2C3B4D', 0.32),
      link(x2+nodeW, 222, 22,  x3, 140, 45,  '#4A6B8A', 0.28),
      link(x2+nodeW, 254, 15,  x3, 248, 22,  '#C9C1B1', 0.35),
      link(x2+nodeW, 278, 10,  x3, 280, 26,  '#D8D0C4', 0.38),
      // Segments → Outcomes
      link(x3+nodeW, 10,  70,  x4, 40,  70,  '#FFB162', 0.45),
      link(x3+nodeW, 90,  40,  x4, 40,  40,  '#4A6B8A', 0.38),
      link(x3+nodeW, 140, 45,  x4, 40,  45,  '#7FA3C0', 0.32),
      link(x3+nodeW, 195, 18,  x4, 240, 18,  '#C9C1B1', 0.35),
      link(x3+nodeW, 223, 15,  x4, 240, 15,  '#D8D0C4', 0.35),
      link(x3+nodeW, 248, 22,  x4, 240, 22,  '#A35139', 0.38),
      link(x3+nodeW, 280, 26,  x4, 240, 26,  '#1B2632', 0.38),
    ].join('');

    // Outcome → terminal
    const termLinks = `
      ${link(x4+nodeW, 40, 190, x5, 30, 190, '#FFB162', 0.45)}
      ${link(x4+nodeW, 240, 90, x5, 240, 90, '#C9C1B1', 0.38)}
    `;

    // Terminal labels
    const terminals = `
      <rect x="${x5}" y="30" width="${nodeW}" height="190" fill="#FFB162" rx="2"/>
      <text x="${x5+nodeW+5}" y="130" fill="var(--blue)" font-size="11" font-family="DM Sans" font-weight="700">Conversion ✓</text>
      <rect x="${x5}" y="240" width="${nodeW}" height="90" fill="#C9C1B1" rx="2"/>
      <text x="${x5+nodeW+5}" y="290" fill="var(--blue-mid)" font-size="11" font-family="DM Sans" font-weight="600">No Conversion</text>
    `;

    // Layer headers
    const headers = `
      <text x="${x1+6}" y="350" text-anchor="middle" fill="var(--blue-mid)" font-size="9" font-family="DM Sans" font-weight="700" letter-spacing="0.08em" text-transform="uppercase">TEAM</text>
      <text x="${x2+6}" y="350" text-anchor="middle" fill="var(--blue-mid)" font-size="9" font-family="DM Sans" font-weight="700" letter-spacing="0.08em">CHANNEL</text>
      <text x="${x3+6}" y="350" text-anchor="middle" fill="var(--blue-mid)" font-size="9" font-family="DM Sans" font-weight="700" letter-spacing="0.08em">SEGMENT</text>
      <text x="${x4+6}" y="350" text-anchor="middle" fill="var(--blue-mid)" font-size="9" font-family="DM Sans" font-weight="700" letter-spacing="0.08em">OUTCOME</text>
    `;

    container.innerHTML = `
      <svg width="100%" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">
        <defs>
          <style>.sankey-link-path:hover{opacity:0.65!important}</style>
        </defs>
        ${svgLinks}
        ${termLinks}
        ${nodeRects(nodes.teams, x1)}
        ${nodeRects(nodes.channels, x2)}
        ${nodeRects(nodes.segments, x3)}
        ${nodeRects(nodes.outcomes, x4)}
        ${terminals}
        ${headers}
      </svg>`;
  },

  // ── HCP JOURNEY CHART ──
  journey(container) {
    const data = MOCK.journeyData;
    const w = container.clientWidth || 700;
    const h = 200;
    const padLeft = 110, padRight = 20, padTop = 10, padBottom = 30;
    const chartW = w - padLeft - padRight;
    const chartH = h - padTop - padBottom;
    const nPeriods = data.periods.length;
    const maxCount = Math.max(...data.segments.flatMap(s => s.counts));

    function xPos(i) { return padLeft + (i / (nPeriods - 1)) * chartW; }
    function yPos(val) { return padTop + (1 - val / maxCount) * chartH; }

    const paths = data.segments.map(seg => {
      const pts = seg.counts.map((c, i) => `${xPos(i)},${yPos(c)}`).join(' ');
      const smooth = data.segments.indexOf(seg);
      return `<polyline points="${pts}" stroke="${seg.color}" stroke-width="2.5" fill="none" opacity="${smooth < 4 ? 0.9 : 0.6}" stroke-linejoin="round"/>`;
    }).join('');

    const dots = data.segments.flatMap(seg =>
      seg.counts.map((c, i) => `<circle cx="${xPos(i)}" cy="${yPos(c)}" r="3" fill="${seg.color}" opacity="0.8">
        <title>${seg.name}: ${c.toLocaleString()} HCPs — ${data.periods[i]}</title>
      </circle>`)
    ).join('');

    const xLabels = data.periods.map((p, i) =>
      `<text x="${xPos(i)}" y="${h - 5}" text-anchor="middle" font-size="8" fill="var(--blue-mid)" font-family="DM Sans">${p}</text>`
    ).join('');

    const gridLines = [0, 0.25, 0.5, 0.75, 1].map(t => {
      const y = padTop + t * chartH;
      const val = Math.round((1 - t) * maxCount);
      return `<line x1="${padLeft}" y1="${y}" x2="${w-padRight}" y2="${y}" stroke="var(--sand)" stroke-width="1"/>
        <text x="${padLeft - 5}" y="${y + 4}" text-anchor="end" font-size="8" fill="var(--blue-mid)" font-family="DM Sans">${val}</text>`;
    }).join('');

    const legend = data.segments.map(seg =>
      `<div class="legend-item"><div class="legend-dot" style="background:${seg.color}"></div>${seg.name}</div>`
    ).join('');

    container.innerHTML = `
      <svg width="100%" height="${h}" viewBox="0 0 ${w} ${h}">
        ${gridLines}
        ${paths}
        ${dots}
        ${xLabels}
      </svg>
      <div class="chart-legend" style="margin-top:8px">${legend}</div>`;
  },

  // ── WATERFALL CHART ──
  waterfall(container, compData) {
    const scA = compData[0];
    const scB = compData[1];

    // Calculate deltas by team
    const teams = scA.team_summary.map(t => t.team);
    const aVals = Object.fromEntries(scA.team_summary.map(t => [t.team, t.pct]));
    const bVals = Object.fromEntries(scB.team_summary.map(t => [t.team, t.pct]));

    const cols = teams.map(t => ({
      label: t,
      delta: (bVals[t] || 0) - (aVals[t] || 0),
      isPositive: (bVals[t] || 0) >= (aVals[t] || 0)
    }));

    const maxAbs = Math.max(...cols.map(c => Math.abs(c.delta)));
    const barMaxH = 160;

    container.innerHTML = `
      <div class="waterfall-wrap">
        <div style="display:flex;gap:4px;align-items:flex-end;height:${barMaxH + 40}px;padding:8px 0 0">
          ${cols.map(c => {
            const h = maxAbs > 0 ? (Math.abs(c.delta) / maxAbs) * barMaxH : 4;
            const sign = c.delta > 0 ? '+' : '';
            return `<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;justify-content:flex-end">
              <span style="font-size:10px;font-weight:700;color:${c.isPositive ? 'var(--amber)' : 'var(--flame)'}">${sign}${c.delta.toFixed(1)}pp</span>
              <div style="width:100%;height:${Math.max(h, 4)}px;border-radius:3px 3px 0 0;background:${c.isPositive ? 'var(--amber)' : 'var(--flame)'}"></div>
              <div style="height:2px;width:100%;background:var(--sand)"></div>
              <span style="font-size:9px;text-align:center;color:var(--blue-mid);font-weight:600;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.label}</span>
            </div>`;
          }).join('')}
        </div>
        <div style="margin-top:10px;font-size:11px;color:var(--blue-mid);text-align:center">
          Δ = <strong style="color:var(--blue)">${scB.name||'Scenario B'}</strong> vs <strong style="color:var(--blue)">${scA.name||'Scenario A'}</strong> (pp difference)
        </div>
      </div>`;
  },

  // ── COMPARISON GROUPED BAR ──
  comparisonBars(container, scA, scB, mode = 'side-by-side') {
    const channels = scA.channels.map(c => c.channel || c.team);
    const aVals = scA.channels.map(c => c.pct);
    const bVals = scB.channels.map(c => c.pct);
    const maxVal = Math.max(...aVals, ...bVals);
    const barMaxW = 160;

    if (mode === 'delta') {
      container.innerHTML = `
        <div class="data-table-wrap">
          <table class="data-table">
            <thead><tr>
              <th>Channel</th>
              <th>${scA.scenario_name||'Scenario A'}</th>
              <th>${scB.scenario_name||'Scenario B'}</th>
              <th>Δ pp</th>
              <th>Δ Relative</th>
            </tr></thead>
            <tbody>
              ${channels.map((ch, i) => {
                const a = aVals[i] || 0;
                const b = bVals[i] || 0;
                const diff = b - a;
                const rel = a > 0 ? ((diff / a) * 100).toFixed(1) : '—';
                const cls = diff > 0 ? 'delta-positive' : diff < 0 ? 'delta-negative' : 'delta-neutral';
                const arrow = diff > 0 ? '▲' : diff < 0 ? '▼' : '—';
                return `<tr>
                  <td style="font-weight:600">${ch}</td>
                  <td>${a}%</td>
                  <td>${b}%</td>
                  <td class="${cls}">${diff > 0 ? '+' : ''}${diff.toFixed(1)}pp ${arrow}</td>
                  <td class="${cls}">${diff !== 0 ? (diff > 0 ? '+' : '') + rel + '%' : '—'}</td>
                </tr>`;
              }).join('')}
            </tbody>
          </table>
        </div>`;
      return;
    }

    container.innerHTML = `
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;min-width:400px">
          <tbody>
            ${channels.map((ch, i) => {
              const a = aVals[i] || 0;
              const b = bVals[i] || 0;
              const wA = (a / maxVal) * barMaxW;
              const wB = (b / maxVal) * barMaxW;
              return `<tr style="border-bottom:1px solid var(--sand)">
                <td style="padding:6px 10px;font-size:12px;font-weight:600;color:var(--blue);width:160px;white-space:nowrap">${ch}</td>
                <td style="padding:4px 8px;width:${barMaxW+60}px">
                  <div style="display:flex;align-items:center;gap:4px;margin-bottom:3px">
                    <div style="width:${wA}px;height:10px;border-radius:2px;background:#FFB162;transition:width 0.6s"></div>
                    <span style="font-size:11px;font-weight:700;color:var(--blue)">${a}%</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:4px">
                    <div style="width:${wB}px;height:10px;border-radius:2px;background:#4A6B8A;transition:width 0.6s"></div>
                    <span style="font-size:11px;font-weight:700;color:var(--blue)">${b}%</span>
                  </div>
                </td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
        <div style="display:flex;gap:14px;padding:10px;font-size:11px">
          <div style="display:flex;align-items:center;gap:5px"><div style="width:14px;height:10px;border-radius:2px;background:#FFB162"></div><strong>${scA.scenario_name||'Scenario A'}</strong></div>
          <div style="display:flex;align-items:center;gap:5px"><div style="width:14px;height:10px;border-radius:2px;background:#4A6B8A"></div><strong>${scB.scenario_name||'Scenario B'}</strong></div>
        </div>
      </div>`;
  },

  // ── DATE COVERAGE ──
  coverage(container, coverageData) {
    const max = Math.max(...coverageData.map(d => d.count));
    container.innerHTML = `
      <div class="coverage-chart">
        ${coverageData.map(d => {
          const h = d.count > 0 ? Math.max((d.count / max) * 56, 4) : 4;
          const color = d.count === 0 ? 'var(--flame)' : 'var(--amber)';
          return `<div class="coverage-bar" style="height:${h}px;background:${color};opacity:${d.count===0?0.6:0.85}" data-tip="${d.period}: ${d.count} records${d.count===0?' — NO DATA':''}"></div>`;
        }).join('')}
      </div>
      <div class="coverage-x-labels">
        ${coverageData.filter((_,i) => i % 3 === 0).map(d => `<div class="coverage-x-label" style="width:${100/(coverageData.filter((_,i) => i%3===0).length)}%">${d.period}</div>`).join('')}
      </div>`;
  }
};