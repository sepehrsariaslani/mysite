<template>
  <div class="table-wrap glass-card">
    <table>
      <thead>
        <tr>
          <th>نشانی صفحه</th>
          <th>بازدید</th>
          <th>نشست یکتا</th>
          <th>میانگین زمان</th>
          <th>پیمایش</th>
          <th>خروج</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.path || row.route"
          class="data-row"
          @mouseenter="hovered = row.path || row.route"
          @mouseleave="hovered = null"
          :class="{ highlighted: hovered === (row.path || row.route) }"
        >
          <!-- Path + bar -->
          <td class="path-cell">
            <div class="path-line">
              <span class="path-text">{{ row.path || row.route || '-' }}</span>
              <span class="views-inline">{{ fa(row.views) }}</span>
            </div>
            <div class="meter-track">
              <div
                class="meter-fill"
                :style="`width: ${widthByMax(row.views)}%`"
                :class="barClass(row.views)"
              ></div>
            </div>
          </td>

          <!-- Views -->
          <td class="num">
            <span class="val-main">{{ fa(row.views) }}</span>
          </td>

          <!-- Unique sessions -->
          <td class="num">{{ fa(row.unique_sessions) }}</td>

          <!-- Avg time -->
          <td class="num">
            <span class="time-val" :class="timeClass(row.avg_time_spent_seconds)">
              {{ fa2(row.avg_time_spent_seconds) }}s
            </span>
          </td>

          <!-- Scroll depth -->
          <td class="num">
            <div class="scroll-cell">
              <div class="scroll-track">
                <div
                  class="scroll-fill"
                  :style="`width:${Math.min(Number(row.avg_scroll_depth || 0), 100)}%`"
                  :class="scrollClass(row.avg_scroll_depth)"
                ></div>
              </div>
              <span>{{ fa2(row.avg_scroll_depth) }}٪</span>
            </div>
          </td>

          <!-- Exit -->
          <td class="num">
            <span class="exit-val" :class="exitClass(row)">{{ fa(row.exits) }}</span>
          </td>
        </tr>

        <tr v-if="!rows.length">
          <td colspan="6" class="empty-cell">
            <span>موردی برای نمایش وجود ندارد.</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const hovered  = ref(null)
const maxViews = computed(() => Math.max(1, ...props.rows.map((r) => Number(r?.views || 0))))
const maxExits = computed(() => Math.max(1, ...props.rows.map((r) => Number(r?.exits || 0))))

const fa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 1 })

const widthByMax = (v) => Math.max(4, Math.min(100, (Number(v || 0) / maxViews.value) * 100))

const barClass = (v) => {
  const pct = (Number(v || 0) / maxViews.value) * 100
  if (pct >= 80) return 'bar-peak'
  if (pct >= 50) return 'bar-high'
  if (pct >= 25) return 'bar-mid'
  return 'bar-low'
}

const scrollClass = (v) => {
  const n = Number(v || 0)
  if (n >= 70) return 'sc-high'
  if (n >= 40) return 'sc-mid'
  return 'sc-low'
}

const timeClass = (v) => {
  const n = Number(v || 0)
  if (n >= 120) return 'time-high'
  if (n >= 30)  return 'time-mid'
  return 'time-low'
}

const exitClass = (row) => {
  const exits = Number(row.exits || 0)
  const views = Number(row.views || 1)
  const rate  = exits / views
  if (rate >= 0.6) return 'exit-high'
  if (rate >= 0.3) return 'exit-mid'
  return 'exit-low'
}
</script>

<style scoped>
/* Glass wrapper */
.glass-card {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  overflow: auto;
}

table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
}

/* Header */
th {
  text-align: right;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--admin-text-soft);
  border-bottom: 1px solid var(--admin-border);
  white-space: nowrap;
  position: sticky;
  top: 0;
  background: var(--admin-panel-bg);
  z-index: 1;
}

/* Rows */
td {
  text-align: right;
  padding: 9px 12px;
  font-size: 12px;
  border-bottom: 1px solid var(--admin-border);
  white-space: nowrap;
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
.data-row { transition: background 0.12s; }
.data-row.highlighted td { background: rgba(255,255,255,0.03); }
.num { text-align: left; font-variant-numeric: tabular-nums; }

/* Path cell */
.path-cell { min-width: 260px; max-width: 320px; }
.path-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 5px;
}
.path-text {
  font-family: monospace;
  font-size: 12px;
  direction: ltr;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  color: var(--text-main);
}
.views-inline {
  font-size: 11px;
  color: var(--admin-text-soft);
  flex-shrink: 0;
}

/* Meter bar */
.meter-track {
  height: 4px;
  background: var(--admin-border);
  border-radius: 99px;
  overflow: hidden;
}
.meter-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.bar-peak { background: linear-gradient(90deg, #6ee7b7, #34d399); }
.bar-high { background: linear-gradient(90deg, #818cf8, #6366f1); }
.bar-mid  { background: linear-gradient(90deg, #a5b4fc, #818cf8); }
.bar-low  { background: linear-gradient(90deg, #6366f1, #4338ca); opacity: 0.6; }

/* Scroll cell */
.scroll-cell { display: flex; align-items: center; gap: 6px; }
.scroll-track {
  width: 48px; height: 4px;
  background: var(--admin-border);
  border-radius: 99px; overflow: hidden;
}
.scroll-fill { height: 100%; border-radius: 99px; }
.sc-high { background: #6ee7b7; }
.sc-mid  { background: #fcd34d; }
.sc-low  { background: #f87171; }

/* Time color */
.time-high { color: #6ee7b7; }
.time-mid  { color: var(--text-main); }
.time-low  { color: var(--admin-text-soft); }

/* Exit color */
.exit-high { color: #f87171; font-weight: 600; }
.exit-mid  { color: #fcd34d; }
.exit-low  { color: var(--admin-text-soft); }

/* val-main */
.val-main { font-weight: 600; }

/* Empty */
.empty-cell {
  text-align: center;
  color: var(--admin-text-soft);
  padding: 24px;
  font-size: 13px;
}
</style>