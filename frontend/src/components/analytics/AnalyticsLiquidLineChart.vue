<template>
  <div class="liquid-line-chart" :style="cssVars">

    <!-- Empty state -->
    <div v-if="!points.length" class="chart-empty">
      <span class="empty-icon">📊</span>
      <span>{{ emptyText }}</span>
    </div>

    <div v-else class="chart-wrap">
      <svg
        class="chart-svg"
        :viewBox="`0 0 ${viewWidth} ${viewHeight}`"
        preserveAspectRatio="none"
        aria-hidden="true"
        @mousemove="onMouseMove"
        @mouseleave="tooltip.visible = false"
        ref="svgRef"
      >
        <defs>
          <!-- Primary gradients -->
          <linearGradient :id="`line-primary-${uid}`" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%"   :stop-color="primaryColor" />
            <stop offset="100%" :stop-color="primaryColorSoft" />
          </linearGradient>
          <linearGradient :id="`area-primary-${uid}`" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   :stop-color="primaryColor" stop-opacity="0.38" />
            <stop offset="100%" :stop-color="primaryColor" stop-opacity="0.03" />
          </linearGradient>

          <!-- Secondary gradients -->
          <linearGradient :id="`line-secondary-${uid}`" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%"   :stop-color="secondaryColor" />
            <stop offset="100%" :stop-color="secondaryColorSoft" />
          </linearGradient>
          <linearGradient :id="`area-secondary-${uid}`" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   :stop-color="secondaryColor" stop-opacity="0.28" />
            <stop offset="100%" :stop-color="secondaryColor" stop-opacity="0.03" />
          </linearGradient>

          <!-- Clip path for draw animation -->
          <clipPath :id="`clip-${uid}`">
            <rect
              x="0" y="0"
              :width="animated ? viewWidth : 0"
              :height="viewHeight"
              class="clip-rect"
            />
          </clipPath>
        </defs>

        <!-- Horizontal grid lines -->
        <line
          v-for="(line, idx) in horizontalGuides"
          :key="`grid-${idx}`"
          :x1="paddingX" :x2="viewWidth - paddingX"
          :y1="line"     :y2="line"
          class="grid-line"
        />

        <!-- Y-axis value labels -->
        <text
          v-for="(item, idx) in yAxisLabels"
          :key="`ylabel-${idx}`"
          :x="paddingX - 4"
          :y="item.y"
          class="y-label"
          text-anchor="end"
          dominant-baseline="middle"
        >{{ item.label }}</text>

        <!-- Clipped chart content (animates in) -->
        <g :clip-path="`url(#clip-${uid})`">
          <!-- Secondary area + line -->
          <path
            v-if="secondaryPoints.length"
            :d="secondaryAreaPath"
            :fill="`url(#area-secondary-${uid})`"
            class="area-path"
          />
          <path
            v-if="secondaryPoints.length"
            :d="secondaryPath"
            :stroke="`url(#line-secondary-${uid})`"
            class="line-path"
          />

          <!-- Primary area + line -->
          <path
            :d="primaryAreaPath"
            :fill="`url(#area-primary-${uid})`"
            class="area-path"
          />
          <path
            :d="primaryPath"
            :stroke="`url(#line-primary-${uid})`"
            class="line-path"
          />

          <!-- Primary dots -->
          <circle
            v-for="(point, idx) in visiblePrimaryDots"
            :key="`dot-${idx}`"
            :cx="point.x" :cy="point.y"
            r="3.8"
            class="point-dot"
            :fill="primaryColor"
          />
        </g>

        <!-- Tooltip crosshair -->
        <g v-if="tooltip.visible">
          <line
            :x1="tooltip.svgX" :x2="tooltip.svgX"
            :y1="paddingTop"   :y2="viewHeight - paddingBottom"
            class="crosshair"
          />
          <circle
            v-if="tooltip.primaryY !== null"
            :cx="tooltip.svgX" :cy="tooltip.primaryY"
            r="5" :fill="primaryColor"
            class="tooltip-dot"
          />
          <circle
            v-if="tooltip.secondaryY !== null"
            :cx="tooltip.svgX" :cy="tooltip.secondaryY"
            r="5" :fill="secondaryColor"
            class="tooltip-dot"
          />
        </g>
      </svg>

      <!-- Tooltip bubble (HTML overlay) -->
      <Teleport to="body">
        <div
          v-if="tooltip.visible"
          class="chart-tooltip"
          :style="{ top: tooltip.pageY + 'px', left: tooltip.pageX + 'px' }"
        >
          <div class="tooltip-label">{{ tooltip.label }}</div>
          <div v-if="primaryLabel" class="tooltip-row">
            <span class="tooltip-dot-swatch" :style="`background:${primaryColor}`"></span>
            <span>{{ primaryLabel }}:</span>
            <strong>{{ faFormat(tooltip.a) }}</strong>
          </div>
          <div v-if="secondaryLabel && tooltip.b !== null" class="tooltip-row">
            <span class="tooltip-dot-swatch" :style="`background:${secondaryColor}`"></span>
            <span>{{ secondaryLabel }}:</span>
            <strong>{{ faFormat(tooltip.b) }}</strong>
          </div>
        </div>
      </Teleport>

      <!-- X-axis labels -->
      <div class="axis-labels">
        <span v-for="item in tickLabels" :key="`label-${item.index}`">{{ item.label }}</span>
      </div>
    </div>

    <!-- Legend -->
    <div v-if="legendItems.length" class="legend-row">
      <span v-for="item in legendItems" :key="item.label" class="legend-item">
        <i :style="{ background: item.color }"></i>
        {{ item.label }}
      </span>
    </div>

  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  points:             { type: Array,  default: () => [] },
  primaryLabel:       { type: String, default: '' },
  secondaryLabel:     { type: String, default: '' },
  primaryColor:       { type: String, default: '#818cf8' },
  primaryColorSoft:   { type: String, default: '#c4b5fd' },
  secondaryColor:     { type: String, default: '#f97316' },
  secondaryColorSoft: { type: String, default: '#fdba74' },
  emptyText:          { type: String, default: 'داده‌ای برای نمایش نمودار وجود ندارد.' },
  height:             { type: Number, default: 260 },
  formatValue:        { type: Function, default: null },
})

const uid       = `lc-${Math.random().toString(36).slice(2, 8)}`
const svgRef    = ref(null)
const animated  = ref(false)

const viewWidth    = 900
const viewHeight   = computed(() => Math.max(Number(props.height) || 0, 160))
const paddingX     = 44   // wider to fit y-axis labels
const paddingTop   = 16
const paddingBottom = 28

// Animate on mount
onMounted(() => {
  nextTick(() => { setTimeout(() => { animated.value = true }, 80) })
})

// ── Data mapping ──────────────────────────────────────────────────────────
const chartPoints = computed(() =>
  (props.points || []).map((row, index) => ({
    index,
    label: String(row?.label || '-'),
    a: Number(row?.a || 0),
    b: Number.isFinite(Number(row?.b)) ? Number(row?.b) : null,
  }))
)

const maxValue = computed(() => {
  const values = []
  chartPoints.value.forEach((row) => {
    values.push(row.a)
    if (row.b !== null) values.push(row.b)
  })
  return Math.max(1, ...values)
})

const innerWidth  = computed(() => viewWidth - paddingX * 2)
const innerHeight = computed(() => viewHeight.value - paddingTop - paddingBottom)

// ── SVG coordinates ───────────────────────────────────────────────────────
const toSvgPoints = (valueKey) => {
  const rows = chartPoints.value
  if (!rows.length) return []
  const den = Math.max(rows.length - 1, 1)
  return rows.map((row, idx) => {
    const val = valueKey === 'a' ? row.a : (row.b || 0)
    return {
      x: paddingX + (idx / den) * innerWidth.value,
      y: paddingTop + innerHeight.value - (val / maxValue.value) * innerHeight.value,
    }
  })
}

const primaryPoints   = computed(() => toSvgPoints('a'))
const secondaryPoints = computed(() => {
  const rows = chartPoints.value
  if (!rows.length || !rows.some((r) => r.b !== null)) return []
  return toSvgPoints('b')
})

// ── Path builders ─────────────────────────────────────────────────────────
const smooth = (pts) => {
  if (!pts.length) return ''
  if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`
  let d = `M ${pts[0].x.toFixed(2)} ${pts[0].y.toFixed(2)}`
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1]
    const curr = pts[i]
    const cpX = (prev.x + curr.x) / 2
    d += ` C ${cpX.toFixed(2)} ${prev.y.toFixed(2)}, ${cpX.toFixed(2)} ${curr.y.toFixed(2)}, ${curr.x.toFixed(2)} ${curr.y.toFixed(2)}`
  }
  return d
}

const toAreaPath = (pts) => {
  if (!pts.length) return ''
  const line = smooth(pts)
  const first = pts[0]
  const last  = pts[pts.length - 1]
  const baseline = paddingTop + innerHeight.value
  return `${line} L ${last.x.toFixed(2)} ${baseline.toFixed(2)} L ${first.x.toFixed(2)} ${baseline.toFixed(2)} Z`
}

const primaryPath      = computed(() => smooth(primaryPoints.value))
const secondaryPath    = computed(() => smooth(secondaryPoints.value))
const primaryAreaPath  = computed(() => toAreaPath(primaryPoints.value))
const secondaryAreaPath = computed(() => toAreaPath(secondaryPoints.value))

// ── Grid & axes ───────────────────────────────────────────────────────────
const horizontalGuides = computed(() => {
  const lines = 4
  return Array.from({ length: lines + 1 }).map((_, idx) => paddingTop + (idx / lines) * innerHeight.value)
})

const yAxisLabels = computed(() => {
  const lines = 4
  return Array.from({ length: lines + 1 }).map((_, idx) => {
    const val = maxValue.value * (1 - idx / lines)
    return {
      y: paddingTop + (idx / lines) * innerHeight.value,
      label: faFormat(val),
    }
  })
})

const tickLabels = computed(() => {
  const rows = chartPoints.value
  if (!rows.length) return []
  if (rows.length <= 5) return rows.map((row, index) => ({ index, label: row.label }))
  const picks = [0, Math.round((rows.length - 1) / 3), Math.round(2 * (rows.length - 1) / 3), rows.length - 1]
  return [...new Set(picks)].map((index) => ({ index, label: rows[index]?.label || '-' }))
})

const visiblePrimaryDots = computed(() => {
  const rows = primaryPoints.value
  if (rows.length <= 12) return rows
  return [rows[0], rows[Math.round((rows.length - 1) / 2)], rows[rows.length - 1]]
})

const legendItems = computed(() => {
  const items = []
  if (props.primaryLabel) items.push({ label: props.primaryLabel, color: props.primaryColor })
  if (props.secondaryLabel && secondaryPoints.value.length) items.push({ label: props.secondaryLabel, color: props.secondaryColor })
  return items
})

// ── Formatter ─────────────────────────────────────────────────────────────
const faFormat = (v) => {
  if (props.formatValue) return props.formatValue(v)
  const n = Number(v || 0)
  if (n >= 1_000_000) return `${(n / 1_000_000).toLocaleString('fa-IR', { maximumFractionDigits: 1 })}M`
  if (n >= 1_000)     return `${(n / 1_000).toLocaleString('fa-IR', { maximumFractionDigits: 1 })}K`
  return n.toLocaleString('fa-IR', { maximumFractionDigits: 1 })
}

// ── Tooltip ───────────────────────────────────────────────────────────────
const tooltip = reactive({
  visible: false,
  label: '',
  a: 0,
  b: null,
  svgX: 0,
  primaryY: null,
  secondaryY: null,
  pageX: 0,
  pageY: 0,
})

function onMouseMove(e) {
  const svgEl = svgRef.value
  if (!svgEl || !chartPoints.value.length) return

  const rect = svgEl.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  // Map to SVG coordinate space
  const svgMouseX = (mouseX / rect.width) * viewWidth

  // Find nearest point
  const rows = chartPoints.value
  const den  = Math.max(rows.length - 1, 1)
  const idx  = Math.round(((svgMouseX - paddingX) / innerWidth.value) * den)
  const clamped = Math.max(0, Math.min(rows.length - 1, idx))
  const row = rows[clamped]

  tooltip.visible   = true
  tooltip.label     = row.label
  tooltip.a         = row.a
  tooltip.b         = row.b
  tooltip.svgX      = paddingX + (clamped / den) * innerWidth.value
  tooltip.primaryY  = paddingTop + innerHeight.value - (row.a / maxValue.value) * innerHeight.value
  tooltip.secondaryY = row.b !== null
    ? paddingTop + innerHeight.value - (row.b / maxValue.value) * innerHeight.value
    : null

  // Page position for HTML tooltip
  tooltip.pageX = e.clientX + 14
  tooltip.pageY = e.clientY - 10
}

const cssVars = computed(() => ({ '--chart-height': `${viewHeight.value}px` }))
</script>

<style scoped>
.liquid-line-chart { display: grid; gap: 10px; }

/* Chart wrap */
.chart-wrap { display: grid; gap: 4px; }

/* SVG canvas */
.chart-svg {
  width: 100%;
  height: var(--chart-height);
  border-radius: 16px;
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.06) 0%,
    rgba(255,255,255,0.02) 100%
  );
  border: 1px solid var(--admin-border);
  cursor: crosshair;
  overflow: visible;
}

/* Animated clip rect */
.clip-rect {
  transition: width 1s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Grid */
.grid-line {
  stroke: var(--admin-border);
  stroke-width: 1;
  stroke-dasharray: 4 8;
}

/* Y-axis labels */
.y-label {
  fill: var(--admin-text-soft);
  font-size: 9px;
  font-family: inherit;
}

/* Paths */
.area-path { pointer-events: none; }
.line-path {
  fill: none;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));
}

/* Dots */
.point-dot {
  stroke: #fff;
  stroke-width: 2;
}

/* Crosshair */
.crosshair {
  stroke: var(--admin-border);
  stroke-width: 1;
  stroke-dasharray: 3 5;
}
.tooltip-dot {
  stroke: #fff;
  stroke-width: 2;
}

/* X-axis labels */
.axis-labels {
  display: flex;
  justify-content: space-between;
  padding-inline: 6px;
  color: var(--admin-text-soft);
  font-size: 11px;
}

/* Legend */
.legend-row { display: flex; flex-wrap: wrap; gap: 14px; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-main); }
.legend-item i { width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 0 2px rgba(255,255,255,0.3); }

/* Empty state */
.chart-empty {
  min-height: 180px;
  border: 1px dashed var(--admin-border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--admin-text-soft);
  font-size: 13px;
  background: rgba(255,255,255,0.02);
}
.empty-icon { font-size: 28px; opacity: 0.5; }
</style>

<!-- Global tooltip (outside scoped) -->
<style>
.chart-tooltip {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  background: var(--admin-panel-bg, #1e1e2e);
  border: 1px solid var(--admin-border, rgba(255,255,255,0.1));
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 140px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.25);
  font-family: inherit;
  animation: tooltipIn 0.12s ease;
}
@keyframes tooltipIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.tooltip-label {
  font-size: 11px;
  color: var(--admin-text-soft, #888);
  margin-bottom: 6px;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.tooltip-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  margin-top: 3px;
  color: var(--text-main, #fff);
}
.tooltip-dot-swatch {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tooltip-row strong {
  margin-right: auto;
  font-size: 13px;
}
</style>