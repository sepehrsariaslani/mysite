<template>
  <section class="technical-tab">
    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری پنل فنی و SEO...
    </div>

    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">
      <div class="kpi-grid">
        <article class="kpi-card glass-card">
          <span>میانگین صفحات هر نشست</span>
          <strong>{{ fa2(data.engagement?.pages_per_session) }}</strong>
        </article>
        <article class="kpi-card glass-card">
          <span>نرخ پرش</span>
          <strong>{{ fa2(data.engagement?.bounce_rate) }}٪</strong>
        </article>
        <article class="kpi-card glass-card">
          <span>بازدیدکننده جدید</span>
          <strong>{{ fa(data.engagement?.new_visitors) }}</strong>
        </article>
        <article class="kpi-card glass-card">
          <span>بازدیدکننده بازگشتی</span>
          <strong>{{ fa(data.engagement?.returning_visitors) }}</strong>
        </article>
      </div>

      <div class="grid-2">
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🔎</span>
            <h3>SEO Panel (GSC + GA4)</h3>
            <button class="ghost-btn" @click="$emit('refresh-settings')" :disabled="settingsLoading">↻</button>
          </div>

          <div class="seo-summary">
            <div class="summary-item">
              <span>Organic Sessions</span>
              <strong>{{ fa(data.seo?.local?.organic_sessions) }}</strong>
              <small>{{ fa2(data.seo?.local?.organic_share) }}٪ سهم ارگانیک</small>
            </div>
            <div class="summary-item">
              <span>GA4</span>
              <strong :class="statusClass(data.seo?.ga4?.connected)">{{ data.seo?.ga4?.connected ? 'متصل' : 'متصل نیست' }}</strong>
              <small>{{ data.seo?.ga4?.error || statusText(data.seo?.ga4?.reason) }}</small>
            </div>
            <div class="summary-item">
              <span>GSC</span>
              <strong :class="statusClass(data.seo?.gsc?.connected)">{{ data.seo?.gsc?.connected ? 'متصل' : 'متصل نیست' }}</strong>
              <small>{{ data.seo?.gsc?.error || statusText(data.seo?.gsc?.reason) }}</small>
            </div>
          </div>

          <div class="mini-grid">
            <div class="mini-item">
              <span>GA4 کاربران</span>
              <strong>{{ fa(ga4Overview.total_users) }}</strong>
            </div>
            <div class="mini-item">
              <span>GA4 نشست</span>
              <strong>{{ fa(ga4Overview.sessions) }}</strong>
            </div>
            <div class="mini-item">
              <span>GA4 نرخ پرش</span>
              <strong>{{ fa2(ga4Overview.bounce_rate) }}٪</strong>
            </div>
            <div class="mini-item">
              <span>GSC کلیک</span>
              <strong>{{ fa(gscOverview.clicks) }}</strong>
            </div>
            <div class="mini-item">
              <span>GSC نمایش</span>
              <strong>{{ fa(gscOverview.impressions) }}</strong>
            </div>
            <div class="mini-item">
              <span>GSC CTR</span>
              <strong>{{ fa2(gscOverview.ctr) }}٪</strong>
            </div>
            <div class="mini-item">
              <span>GSC رتبه</span>
              <strong>{{ fa2(gscOverview.position) }}</strong>
            </div>
            <div class="mini-item">
              <span>CWV وضعیت</span>
              <strong>{{ cwvStatusLabel }}</strong>
            </div>
          </div>

          <div class="settings-block">
            <h4>تنظیم اتصال GA4 / GSC</h4>
            <div class="form-grid">
              <label>
                <span>GA4 فعال</span>
                <input type="checkbox" v-model="local.ga4.enabled" :true-value="1" :false-value="0" />
              </label>
              <label>
                <span>GA4 Property ID</span>
                <input v-model="local.ga4.property_id" placeholder="مثلاً 123456789" />
              </label>
              <label class="full">
                <span>GA4 Service Account JSON (اختیاری)</span>
                <textarea v-model="local.ga4.service_account_json" rows="3" placeholder='{"type":"service_account", ...}'></textarea>
              </label>
              <label>
                <span>GA4 Service Account Path (اختیاری)</span>
                <input v-model="local.ga4.service_account_path" placeholder="/path/to/ga4-service-account.json" />
              </label>

              <label>
                <span>GSC فعال</span>
                <input type="checkbox" v-model="local.gsc.enabled" :true-value="1" :false-value="0" />
              </label>
              <label>
                <span>GSC Site URL</span>
                <input v-model="local.gsc.site_url" placeholder="https://example.com/" />
              </label>
              <label class="full">
                <span>GSC Service Account JSON (اختیاری)</span>
                <textarea v-model="local.gsc.service_account_json" rows="3" placeholder='{"type":"service_account", ...}'></textarea>
              </label>
              <label>
                <span>GSC Service Account Path (اختیاری)</span>
                <input v-model="local.gsc.service_account_path" placeholder="/path/to/gsc-service-account.json" />
              </label>
            </div>
            <div class="actions">
              <button class="save-btn" @click="saveSettings" :disabled="settingsSaving">
                {{ settingsSaving ? 'در حال ذخیره...' : 'ذخیره تنظیمات اتصال' }}
              </button>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>کانال ترافیک (GA4)</th><th>نشست</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in ga4Channels" :key="`ga4-${row.channel}`">
                  <td>{{ row.channel }}</td>
                  <td class="num">{{ fa(row.sessions) }}</td>
                </tr>
                <tr v-if="!ga4Channels.length">
                  <td colspan="2" class="empty-cell">برای دیدن کانال‌ها اتصال GA4 لازم است.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Top Query (GSC)</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in gscQueries" :key="`query-${row.query}`">
                  <td>{{ row.query }}</td>
                  <td class="num">{{ fa(row.clicks) }}</td>
                  <td class="num">{{ fa(row.impressions) }}</td>
                  <td class="num">{{ fa2(row.ctr) }}٪</td>
                  <td class="num">{{ fa2(row.position) }}</td>
                </tr>
                <tr v-if="!gscQueries.length">
                  <td colspan="5" class="empty-cell">برای دیدن Queryها اتصال GSC لازم است.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Top Page (GSC)</th><th>Clicks</th><th>Impressions</th><th>Position</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in gscPages" :key="`page-${row.page}`">
                  <td>{{ row.page }}</td>
                  <td class="num">{{ fa(row.clicks) }}</td>
                  <td class="num">{{ fa(row.impressions) }}</td>
                  <td class="num">{{ fa2(row.position) }}</td>
                </tr>
                <tr v-if="!gscPages.length">
                  <td colspan="4" class="empty-cell">برای دیدن صفحات برتر اتصال GSC لازم است.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="crawl-grid">
            <div class="mini-item">
              <span>Crawl 404</span>
              <strong>{{ fa(crawlErrors.total_404) }}</strong>
            </div>
            <div class="mini-item">
              <span>Crawl 500</span>
              <strong>{{ fa(crawlErrors.total_500) }}</strong>
            </div>
            <div class="mini-item">
              <span>Bot 404</span>
              <strong>{{ fa(crawlErrors.bot_404) }}</strong>
            </div>
            <div class="mini-item">
              <span>Bot 500</span>
              <strong>{{ fa(crawlErrors.bot_500) }}</strong>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>مسیر دارای Crawl Error</th><th>تعداد</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in crawlErrors.top_paths || []" :key="`crawl-${row.path}`">
                  <td>{{ row.path }}</td>
                  <td class="num">{{ fa(row.errors) }}</td>
                </tr>
                <tr v-if="!(crawlErrors.top_paths || []).length">
                  <td colspan="2" class="empty-cell">در این بازه crawl error ثبت نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🧪</span>
            <h3>تب فنی (CWV + Error + Uptime)</h3>
          </div>

          <div class="tech-kpis">
            <div class="tech-item">
              <span>LCP</span>
              <strong>{{ fa2(data.technical?.core_web_vitals?.lcp_ms) }} ms</strong>
            </div>
            <div class="tech-item">
              <span>CLS</span>
              <strong>{{ fa2(data.technical?.core_web_vitals?.cls_score) }}</strong>
            </div>
            <div class="tech-item">
              <span>FID</span>
              <strong>{{ fa2(data.technical?.core_web_vitals?.fid_ms) }} ms</strong>
            </div>
            <div class="tech-item">
              <span>INP</span>
              <strong>{{ fa2(data.technical?.core_web_vitals?.inp_ms) }} ms</strong>
            </div>
            <div class="tech-item">
              <span>Load (Avg)</span>
              <strong>{{ fa2(data.technical?.page_speed?.avg_page_load_ms) }} ms</strong>
            </div>
            <div class="tech-item">
              <span>Mobile Load</span>
              <strong>{{ fa2(data.technical?.page_speed?.avg_mobile_page_load_ms) }} ms</strong>
            </div>
            <div class="tech-item">
              <span>404</span>
              <strong>{{ fa(data.technical?.errors?.http_404) }}</strong>
            </div>
            <div class="tech-item">
              <span>500</span>
              <strong>{{ fa(data.technical?.errors?.http_500) }}</strong>
            </div>
            <div class="tech-item full">
              <span>Uptime (Estimated)</span>
              <strong>{{ fa2(data.technical?.uptime?.uptime_percent) }}٪</strong>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Gateway</th><th>Success</th><th>Failed</th><th>Success Rate</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in data.technical?.payment?.gateways || []" :key="row.gateway">
                  <td>{{ row.gateway }}</td>
                  <td class="num">{{ fa(row.success_count) }}</td>
                  <td class="num">{{ fa(row.failed_count) }}</td>
                  <td class="num">{{ fa2(row.success_rate) }}٪</td>
                </tr>
                <tr v-if="!(data.technical?.payment?.gateways || []).length">
                  <td colspan="4" class="empty-cell">داده‌ای برای وضعیت پرداخت ثبت نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <div class="grid-2">
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">👥</span>
            <h3>Audience (City / Device / Source / Browser / OS / Language)</h3>
          </div>

          <div class="mini-grid">
            <div class="mini-item">
              <span>دستگاه</span>
              <strong>{{ fa(audienceDevicesTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>مرورگر</span>
              <strong>{{ fa(audienceBrowsersTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>سیستم عامل</span>
              <strong>{{ fa(audienceOsTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>زبان</span>
              <strong>{{ fa(audienceLanguagesTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>منبع</span>
              <strong>{{ fa(audienceSourcesTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>شهر</span>
              <strong>{{ fa(audienceCitiesTotal) }}</strong>
            </div>
            <div class="mini-item">
              <span>سن (GA4)</span>
              <strong>{{ fa((audienceDemographics.age_brackets || []).length) }}</strong>
            </div>
            <div class="mini-item">
              <span>جنسیت (GA4)</span>
              <strong>{{ fa((audienceDemographics.gender || []).length) }}</strong>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Source</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceSources" :key="`source-${row.source_channel}`">
                  <td>{{ row.source_channel }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceSources.length">
                  <td colspan="2" class="empty-cell">داده منبع کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>City</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceCities" :key="`city-${row.city}`">
                  <td>{{ row.city }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceCities.length">
                  <td colspan="2" class="empty-cell">داده شهر کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Heatmap</th><th>Day / Hour</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceHeatmapTop" :key="`heat-${row.weekday}-${row.hour}`">
                  <td>
                    <span class="heat-chip" :style="{ '--heat': row.intensity }"></span>
                  </td>
                  <td>{{ weekdayLabel(row.weekday) }} / {{ toHour(row.hour) }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceHeatmapTop.length">
                  <td colspan="3" class="empty-cell">داده heatmap کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Device</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceDevices" :key="`dev-${row.device_type}`">
                  <td>{{ row.device_type }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceDevices.length">
                  <td colspan="2" class="empty-cell">داده دستگاه کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Browser</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceBrowsers" :key="`browser-${row.browser || row.label}`">
                  <td>{{ row.browser || row.label }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceBrowsers.length">
                  <td colspan="2" class="empty-cell">داده مرورگر کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>OS</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceOs" :key="`os-${row.os || row.label}`">
                  <td>{{ row.os || row.label }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceOs.length">
                  <td colspan="2" class="empty-cell">داده سیستم عامل کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Language</th><th>Count</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in audienceLanguages" :key="`lang-${row.language || row.label}`">
                  <td>{{ row.language || row.label }}</td>
                  <td class="num">{{ fa(row.value) }}</td>
                </tr>
                <tr v-if="!audienceLanguages.length">
                  <td colspan="2" class="empty-cell">داده زبان کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📣</span>
            <h3>Social (Traffic / Conversion / Best Content)</h3>
          </div>

          <div class="mini-grid">
            <div class="mini-item">
              <span>کل بازدید اجتماعی</span>
              <strong>{{ fa(data.social?.total_social_views) }}</strong>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>شبکه</th><th>بازدید</th><th>Add To Cart</th><th>Order</th><th>Conversion</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in socialChannels" :key="`social-${row.channel}`">
                  <td>{{ row.channel }}</td>
                  <td class="num">{{ fa(row.page_views) }}</td>
                  <td class="num">{{ fa(row.add_to_cart) }}</td>
                  <td class="num">{{ fa(row.orders) }}</td>
                  <td class="num">{{ fa2(row.conversion_rate) }}٪</td>
                </tr>
                <tr v-if="!socialChannels.length">
                  <td colspan="5" class="empty-cell">داده اجتماعی کافی نیست.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>شبکه</th><th>محتوا</th><th>بازدید</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in socialBestContent" :key="`social-content-${row.channel}-${row.content}`">
                  <td>{{ row.channel }}</td>
                  <td>{{ row.content }}</td>
                  <td class="num">{{ fa(row.views) }}</td>
                </tr>
                <tr v-if="!socialBestContent.length">
                  <td colspan="3" class="empty-cell">محتوای برتر اجتماعی هنوز ثبت نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  settings: { type: Object, default: () => ({ ga4: {}, gsc: {} }) },
  settingsLoading: { type: Boolean, default: false },
  settingsSaving: { type: Boolean, default: false },
})

const emit = defineEmits(['save-settings', 'refresh-settings'])

const local = reactive({
  ga4: { enabled: 0, property_id: '', service_account_path: '', service_account_json: '' },
  gsc: { enabled: 0, site_url: '', service_account_path: '', service_account_json: '' },
})

watch(
  () => props.settings,
  (value) => {
    local.ga4 = {
      enabled: Number(value?.ga4?.enabled || 0),
      property_id: value?.ga4?.property_id || '',
      service_account_path: value?.ga4?.service_account_path || '',
      service_account_json: value?.ga4?.service_account_json || '',
    }
    local.gsc = {
      enabled: Number(value?.gsc?.enabled || 0),
      site_url: value?.gsc?.site_url || '',
      service_account_path: value?.gsc?.service_account_path || '',
      service_account_json: value?.gsc?.service_account_json || '',
    }
  },
  { deep: true, immediate: true },
)

const gscQueries = computed(() => {
  const rows = props.data?.seo?.gsc?.top_queries || []
  if (rows.length) return rows
  return (props.data?.seo?.local?.top_keywords || []).map((row) => ({
    query: row.query,
    clicks: row.count || 0,
    impressions: 0,
    ctr: 0,
    position: 0,
  }))
})
const gscPages = computed(() => {
  const rows = props.data?.seo?.gsc?.top_pages || []
  if (rows.length) return rows
  return (props.data?.seo?.local?.top_landing_pages || []).map((row) => ({
    page: row.path,
    clicks: row.views || 0,
    impressions: 0,
    position: 0,
  }))
})
const ga4Channels = computed(() => props.data?.seo?.ga4?.channels || [])
const ga4Overview = computed(() => props.data?.seo?.ga4?.overview || {})
const gscOverview = computed(() => props.data?.seo?.gsc?.overview || {})
const crawlErrors = computed(() => props.data?.seo?.crawl_errors || { total_404: 0, total_500: 0, bot_404: 0, bot_500: 0, top_paths: [] })
const cwvStatusLabel = computed(() => {
  const value = String(props.data?.seo?.cwv_snapshot?.status || props.data?.technical?.core_web_vitals?.status || '').toLowerCase()
  if (value === 'good') return 'خوب'
  if (value === 'needs_improvement') return 'نیازمند بهبود'
  if (value === 'poor') return 'ضعیف'
  return '-'
})

const audienceDevices = computed(() => props.data?.audience?.device_breakdown || [])
const audienceSources = computed(() => props.data?.audience?.source_breakdown || [])
const audienceCities = computed(() => props.data?.audience?.city_breakdown || [])
const audienceBrowsers = computed(() => props.data?.audience?.browser_breakdown?.length ? props.data.audience.browser_breakdown : props.data?.audience?.ga4_audience?.by_browser || [])
const audienceOs = computed(() => props.data?.audience?.os_breakdown?.length ? props.data.audience.os_breakdown : props.data?.audience?.ga4_audience?.by_os || [])
const audienceLanguages = computed(() => props.data?.audience?.language_breakdown?.length ? props.data.audience.language_breakdown : props.data?.audience?.ga4_audience?.by_language || [])
const audienceDemographics = computed(() => props.data?.audience?.demographics || { gender: [], age_brackets: [] })
const audienceHeatmapTop = computed(() => {
  const rows = props.data?.audience?.time_heatmap || []
  const max = Math.max(1, ...rows.map((row) => Number(row?.value || 0)))
  return [...rows]
    .sort((a, b) => Number(b?.value || 0) - Number(a?.value || 0))
    .slice(0, 24)
    .map((row) => ({
      ...row,
      intensity: Math.max(0.08, Math.min(1, Number(row?.value || 0) / max)),
    }))
})
const socialChannels = computed(() => props.data?.social?.channels || [])
const socialBestContent = computed(() => props.data?.social?.best_content || [])

const audienceDevicesTotal = computed(() => audienceDevices.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))
const audienceSourcesTotal = computed(() => audienceSources.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))
const audienceCitiesTotal = computed(() => audienceCities.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))
const audienceBrowsersTotal = computed(() => audienceBrowsers.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))
const audienceOsTotal = computed(() => audienceOs.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))
const audienceLanguagesTotal = computed(() => audienceLanguages.value.reduce((sum, row) => sum + Number(row?.value || 0), 0))

const fa = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })

const statusClass = (ok) => (ok ? 'ok' : 'bad')
const reasonMap = {
  ok: 'اتصال برقرار است.',
  disabled: 'غیرفعال است.',
  missing_property_id: 'Property ID تنظیم نشده است.',
  missing_site_url: 'Site URL تنظیم نشده است.',
  missing_credentials: 'Service Account تنظیم نشده است.',
  missing_sdk: 'کتابخانه Google SDK روی سرور نصب نیست.',
  request_failed: 'اتصال برقرار نشد.',
}
const statusText = (reason) => reasonMap[String(reason || '').toLowerCase()] || '-'
const weekdayNames = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
const weekdayLabel = (index) => weekdayNames[Number(index)] || '-'
const toHour = (h) => `${String(Number(h || 0)).padStart(2, '0')}:00`

function saveSettings() {
  emit('save-settings', {
    ga4: { ...local.ga4 },
    gsc: { ...local.gsc },
  })
}
</script>

<style scoped>
.technical-tab { display: grid; gap: 12px; }

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

.glass-card {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.kpi-card {
  padding: 12px;
  display: grid;
  gap: 5px;
}

.kpi-card span { font-size: 11px; color: var(--admin-text-soft); }
.kpi-card strong { font-size: 1.1rem; }

.grid-2 {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 12px;
}

.panel { overflow: hidden; }

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--admin-border);
}

.panel-header h3 {
  margin: 0;
  font-size: 0.92rem;
  flex: 1;
}

.panel-icon { font-size: 16px; }

.ghost-btn,
.save-btn {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 7px 12px;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}

.ghost-btn { background: var(--admin-input-bg); color: var(--text-main); }
.save-btn {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  border-color: transparent;
}

.seo-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  background: var(--admin-border);
}

.mini-grid {
  padding: 10px 12px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.mini-item {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 8px 10px;
  display: grid;
  gap: 3px;
}

.mini-item span {
  font-size: 11px;
  color: var(--admin-text-soft);
}

.mini-item strong {
  font-size: 0.96rem;
}

.crawl-grid {
  padding: 0 12px 12px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.summary-item {
  background: var(--admin-panel-bg);
  padding: 10px;
  display: grid;
  gap: 4px;
}

.summary-item span { font-size: 11px; color: var(--admin-text-soft); }
.summary-item strong { font-size: 1rem; }
.summary-item strong.ok { color: #6ee7b7; }
.summary-item strong.bad { color: #fca5a5; }
.summary-item small {
  font-size: 10px;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.settings-block {
  padding: 12px;
  border-top: 1px solid var(--admin-border);
  border-bottom: 1px solid var(--admin-border);
}

.settings-block h4 {
  margin: 0 0 8px;
  font-size: 0.85rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.form-grid label {
  display: grid;
  gap: 4px;
}

.form-grid label.full {
  grid-column: 1 / -1;
}

.form-grid span {
  font-size: 11px;
  color: var(--admin-text-soft);
}

.form-grid input,
.form-grid textarea {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: 12px;
}

.actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.tech-kpis {
  padding: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.tech-item {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 8px 10px;
  display: grid;
  gap: 3px;
}

.tech-item.full {
  grid-column: 1 / -1;
}

.tech-item span { font-size: 11px; color: var(--admin-text-soft); }
.tech-item strong { font-size: 0.98rem; }

.table-wrap { overflow-x: auto; }

table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right;
  padding: 8px 12px;
  font-size: 12px;
  border-bottom: 1px solid var(--admin-border);
  white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
.num { text-align: left; font-variant-numeric: tabular-nums; }
.empty-cell { text-align: center; color: var(--admin-text-soft); }

.heat-chip {
  --heat: 0.15;
  width: 100%;
  max-width: 52px;
  height: 12px;
  border-radius: 999px;
  display: inline-block;
  background: linear-gradient(
    90deg,
    rgba(125, 211, 252, calc(var(--heat) * 0.45)),
    rgba(99, 102, 241, calc(var(--heat) * 0.95))
  );
  border: 1px solid rgba(129, 140, 248, 0.18);
}

@media (max-width: 1000px) {
  .grid-2 { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .seo-summary { grid-template-columns: 1fr; }
  .mini-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .crawl-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .tech-kpis { grid-template-columns: 1fr; }
  .mini-grid { grid-template-columns: 1fr; }
  .crawl-grid { grid-template-columns: 1fr; }
}
</style>
