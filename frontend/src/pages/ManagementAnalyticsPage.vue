<template>
  <div class="analytics-page" dir="rtl">
<!-- Ambient background - lighter, fewer blobs -->
    <div class="ambient-bg">
      <div class="blob b1"></div>
      <div class="blob b2"></div>
    </div>

    <div class="layout">
      <!-- ═══════════════════════════════════════════
           SIDEBAR - Desktop only
      ══════════════════════════════════════════════ -->
      <aside class="sidebar glass-card">
        <div class="brand">
          <div class="brand-icon">آ</div>
          <div class="brand-text">
            <strong>آنالیتیکس</strong>
            <small>نمای مدیریتی</small>
          </div>
        </div>

        <nav class="sidebar-nav">
          <a
            v-for="tab in tabs"
            :key="tab.id"
            :href="tab.href"
            class="nav-item"
            :class="{ active: sectionId === tab.id }"
          >
            <component :is="tab.icon" :size="16" class="nav-icon" />
            <span>{{ tab.label }}</span>
          </a>
        </nav>

        <div class="sidebar-meta">
          <div class="meta-chip">
            <span class="meta-label">صفحه فعال</span>
            <strong>{{ activeTabLabel }}</strong>
            <small>{{ jalaliRangeLabel }}</small>
          </div>
          <a class="back-btn" href="/management"><ArrowLeft :size="14" /> بازگشت</a>
        </div>
      </aside>

      <!-- ═══════════════════════════════════════════
           MAIN CONTENT
      ══════════════════════════════════════════════ -->
      <main class="main-col">

        <!-- Compact Header -->
        <header class="page-header glass-card">
          <div class="header-left">
            <span class="eyebrow">{{ activeTabLabel }}</span>
            <h1>داشبورد آنالیتیکس</h1>
          </div>
          <div class="header-right">
            <label class="segment-filter">
              <span>سگمنت</span>
              <select v-model="advanced.segmentKey" @change="applySegment">
                <option v-for="row in segmentOptions" :key="`segment-${row.key}`" :value="row.key">
                  {{ row.title }}
                </option>
              </select>
            </label>
            <!-- Date Range Popover Trigger -->
            <div class="date-popover-wrap" :class="{ open: showDatePicker }">
              <button class="date-trigger" @click="showDatePicker = !showDatePicker">
                <Calendar :size="16" class="date-trigger-icon" />
                <span>{{ jalaliRangeLabel }}</span>
                <component :is="showDatePicker ? ChevronUp : ChevronDown" :size="14" class="caret" />
              </button>

              <!-- Popover -->
              <div class="date-popover glass-card" v-if="showDatePicker" @click.stop>
                <div class="popover-presets">
                  <button
                    v-for="p in presets"
                    :key="p.value"
                    class="preset-btn"
                    :class="{ active: range.preset === p.value }"
                    @click="selectPreset(p.value)"
                  >{{ p.label }}</button>
                </div>
                <div class="popover-custom">
                  <label>
                    <span>از</span>
                    <input type="date" v-model="range.fromDate" />
                  </label>
                  <label>
                    <span>تا</span>
                    <input type="date" v-model="range.toDate" />
                  </label>
                </div>
                <button class="apply-btn" @click="applyAndClose">اعمال و بروزرسانی</button>
              </div>
            </div>

            <button class="refresh-btn" @click="refreshDashboard" :disabled="isLoading">
              <RotateCcw :size="16" :class="{ spinning: isLoading }" />
            </button>
          </div>
        </header>

        <!-- KPI Strip - improved visual hierarchy -->
        <section class="kpi-strip" v-if="sectionId === 'overview' && quickKpis.length">
          <article
            v-for="item in quickKpis"
            :key="item.label"
            class="kpi-card glass-card"
            :style="`--accent: ${item.color}`"
          >
            <div class="kpi-top">
              <component :is="item.icon" :size="16" class="kpi-icon" />
              <span class="kpi-label">{{ item.label }}</span>
            </div>
            <div class="kpi-value">{{ item.value }}</div>
            <div class="kpi-note">{{ item.note }}</div>
          </article>
        </section>

        <section v-if="sectionId === 'overview'" class="overview-hero-grid">
          <article class="overview-hero-main glass-card">
            <div class="hero-head">
              <div>
                <p class="hero-eyebrow">روند بازدید</p>
                <h2>نمودار خطی بازدید کل سایت</h2>
              </div>
              <div class="hero-total">
                <span>مجموع بازدید</span>
                <strong>{{ toFa(overview.data?.kpis?.total_views) }}</strong>
              </div>
            </div>
            <AnalyticsLiquidLineChart
              :points="overviewTrendPoints"
              primary-label="کل بازدید"
              primary-color="#8b5cf6"
              primary-color-soft="#d8b4fe"
              empty-text="برای این بازه زمانی داده‌ای ثبت نشده است."
              :height="260"
            />
          </article>

          <article class="overview-hero-side glass-card">
            <div class="hero-side-head">
              <h3>منبع بازدیدها</h3>
              <span>کل: {{ toFa(overviewSourceTotal) }}</span>
            </div>
            <div class="hero-source-list">
              <div v-for="item in overviewTrafficSources" :key="`hero-src-${item.source_channel}`" class="hero-source-row">
                <div class="hero-source-meta">
                  <strong>{{ sourceLabel(item.source_channel) }}</strong>
                  <span>{{ toFa(item.views) }}</span>
                </div>
                <div class="hero-source-track"><i :style="{ width: `${item.percent}%` }"></i></div>
              </div>
            </div>
            <p class="hero-side-hint">تفکیک منبع: ارگانیک، تبلیغاتی، اجتماعی، ارجاعی و مستقیم</p>
          </article>
        </section>

        <!-- ── OVERVIEW ── -->
        <section v-if="sectionId === 'overview'">
          <AnalyticsOverviewTab
            :data="overview.data"
            :loading="overview.loading"
            :error="overview.error"
            :advanced="advanced.data"
            :advanced-loading="advanced.loading"
            :advanced-error="advanced.error"
          />
        </section>

        <!-- ── TRAFFIC ── -->
        <section v-else-if="sectionId === 'traffic'" class="tab-section">
          <CollapseFilters label="فیلترهای ترافیک">
            <div class="filters-grid">
              <label>
                <span>گروه اصلی</span>
                <select v-model="traffic.filters.group_key">
                  <option value="__all__">همه گروه‌ها</option>
                  <option value="">پیش‌فرض</option>
                  <option v-for="row in traffic.data?.group_summary || []" :key="`group-${row.group_key}`" :value="row.group_key">
                    {{ row.label }} ({{ toFa(row.views) }})
                  </option>
                </select>
              </label>
              <label>
                <span>صفحه</span>
                <select v-model="traffic.filters.page_path">
                  <option value="">پیش‌فرض</option>
                  <option v-for="row in traffic.data?.selected_group?.pages || traffic.data?.available_pages || []" :key="`route-${row.path}`" :value="row.path">
                    {{ row.path }} ({{ toFa(row.views) }})
                  </option>
                </select>
              </label>
              <label>
                <span>تعداد ردیف</span>
                <select v-model.number="traffic.filters.limit">
                  <option :value="10">۱۰</option>
                  <option :value="20">۲۰</option>
                  <option :value="40">۴۰</option>
                  <option :value="80">۸۰</option>
                </select>
              </label>
              <button class="apply-filter-btn" @click="loadTraffic">اعمال فیلتر</button>
            </div>
          </CollapseFilters>
          <AnalyticsTrafficTab
            :data="traffic.data" :loading="traffic.loading" :error="traffic.error"
            :advanced="advanced.data"
            :advanced-loading="advanced.loading"
            :advanced-error="advanced.error"
            @pick-page="pickTrafficPage" @pick-group="pickTrafficGroup"
          />
        </section>

        <!-- ── FUNNEL ── -->
        <section v-else-if="sectionId === 'funnel'" class="tab-section">
          <CollapseFilters label="فیلترهای فانل">
            <div class="filters-grid">
              <label><span>دسته</span><input v-model.trim="funnel.filters.category" placeholder="مثلاً مبل" /></label>
              <label>
                <span>دستگاه</span>
                <select v-model="funnel.filters.device_type">
                  <option value="">همه</option><option value="mobile">موبایل</option><option value="desktop">دسکتاپ</option><option value="tablet">تبلت</option>
                </select>
              </label>
              <label>
                <span>منبع</span>
                <select v-model="funnel.filters.source_channel">
                  <option value="">همه</option>
                  <option value="direct">مستقیم</option>
                  <option value="google">گوگل</option>
                  <option value="bing">بینگ</option>
                  <option value="instagram">اینستاگرام</option>
                  <option value="telegram">تلگرام</option>
                  <option value="whatsapp">واتساپ</option>
                  <option value="email">ایمیل</option>
                  <option value="referral">ارجاعی</option>
                  <option value="paid">تبلیغاتی</option>
                </select>
              </label>
              <button class="apply-filter-btn" @click="loadFunnel">اعمال فیلتر</button>
            </div>
          </CollapseFilters>
          <AnalyticsFunnelTab
            :data="funnel.data" :loading="funnel.loading" :error="funnel.error"
            :diagnosis="funnel.diagnosis" :diagnosisLoading="funnel.diagnosisLoading"
            @diagnose="loadDiagnosis"
          />
        </section>

        <!-- ── BEHAVIOR ── -->
        <section v-else-if="sectionId === 'behavior'">
          <AnalyticsBehaviorTab
            :data="behavior.data"
            :loading="behavior.loading"
            :error="behavior.error"
            :advanced="advanced.data"
            :advanced-loading="advanced.loading"
            :advanced-error="advanced.error"
          />
        </section>

        <!-- ── PRODUCTS ── -->
        <section v-else-if="sectionId === 'products'" class="tab-section">
          <CollapseFilters label="فیلترها و خروجی">
            <div class="filters-grid">
              <label><span>دسته</span><input v-model.trim="products.filters.category" placeholder="همه دسته‌ها" /></label>
              <label>
                <span>مرتب‌سازی</span>
                <select v-model="products.filters.sort_by">
                  <option value="views">بازدید</option>
                  <option value="add_to_cart">افزوده به سبد</option>
                  <option value="purchases">خرید</option>
                  <option value="conversion_rate">نرخ تبدیل</option>
                  <option value="revenue">درآمد</option>
                  <option value="avg_decision_minutes">زمان تصمیم</option>
                </select>
              </label>
              <label>
                <span>ترتیب</span>
                <select v-model="products.filters.sort_order">
                  <option value="desc">نزولی</option>
                  <option value="asc">صعودی</option>
                </select>
              </label>
              <div class="filter-actions">
                <button class="apply-filter-btn" @click="loadProducts(1)">اعمال</button>
                <button class="export-btn" @click="exportProducts('xlsx')">Excel ↓</button>
                <button class="export-btn" @click="exportProducts('csv')">CSV ↓</button>
              </div>
            </div>
          </CollapseFilters>
          <AnalyticsProductsTab :data="products.data" :loading="products.loading" :error="products.error" />
          <div class="pager glass-card" v-if="products.data">
            <button class="pager-btn" :disabled="(products.data.page || 1) <= 1" @click="loadProducts((products.data.page || 1) - 1)"><ArrowLeft :size="14" /> قبلی</button>
            <span class="pager-info">صفحه {{ products.data.page || 1 }} از {{ products.data.total_pages || 1 }}</span>
            <button class="pager-btn" :disabled="(products.data.page || 1) >= (products.data.total_pages || 1)" @click="loadProducts((products.data.page || 1) + 1)">بعدی <ArrowRight :size="14" /></button>
          </div>
        </section>

        <!-- ── TIME COMPARISON ── -->
        <section v-else-if="sectionId === 'time'" class="tab-section">
          <CollapseFilters label="تنظیمات مقایسه زمانی" :open-by-default="true">
            <div class="filters-grid six-col">
              <label><span>بازه اول از</span><input type="date" v-model="time.filters.left_from" /></label>
              <label><span>بازه اول تا</span><input type="date" v-model="time.filters.left_to" /></label>
              <label><span>بازه دوم از</span><input type="date" v-model="time.filters.right_from" /></label>
              <label><span>بازه دوم تا</span><input type="date" v-model="time.filters.right_to" /></label>
              <label>
                <span>بازه آماده</span>
                <select v-model="time.filters.preset">
                  <option value="week_vs_previous">هفته جاری vs قبل</option>
                  <option value="month_vs_previous">ماه جاری vs قبل</option>
                  <option value="year_same_period">همین بازه سال قبل</option>
                </select>
              </label>
              <button class="apply-filter-btn" @click="loadTimeComparison">مقایسه</button>
            </div>
          </CollapseFilters>
          <AnalyticsTimeComparisonTab :data="time.data" :loading="time.loading" :error="time.error" />
        </section>

        <!-- ── SEO + TECHNICAL ── -->
        <section v-else-if="sectionId === 'technical'" class="tab-section">
          <AnalyticsTechnicalTab
            :data="technical.data"
            :loading="technical.loading"
            :error="technical.error"
            :settings="technical.settings || technical.data?.integration_settings || {}"
            :settings-loading="technical.settingsLoading"
            :settings-saving="technical.settingsSaving"
            @refresh-settings="loadTechnicalSettings"
            @save-settings="saveTechnicalSettings"
          />
        </section>

        <!-- ── SETTINGS ── -->
        <section v-else-if="sectionId === 'settings'" class="tab-section">
          <AnalyticsTrackingSettingsTab
            :data="settings.data" :loading="settings.loading"
            :error="settings.error" :saving="settings.saving"
            @refresh="loadSettings" @save="saveSettings"
          />
        </section>

      </main>
    </div>

    <!-- ═══════════════════════════════════════════
         MOBILE BOTTOM TAB BAR
    ══════════════════════════════════════════════ -->
    <nav class="bottom-bar">
      <a
        v-for="tab in tabs"
        :key="tab.id"
        :href="tab.href"
        class="bottom-tab"
        :class="{ active: sectionId === tab.id }"
      >
        <component :is="tab.icon" :size="18" class="bottom-tab-icon" />
        <span class="bottom-tab-label">{{ tab.shortLabel }}</span>
      </a>
    </nav>

    <!-- Backdrop to close date picker -->
    <div v-if="showDatePicker" class="backdrop" @click="showDatePicker = false"></div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  BarChart3, TrendingUp, Filter, User, Package, Clock,
  Search, Settings, ChevronDown, ChevronUp, Calendar,
  RotateCcw, ArrowLeft, ArrowRight, Eye, Zap, Banknote,
  ShoppingCart, TrendingDown
} from 'lucide-vue-next'
import AnalyticsOverviewTab from '../components/analytics/AnalyticsOverviewTab.vue'
import AnalyticsTrafficTab from '../components/analytics/AnalyticsTrafficTab.vue'
import AnalyticsFunnelTab from '../components/analytics/AnalyticsFunnelTab.vue'
import AnalyticsBehaviorTab from '../components/analytics/AnalyticsBehaviorTab.vue'
import AnalyticsProductsTab from '../components/analytics/AnalyticsProductsTab.vue'
import AnalyticsTimeComparisonTab from '../components/analytics/AnalyticsTimeComparisonTab.vue'
import AnalyticsTrackingSettingsTab from '../components/analytics/AnalyticsTrackingSettingsTab.vue'
import AnalyticsTechnicalTab from '../components/analytics/AnalyticsTechnicalTab.vue'
import AnalyticsLiquidLineChart from '../components/analytics/AnalyticsLiquidLineChart.vue'

// ── Inline CollapseFilters component ──────────────────────────────────────
const CollapseFilters = {
  name: 'CollapseFilters',
  props: {
    label: String,
    openByDefault: { type: Boolean, default: false },
  },
  emits: [],
  setup(props) {
    const open = ref(props.openByDefault)
    return { open }
  },
  template: `
    <div class="collapse-filters glass-card">
      <button class="collapse-trigger" @click="open = !open">
        <span>{{ label }}</span>
        <component :is="open ? ChevronUp : ChevronDown" :size="14" class="collapse-caret" />
      </button>
      <div class="collapse-body" v-show="open">
        <slot />
      </div>
    </div>
  `,
}

// ── Page / Section ─────────────────────────────────────────────────────────
const page = window._PAGE || 'management-analytics'
const pageToSection = {
  'management-analytics': 'overview',
  'management-analytics-overview': 'overview',
  'management-analytics-traffic': 'traffic',
  'management-analytics-funnel': 'funnel',
  'management-analytics-behavior': 'behavior',
  'management-analytics-products': 'products',
  'management-analytics-time': 'time',
  'management-analytics-technical': 'technical',
  'management-analytics-settings': 'settings',
}
const sectionId = pageToSection[page] || 'overview'

const tabs = [
  { id: 'overview',  label: 'نمای کلی',        shortLabel: 'کلی',     icon: 'BarChart3', href: '/management-analytics-overview'  },
  { id: 'traffic',   label: 'ترافیک',           shortLabel: 'ترافیک', icon: 'TrendingUp', href: '/management-analytics-traffic'   },
  { id: 'funnel',    label: 'فانل تبدیل',       shortLabel: 'فانل',   icon: 'Filter', href: '/management-analytics-funnel'    },
  { id: 'behavior',  label: 'رفتار کاربر',      shortLabel: 'رفتار',  icon: 'User', href: '/management-analytics-behavior'  },
  { id: 'products',  label: 'گزارش محصولات',    shortLabel: 'محصول',  icon: 'Package', href: '/management-analytics-products'  },
  { id: 'time',      label: 'مقایسه زمانی',     shortLabel: 'زمان',   icon: 'Clock', href: '/management-analytics-time'      },
  { id: 'technical', label: 'SEO و فنی',         shortLabel: 'SEO',    icon: 'Search', href: '/management-analytics-technical' },
  { id: 'settings',  label: 'تنظیمات رهگیری',  shortLabel: 'تنظیم',  icon: 'Settings', href: '/management-analytics-settings'  },
]

const presets = [
  { value: 'today',  label: 'امروز'  },
  { value: 'yesterday', label: 'دیروز' },
  { value: '7d',    label: '۷ روز'  },
  { value: '30d',   label: '۳۰ روز' },
  { value: '90d',   label: '۳ ماه'  },
  { value: '180d',  label: '۶ ماه'  },
  { value: '365d',  label: '۱ سال'  },
]

// ── State ──────────────────────────────────────────────────────────────────
const showDatePicker = ref(false)
const isLoading = ref(false)
const DEFAULT_SEGMENT_KEY = '__all__'

const today = new Date().toISOString().slice(0, 10)
const sevenDaysAgo = new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)

const range = reactive({ preset: '30d', fromDate: sevenDaysAgo, toDate: today })
const overview  = reactive({ loading: false, error: '', data: null })
const funnel    = reactive({ loading: false, error: '', data: null, diagnosis: null, diagnosisLoading: false, filters: { category: '', device_type: '', source_channel: '' } })
const behavior  = reactive({ loading: false, error: '', data: null })
const traffic   = reactive({ loading: false, error: '', data: null, filters: { group_key: '__all__', page_path: '', limit: 20 } })
const products  = reactive({ loading: false, error: '', data: null, filters: { category: '', sort_by: 'views', sort_order: 'desc' } })
const time      = reactive({ loading: false, error: '', data: null, filters: { left_from: '', left_to: '', right_from: '', right_to: '', preset: 'week_vs_previous' } })
const technical = reactive({ loading: false, error: '', data: null, settings: null, settingsLoading: false, settingsSaving: false })
const settings  = reactive({ loading: false, error: '', data: { toggles: [], goals: [], funnels: [], segments: [], alerts: [], ip_exclusions: [] }, saving: false })
const advanced  = reactive({ loading: false, error: '', data: null, segmentKey: DEFAULT_SEGMENT_KEY })

// ── Helpers ────────────────────────────────────────────────────────────────
const toFa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const toFa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })
const toMoney = (v) => `${toFa(Math.round(Number(v || 0)))} تومان`
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
  organic: 'ارگانیک',
  social: 'شبکه اجتماعی',
  other: 'سایر',
}
const sourceLabel = (value) => sourceMap[value] || value || '-'

const activeTabLabel = computed(() => tabs.find((t) => t.id === sectionId)?.label || '-')
const segmentOptions = computed(() => {
  const rows = advanced.data?.segments || settings.data?.segments || []
  const activeRows = rows.filter((row) => Number(row?.is_active ?? 1))
  if (activeRows.length) return activeRows
  return [{ key: DEFAULT_SEGMENT_KEY, title: 'مشاهده همه' }]
})

const jalaliRangeLabel = computed(() => {
  try {
    const fmt = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { year: 'numeric', month: '2-digit', day: '2-digit' })
    const from = range.fromDate ? fmt.format(new Date(range.fromDate)) : '-'
    const to   = range.toDate   ? fmt.format(new Date(range.toDate))   : '-'
    return `${from} تا ${to}`
  } catch {
    return `${range.fromDate || '-'} تا ${range.toDate || '-'}`
  }
})

const quickKpis = computed(() => {
  const kpis = overview.data?.kpis
  if (!kpis) return []
  return [
    { label: 'بازدید کل',  value: toFa(kpis.total_views),                    note: 'محصولات مشاهده‌شده',              icon: 'Eye',  color: '#6ee7b7' },
    { label: 'نرخ تبدیل', value: `${toFa2(kpis.conversion_rate)}%`,           note: 'بازدید → سفارش',                  icon: 'Zap',  color: '#93c5fd' },
    { label: 'درآمد',      value: toMoney(kpis.total_revenue),                note: 'جمع فروش سفارش‌ها',              icon: 'Banknote',  color: '#fcd34d' },
    { label: 'سفارش',      value: toFa(kpis.total_orders),                    note: `AOV: ${toMoney(kpis.average_order_value)}`, icon: 'ShoppingCart', color: '#c4b5fd' },
    { label: 'ریزش سبد',  value: `${toFa2(kpis.cart_abandonment_rate)}%`,    note: 'ریزش از افزودن',                  icon: 'TrendingDown',  color: '#fca5a5' },
  ]
})

const shortDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' })
}

const overviewTrendPoints = computed(() => {
  const rows = overview.data?.charts?.daily_views || []
  return rows.map((row) => ({
    label: shortDate(row.date),
    a: Number(row.value || 0),
  }))
})

const overviewTrafficSources = computed(() => {
  const grouped = traffic.data?.charts?.channel_group_breakdown || []
  const rawRows = grouped.length
    ? grouped.map((row) => ({ source_channel: row.channel_group || 'other', views: Number(row.views || 0) }))
    : (traffic.data?.charts?.source_breakdown || []).map((row) => ({ source_channel: row.source_channel || 'other', views: Number(row.views || 0) }))
  const total = Math.max(1, rawRows.reduce((sum, row) => sum + Number(row.views || 0), 0))
  return rawRows
    .sort((a, b) => Number(b.views || 0) - Number(a.views || 0))
    .slice(0, 6)
    .map((item) => ({
      ...item,
      percent: Math.max(5, Math.min(100, (Number(item.views || 0) / total) * 100)),
    }))
})

const overviewSourceTotal = computed(() =>
  overviewTrafficSources.value.reduce((total, row) => total + Number(row.views || 0), 0),
)

// ── Date Picker ────────────────────────────────────────────────────────────
function selectPreset(value) {
  range.preset = value
  applyPreset()
}

function applyPreset() {
  const now = new Date()
  const day = 24 * 60 * 60 * 1000
  const iso = (d) => d.toISOString().slice(0, 10)
  if (range.preset === 'today')     { range.fromDate = iso(now);                        range.toDate = iso(now) }
  else if (range.preset === 'yesterday') { const d = new Date(Date.now() - day); range.fromDate = iso(d); range.toDate = iso(d) }
  else if (range.preset === '7d')   { range.fromDate = iso(new Date(Date.now() - 6*day));   range.toDate = iso(now) }
  else if (range.preset === '30d')  { range.fromDate = iso(new Date(Date.now() - 29*day));  range.toDate = iso(now) }
  else if (range.preset === '90d')  { range.fromDate = iso(new Date(Date.now() - 89*day));  range.toDate = iso(now) }
  else if (range.preset === '180d') { range.fromDate = iso(new Date(Date.now() - 179*day)); range.toDate = iso(now) }
  else if (range.preset === '365d') { range.fromDate = iso(new Date(Date.now() - 364*day)); range.toDate = iso(now) }
}

async function applyAndClose() {
  showDatePicker.value = false
  await refreshDashboard()
}

// ── API Helpers ────────────────────────────────────────────────────────────
function makeQuery(extra = {}) {
  const params = new URLSearchParams()
  if (range.preset && range.preset !== 'custom') params.set('range_key', range.preset)
  if (range.fromDate) params.set('from_date', range.fromDate)
  if (range.toDate)   params.set('to_date',   range.toDate)
  Object.entries(extra).forEach(([k, v]) => { if (v !== undefined && v !== null && `${v}` !== '') params.set(k, v) })
  return params.toString()
}

async function getJson(url) {
  const res = await fetch(url, { credentials: 'same-origin' })
  const data = await res.json()
  if (!res.ok || data.exception || data.exc_type) throw new Error(data._server_messages || data.message || 'request_failed')
  return data.message || data
}

async function postJson(url, body = {}) {
  const res = await fetch(url, {
    method: 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.csrf_token || '' },
    body: JSON.stringify(body),
  })
  const data = await res.json()
  if (!res.ok || data.exception || data.exc_type) throw new Error(data._server_messages || data.message || 'request_failed')
  return data.message || data
}

// ── Loaders ────────────────────────────────────────────────────────────────
async function loadOverview() {
  overview.loading = true; overview.error = ''
  try { overview.data = await getJson(`/api/method/mysite.analytics_api.get_overview?${makeQuery()}`) }
  catch { overview.error = 'خطا در دریافت نمای کلی.' }
  finally { overview.loading = false }
}

async function loadFunnel() {
  funnel.loading = true; funnel.error = ''
  try { funnel.data = await getJson(`/api/method/mysite.analytics_api.get_conversion_funnel?${makeQuery(funnel.filters)}`); funnel.diagnosis = null }
  catch { funnel.error = 'خطا در دریافت فانل تبدیل.' }
  finally { funnel.loading = false }
}

async function loadDiagnosis(step) {
  funnel.diagnosisLoading = true
  try { funnel.diagnosis = await getJson(`/api/method/mysite.analytics_api.get_funnel_drop_diagnosis?${makeQuery({ step })}`) }
  catch { funnel.diagnosis = { reasons: [{ message: 'تحلیل مرحله با خطا مواجه شد.' }] } }
  finally { funnel.diagnosisLoading = false }
}

async function loadBehavior() {
  behavior.loading = true; behavior.error = ''
  try { behavior.data = await getJson(`/api/method/mysite.analytics_api.get_user_behavior?${makeQuery({ limit: 12 })}`) }
  catch { behavior.error = 'خطا در دریافت رفتار کاربر.' }
  finally { behavior.loading = false }
}

async function loadTraffic() {
  traffic.loading = true; traffic.error = ''
  try {
    traffic.data = await getJson(`/api/method/mysite.analytics_api.get_site_traffic?${makeQuery(traffic.filters)}`)
    if (!traffic.filters.group_key && traffic.data?.selected_group?.group_key) traffic.filters.group_key = traffic.data.selected_group.group_key
    if (!traffic.filters.page_path && traffic.data?.selected_page?.path)       traffic.filters.page_path = traffic.data.selected_page.path
  } catch { traffic.error = 'خطا در دریافت ترافیک سایت.' }
  finally { traffic.loading = false }
}

async function pickTrafficPage(path)     { traffic.filters.page_path = path || ''; await loadTraffic() }
async function pickTrafficGroup(groupKey){ traffic.filters.group_key = groupKey || ''; traffic.filters.page_path = ''; await loadTraffic() }

async function loadAdvanced() {
  advanced.loading = true
  advanced.error = ''
  try {
    advanced.data = await getJson(
      `/api/method/mysite.analytics_api.get_advanced_insights?${makeQuery({ segment_key: advanced.segmentKey || DEFAULT_SEGMENT_KEY })}`,
    )
    if (advanced.data?.segment?.key) {
      advanced.segmentKey = advanced.data.segment.key
    }
  } catch {
    advanced.error = 'خطا در دریافت گزارش پیشرفته.'
  } finally {
    advanced.loading = false
  }
}

async function applySegment() {
  await loadAdvanced()
}

async function loadProducts(p = 1) {
  products.loading = true; products.error = ''
  try { products.data = await getJson(`/api/method/mysite.analytics_api.get_products_report?${makeQuery({ ...products.filters, page: p, page_size: 20 })}`) }
  catch { products.error = 'خطا در دریافت گزارش محصولات.' }
  finally { products.loading = false }
}

function exportProducts(fileType) {
  window.open(`/api/method/mysite.analytics_api.export_products_report?${makeQuery({ ...products.filters, file_type: fileType })}`, '_blank', 'noopener,noreferrer')
}

async function loadTimeComparison() {
  time.loading = true; time.error = ''
  try {
    const p = { left_from: time.filters.left_from, left_to: time.filters.left_to, right_from: time.filters.right_from, right_to: time.filters.right_to, preset: time.filters.preset }
    time.data = await getJson(`/api/method/mysite.analytics_api.get_time_comparison?${new URLSearchParams(p).toString()}`)
  } catch { time.error = 'خطا در دریافت مقایسه زمانی.' }
  finally { time.loading = false }
}

async function loadSettings() {
  settings.loading = true; settings.error = ''
  try {
    settings.data = await getJson('/api/method/mysite.analytics_api.get_tracking_settings')
  }
  catch { settings.error = 'خطا در دریافت تنظیمات.' }
  finally { settings.loading = false }
}

async function loadTechnical() {
  technical.loading = true
  technical.error = ''
  try {
    technical.data = await getJson(`/api/method/mysite.analytics_api.get_technical_dashboard?${makeQuery()}`)
    technical.settings = technical.data?.integration_settings || technical.settings || null
  } catch {
    technical.error = 'خطا در دریافت پنل SEO و فنی.'
  } finally {
    technical.loading = false
  }
}

async function loadTechnicalSettings() {
  technical.settingsLoading = true
  try {
    technical.settings = await getJson('/api/method/mysite.analytics_api.get_external_analytics_settings')
  } catch {
    technical.error = technical.error || 'خطا در دریافت تنظیمات اتصال GA4/GSC.'
  } finally {
    technical.settingsLoading = false
  }
}

async function saveTechnicalSettings(payload) {
  technical.settingsSaving = true
  technical.error = ''
  try {
    const response = await postJson('/api/method/mysite.analytics_api.update_external_analytics_settings', payload)
    technical.settings = response?.settings || payload
    await loadTechnical()
  } catch {
    technical.error = 'ذخیره تنظیمات اتصال با خطا مواجه شد.'
  } finally {
    technical.settingsSaving = false
  }
}

async function saveSettings(payload) {
  settings.saving = true; settings.error = ''
  try { await postJson('/api/method/mysite.analytics_api.update_tracking_settings', payload); await loadSettings() }
  catch { settings.error = 'ذخیره با خطا مواجه شد.' }
  finally { settings.saving = false }
}

async function reloadCurrentSection() {
  if (sectionId === 'overview')  return loadOverview()
  if (sectionId === 'traffic')   return loadTraffic()
  if (sectionId === 'funnel')    return loadFunnel()
  if (sectionId === 'behavior')  return loadBehavior()
  if (sectionId === 'products')  return loadProducts(products.data?.page || 1)
  if (sectionId === 'time')      return loadTimeComparison()
  if (sectionId === 'technical') return Promise.all([loadTechnical(), loadTechnicalSettings()])
  if (sectionId === 'settings')  return loadSettings()
}

async function refreshDashboard() {
  isLoading.value = true
  await Promise.all([loadOverview(), loadAdvanced()])
  if (sectionId === 'overview') await loadTraffic()
  else await reloadCurrentSection()
  isLoading.value = false
}

onMounted(async () => {
  applyPreset()
  await Promise.all([loadOverview(), loadAdvanced()])
  if (sectionId === 'overview') await loadTraffic()
  else await reloadCurrentSection()
})
</script>

<style scoped>
/* ══════════════════════════════════════════════
   BASE & TOKENS
══════════════════════════════════════════════ */
.analytics-page {
  min-height: 100vh;
  background: var(--admin-bg);
  color: var(--text-main);
  position: relative;
  overflow-x: hidden;
  /* Extra padding for mobile bottom bar */
  padding-bottom: 0;
}

/* ── Ambient background (lighter, 2 blobs) ── */
.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.45; /* reduced from full */
}
.b1 {
  width: 500px; height: 500px;
  background: var(--admin-orb-warm);
  top: -160px; right: -160px;
}
.b2 {
  width: 600px; height: 600px;
  background: var(--admin-orb-cool);
  bottom: -220px; left: -200px;
}

/* ── Glass card base ── */
.glass-card {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

/* ══════════════════════════════════════════════
   LAYOUT
══════════════════════════════════════════════ */
.layout {
  display: grid;
  position: relative;
  z-index: 2;
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-5) var(--space-4) 80px;
  grid-template-columns: 1fr 250px;
  gap: var(--space-4);
  overflow-x: hidden;
  box-sizing: border-box;
}
.main-col {
  display: grid;
  gap: var(--space-3);
  align-content: start;
  grid-column: 1;
}

/* ══════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════ */
.sidebar {
  padding: var(--space-4);
  display: grid;
  align-content: start;
  gap: var(--space-3);
  position: sticky;
  top: 88px;
  max-height: calc(100vh - 104px);
  overflow: auto;
  grid-column: 2;
  background: linear-gradient(175deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.12));
  align-self: start;
}
.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.brand-icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1rem;
  flex-shrink: 0;
}
.brand-text strong { display: block; font-size: 0.9rem; }
.brand-text small  { color: var(--admin-text-soft); font-size: var(--text-xs); }

.sidebar-nav { display: grid; gap: var(--space-1); }
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 9px 10px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-main);
  font-size: var(--text-base);
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
  border: 1px solid color-mix(in srgb, var(--admin-border) 82%, transparent);
}
.nav-item:hover { background: var(--admin-chip-bg); }
.nav-item.active {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}
.nav-icon {
  font-size: 15px;
  width: 24px;
  height: 24px;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.24);
}

.sidebar-meta { display: grid; gap: var(--space-2); margin-top: 4px; }
.meta-chip {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-1);
}
.meta-label { font-size: var(--text-xs); color: var(--admin-text-soft); }
.meta-chip strong { font-size: 0.9rem; }
.meta-chip small  { color: var(--text-muted); font-size: var(--text-xs); }

.back-btn {
  display: block;
  text-align: center;
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2);
  text-decoration: none;
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
  transition: background var(--duration-fast) var(--ease-out);
}
.back-btn:hover { background: var(--admin-chip-bg); }

.overview-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(0, 0.8fr);
  gap: var(--space-3);
}

.overview-hero-main,
.overview-hero-side {
  padding: var(--space-4);
  border-radius: var(--radius-xl);
}

.hero-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: center;
  margin-bottom: 10px;
}

.hero-eyebrow {
  margin: 0 0 3px;
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
}

.hero-head h2 {
  margin: 0;
  font-size: 1.1rem;
}

.hero-total {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  padding: var(--space-2) var(--space-3);
  background: var(--admin-input-bg);
  text-align: center;
  min-width: 104px;
}

.hero-total span {
  display: block;
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.hero-total strong {
  font-size: 1rem;
}

.hero-side-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: 8px;
}

.hero-side-head h3 {
  margin: 0;
  font-size: 1rem;
}

.hero-side-head span {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.hero-source-list {
  display: grid;
  gap: var(--space-2);
}

.hero-source-row {
  display: grid;
  gap: 5px;
}

.hero-source-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-sm);
}

.hero-source-track {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-pill);
  height: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.3);
}

.hero-source-track i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #2f6fba, #8b5cf6);
}

.hero-side-hint {
  margin: 10px 0 0;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

/* ══════════════════════════════════════════════
   COMPACT HEADER
══════════════════════════════════════════════ */
.page-header {
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}
.header-left .eyebrow {
  font-size: var(--text-xs);
  letter-spacing: 0.14em;
  color: var(--accent-gold, #f59e0b);
  font-weight: 700;
  text-transform: uppercase;
  display: block;
  margin-bottom: 2px;
}
.header-left h1 {
  margin: 0;
  font-size: 1.3rem;
  line-height: 1.2;
}
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.segment-filter {
  display: grid;
  gap: var(--space-1);
}

.segment-filter span {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.segment-filter select {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: var(--text-sm);
  min-width: 168px;
}

/* ── Date Popover ── */
.date-popover-wrap { position: relative; }

.date-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  cursor: pointer;
  font-family: inherit;
  font-size: var(--text-base);
  white-space: nowrap;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.date-trigger:hover { border-color: var(--accent-gold, #f59e0b); }
.date-trigger-icon { font-size: 14px; }
.caret { font-size: var(--text-xs); color: var(--admin-text-soft); }

.date-popover {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  z-index: var(--z-overlay);
  min-width: 320px;
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
  box-shadow: 0 16px 48px rgba(0,0,0,0.2);
  animation: popoverIn 0.15s ease;
}
@keyframes popoverIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.popover-presets {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.preset-btn {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.preset-btn:hover { border-color: var(--accent-gold, #f59e0b); }
.preset-btn.active {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  border-color: transparent;
}
.popover-custom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}
.popover-custom label {
  display: grid;
  gap: var(--space-1);
}
.popover-custom span {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}
.popover-custom input {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-sm);
  padding: 7px 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: var(--text-sm);
}
.apply-btn {
  width: 100%;
  padding: 9px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  font-family: inherit;
  font-size: var(--text-base);
  cursor: pointer;
  font-weight: 600;
}

.refresh-btn {
  width: 36px; height: 36px;
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  color: var(--text-main);
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.refresh-btn:disabled { opacity: 0.5; }
.refresh-btn:hover    { border-color: var(--accent-gold, #f59e0b); }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.7s linear infinite; }

/* Backdrop */
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 99;
}

/* ══════════════════════════════════════════════
   KPI STRIP - improved
══════════════════════════════════════════════ */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--space-3);
}
.kpi-card {
  padding: var(--space-4);
  position: relative;
  overflow: hidden;
  transition: transform var(--duration-fast) var(--ease-out);
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
.kpi-top {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: 8px;
}
.kpi-icon { color: var(--accent); flex-shrink: 0; }
.kpi-label { font-size: var(--text-sm); color: var(--admin-text-soft); }
.kpi-value { font-size: 1.25rem; font-weight: 700; line-height: 1.2; margin-bottom: 4px; }
.kpi-note  { font-size: var(--text-xs); color: var(--text-muted, #999); }

/* ══════════════════════════════════════════════
   COLLAPSE FILTERS
══════════════════════════════════════════════ */
.collapse-filters { overflow: hidden; }
.collapse-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  color: var(--text-main);
  font-family: inherit;
  font-size: var(--text-base);
  cursor: pointer;
  font-weight: 600;
}
.collapse-caret { font-size: var(--text-xs); color: var(--admin-text-soft); }
.collapse-body {
  padding: 0 12px 12px;
  border-top: 1px solid var(--admin-border);
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-2);
  padding-top: 10px;
  align-items: end;
}
.filters-grid.six-col { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.filters-grid label { display: grid; gap: var(--space-1); }
.filters-grid span  { font-size: var(--text-sm); color: var(--admin-text-soft); }
.filters-grid input,
.filters-grid select {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2);
  font-family: inherit;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-size: var(--text-base);
}
.filter-actions { display: flex; gap: var(--space-2); align-items: end; }
.apply-filter-btn {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  font-family: inherit;
  cursor: pointer;
  color: var(--text-main);
  background: var(--admin-input-bg);
  font-size: var(--text-base);
  white-space: nowrap;
  transition: all var(--duration-fast) var(--ease-out);
}
.apply-filter-btn:hover {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  border-color: transparent;
}
.export-btn {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
  cursor: pointer;
  color: var(--admin-text-soft);
  background: var(--admin-input-bg);
  font-size: var(--text-sm);
  white-space: nowrap;
}

/* ── Tab sections ── */
.tab-section { display: grid; gap: var(--space-3); }

/* ── Pager ── */
.pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
}
.pager-btn {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
  cursor: pointer;
  color: var(--text-main);
  background: var(--admin-input-bg);
  font-size: var(--text-base);
}
.pager-btn:disabled { opacity: 0.4; cursor: default; }
.pager-info { font-size: var(--text-base); color: var(--admin-text-soft); }

/* ══════════════════════════════════════════════
   MOBILE BOTTOM BAR (hidden on desktop)
══════════════════════════════════════════════ */
.bottom-bar {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: var(--z-modal);
  background: var(--admin-panel-bg);
  border-top: 1px solid var(--admin-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 6px 0 env(safe-area-inset-bottom, 0);
  overflow-x: auto;
}
.bottom-tab {
  flex: 1;
  min-width: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: 6px 4px;
  text-decoration: none;
  color: var(--admin-text-soft);
  font-size: var(--text-xs);
  transition: color var(--duration-fast) var(--ease-out);
}
.bottom-tab.active { color: var(--admin-tab-active-start, #6366f1); }
.bottom-tab-icon   { font-size: 18px; }
.bottom-tab-label  { font-size: var(--text-xs); }

/* ══════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════ */
@media (max-width: 1200px) {
  .layout {
    grid-template-columns: 1fr;
    padding-bottom: 100px; /* room for bottom bar */
  }
  .sidebar { display: none; } /* replaced by bottom bar */
  .bottom-bar { display: flex; }
  .overview-hero-grid { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .filters-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .filters-grid.six-col { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .header-right {
    width: 100%;
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    align-items: stretch;
  }
  .segment-filter select { min-width: 0; width: 100%; }
  .date-popover-wrap { min-width: 0; }
  .date-trigger { flex: 1; justify-content: space-between; }
  .date-popover { left: 0; right: 0; min-width: 0; }
  .refresh-btn { justify-content: center; min-height: 40px; }
  .pager { flex-wrap: wrap; gap: var(--space-2); }
  .pager-btn { flex: 1; min-width: 120px; text-align: center; }
  .hero-head { flex-direction: column; align-items: flex-start; }
  .hero-total { width: 100%; text-align: right; }
  .kpi-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 480px) {
  .layout { padding: 12px 10px 100px; }
  .page-header { padding: var(--space-3); }
  .header-right { grid-template-columns: minmax(0, 1fr) auto; }
  .kpi-strip { grid-template-columns: 1fr; }
  .filters-grid { grid-template-columns: 1fr; }
  .filter-actions { display: grid; grid-template-columns: 1fr; }
  .apply-filter-btn, .export-btn { width: 100%; justify-content: center; }
  .bottom-tab { min-width: 68px; }
  .bottom-tab-icon { font-size: 17px; }
  .bottom-tab-label { font-size: 9px; }
  .header-left h1 { font-size: 1.1rem; }
  .overview-hero-main { padding: var(--space-3); }
  .hero-source-list { gap: var(--space-2); }
  .hero-source-track { height: 8px; }
}

@media (max-width: 380px) {
  .header-right { grid-template-columns: 1fr; }
  .segment-filter select { width: 100%; }
  .date-popover { min-width: 0; left: 0; right: 0; }
}
</style>
