<template>
  <section class="traffic-tab">

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری ترافیک سایت...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">

      <!-- ── Top KPIs ── -->
      <div class="kpi-strip">
        <article class="kpi-card glass-card" v-for="kpi in topKpis" :key="kpi.label" :style="`--accent:${kpi.color}`">
          <div class="kpi-top">
            <span class="kpi-icon">{{ kpi.icon }}</span>
            <span class="kpi-label">{{ kpi.label }}</span>
          </div>
          <div class="kpi-value">{{ kpi.value }}</div>
        </article>
      </div>

      <!-- ── Trend chart + Source breakdown ── -->
      <div class="grid-2">

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📈</span>
            <h3>بازدید روزانه (کل سایت / صفحه انتخاب‌شده)</h3>
          </div>
          <div class="chart-pad">
            <AnalyticsLiquidLineChart
              :points="trendPoints"
              primary-label="کل سایت"
              secondary-label="صفحه انتخاب‌شده"
              primary-color="#818cf8"
              primary-color-soft="#c4b5fd"
              secondary-color="#f97316"
              secondary-color-soft="#fde68a"
              empty-text="داده‌ای برای بازدید روزانه ثبت نشده است."
              :height="240"
            />
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🌐</span>
            <h3>منابع بازدید</h3>
          </div>

          <!-- Source highlight chips -->
          <div class="source-chips">
            <div
              v-for="row in sourceHighlights"
              :key="`chip-${row.source_channel}`"
              class="source-chip"
              :style="`--src-color:${sourceColor(row.source_channel)}`"
            >
              <span class="src-icon">{{ sourceIcon(row.source_channel) }}</span>
              <div class="src-info">
                <span class="src-name">{{ sourceLabel(row.source_channel) }}</span>
                <strong class="src-count">{{ fa(row.views) }}</strong>
              </div>
              <span class="src-pct">{{ fa1(row.percent) }}٪</span>
            </div>
          </div>

          <!-- Bar breakdown -->
          <div class="source-bars">
            <div
              v-for="row in data.charts?.source_breakdown || []"
              :key="row.source_channel"
              class="src-bar-row"
            >
              <span class="src-bar-label">{{ sourceLabel(row.source_channel) }}</span>
              <div class="src-bar-track">
                <div
                  class="src-bar-fill"
                  :style="`width:${sourceWidth(row.views)}%; background:${sourceColor(row.source_channel)}`"
                ></div>
              </div>
              <span class="src-bar-val">{{ fa(row.views) }}</span>
            </div>
            <p v-if="!(data.charts?.source_breakdown || []).length" class="empty-cell">
              داده‌ای برای منبع ترافیک ثبت نشده است.
            </p>
          </div>

          <div class="channel-group-wrap">
            <h4>تفکیک کانال بازاریابی</h4>
            <div class="source-bars">
              <div
                v-for="row in data.charts?.channel_group_breakdown || []"
                :key="`channel-${row.channel_group}`"
                class="src-bar-row"
              >
                <span class="src-bar-label">{{ channelGroupLabel(row.channel_group) }}</span>
                <div class="src-bar-track">
                  <div
                    class="src-bar-fill"
                    :style="`width:${channelGroupWidth(row.views)}%; background:${channelGroupColor(row.channel_group)}`"
                  ></div>
                </div>
                <span class="src-bar-val">{{ fa(row.views) }}</span>
              </div>
              <p v-if="!(data.charts?.channel_group_breakdown || []).length" class="empty-cell">
                داده‌ای برای کانال بازاریابی ثبت نشده است.
              </p>
            </div>
          </div>
        </article>

      </div>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🎯</span>
          <h3>Attribution کمپین‌ها (First / Last Touch)</h3>
        </div>
        <div v-if="advancedLoading" class="empty-cell">در حال بارگذاری Attribution...</div>
        <div v-else-if="advancedError" class="empty-cell error-text">{{ advancedError }}</div>
        <template v-else>
          <div class="attribution-summary">
            <div class="attr-chip">
              <span>تبدیل کل</span>
              <strong>{{ fa(attribution.conversions_total || 0) }}</strong>
            </div>
            <div class="attr-chip">
              <span>درآمد کل</span>
              <strong>{{ fa(attribution.revenue_total || 0) }} تومان</strong>
            </div>
          </div>
          <div class="grid-2 attr-grid">
            <article class="nested-panel glass-card">
              <div class="panel-header">
                <span class="panel-icon">1st</span>
                <h3>First Touch</h3>
              </div>
              <div class="table-wrap">
                <table>
                  <thead><tr><th>کانال / کمپین</th><th>تبدیل</th><th>سهم</th><th>درآمد</th></tr></thead>
                  <tbody>
                    <tr v-for="row in firstTouchRows" :key="`ft-${row.label}-${row.utm_campaign}`">
                      <td>
                        <div class="utm-title">{{ row.label || '-' }}</div>
                        <small class="utm-meta">
                          {{ row.utm_campaign || row.utm_source || row.source_channel || 'بدون UTM' }}
                        </small>
                      </td>
                      <td class="num">{{ fa(row.conversions) }}</td>
                      <td class="num">{{ fa2(row.conversion_share) }}٪</td>
                      <td class="num">{{ fa(row.revenue) }}</td>
                    </tr>
                    <tr v-if="!firstTouchRows.length">
                      <td colspan="4" class="empty-cell">داده‌ای ثبت نشده.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>
            <article class="nested-panel glass-card">
              <div class="panel-header">
                <span class="panel-icon">Last</span>
                <h3>Last Touch</h3>
              </div>
              <div class="table-wrap">
                <table>
                  <thead><tr><th>کانال / کمپین</th><th>تبدیل</th><th>سهم</th><th>درآمد</th></tr></thead>
                  <tbody>
                    <tr v-for="row in lastTouchRows" :key="`lt-${row.label}-${row.utm_campaign}`">
                      <td>
                        <div class="utm-title">{{ row.label || '-' }}</div>
                        <small class="utm-meta">
                          {{ row.utm_campaign || row.utm_source || row.source_channel || 'بدون UTM' }}
                        </small>
                      </td>
                      <td class="num">{{ fa(row.conversions) }}</td>
                      <td class="num">{{ fa2(row.conversion_share) }}٪</td>
                      <td class="num">{{ fa(row.revenue) }}</td>
                    </tr>
                    <tr v-if="!lastTouchRows.length">
                      <td colspan="4" class="empty-cell">داده‌ای ثبت نشده.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>
          </div>
        </template>
      </article>

      <!-- ── Group summary table ── -->
      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">📁</span>
          <h3>گروه‌بندی صفحات اصلی</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>گروه</th><th>بازدید</th><th>نشست</th><th>زیرصفحه</th><th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in data.group_summary || []"
                :key="row.group_key"
                :class="{ 'active-row': data.selected_group?.group_key === row.group_key }"
              >
                <td class="group-name">
                  <span class="group-dot"></span>
                  {{ row.label }}
                </td>
                <td class="num">{{ fa(row.views) }}</td>
                <td class="num">{{ fa(row.unique_sessions) }}</td>
                <td class="num">{{ fa(row.pages_count) }}</td>
                <td>
                  <button class="pick-btn" @click="$emit('pick-group', row.group_key)">
                    انتخاب ←
                  </button>
                </td>
              </tr>
              <tr v-if="!(data.group_summary || []).length">
                <td colspan="5" class="empty-cell">گروهی یافت نشد.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- ── Subpages of selected group ── -->
      <article class="panel glass-card" v-if="data.selected_group">
        <div class="panel-header">
          <span class="panel-icon">📄</span>
          <h3>زیرصفحه‌های گروه</h3>
          <span class="active-badge">{{ data.selected_group.label }}</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>مسیر</th><th>بازدید</th><th>نشست</th><th>نرخ خروج</th><th>نرخ پرش</th><th>تبدیل Landing</th><th></th></tr>
            </thead>
            <tbody>
              <tr
                v-for="row in data.selected_group?.pages || []"
                :key="row.path"
                :class="{ 'active-row': data.selected_page?.path === row.path }"
              >
                <td><code class="path-code">{{ row.path }}</code></td>
                <td class="num">{{ fa(row.views) }}</td>
                <td class="num">{{ fa(row.unique_sessions) }}</td>
                <td class="num">
                  <span class="badge" :class="exitClass(row.exit_rate)">
                    {{ fa2(row.exit_rate) }}٪
                  </span>
                </td>
                <td class="num">
                  <span class="badge" :class="bounceClass(row.bounce_rate)">
                    {{ fa2(row.bounce_rate) }}٪
                  </span>
                </td>
                <td class="num">
                  <span class="badge" :class="landingClass(row.landing_conversion_rate)">
                    {{ fa2(row.landing_conversion_rate) }}٪
                  </span>
                </td>
                <td>
                  <button class="pick-btn" @click="$emit('pick-page', row.path)">
                    انتخاب ←
                  </button>
                </td>
              </tr>
              <tr v-if="!(data.selected_group?.pages || []).length">
                <td colspan="7" class="empty-cell">صفحه‌ای یافت نشد.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- ── Selected page deep-dive ── -->
      <article class="panel glass-card selected-panel" v-if="data.selected_page">
        <div class="panel-header">
          <span class="panel-icon">🔎</span>
          <h3>تحلیل صفحه انتخاب‌شده</h3>
          <code class="path-code small">{{ data.selected_page?.path || '-' }}</code>
        </div>

        <!-- Page KPIs -->
        <div class="page-kpis">
          <div class="page-kpi" v-for="k in pageKpis" :key="k.label">
            <span class="page-kpi-icon">{{ k.icon }}</span>
            <div>
              <span class="page-kpi-label">{{ k.label }}</span>
              <strong class="page-kpi-val">{{ k.value }}</strong>
            </div>
          </div>
        </div>

        <!-- Page charts -->
        <div class="grid-2">
          <article class="nested-panel glass-card">
            <div class="panel-header">
              <span class="panel-icon">📅</span>
              <h3>بازدید روزانه این صفحه</h3>
            </div>
            <div class="chart-pad">
              <AnalyticsLiquidLineChart
                :points="selectedTrendPoints"
                primary-label="بازدید صفحه"
                primary-color="#6ee7b7"
                primary-color-soft="#a7f3d0"
                empty-text="برای این صفحه داده روزانه ثبت نشده است."
                :height="200"
              />
            </div>
          </article>

          <article class="nested-panel glass-card">
            <div class="panel-header">
              <span class="panel-icon">🌐</span>
              <h3>منبع بازدید این صفحه</h3>
            </div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>منبع</th><th>بازدید</th><th>نشست</th></tr></thead>
                <tbody>
                  <tr v-for="row in data.selected_page?.source_breakdown || []" :key="`sel-src-${row.source_channel}`">
                    <td>
                      <span class="src-dot" :style="`background:${sourceColor(row.source_channel)}`"></span>
                      {{ sourceLabel(row.source_channel) }}
                    </td>
                    <td class="num">{{ fa(row.views) }}</td>
                    <td class="num">{{ fa(row.unique_sessions) }}</td>
                  </tr>
                  <tr v-if="!(data.selected_page?.source_breakdown || []).length">
                    <td colspan="3" class="empty-cell">داده‌ای ثبت نشده.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </div>
        <article class="nested-panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🧭</span>
            <h3>کانال‌های این صفحه (Organic / Paid / ...)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>کانال</th><th>بازدید</th><th>نشست</th><th>سهم</th></tr></thead>
              <tbody>
                <tr v-for="row in data.selected_page?.channel_group_breakdown || []" :key="`sel-grp-${row.channel_group}`">
                  <td>
                    <span class="src-dot" :style="`background:${channelGroupColor(row.channel_group)}`"></span>
                    {{ channelGroupLabel(row.channel_group) }}
                  </td>
                  <td class="num">{{ fa(row.views) }}</td>
                  <td class="num">{{ fa(row.unique_sessions) }}</td>
                  <td class="num">{{ fa2(row.share_percent) }}٪</td>
                </tr>
                <tr v-if="!(data.selected_page?.channel_group_breakdown || []).length">
                  <td colspan="4" class="empty-cell">داده‌ای ثبت نشده.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </article>

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

defineEmits(['pick-page', 'pick-group'])

const fa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa1 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 1 })
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })

// ── Source helpers ─────────────────────────────────────────────────────────
const sourceMap   = {
  direct: 'مستقیم',
  google: 'گوگل',
  bing: 'بینگ',
  yahoo: 'یاهو',
  instagram: 'اینستاگرام',
  telegram: 'تلگرام',
  facebook: 'فیسبوک',
  pinterest: 'پینترست',
  linkedin: 'لینکدین',
  x: 'ایکس',
  youtube: 'یوتیوب',
  tiktok: 'تیک‌تاک',
  whatsapp: 'واتساپ',
  email: 'ایمیل',
  referral: 'ارجاعی',
  paid: 'تبلیغاتی',
  other: 'سایر',
}
const srcColors   = {
  direct: '#6ee7b7',
  google: '#93c5fd',
  bing: '#7dd3fc',
  yahoo: '#a78bfa',
  instagram: '#f9a8d4',
  telegram: '#6dd5fa',
  facebook: '#60a5fa',
  pinterest: '#fb7185',
  linkedin: '#38bdf8',
  x: '#94a3b8',
  youtube: '#f87171',
  tiktok: '#f472b6',
  whatsapp: '#34d399',
  email: '#fbbf24',
  referral: '#c4b5fd',
  paid: '#fb923c',
  other: '#cbd5e1',
}
const srcIcons    = {
  direct: '🔗',
  google: '🔍',
  bing: '🔎',
  yahoo: '🔎',
  instagram: '📸',
  telegram: '✈️',
  facebook: '📘',
  pinterest: '📌',
  linkedin: '💼',
  x: '✖️',
  youtube: '▶️',
  tiktok: '🎵',
  whatsapp: '💬',
  email: '✉️',
  referral: '🔁',
  paid: '💳',
  other: '🌐',
}
const sourceLabel = (v) => sourceMap[v]  || v || '-'
const sourceColor = (v) => srcColors[v]  || '#c4b5fd'
const sourceIcon  = (v) => srcIcons[v]   || '🌐'

const sourceMax = computed(() =>
  Math.max(1, ...(props.data?.charts?.source_breakdown || []).map((r) => Number(r.views || 0)))
)
const sourceWidth = (v) => Math.max(4, (Number(v || 0) / sourceMax.value) * 100)

const sourceHighlights = computed(() => {
  const rows  = props.data?.charts?.source_breakdown || []
  const total = Math.max(1, rows.reduce((s, r) => s + Number(r.views || 0), 0))
  return rows.slice(0, 4).map((r) => ({ ...r, percent: (Number(r.views || 0) / total) * 100 }))
})
const attribution = computed(() => props.advanced?.attribution || {})
const firstTouchRows = computed(() => attribution.value?.first_touch || [])
const lastTouchRows = computed(() => attribution.value?.last_touch || [])

const channelGroupMap = {
  organic: 'ارگانیک',
  paid: 'تبلیغاتی',
  email: 'ایمیل',
  referral: 'ارجاعی',
  social: 'شبکه اجتماعی',
  direct: 'مستقیم',
  other: 'سایر',
}
const channelGroupColors = {
  organic: '#22c55e',
  paid: '#fb923c',
  email: '#f59e0b',
  referral: '#a78bfa',
  social: '#38bdf8',
  direct: '#34d399',
  other: '#94a3b8',
}
const channelGroupLabel = (v) => channelGroupMap[v] || v || '-'
const channelGroupColor = (v) => channelGroupColors[v] || '#94a3b8'
const channelGroupMax = computed(() =>
  Math.max(1, ...(props.data?.charts?.channel_group_breakdown || []).map((r) => Number(r.views || 0)))
)
const channelGroupWidth = (v) => Math.max(4, (Number(v || 0) / channelGroupMax.value) * 100)

// ── KPIs ───────────────────────────────────────────────────────────────────
const topKpis = computed(() => {
  const t = props.data?.totals || {}
  return [
    { label: 'کل بازدید صفحات',    value: fa(t.views),                            icon: '👁',  color: '#6ee7b7' },
    { label: 'نشست یکتا',          value: fa(t.unique_sessions),                  icon: '👤',  color: '#93c5fd' },
    { label: 'صفحه در هر نشست',    value: fa2(t.pages_per_session),               icon: '🧭',  color: '#f9a8d4' },
    { label: 'نرخ پرش کل',         value: `${fa2(t.bounce_rate)}٪`,               icon: '↩️',  color: '#fca5a5' },
    { label: 'کاربر جدید',         value: fa(t.new_visitors),                     icon: '🆕',  color: '#a7f3d0' },
    { label: 'کاربر بازگشتی',      value: fa(t.returning_visitors),               icon: '🔁',  color: '#c4b5fd' },
    { label: 'میانگین حضور',        value: `${fa2(t.avg_time_spent_seconds)} ثانیه`, icon: '⏱', color: '#fcd34d' },
    { label: 'میانگین عمق پیمایش', value: `${fa2(t.avg_scroll_depth)}٪`,          icon: '📜',  color: '#c4b5fd' },
  ]
})

const pageKpis = computed(() => {
  const m = props.data?.selected_page?.metrics || {}
  return [
    { label: 'بازدید صفحه',  value: fa(m.views),                            icon: '👁'  },
    { label: 'نشست یکتا',    value: fa(m.unique_sessions),                  icon: '👤'  },
    { label: 'میانگین حضور', value: `${fa2(m.avg_time_spent_seconds)} ثانیه`, icon: '⏱' },
    { label: 'نرخ خروج',     value: `${fa2(m.exit_rate)}٪`,                 icon: '🚪'  },
    { label: 'Landing Session', value: fa(m.landing_sessions),               icon: '🎯'  },
    { label: 'تبدیل Landing', value: `${fa2(m.landing_conversion_rate)}٪`,   icon: '✅'  },
    { label: 'نرخ پرش صفحه', value: `${fa2(m.bounce_rate)}٪`,                icon: '↩️'  },
  ]
})

// ── Date helpers ───────────────────────────────────────────────────────────
const shortDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return v
  return d.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' })
}

const trendPoints = computed(() => {
  const siteRows     = props.data?.charts?.daily_views || []
  const selectedRows = props.data?.selected_page?.daily_views || []
  const siteMap      = new Map(siteRows.map((r) => [String(r.date), Number(r.views || 0)]))
  const selMap       = new Map(selectedRows.map((r) => [String(r.date), Number(r.views || 0)]))
  const allDates     = [...new Set([...siteMap.keys(), ...selMap.keys()])].sort()
  const hasSelected  = selMap.size > 0
  return allDates.map((k) => ({
    label: shortDate(k),
    a: siteMap.get(k) || 0,
    b: hasSelected ? (selMap.get(k) || 0) : null,
  }))
})

const selectedTrendPoints = computed(() =>
  (props.data?.selected_page?.daily_views || []).map((r) => ({
    label: shortDate(r.date),
    a: Number(r.views || 0),
  }))
)

// ── Badge helpers ──────────────────────────────────────────────────────────
const exitClass = (v) => {
  const n = Number(v || 0)
  if (n <= 30) return 'green'
  if (n <= 60) return 'yellow'
  return 'red'
}
const bounceClass = (v) => {
  const n = Number(v || 0)
  if (n <= 40) return 'green'
  if (n <= 70) return 'yellow'
  return 'red'
}
const landingClass = (v) => {
  const n = Number(v || 0)
  if (n >= 8) return 'green'
  if (n >= 3) return 'yellow'
  return 'red'
}
</script>

<style scoped>
.traffic-tab { display: grid; gap: 12px; }

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

/* Panel header */
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
  flex-wrap: wrap;
}
.panel-icon { font-size: 15px; }
.panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; flex: 1; }

.active-badge {
  font-size: 11px; font-weight: 600; color: #818cf8;
  background: rgba(129,140,248,0.12); border: 1px solid rgba(129,140,248,0.3);
  border-radius: 999px; padding: 2px 10px;
}

/* ── KPI strip ── */
.kpi-strip {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px;
}
.kpi-card {
  padding: 14px; position: relative; overflow: hidden; transition: transform 0.15s;
}
.kpi-card::before {
  content: ''; position: absolute; top: 0; right: 0;
  width: 3px; height: 100%; background: var(--accent); border-radius: 0 18px 18px 0;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-top   { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.kpi-icon  { font-size: 15px; }
.kpi-label { font-size: 11px; color: var(--admin-text-soft); }
.kpi-value { font-size: 1.15rem; font-weight: 700; }

/* ── Grid 2 ── */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.chart-pad { padding: 12px; }

/* ── Source chips ── */
.source-chips { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 12px 14px 0; }
.source-chip {
  display: flex; align-items: center; gap: 8px;
  border: 1px solid var(--admin-border);
  border-radius: 12px; padding: 8px 10px;
  background: rgba(255,255,255,0.03);
  border-right: 3px solid var(--src-color);
}
.src-icon  { font-size: 16px; flex-shrink: 0; }
.src-info  { flex: 1; display: grid; gap: 1px; min-width: 0; }
.src-name  { font-size: 11px; color: var(--admin-text-soft); }
.src-count { font-size: 13px; font-weight: 700; }
.src-pct   { font-size: 12px; font-weight: 600; color: var(--src-color); white-space: nowrap; }

/* ── Source bar breakdown ── */
.source-bars { padding: 10px 14px; display: grid; gap: 8px; }
.src-bar-row { display: flex; align-items: center; gap: 8px; }
.src-bar-label { font-size: 12px; min-width: 70px; color: var(--admin-text-soft); }
.src-bar-track { flex: 1; height: 6px; background: var(--admin-border); border-radius: 99px; overflow: hidden; }
.src-bar-fill  { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.src-bar-val   { font-size: 12px; min-width: 50px; text-align: left; color: var(--text-main); }
.channel-group-wrap {
  border-top: 1px solid var(--admin-border);
  margin-top: 4px;
  padding-top: 6px;
}
.channel-group-wrap h4 {
  margin: 6px 14px 4px;
  font-size: 12px;
  color: var(--admin-text-soft);
}

/* ── Tables ── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right; padding: 8px 12px;
  font-size: 12px; border-bottom: 1px solid var(--admin-border); white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
tr.active-row td { background: rgba(129,140,248,0.06); }
.num { text-align: left; font-variant-numeric: tabular-nums; }
.empty-cell { text-align: center; color: var(--admin-text-soft); font-size: 12px; padding: 14px; }
.error-text { color: #f87171; }

.group-name { display: flex; align-items: center; gap: 7px; }
.group-dot  { width: 7px; height: 7px; border-radius: 50%; background: #818cf8; flex-shrink: 0; }

.path-code { font-family: monospace; font-size: 11px; background: var(--admin-chip-bg); padding: 2px 6px; border-radius: 5px; }
.path-code.small { font-size: 11px; }

.src-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 6px; vertical-align: middle; }

/* Badges */
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.badge.green  { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.badge.yellow { background: rgba(252,211,77,0.15);  color: #fcd34d; }
.badge.red    { background: rgba(248,113,113,0.15); color: #f87171; }

/* Pick button */
.pick-btn {
  border: 1px solid var(--admin-border); border-radius: 8px;
  padding: 5px 10px; font-family: inherit; font-size: 12px;
  cursor: pointer; color: var(--text-main); background: var(--admin-input-bg);
  transition: all 0.12s;
}
.pick-btn:hover {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff; border-color: transparent;
}

/* ── Attribution ── */
.attribution-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-border);
}
.attr-chip {
  background: var(--admin-panel-bg);
  padding: 10px 12px;
  display: grid;
  gap: 3px;
}
.attr-chip span { font-size: 11px; color: var(--admin-text-soft); }
.attr-chip strong { font-size: 1rem; }
.attr-grid { padding: 10px; }
.utm-title { font-size: 12px; }
.utm-meta { color: var(--admin-text-soft); font-size: 10px; }

/* ── Selected page section ── */
.selected-panel { display: grid; gap: 0; }
.page-kpis {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1px; background: var(--admin-border);
  border-bottom: 1px solid var(--admin-border);
}
.page-kpi {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; background: var(--admin-panel-bg);
}
.page-kpi-icon  { font-size: 18px; }
.page-kpi-label { display: block; font-size: 11px; color: var(--admin-text-soft); margin-bottom: 2px; }
.page-kpi-val   { display: block; font-size: 1rem; font-weight: 700; }

.nested-panel { overflow: hidden; }

/* ── Responsive ── */
@media (max-width: 1200px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .page-kpis { grid-template-columns: repeat(2, 1fr); }
  .source-chips { grid-template-columns: 1fr; }
}
@media (max-width: 980px) {
  .grid-2 { grid-template-columns: 1fr; }
  .attribution-summary { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .panel-header { padding: 10px 12px; }
  .table-wrap table { min-width: 560px; }
  .path-code {
    display: inline-block;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    direction: ltr;
    vertical-align: middle;
  }
  .source-bars { padding: 10px 12px; }
  .kpi-strip { grid-template-columns: 1fr; }
  .page-kpis { grid-template-columns: 1fr; }
}
</style>
