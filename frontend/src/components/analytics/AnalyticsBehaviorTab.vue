<template>
  <section class="behavior-tab">

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری رفتار کاربر...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <!-- Content -->
    <template v-else-if="data">

      <!-- Row 1: Entry sources + Exit pages -->
      <div class="grid-2">

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📥</span>
            <h3>ورودی ترافیک</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>منبع</th><th>نشست</th><th>سهم</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in sourcesWithShare" :key="row.source_channel">
                  <td>
                    <span class="source-dot" :style="`background:${sourceColor(row.source_channel)}`"></span>
                    {{ sourceLabel(row.source_channel) }}
                  </td>
                  <td class="num">{{ fa(row.sessions) }}</td>
                  <td class="num">
                    <div class="bar-cell">
                      <div class="bar-track">
                        <div class="bar-fill" :style="`width:${row.share}%;background:${sourceColor(row.source_channel)}`"></div>
                      </div>
                      <span>{{ fa1(row.share) }}٪</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🚪</span>
            <h3>صفحات خروج</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>نشانی</th><th>خروج</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in data.exit_pages || []" :key="row.url">
                  <td class="url-cell" :title="row.url">{{ row.url }}</td>
                  <td class="num">{{ fa(row.exits) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

      </div>

      <div class="grid-3">
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📞</span>
            <h3>CTA ها (تماس/واتساپ/ایمیل)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>نوع</th><th>کلیک</th><th>نشست</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in ctaSummaryRows" :key="`cta-${row.event_type}`">
                  <td>{{ row.label || row.event_type }}</td>
                  <td class="num">{{ fa(row.clicks) }}</td>
                  <td class="num">{{ fa(row.sessions) }}</td>
                </tr>
                <tr v-if="!ctaSummaryRows.length">
                  <td colspan="3" class="empty-cell">داده‌ای ثبت نشده.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📝</span>
            <h3>ارسال فرم‌ها</h3>
          </div>
          <div class="summary-strip compact">
            <div class="summary-card">
              <span class="summary-icon">Σ</span>
              <div>
                <p>کل ارسال</p>
                <strong>{{ fa(data.form_interactions?.total_submissions) }}</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon">👥</span>
              <div>
                <p>نشست یکتا</p>
                <strong>{{ fa(data.form_interactions?.unique_sessions) }}</strong>
              </div>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>نوع فرم</th><th>ارسال</th><th>نشست</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in formTypeRows" :key="`form-${row.form_type}`">
                  <td>{{ row.form_type || '-' }}</td>
                  <td class="num">{{ fa(row.submissions) }}</td>
                  <td class="num">{{ fa(row.sessions) }}</td>
                </tr>
                <tr v-if="!formTypeRows.length">
                  <td colspan="3" class="empty-cell">داده‌ای ثبت نشده.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🔎</span>
            <h3>عبارات جستجوی داخلی</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>عبارت</th><th>تعداد</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in searchTermRows" :key="`search-${row.term}`">
                  <td>{{ row.term }}</td>
                  <td class="num">{{ fa(row.count) }}</td>
                </tr>
                <tr v-if="!searchTermRows.length">
                  <td colspan="2" class="empty-cell">جستجویی ثبت نشده.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">📍</span>
          <h3>CTA بر اساس صفحه</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>مسیر</th><th>تماس</th><th>واتساپ</th><th>ایمیل</th><th>کل</th><th>نشست</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in ctaPageRows" :key="`cta-page-${row.path}`">
                <td class="url-cell" :title="row.path">{{ row.path }}</td>
                <td class="num">{{ fa(row.call_click) }}</td>
                <td class="num">{{ fa(row.whatsapp_click) }}</td>
                <td class="num">{{ fa(row.email_click) }}</td>
                <td class="num">{{ fa(row.total_clicks) }}</td>
                <td class="num">{{ fa(row.sessions) }}</td>
              </tr>
              <tr v-if="!ctaPageRows.length">
                <td colspan="6" class="empty-cell">داده‌ای ثبت نشده.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- Row 2: Product page analysis -->
      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">📄</span>
          <h3>تحلیل صفحه محصول</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>مدل</th>
                <th>بازدید</th>
                <th>زمان (ثانیه)</th>
                <th>پیمایش٪</th>
                <th>باز کردن تصویر٪</th>
                <th>افزودن به سبد٪</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.product_page_analysis || []" :key="row.model_name">
                <td class="model-name">{{ row.model_name }}</td>
                <td class="num">{{ fa(row.view_sessions) }}</td>
                <td class="num">{{ fa2(row.avg_time_spent_seconds) }}</td>
                <td class="num">
                  <span class="badge" :class="scrollClass(row.avg_scroll_depth)">{{ fa2(row.avg_scroll_depth) }}٪</span>
                </td>
                <td class="num">{{ fa2(row.images_open_rate) }}٪</td>
                <td class="num">
                  <span class="badge" :class="cartClass(row.add_to_cart_rate)">{{ fa2(row.add_to_cart_rate) }}٪</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">📆</span>
          <h3>گزارش Cohort و نگهداشت</h3>
        </div>

        <div v-if="advancedLoading" class="empty-cell">در حال بارگذاری کوهورت...</div>
        <div v-else-if="advancedError" class="empty-cell error-text">{{ advancedError }}</div>
        <template v-else>
          <div class="summary-strip retention-strip">
            <div class="summary-card">
              <span class="summary-icon">7</span>
              <div>
                <p>نگهداشت ۷ روزه</p>
                <strong>{{ fa2(cohortOverall.retention_7_rate) }}٪</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon">30</span>
              <div>
                <p>نگهداشت ۳۰ روزه</p>
                <strong>{{ fa2(cohortOverall.retention_30_rate) }}٪</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon">90</span>
              <div>
                <p>نگهداشت ۹۰ روزه</p>
                <strong>{{ fa2(cohortOverall.retention_90_rate) }}٪</strong>
              </div>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>شروع کوهورت</th>
                  <th>اندازه کوهورت</th>
                  <th>بازگشت ۷ روز</th>
                  <th>بازگشت ۳۰ روز</th>
                  <th>بازگشت ۹۰ روز</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in cohortRows" :key="row.cohort_start">
                  <td>{{ row.cohort_start }}</td>
                  <td class="num">{{ fa(row.cohort_size) }}</td>
                  <td class="num">{{ fa2(row.retention_7_rate) }}٪</td>
                  <td class="num">{{ fa2(row.retention_30_rate) }}٪</td>
                  <td class="num">{{ fa2(row.retention_90_rate) }}٪</td>
                </tr>
                <tr v-if="!cohortRows.length">
                  <td colspan="5" class="empty-cell">داده‌ای برای کوهورت ثبت نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </article>

      <!-- Row 3: Cart analysis -->
      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🛒</span>
          <h3>تحلیل سبد خرید</h3>
        </div>

        <!-- Summary cards -->
        <div class="summary-strip">
          <div class="summary-card">
            <span class="summary-icon">⏱</span>
            <div>
              <p>میانگین زمان افزودن → سفارش</p>
              <strong>{{ fa2(data.cart_analysis?.avg_minutes_add_to_order) }} دقیقه</strong>
            </div>
          </div>
          <div class="summary-card">
            <span class="summary-icon">🔁</span>
            <div>
              <p>میانگین دفعات بازکردن سبد</p>
              <strong>{{ fa2(data.cart_analysis?.avg_cart_open_per_session) }} بار</strong>
            </div>
          </div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>مدل</th>
                <th>افزودن به سبد</th>
                <th>ثبت سفارش</th>
                <th>رها شده</th>
                <th>نرخ ریزش</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.cart_analysis?.abandoned_products || []" :key="row.model_name">
                <td class="model-name">{{ row.model_name }}</td>
                <td class="num">{{ fa(row.add_to_cart) }}</td>
                <td class="num">{{ fa(row.order_submit) }}</td>
                <td class="num loss">{{ fa(row.abandoned) }}</td>
                <td class="num">
                  <span class="badge" :class="abandonClass(abandonRate(row))">
                    {{ fa1(abandonRate(row)) }}٪
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
  data:    { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error:   { type: String, default: '' },
  advanced: { type: Object, default: null },
  advancedLoading: { type: Boolean, default: false },
  advancedError: { type: String, default: '' },
})

const fa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa1 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 1 })
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })

const sourceMap = {
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
const colorMap  = {
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
const sourceLabel = (v) => sourceMap[v] || v || '-'
const sourceColor = (v) => colorMap[v] || '#c4b5fd'

const sourcesWithShare = computed(() => {
  const rows = props.data?.entry_sources || []
  const total = rows.reduce((s, r) => s + Number(r.sessions || 0), 0)
  return rows.map((r) => ({ ...r, share: total ? (Number(r.sessions || 0) / total) * 100 : 0 }))
})
const ctaSummaryRows = computed(() => props.data?.cta_actions?.summary || [])
const ctaPageRows = computed(() => props.data?.cta_actions?.by_page || [])
const formTypeRows = computed(() => props.data?.form_interactions?.by_form_type || [])
const searchTermRows = computed(() => props.data?.internal_search_terms || [])

const cohortRows = computed(() => props.advanced?.cohort?.cohorts || [])
const cohortOverall = computed(() => props.advanced?.cohort?.overall || { retention_7_rate: 0, retention_30_rate: 0, retention_90_rate: 0 })

const abandonRate = (row) => {
  const add = Number(row.add_to_cart || 0)
  if (!add) return 0
  return (Number(row.abandoned || 0) / add) * 100
}

const scrollClass   = (v) => v >= 60 ? 'badge-green' : v >= 30 ? 'badge-yellow' : 'badge-red'
const cartClass     = (v) => v >= 10 ? 'badge-green' : v >= 4  ? 'badge-yellow' : 'badge-red'
const abandonClass  = (v) => v <= 30 ? 'badge-green' : v <= 60 ? 'badge-yellow' : 'badge-red'
</script>

<style scoped>
.behavior-tab {
  display: grid;
  gap: 12px;
}

/* ── State cards ── */
.state-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border-radius: 14px;
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  font-size: 14px;
  color: var(--admin-text-soft);
}
.state-card.error { color: #f87171; }
.state-icon { font-size: 18px; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.7s linear infinite; }

/* ── Layout ── */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

/* ── Panel ── */
.glass-card {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.panel { padding: 0; overflow: hidden; }

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--admin-border);
}
.panel-icon { font-size: 16px; }
.panel-header h3 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

/* ── Table ── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right;
  padding: 8px 12px;
  font-size: 12px;
  border-bottom: 1px solid var(--admin-border);
  white-space: nowrap;
}
th {
  color: var(--admin-text-soft);
  font-weight: 600;
  background: transparent;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
.empty-cell { text-align: center; color: var(--admin-text-soft); font-size: 12px; padding: 12px; }
.error-text { color: #f87171; }

.num { font-variant-numeric: tabular-nums; text-align: left; }
.url-cell {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.model-name {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.loss { color: #f87171; }

/* ── Source dot ── */
.source-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-left: 6px;
  vertical-align: middle;
}

/* ── Bar cell ── */
.bar-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}
.bar-track {
  flex: 1;
  height: 5px;
  background: var(--admin-border);
  border-radius: 99px;
  overflow: hidden;
  min-width: 50px;
}
.bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.4s ease;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}
.badge-green  { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.badge-yellow { background: rgba(252,211,77,0.15);  color: #fcd34d; }
.badge-red    { background: rgba(248,113,113,0.15); color: #f87171; }

/* ── Summary strip ── */
.summary-strip {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-border);
}
.summary-strip.compact {
  border-bottom: none;
}
.summary-strip.retention-strip { grid-template-columns: repeat(3, 1fr); }
.summary-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--admin-panel-bg);
}
.summary-icon { font-size: 22px; }
.summary-card p {
  margin: 0;
  font-size: 11px;
  color: var(--admin-text-soft);
}
.summary-card strong {
  display: block;
  margin-top: 3px;
  font-size: 1rem;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
  .summary-strip { grid-template-columns: 1fr; }
  .summary-strip.retention-strip { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  th, td { padding: 7px 8px; }
}
</style>
