const ACCENT_PALETTE = [
  '#0F766E', '#B45309', '#BE123C', '#047857', '#A16207',
  '#334155', '#0E7490', '#9F1239', '#15803D', '#92400E',
  '#0F766E', '#B91C1C', '#166534', '#475569', '#CA8A04',
  '#0F766E', '#854D0E', '#0E7490', '#365314', '#A21CAF',
];

function tickerColor(ticker) {
  let h = 0;
  for (let i = 0; i < ticker.length; i++) h = (h * 31 + ticker.charCodeAt(i)) >>> 0;
  return ACCENT_PALETTE[h % ACCENT_PALETTE.length];
}

function fmtPct(x, digits = 1) {
  if (x === null || x === undefined || Number.isNaN(x)) return '—';
  const sign = x >= 0 ? '+' : '';
  return `${sign}${(x * 100).toFixed(digits)}%`;
}

function fmtMoney(x) {
  if (x === null || x === undefined || Number.isNaN(x)) return '—';
  return `$${Math.round(x).toLocaleString()}`;
}

function fmtDay(s) {
  if (!s) return '';
  const d = new Date(s + 'T00:00');
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function fmtMonth(s) {
  if (!s) return '';
  const d = new Date(s + 'T00:00');
  return d.toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
}

function bgFromReturn(ret, maxAbs) {
  if (ret === null || ret === undefined) return '#FFFFFF';
  const intensity = Math.min(1, Math.pow(Math.abs(ret) / Math.max(maxAbs, 1e-9), 0.6));
  const pos = [220, 245, 237];
  const neg = [255, 228, 230];
  const neutral = [250, 248, 244];
  const target = ret >= 0 ? pos : neg;
  const c = neutral.map((n, i) => Math.round(n + (target[i] - n) * intensity));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

function pickCard(pick, opts = {}) {
  const { isOpen = false, compact = false, maxAbs = 0.5, rankLabel = null } = opts;
  const color = tickerColor(pick.ticker);
  const bg = bgFromReturn(pick.stock_return, maxAbs);
  const positive = (pick.stock_return ?? 0) >= 0;
  const retColor = positive ? 'text-teal-700' : 'text-rose-700';
  const border = isOpen ? 'border-2 border-dashed border-teal-700' : 'border border-stone-300';

  if (compact) {
    return `
      <div class="card rounded-lg ${border} bg-white overflow-hidden flex items-stretch">
        <div class="w-1" style="background:${color}"></div>
        <div class="flex-1 flex items-center justify-between px-2.5 py-1.5" style="background:${bg}">
          <div class="text-sm font-bold text-zinc-950 leading-tight">${pick.ticker}</div>
          <div class="text-sm font-semibold ${retColor} leading-tight">${fmtPct(pick.stock_return)}</div>
        </div>
      </div>
    `;
  }

  return `
    <div class="card rounded-xl ${border} bg-white overflow-hidden">
      <div class="accent-stripe" style="background:${color}"></div>
      <div class="p-5" style="background:${bg}">
        <div class="flex items-center justify-between">
          <div class="text-3xl font-bold text-zinc-950">${pick.ticker}</div>
          <div class="text-[10px] text-zinc-600 font-medium">${rankLabel || `#${pick.rank}`}</div>
        </div>
        <div class="mt-1 text-lg font-semibold ${retColor}">${fmtPct(pick.stock_return)}</div>
        <div class="mt-2 text-[10px] font-semibold tracking-wider px-1.5 py-0.5 rounded bg-stone-200 text-zinc-700 inline-block">MTD</div>
      </div>
    </div>
  `;
}

function renderStats(data) {
  const stats = data.stats || {};
  const card = (label, value, sub) => `
    <div class="rounded-xl bg-white border border-stone-300 p-4">
      <div class="text-xs font-medium text-zinc-600 uppercase tracking-wider">${label}</div>
      <div class="text-2xl font-bold text-zinc-950 mt-1">${value}</div>
      ${sub ? `<div class="text-xs text-zinc-600 mt-1">${sub}</div>` : ''}
    </div>
  `;
  document.getElementById('stats-grid').innerHTML = [
    card('CAGR', fmtPct(stats.cagr), `SPY value ${fmtMoney(stats.spy_value)}`),
    card('Final value', fmtMoney(stats.final_value), 'from $100,000 initial capital'),
    card('Max drawdown', fmtPct(stats.max_drawdown), `Sharpe ${(stats.sharpe ?? 0).toFixed(2)}`),
    card('Win vs SPY', fmtPct(stats.win_rate_vs_spy), `Turnover ${fmtPct(stats.average_turnover)}/mo`),
  ].join('');
}

function renderOverlay(data) {
  const overlay = data.nasdaq_overlay || {};
  const excluded = overlay.excluded || [];
  const adjusted = overlay.adjusted || [];
  const maxAbs = Math.max(...adjusted.map(p => Math.abs(p.stock_return || 0)), 0.1);
  document.getElementById('overlay-note').textContent =
    `Excluded Nasdaq open picks: ${excluded.join(', ') || 'none'}. Backfilled from the next S&P 500 Titan-12 ranks.`;
  document.getElementById('overlay-grid').innerHTML = adjusted
    .map(p => pickCard(p, { isOpen: true, maxAbs, rankLabel: `S&P rank #${p.rank}` }))
    .join('');
}

function renderHistory(data) {
  const recent = data.recent || [];
  document.getElementById('history-count').textContent = recent.length;
  const allPicks = recent.flatMap(r => r.picks || []);
  const maxAbs = Math.max(...allPicks.map(p => Math.abs(p.stock_return || 0)), 0.1);
  document.getElementById('history-list').innerHTML = recent.slice().reverse().map(row => {
    const retColor = row.portfolio_return >= 0 ? 'text-teal-700' : 'text-rose-700';
    return `
      <div class="rounded-lg bg-white border border-stone-300 px-3 py-2 flex items-center gap-3">
        <div class="w-28 flex-shrink-0 flex items-baseline gap-2">
          <div class="text-xs font-semibold text-zinc-700 leading-tight">${row.label}</div>
          <div class="text-xs font-bold ${retColor} leading-tight">${fmtPct(row.portfolio_return)}</div>
        </div>
        <div class="flex-1">
          <div class="mb-1 text-[10px] text-zinc-500">Excluded: ${(row.excluded || []).join(', ') || 'none'}</div>
          <div class="grid grid-cols-3 gap-2">
          ${row.picks.map(p => pickCard(p, { compact: true, maxAbs })).join('')}
          </div>
        </div>
      </div>
    `;
  }).join('');

  const w = data.window || {};
  document.getElementById('window-cum').innerHTML =
    `Adjusted <span class="font-semibold text-teal-700">${fmtPct(w.strategy_return, 1)}</span>
     · SPY <span class="font-medium text-zinc-700">${fmtPct(w.spy_return, 1)}</span>`;
}

function renderUpdated(data) {
  const dt = new Date(data.computed_at);
  document.getElementById('last-updated').innerHTML = `
    <div>updated ${dt.toLocaleString(undefined, { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}</div>
    <div class="text-[10px] text-zinc-500">prices through ${fmtDay(data.data_freshness)}</div>
  `;
}

async function load() {
  const refreshBtn = document.getElementById('refresh-btn');
  const refreshLabel = document.getElementById('refresh-label');
  const refreshIcon = document.getElementById('refresh-icon');
  const err = document.getElementById('error');
  err.classList.add('hidden');
  refreshBtn.disabled = true;
  refreshLabel.textContent = 'Loading…';
  refreshIcon.classList.add('animate-spin');
  try {
    let resp = await fetch('/api/dashboard', { cache: 'no-store' });
    if (!resp.ok) {
      resp = await fetch('/dashboard.json', { cache: 'no-store' });
    }
    if (!resp.ok) throw new Error(`HTTP ${resp.status} while loading dashboard data`);
    const data = await resp.json();
    renderStats(data);
    renderOverlay(data);
    renderHistory(data);
    renderUpdated(data);
  } catch (e) {
    err.textContent = `Failed to load dashboard: ${e.message}`;
    err.classList.remove('hidden');
  } finally {
    refreshBtn.disabled = false;
    refreshLabel.textContent = 'Refresh';
    refreshIcon.classList.remove('animate-spin');
  }
}

document.getElementById('refresh-btn').addEventListener('click', load);
load();
