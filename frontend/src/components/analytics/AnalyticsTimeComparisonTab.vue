<template>
  <section class="time-tab">

    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال مقایسه بازه‌ها...
    </div>

    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">

      <!-- ── Two range summary cards ── -->
      <div class="ranges-grid">
        <article class="range-card glass-card" v-for="side in rangeSides" :key="side.key">
          <div class="range-header">
            <div class="range-dot" :style="`background:${side.color}`"></div>
            <div>
              <h3>{{ side.title }}</h3>
              <span class="range-dates">{{ side.from }} تا {{ side.to }}</span>
            </div>
          </div>
          <div class="range-metrics">
            <div class="metric-row" v-for="m in side.metrics" :key="m.label">
              <span class="metric-label">
                <span class="metric-icon">{{ m.icon }}</span>
                {{ m.label }}
              </span>
              <strong class="metric-val">{{ m.value }}</strong>
            </div>
          </div>
        </article>

        <!-- ── Delta summary card ── -->
        <article class="delta-card glass-card">
          <div class="panel-header">
            <span class="panel-icon">⚖️</span>
            <h3>تفاوت بین دو بازه</h3>
          </div>
          <div class="delta-list">
            <div
              v-for="(value, key) in data.delta || {}"
              :key="key"
              class="delta-row"
            >
              <span class="delta-label">{{ deltaLabel(key) }}</span>
              <div class="delta-right">
                <div class="delta-bar-track">
                  <div
                    class="delta-bar-fill"
                    :class="value >= 0 ? 'pos' : 'neg'"
                    :style="`width:${Math.min(Math.abs(value), 100)}%`"
                  ></div>
                </div>
                <span class="delta-val" :class="value >= 0 ? 'pos' : 'neg'">
                  {{ value >= 0 ? '▲' : '▼' }} {{ fa2(Math.abs(value)) }}٪
                </span>
              </div>
            </div>
            <div v-if="!Object.keys(data.delta || {}).length" class="empty-cell">
              داده‌ای برای مقایسه وجود ندارد.
            </div>
          </div>
        </article>
      </div>

      <!-- ── Revenue overlay chart ── -->
      <article class="panel glass-card" v-if="mergedOverlay.length">
        <div class="panel-header">
          <span class="panel-icon">📊</span>
          <h3>مقایسه درآمد روزانه</h3>
          <div class="chart-legend">
            <span class="legend-dot" style="background:#818cf8"></span>بازه اول
            <span class="legend-dot" style="background:#f97316; margin-right:10px"></span>بازه دوم
          </div>
        </div>

        <!-- Mini bar chart -->
        <div class="overlay-chart">
          <div
            v-for="(row, idx) in mergedOverlay"
            :key="`bar-${idx}`"
            class="overlay-col"
            :title="`${row.date} | بازه اول: ${money(row.leftRevenue)} | بازه دوم: ${money(row.rightRevenue)}`"
          >
            <div class="bar-pair">
              <div
                class="bar left-bar"
                :style="`height:${barHeight(row.leftRevenue)}%`"
              ></div>
              <div
                class="bar right-bar"
                :style="`height:${barHeight(row.rightRevenue)}%`"
              ></div>
            </div>
            <span class="col-label" v-if="idx === 0 || idx === mergedOverlay.length - 1 || idx % Math.ceil(mergedOverlay.length / 5) === 0">
              {{ row.date }}
            </span>
          </div>
        </div>

        <!-- Data table -->
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>تاریخ / دوره</th>
                <th>
                  <span class="th-dot" style="background:#818cf8"></span>
                  درآمد بازه اول
                </th>
                <th>
                  <span class="th-dot" style="background:#f97316"></span>
                  درآمد بازه دوم
                </th>
                <th>اختلاف</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in mergedOverlay" :key="`row-${idx}`">
                <td>{{ row.date }}</td>
                <td class="num left-val">{{ money(row.leftRevenue) }}</td>
                <td class="num right-val">{{ money(row.rightRevenue) }}</td>
                <td class="num">
                  <span
                    class="diff-badge"
                    :class="row.leftRevenue >= row.rightRevenue ? 'pos' : 'neg'"
                  >
                    {{ row.leftRevenue >= row.rightRevenue ? '▲' : '▼' }}
                    {{ money(Math.abs(row.leftRevenue - row.rightRevenue)) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data:    { type: Object,  default: null  },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: ''    },
})

const fa    = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2   = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })
const money = (v) => `${Number(v || 0).toLocaleString('fa-IR')} تومان`

const deltaLabelMap = {
  views:               'بازدید',
  orders:              'سفارش',
  revenue:             'درآمد',
  conversion_rate:     'نرخ تبدیل',
  aov:                 'میانگین ارزش سفارش',
  cart_abandonment_rate: 'ریزش سبد',
}
const deltaLabel = (key) => deltaLabelMap[key] || key

// ── Range side cards ────────────────────────────────────────────────────────
const rangeSides = computed(() => {
  const d = props.data
  return [
    {
      key: 'left', title: 'بازه اول', color: '#818cf8',
      from: d?.left_range?.from_date || '-',
      to:   d?.left_range?.to_date   || '-',
      metrics: [
        { label: 'بازدید',       icon: '👁',  value: fa(d?.left?.views) },
        { label: 'سفارش',        icon: '🛒',  value: fa(d?.left?.orders) },
        { label: 'درآمد',        icon: '💰',  value: money(d?.left?.revenue) },
        { label: 'نرخ تبدیل',   icon: '⚡',  value: `${fa2(d?.left?.conversion_rate)}٪` },
      ],
    },
    {
      key: 'right', title: 'بازه دوم', color: '#f97316',
      from: d?.right_range?.from_date || '-',
      to:   d?.right_range?.to_date   || '-',
      metrics: [
        { label: 'بازدید',       icon: '👁',  value: fa(d?.right?.views) },
        { label: 'سفارش',        icon: '🛒',  value: fa(d?.right?.orders) },
        { label: 'درآمد',        icon: '💰',  value: money(d?.right?.revenue) },
        { label: 'نرخ تبدیل',   icon: '⚡',  value: `${fa2(d?.right?.conversion_rate)}٪` },
      ],
    },
  ]
})

// ── Overlay data ────────────────────────────────────────────────────────────
const mergedOverlay = computed(() => {
  const left  = props.data?.overlay?.left  || []
  const right = props.data?.overlay?.right || []
  const maxLen = Math.max(left.length, right.length)
  return Array.from({ length: maxLen }, (_, i) => ({
    date:         left[i]?.date || right[i]?.date || `#${i + 1}`,
    leftRevenue:  Number(left[i]?.revenue  || 0),
    rightRevenue: Number(right[i]?.revenue || 0),
  }))
})

const overlayMax = computed(() =>
  Math.max(1, ...mergedOverlay.value.map((r) => Math.max(r.leftRevenue, r.rightRevenue)))
)
const barHeight = (v) => Math.max(4, (Number(v || 0) / overlayMax.value) * 100)
</script>

<style scoped>
.time-tab { display: grid; gap: 12px; }

/* State */
.state-card {
  display: flex; align-items: center; gap: 10px;
  padding: 20px; border-radius: 14px;
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  font-size: 14px; color: var(--admin-text-soft);
}
.state-card.error { color: #f87171; }
.state-icon { font-size: 18px; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.7s linear infinite; }

.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}
.panel { overflow: hidden; }

.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
}
.panel-icon { font-size: 15px; }
.panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; flex: 1; }

/* ── Ranges grid ── */
.ranges-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

/* Range card */
.range-card { padding: 0; overflow: hidden; }
.range-header {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--admin-border);
}
.range-dot {
  width: 10px; height: 10px; border-radius: 50%;
  flex-shrink: 0; margin-top: 5px;
}
.range-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; }
.range-dates { font-size: 11px; color: var(--admin-text-soft); }

.range-metrics { padding: 10px 14px; display: grid; gap: 8px; }
.metric-row    { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label  { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--admin-text-soft); }
.metric-icon   { font-size: 13px; }
.metric-val    { font-size: 13px; font-weight: 600; }

/* Delta card */
.delta-card { overflow: hidden; }
.delta-list  { padding: 10px 14px; display: grid; gap: 10px; }
.delta-row   { display: grid; gap: 4px; }
.delta-label { font-size: 12px; color: var(--admin-text-soft); }
.delta-right { display: flex; align-items: center; gap: 8px; }
.delta-bar-track {
  flex: 1; height: 5px; background: var(--admin-border);
  border-radius: 99px; overflow: hidden;
}
.delta-bar-fill {
  height: 100%; border-radius: 99px; transition: width 0.5s ease;
}
.delta-bar-fill.pos { background: #6ee7b7; }
.delta-bar-fill.neg { background: #f87171; }
.delta-val { font-size: 12px; font-weight: 600; white-space: nowrap; min-width: 60px; text-align: left; }
.delta-val.pos { color: #6ee7b7; }
.delta-val.neg { color: #f87171; }

/* ── Overlay bar chart ── */
.chart-legend {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: var(--admin-text-soft);
}
.legend-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}

.overlay-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 120px;
  padding: 12px 14px 0;
  overflow-x: auto;
}
.overlay-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 20px;
  max-width: 40px;
  height: 100%;
  justify-content: flex-end;
}
.bar-pair {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  flex: 1;
  width: 100%;
  justify-content: center;
}
.bar {
  width: 45%;
  border-radius: 4px 4px 0 0;
  min-height: 3px;
  transition: height 0.4s ease;
}
.left-bar  { background: #818cf8; opacity: 0.85; }
.right-bar { background: #f97316; opacity: 0.85; }
.col-label { font-size: 9px; color: var(--admin-text-soft); white-space: nowrap; }

/* ── Table ── */
.table-wrap { overflow-x: auto; border-top: 1px solid var(--admin-border); }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right; padding: 8px 12px;
  font-size: 12px; border-bottom: 1px solid var(--admin-border); white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
.num { text-align: left; font-variant-numeric: tabular-nums; }
.left-val  { color: #a5b4fc; }
.right-val { color: #fdba74; }
.th-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 5px; }

.diff-badge {
  display: inline-block; padding: 2px 8px;
  border-radius: 999px; font-size: 11px; font-weight: 600;
}
.diff-badge.pos { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.diff-badge.neg { background: rgba(248,113,113,0.15); color: #f87171; }

.empty-cell { font-size: 12px; color: var(--admin-text-soft); padding: 8px 0; }

/* ── Responsive ── */
@media (max-width: 1100px) { .ranges-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px)  { .ranges-grid { grid-template-columns: 1fr; } }
</style>