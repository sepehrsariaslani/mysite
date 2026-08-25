<template>
  <section class="overview-tab">

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری آمار...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">

      <!-- ── KPI Grid ── -->
      <div class="kpi-grid">
        <article class="kpi-card glass-card" v-for="kpi in kpiItems" :key="kpi.label" :style="`--accent:${kpi.color}`">
          <div class="kpi-top">
            <span class="kpi-icon">{{ kpi.icon }}</span>
            <span class="kpi-label">{{ kpi.label }}</span>
          </div>
          <div class="kpi-value">{{ kpi.value }}</div>
          <div class="kpi-sub" v-if="kpi.sub">{{ kpi.sub }}</div>
        </article>
      </div>

      <!-- ── Charts grid ── -->
      <div class="chart-grid">

        <!-- Daily views line chart -->
        <article class="chart-card glass-card">
          <div class="card-header">
            <span class="card-icon">📈</span>
            <h3>بازدید روزانه</h3>
          </div>
          <AnalyticsLiquidLineChart
            :points="dailyPoints"
            primary-label="بازدید"
            primary-color="#818cf8"
            primary-color-soft="#c4b5fd"
            empty-text="داده‌ای برای بازدید روزانه ثبت نشده است."
            :height="220"
          />
        </article>

        <!-- Weekly sales comparison -->
        <article class="chart-card glass-card">
          <div class="card-header">
            <span class="card-icon">🗓</span>
            <h3>فروش هفتگی (جاری / قبلی)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>هفته</th><th>جاری</th><th>قبلی</th><th>تغییر</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in weeklySalesWithDelta" :key="row.label">
                  <td>{{ row.label }}</td>
                  <td class="num">{{ money(row.current) }}</td>
                  <td class="num muted">{{ money(row.previous) }}</td>
                  <td class="num">
                    <span class="delta-badge" :class="row.deltaClass">{{ row.deltaLabel }}</span>
                  </td>
                </tr>
                <tr v-if="!weeklySalesWithDelta.length">
                  <td colspan="4" class="empty-cell">داده‌ای ثبت نشده.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <!-- Heatmap - full width -->
        <article class="chart-card glass-card full">
          <div class="card-header">
            <span class="card-icon">🔥</span>
            <h3>نقشه حرارتی — پرترافیک‌ترین ساعات هفته</h3>
          </div>

          <!-- Visual heatmap grid -->
          <div class="heatmap-section" v-if="heatmapGrid.length">
            <div class="heatmap-y-labels">
              <span v-for="h in heatHours" :key="h">{{ h }}</span>
            </div>
            <div class="heatmap-main">
              <div class="heatmap-x-labels">
                <span v-for="d in heatDays" :key="d">{{ d }}</span>
              </div>
              <div class="heatmap-grid">
                <div
                  v-for="cell in heatmapGrid"
                  :key="`${cell.weekday}-${cell.hour}`"
                  class="heat-cell"
                  :style="`opacity:${cell.opacity}; background:${cell.color}`"
                  :title="`روز ${cell.weekday} / ساعت ${cell.hour}: ${fa(cell.value)}`"
                ></div>
              </div>
            </div>
          </div>

          <!-- Fallback list if grid sparse -->
          <div class="heat-list" v-else>
            <div v-for="(row, idx) in sortedHeat" :key="`${row.weekday}-${row.hour}-${idx}`" class="heat-row">
              <div class="heat-row-info">
                <span class="heat-dot" :style="`opacity:${0.4 + 0.6 * (idx / sortedHeat.length)}`"></span>
                <span>روز {{ row.weekday }} / ساعت {{ row.hour }}</span>
              </div>
              <div class="heat-row-right">
                <div class="heat-bar-track">
                  <div class="heat-bar-fill" :style="`width:${heatPercent(row.value)}%`"></div>
                </div>
                <strong>{{ fa(row.value) }}</strong>
              </div>
            </div>
            <p v-if="!sortedHeat.length" class="empty-cell">داده‌ای برای نقشه حرارتی ثبت نشده است.</p>
          </div>
        </article>

      </div>

      <div class="advanced-grid">
        <article class="chart-card glass-card">
          <div class="card-header">
            <span class="card-icon">🎯</span>
            <h3>Goals قابل تعریف</h3>
          </div>
          <div v-if="advancedLoading" class="mini-state">در حال بارگذاری Goals...</div>
          <div v-else-if="advancedError" class="mini-state error">{{ advancedError }}</div>
          <div v-else class="goals-wrap">
            <div v-for="goal in advancedGoals" :key="goal.name || goal.title" class="goal-card">
              <div class="goal-head">
                <strong>{{ goal.title }}</strong>
                <span>{{ fa2(goal.conversion_rate) }}٪ تبدیل</span>
              </div>
              <div class="goal-meta">
                <span>مسیر: {{ fa(goal.total_journeys) }}</span>
                <span>تکمیل: {{ fa(goal.conversion_sessions) }}</span>
              </div>
              <div class="goal-steps">
                <div v-for="step in goal.steps || []" :key="`${goal.name}-${step.step}`" class="goal-step">
                  <div class="step-head">
                    <span>{{ step.step }}</span>
                    <span>{{ fa(step.sessions) }}</span>
                  </div>
                  <div class="step-bar"><i :style="{ width: `${goalStepWidth(goal, step)}%` }"></i></div>
                </div>
              </div>
            </div>
            <p v-if="!advancedGoals.length" class="empty-cell">Goal فعالی ثبت نشده است.</p>
          </div>
        </article>

        <article class="chart-card glass-card">
          <div class="card-header">
            <span class="card-icon">🛡</span>
            <h3>کنترل کیفیت داده</h3>
          </div>
          <div v-if="advancedLoading" class="mini-state">در حال بررسی کیفیت داده...</div>
          <div v-else-if="advancedError" class="mini-state error">{{ advancedError }}</div>
          <div v-else class="quality-wrap">
            <div class="quality-score" :class="qualityClass(quality?.quality_score)">
              <span>امتیاز کیفیت</span>
              <strong>{{ fa2(quality?.quality_score) }}</strong>
            </div>
            <div class="quality-grid">
              <div class="quality-item" v-for="row in qualityRows" :key="row.label">
                <span>{{ row.label }}</span>
                <strong>{{ row.value }}</strong>
              </div>
            </div>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import AnalyticsLiquidLineChart from './AnalyticsLiquidLineChart.vue'

const props = defineProps({
  data:    { type: Object,  default: null  },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: ''    },
  advanced: { type: Object, default: null },
  advancedLoading: { type: Boolean, default: false },
  advancedError: { type: String, default: '' },
})

const fa    = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2   = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })
const money = (v) => `${Number(v || 0).toLocaleString('fa-IR')} تومان`

// ── KPI items ──────────────────────────────────────────────────────────────
const kpiItems = computed(() => {
  const k = props.data?.kpis || {}
  return [
    { label: 'بازدید کل',       value: fa(k.total_views),              icon: '👁',  color: '#6ee7b7', sub: null },
    { label: 'نرخ تبدیل',       value: `${fa2(k.conversion_rate)}٪`,   icon: '⚡',  color: '#93c5fd', sub: 'بازدید → سفارش' },
    { label: 'درآمد',           value: money(k.total_revenue),          icon: '💰',  color: '#fcd34d', sub: null },
    { label: 'سفارش',           value: fa(k.total_orders),              icon: '🛒',  color: '#c4b5fd', sub: `AOV: ${money(k.average_order_value)}` },
    { label: 'میانگین سفارش',   value: money(k.average_order_value),    icon: '📦',  color: '#86efac', sub: null },
    { label: 'ریزش سبد',        value: `${fa2(k.cart_abandonment_rate)}٪`, icon: '📉', color: '#fca5a5', sub: 'از افزودن به سبد' },
  ]
})

const advancedGoals = computed(() => props.advanced?.goals || [])
const quality = computed(() => props.advanced?.data_quality || null)

const qualityRows = computed(() => {
  const q = quality.value || {}
  return [
    { label: 'کل رویداد', value: fa(q.total_events || 0) },
    { label: 'رویداد تکراری', value: `${fa(q.duplicate_events || 0)} (${fa2(q.rates?.duplicate_rate || 0)}٪)` },
    { label: 'تکرار سریع', value: `${fa(q.rapid_duplicate_events || 0)} (${fa2(q.rates?.rapid_duplicate_rate || 0)}٪)` },
    { label: 'ربات', value: `${fa(q.bot_events || 0)} (${fa2(q.rates?.bot_rate || 0)}٪)` },
    { label: 'ترافیک داخلی', value: `${fa(q.internal_events || 0)} (${fa2(q.rates?.internal_rate || 0)}٪)` },
    { label: 'بدون Session', value: fa(q.missing_session_events || 0) },
  ]
})

const goalStepWidth = (goal, step) => {
  const first = Number(goal?.steps?.[0]?.sessions || 0)
  const curr = Number(step?.sessions || 0)
  if (!first) return 0
  return Math.max(4, Math.min(100, (curr / first) * 100))
}

const qualityClass = (score) => {
  const n = Number(score || 0)
  if (n >= 90) return 'good'
  if (n >= 75) return 'mid'
  return 'low'
}

// ── Daily chart points ─────────────────────────────────────────────────────
const shortDate = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' })
}

const dailyPoints = computed(() =>
  (props.data?.charts?.daily_views || []).map((row) => ({
    label: shortDate(row.date),
    a: Number(row.value || 0),
  }))
)

// ── Weekly sales with delta ────────────────────────────────────────────────
const weeklySalesWithDelta = computed(() =>
  (props.data?.charts?.weekly_sales_compare || []).map((row) => {
    const cur  = Number(row.current  || 0)
    const prev = Number(row.previous || 0)
    const delta = prev ? ((cur - prev) / prev) * 100 : null
    return {
      ...row,
      deltaLabel: delta === null ? '-' : `${delta >= 0 ? '▲' : '▼'} ${Math.abs(delta).toLocaleString('fa-IR', { maximumFractionDigits: 1 })}٪`,
      deltaClass: delta === null ? '' : delta >= 0 ? 'positive' : 'negative',
    }
  })
)

// ── Heatmap ────────────────────────────────────────────────────────────────
const sortedHeat = computed(() =>
  [...(props.data?.charts?.traffic_heatmap || [])]
    .sort((a, b) => Number(b.value || 0) - Number(a.value || 0))
    .slice(0, 20)
)

const heatMax = computed(() => Math.max(1, ...sortedHeat.value.map((r) => Number(r.value || 0))))
const heatPercent = (v) => (Number(v || 0) / heatMax.value) * 100

// Build visual grid (days 1-7, hours 0-23)
const heatDays  = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
const heatHours = Array.from({ length: 8 }, (_, i) => `${i * 3}`)

const heatmapGrid = computed(() => {
  const raw = props.data?.charts?.traffic_heatmap || []
  if (!raw.length) return []
  const map = {}
  raw.forEach((r) => { map[`${r.weekday}-${r.hour}`] = Number(r.value || 0) })
  const max = Math.max(1, ...Object.values(map))
  const cells = []
  for (let day = 1; day <= 7; day++) {
    for (let block = 0; block < 8; block++) {
      const hour = block * 3
      const val  = map[`${day}-${hour}`] || 0
      cells.push({
        weekday: day,
        hour,
        value: val,
        opacity: 0.08 + (val / max) * 0.92,
        color: val / max > 0.6 ? '#f87171' : val / max > 0.3 ? '#fcd34d' : '#6ee7b7',
      })
    }
  }
  return cells
})
</script>

<style scoped>
.overview-tab { display: grid; gap: 12px; }

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

/* Glass */
.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}

/* ── KPI Grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}
.kpi-card {
  padding: 14px;
  position: relative;
  overflow: hidden;
  transition: transform 0.15s;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 3px; height: 100%;
  background: var(--accent);
  border-radius: 0 18px 18px 0;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-top   { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.kpi-icon  { font-size: 15px; }
.kpi-label { font-size: 11px; color: var(--admin-text-soft); }
.kpi-value { font-size: 1.1rem; font-weight: 700; line-height: 1.2; }
.kpi-sub   { font-size: 11px; color: var(--text-muted, #999); margin-top: 4px; }

/* ── Chart grid ── */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.chart-card { overflow: hidden; }
.chart-card.full { grid-column: 1 / -1; }

.advanced-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 12px;
}

.card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--admin-border);
}
.card-icon { font-size: 15px; }
.card-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; }

/* Padding wrapper for chart content */
.chart-card > :deep(.liquid-line-chart) { padding: 12px; }

/* ── Table ── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right; padding: 8px 12px;
  font-size: 12px; border-bottom: 1px solid var(--admin-border); white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
.num   { text-align: left; font-variant-numeric: tabular-nums; }
.muted { color: var(--admin-text-soft); }
.empty-cell { text-align: center; color: var(--admin-text-soft); font-size: 12px; }

.mini-state {
  padding: 16px 14px;
  color: var(--admin-text-soft);
  font-size: 12px;
}
.mini-state.error { color: #f87171; }

.goals-wrap {
  padding: 12px;
  display: grid;
  gap: 8px;
}
.goal-card {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
}
.goal-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}
.goal-head strong { font-size: 13px; }
.goal-head span { font-size: 12px; color: var(--admin-text-soft); }
.goal-meta {
  margin-top: 4px;
  display: flex;
  gap: 10px;
  color: var(--text-muted);
  font-size: 11px;
}
.goal-steps {
  margin-top: 8px;
  display: grid;
  gap: 6px;
}
.goal-step { display: grid; gap: 4px; }
.step-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}
.step-bar {
  border: 1px solid var(--admin-border);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.3);
}
.step-bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #22d3ee);
}

.quality-wrap {
  padding: 12px;
  display: grid;
  gap: 10px;
}
.quality-score {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quality-score span { font-size: 12px; color: var(--admin-text-soft); }
.quality-score strong { font-size: 1.2rem; }
.quality-score.good strong { color: #6ee7b7; }
.quality-score.mid strong { color: #fcd34d; }
.quality-score.low strong { color: #f87171; }
.quality-grid { display: grid; gap: 6px; }
.quality-item {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 8px 10px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
}

/* Delta badge */
.delta-badge {
  display: inline-block; padding: 2px 7px;
  border-radius: 999px; font-size: 11px; font-weight: 600;
}
.delta-badge.positive { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.delta-badge.negative { background: rgba(248,113,113,0.15); color: #f87171; }

/* ── Visual heatmap ── */
.heatmap-section {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  overflow-x: auto;
}
.heatmap-y-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-top: 22px;
  font-size: 10px;
  color: var(--admin-text-soft);
  min-width: 22px;
  text-align: left;
}
.heatmap-main { flex: 1; display: grid; gap: 4px; }
.heatmap-x-labels {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
  font-size: 10px;
  color: var(--admin-text-soft);
  text-align: center;
}
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(8, 1fr);
  gap: 3px;
}
.heat-cell {
  aspect-ratio: 1;
  border-radius: 4px;
  min-width: 24px;
  min-height: 20px;
  transition: opacity 0.2s, transform 0.15s;
  cursor: default;
}
.heat-cell:hover { transform: scale(1.15); }

/* ── Fallback heat list ── */
.heat-list { padding: 10px 14px; display: grid; gap: 7px; }
.heat-row {
  display: flex; align-items: center;
  justify-content: space-between; gap: 12px;
}
.heat-row-info { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.heat-dot { width: 8px; height: 8px; border-radius: 50%; background: #818cf8; flex-shrink: 0; }
.heat-row-right { display: flex; align-items: center; gap: 8px; flex: 1; justify-content: flex-end; }
.heat-bar-track { width: 80px; height: 5px; background: var(--admin-border); border-radius: 99px; overflow: hidden; }
.heat-bar-fill  { height: 100%; background: linear-gradient(90deg, #818cf8, #c4b5fd); border-radius: 99px; }
.heat-row-right strong { font-size: 12px; min-width: 50px; text-align: left; }

/* ── Responsive ── */
@media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 860px) {
  .kpi-grid  { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .chart-grid { grid-template-columns: 1fr; }
  .advanced-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .card-header { padding: 10px 12px; }
  .table-wrap table { min-width: 500px; }
  .heatmap-main { min-width: 300px; }
}
</style>
