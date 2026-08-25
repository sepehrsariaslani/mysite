<template>
  <div class="daily-chart">

    <!-- Empty -->
    <div v-if="!rows.length" class="empty">
      <span class="empty-icon">📊</span>
      داده بازدید ثبت نشده است.
    </div>

    <template v-else>
      <!-- Y-axis + bars -->
      <div class="chart-area">
        <!-- Y labels -->
        <div class="y-axis">
          <span v-for="tick in yTicks" :key="tick">{{ tick }}</span>
        </div>

        <!-- Bars -->
        <div class="bars-wrap">
          <!-- Grid lines -->
          <div class="grid-lines">
            <div v-for="n in 4" :key="n" class="grid-line"></div>
          </div>

          <!-- Bar columns -->
          <div class="bars" ref="barsRef">
            <div
              v-for="(row, idx) in rows"
              :key="row.date"
              class="bar-col"
              @mouseenter="showTip(row, idx, $event)"
              @mouseleave="hideTip"
            >
              <div
                class="bar"
                :class="barClass(row.views)"
                :style="`height: ${animated ? barHeight(row.views) : 0}%; transition-delay: ${idx * 12}ms`"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- X labels -->
      <div class="x-labels">
        <span v-for="item in xTickLabels" :key="item.idx">{{ item.label }}</span>
      </div>

      <!-- Tooltip -->
      <Teleport to="body">
        <div
          v-if="tip.visible"
          class="bar-tooltip"
          :style="{ top: tip.y + 'px', left: tip.x + 'px' }"
        >
          <span class="tip-date">{{ tip.date }}</span>
          <strong class="tip-val">{{ fa(tip.views) }}</strong>
          <span class="tip-note" v-if="tip.rank === 'high'">🔺 پیک بازدید</span>
          <span class="tip-note low" v-else-if="tip.rank === 'low'">🔻 کمترین بازدید</span>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, nextTick } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const animated = ref(false)
onMounted(() => { nextTick(() => setTimeout(() => { animated.value = true }, 60)) })

// ── Helpers ────────────────────────────────────────────────────────────────
const fa = (v) => Number(v || 0).toLocaleString('fa-IR')

const faCompact = (v) => {
  const n = Number(v || 0)
  if (n >= 1_000_000) return `${(n / 1_000_000).toLocaleString('fa-IR', { maximumFractionDigits: 1 })}M`
  if (n >= 1_000)     return `${(n / 1_000).toLocaleString('fa-IR', { maximumFractionDigits: 0 })}K`
  return n.toLocaleString('fa-IR')
}

const maxViews = computed(() => Math.max(1, ...props.rows.map((r) => Number(r?.views || 0))))
const minViews = computed(() => Math.min(...props.rows.map((r) => Number(r?.views || 0))))

const barHeight = (v) => Math.max(4, (Number(v || 0) / maxViews.value) * 100)

const barClass = (v) => {
  const n = Number(v || 0)
  if (n === maxViews.value) return 'peak'
  if (n === minViews.value) return 'low'
  if (n >= maxViews.value * 0.7) return 'high'
  if (n <= maxViews.value * 0.3) return 'dim'
  return ''
}

// Y-axis ticks
const yTicks = computed(() => {
  const max = maxViews.value
  return [max, Math.round(max * 0.75), Math.round(max * 0.5), Math.round(max * 0.25), 0]
    .map(faCompact)
})

// X-axis: show ~5 labels
const xTickLabels = computed(() => {
  const n = props.rows.length
  if (!n) return []
  const picks = n <= 6
    ? props.rows.map((r, i) => ({ idx: i, label: formatDate(r.date) }))
    : [0, Math.round(n / 4), Math.round(n / 2), Math.round(3 * n / 4), n - 1]
        .map((i) => ({ idx: i, label: formatDate(props.rows[i]?.date) }))
  return picks
})

const formatDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return v
  return d.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' })
}

// ── Tooltip ────────────────────────────────────────────────────────────────
const tip = reactive({ visible: false, date: '', views: 0, rank: '', x: 0, y: 0 })

function showTip(row, idx, e) {
  const v = Number(row.views || 0)
  tip.date    = formatDate(row.date)
  tip.views   = v
  tip.rank    = v === maxViews.value ? 'high' : v === minViews.value ? 'low' : ''
  tip.visible = true
  tip.x = e.clientX + 12
  tip.y = e.clientY - 10
}
function hideTip() { tip.visible = false }
</script>

<style scoped>
.daily-chart { display: grid; gap: 6px; }

/* Empty */
.empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; min-height: 160px;
  border: 1px dashed var(--admin-border); border-radius: 14px;
  color: var(--admin-text-soft); font-size: 13px;
  background: rgba(255,255,255,0.02);
}
.empty-icon { font-size: 26px; opacity: 0.5; }

/* Chart area = y-axis + bars */
.chart-area {
  display: flex;
  gap: 6px;
  height: 200px;
}

/* Y-axis */
.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 9px;
  color: var(--admin-text-soft);
  text-align: left;
  min-width: 32px;
  padding-bottom: 2px;
  flex-shrink: 0;
}

/* Bars wrap (relative, contains grid lines + bars) */
.bars-wrap {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* Grid lines */
.grid-lines {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}
.grid-line {
  border-top: 1px dashed var(--admin-border);
  opacity: 0.5;
}

/* Bars */
.bars {
  flex: 1;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: flex-end;
  gap: 3px;
  position: relative;
}

.bar-col {
  height: 100%;
  display: flex;
  align-items: flex-end;
  cursor: crosshair;
}

.bar {
  width: 100%;
  min-width: 4px;
  border-radius: 5px 5px 0 0;
  background: linear-gradient(180deg, #818cf8 0%, #6366f1 100%);
  transition: height 0.5s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.15s;
  opacity: 0.75;
}
.bar-col:hover .bar { opacity: 1; transform: scaleX(1.08); }

/* Color variants */
.bar.peak { background: linear-gradient(180deg, #6ee7b7, #34d399); opacity: 0.95; }
.bar.high { background: linear-gradient(180deg, #a5b4fc, #818cf8); opacity: 0.85; }
.bar.dim  { background: linear-gradient(180deg, #6366f1, #4338ca); opacity: 0.5; }
.bar.low  { background: linear-gradient(180deg, #f87171, #ef4444); opacity: 0.7; }

/* X-axis labels */
.x-labels {
  display: flex;
  justify-content: space-between;
  padding-right: 38px; /* offset for y-axis width */
  font-size: 10px;
  color: var(--admin-text-soft);
}
</style>

<!-- Global tooltip -->
<style>
.bar-tooltip {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  background: var(--admin-panel-bg, #1e1e2e);
  border: 1px solid var(--admin-border, rgba(255,255,255,0.1));
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 110px;
  backdrop-filter: blur(16px);
  box-shadow: 0 10px 28px rgba(0,0,0,0.22);
  font-family: inherit;
  animation: barTipIn 0.1s ease;
}
@keyframes barTipIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.tip-date { font-size: 11px; color: var(--admin-text-soft, #888); }
.tip-val  { font-size: 15px; font-weight: 700; color: var(--text-main, #fff); }
.tip-note { font-size: 11px; color: var(--admin-text-soft, #888); }
.tip-note.low { color: #f87171; }
</style>