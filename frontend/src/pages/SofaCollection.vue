<template>
  <div class="sofas-page" dir="rtl">
    <ProductHero
      title="مجموعه مبلمان"
      description="تجربه‌ای متفاوت از راحتی و زیبایی با مبلمان مدرن DenRoom"
      :stats="heroStats"
    />

    <main class="sofas-main">
      <div class="sofas-toolbar">
        <FloatingFilter
          :available-models="filterOptions.models"
          :available-colors="filterOptions.colors"
          :min-bound="filterOptions.minBound"
          :max-bound="filterOptions.maxBound"
          :step="filterOptions.step"
          trigger-label="فیلتر"
          @apply="onFilterApply"
          @reset="clearFilters"
        />
        <button class="fabric-tab-btn" type="button" @click="fabricOpen = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5z"/>
            <path d="M4 9h16M9 4v16"/>
          </svg>
          <span>{{ selectedFabric ? 'پارچه: ' + selectedFabric.qualityName + (selectedFabric.colorName ? ' - ' + selectedFabric.colorName : '') : 'پارچه' }}</span>
          <span v-if="selectedFabric" class="fabric-color-dot"></span>
        </button>
      </div>

      <section
        v-for="model in filteredProducts"
        :key="model.sofa_model_name"
        class="model-section"
      >
        <div class="model-shell">
          <div class="model-header">
            <div class="model-heading">
              <h2 class="model-name">{{ model.sofa_model_name }}</h2>
              <p class="model-meta">
                <span>{{ getModules(model).length }} ماژول</span>
                <span class="dot-divider">•</span>
                <span>{{ getBundles(model).length }} بسته آماده</span>
              </p>
            </div>

            <div class="header-actions">
              <a
                class="more-info-link"
                :href="buildSofaRoute(`sofas/${encodeURIComponent(model.sofa_model_name)}`)"
              >
                مشاهده مدل
              </a>
              <div class="view-tabs">
                <button
                  class="tab-btn"
                  type="button"
                  :class="{ active: activeViews[model.sofa_model_name] !== 'bundles' }"
                  @click="setView(model.sofa_model_name, 'modules')"
                >
                  ماژول‌ها
                </button>
                <button
                  class="tab-btn"
                  type="button"
                  :disabled="!getBundles(model).length"
                  :class="{ active: activeViews[model.sofa_model_name] === 'bundles' }"
                  @click="setView(model.sofa_model_name, 'bundles')"
                >
                  بسته‌ها
                </button>
              </div>
            </div>
          </div>

          <div class="model-row">
            <div class="col-hero">
              <img
                v-if="getModelCoverImage(model)"
                class="hero-img"
                :src="getModelCoverImage(model)"
                :alt="model.sofa_model_name"
              />
              <div v-else class="hero-img card-img-placeholder"></div>
            </div>

            <div class="col-center">
              <div
                v-if="activeViews[model.sofa_model_name] !== 'bundles'"
                class="col-cards card-grid"
              >
                <article
                  v-for="mod in getModules(model)"
                  :key="mod.sofa_module_name"
                  class="product-card"
                  @click="navigateToProduct(mod)"
                >
                  <button class="info-btn" type="button" @click.stop="openModal(mod)">i</button>
                  <div class="card-img-wrap">
                    <img v-if="getCoverImage(mod)" class="card-img" :src="getCoverImage(mod)" :alt="mod.sofa_module_name" />
                    <div v-else class="card-img-placeholder"></div>
                  </div>
                  <div class="card-info">
                    <p class="card-title">{{ mod.sofa_module_name }}</p>
                    <p class="card-feature">{{ getFeature(mod) || 'مدل پایه' }}</p>
                    <div class="card-specs">
                      <span v-if="hasMeaningfulValue(mod.sofa_length)" class="spec-label">طول {{ mod.sofa_length }}</span>
                      <span v-if="hasMeaningfulValue(mod.sofa_width)" class="spec-label">عرض {{ mod.sofa_width }}</span>
                      <span v-if="hasMeaningfulValue(mod.sofa_shape)" class="spec-label">{{ mod.sofa_shape }}</span>
                    </div>
                    <p class="card-price">{{ getModulePrice(mod) }}</p>
                    <p v-if="selectedFabric && mod.sofa_odd_cloth" class="card-fabric-price">
                      + {{ calcFabricAdded(mod.sofa_odd_cloth) }}
                    </p>
                    <p v-if="selectedFabric && mod.sofa_odd_cloth" class="card-total-price">
                      {{ calcTotal(getModulePriceRaw(mod), mod.sofa_odd_cloth) }}
                    </p>
                  </div>
                </article>
              </div>

              <div v-else class="col-cards card-grid">
                <article
                  v-for="bundle in getBundles(model)"
                  :key="bundle.bundle_name || bundle.name"
                  class="product-card"
                  @click="navigateToBundle(bundle)"
                >
                  <button class="info-btn" type="button" @click.stop="openBundleModal(bundle)">i</button>
                  <div class="card-img-wrap">
                    <img
                      v-if="bundle.bundle_cover_photo"
                      class="card-img"
                      :src="normalizeImageUrl(bundle.bundle_cover_photo)"
                      :alt="bundle.sofa_bundle_display_name || bundle.name"
                    />
                    <div v-else class="card-img-placeholder"></div>
                  </div>
                  <div class="card-info">
                    <p class="card-title">{{ bundle.sofa_bundle_display_name || bundle.name }}</p>
                    <div class="card-specs">
                      <span class="spec-label">{{ bundleUnitCount(bundle) }} آیتم</span>
                      <span v-if="hasMeaningfulValue(bundle.total_fabric)" class="spec-label">
                        {{ bundle.total_fabric }} متر پارچه
                      </span>
                    </div>
                    <p class="card-price">{{ bundle.bundle_formatted_price }}</p>
                  </div>
                </article>
                <p v-if="!getBundles(model).length" class="empty-bundles">بسته آماده‌ای برای این مدل ثبت نشده است.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div v-if="!filteredProducts.length" class="sofa-empty-state">
        <p>محصولی با فیلترهای انتخابی پیدا نشد.</p>
        <button type="button" @click="clearFilters">پاک کردن فیلترها</button>
      </div>
    </main>

    <div class="fabric-overlay-bg" :class="{ active: fabricOpen }" @click="fabricOpen = false"></div>
    <FabricSidebar
      :open="fabricOpen"
      :cloth-groups="clothGroups"
      :selected-fabric="selectedFabric"
      @close="fabricOpen = false"
      @select="onFabricSelect"
    />

    <div v-if="activeModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <button class="modal-close" type="button" @click="closeModal">×</button>
        <div class="modal-header">
          <h3>{{ activeModal.sofa_module_name }}</h3>
          <span class="badge">ماژول</span>
        </div>
        <div class="fabric-row">
          <div class="fabric-chip">
            <span class="chip-label">تعداد آیتم</span>
            <span class="chip-val">{{ activeModal.sofa_module_items?.length || 0 }}</span>
          </div>
          <div class="fabric-chip" v-if="activeModal.sofa_odd_cloth">
            <span class="chip-label">مصرف پارچه</span>
            <span class="chip-val">{{ activeModal.sofa_odd_cloth }} متر</span>
          </div>
        </div>
        <ul class="item-list">
          <li v-for="item in activeModal.sofa_module_items || []" :key="item.item_code || item.item_name">
            <span>{{ item.module_feature || item.item_name || 'مدل پایه' }}</span>
            <span class="item-price">{{ item.formatted_Price || fmtToman(item.Price) }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div v-if="activeBundleModal" class="modal-overlay" @click.self="activeBundleModal = null">
      <div class="modal-box">
        <button class="modal-close" type="button" @click="activeBundleModal = null">×</button>
        <div class="modal-header">
          <h3>{{ activeBundleModal.sofa_bundle_display_name || activeBundleModal.name }}</h3>
          <span class="badge">بسته</span>
        </div>
        <div class="fabric-row">
          <div class="fabric-chip">
            <span class="chip-label">تعداد کل</span>
            <span class="chip-val">{{ bundleUnitCount(activeBundleModal) }} آیتم</span>
          </div>
          <div class="fabric-chip" v-if="hasMeaningfulValue(activeBundleModal.total_fabric)">
            <span class="chip-label">مصرف پارچه</span>
            <span class="chip-val">{{ activeBundleModal.total_fabric }} متر</span>
          </div>
        </div>
        <ul class="item-list">
          <li
            v-for="(row, rowIdx) in activeBundleModal.sofa_bundle_table_items || []"
            :key="`${row.module_name || row.name}-${row.idx || row.qty}-${rowIdx}`"
          >
            <span>{{ row.module_name || row.name }}</span>
            <span class="item-qty">×{{ row.qty || 1 }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import ProductHero from '../components/ProductHero.vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import FloatingFilter from '../components/FloatingFilter.vue'
import { useFabricStore } from '../stores/fabricStore'
import { buildFilterOptions, filterItems, sortItems } from '../utils/productFiltering'

const products = ref(window.NestedSofaProducts || [])
const clothGroups = ref(window.ClothGroups || [])
const activeViews = reactive({})
const activeModal = ref(null)
const activeBundleModal = ref(null)
const fabricOpen = ref(false)
const { selectedFabric, setSelectedFabric } = useFabricStore()
const selectedCustomer = ref(window.SelectedCustomer || '')
const activeFilters = ref({
  models: [],
  colors: [],
  priceMin: 0,
  priceMax: Number.MAX_SAFE_INTEGER,
  priceActive: false,
  sort: 'default',
})

function appendCustomerQuery(route) {
  if (!route || !selectedCustomer.value) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

function buildSofaRoute(route) {
  return appendCustomerQuery(`/${route}`)
}

products.value.forEach(m => { activeViews[m.sofa_model_name] = 'modules' })

const getModules = (model) => {
  return (model?.sofa_modules || []).filter((mod) => mod?.sofa_module_items?.length)
}

const bundleUnitCount = (bundle) => {
  return (bundle?.sofa_bundle_table_items || []).reduce((sum, row) => {
    const qty = Number(row?.qty || 1)
    return sum + (Number.isFinite(qty) ? qty : 1)
  }, 0)
}

const getBundles = (model) => {
  return (model?.sofa_bundles || []).filter((bundle) => bundleUnitCount(bundle) > 1)
}

function getModelCoverImage(model) {
  const groupPhoto = normalizeImageUrl(
    model?.sofa_main_photo || model?.main_photo || model?.cover_photo || ''
  )
  if (groupPhoto) return groupPhoto

  const modelImages = Array.isArray(model?.sofa_images) ? model.sofa_images : []
  if (modelImages.length) {
    const cover = modelImages.find((image) => image?.cover) || modelImages[0]
    const imageUrl = normalizeImageUrl(cover?.file_url || cover?.image || '')
    if (imageUrl) return imageUrl
  }

  const firstModule = getModules(model)[0]
  return firstModule ? getCoverImage(firstModule) : ''
}

function setView(name, value) {
  activeViews[name] = value
}

function getModelColors(model) {
  const seen = new Set()
  getModules(model).forEach((mod) => {
    ;(mod?.sofa_module_items || []).forEach((item) => {
      const bodyColor = String(item?.body_color || '').trim()
      if (bodyColor) seen.add(bodyColor)
      ;(item?.all_wood_colors || []).forEach((woodColor) => {
        const normalized = String(woodColor || '').trim()
        if (normalized) seen.add(normalized)
      })
    })
  })
  return [...seen]
}

function getModelPrices(model) {
  const prices = []
  getModules(model).forEach((mod) => {
    ;(mod?.sofa_module_items || []).forEach((item) => {
      const numeric = Number(item?.Price || item?.price_list_rate || 0)
      if (Number.isFinite(numeric) && numeric > 0) prices.push(numeric)
    })
  })
  return prices
}

const filterAdapter = {
  getName: (model) => model?.sofa_model_name || '',
  getColors: getModelColors,
  getPrices: getModelPrices,
}

const filterOptions = computed(() => {
  return buildFilterOptions(products.value, filterAdapter)
})

const filteredProducts = computed(() => {
  const filtered = filterItems(products.value, activeFilters.value, filterAdapter)
  return sortItems(filtered, activeFilters.value.sort, filterAdapter)
})

function onFilterApply(filters) {
  activeFilters.value = filters
}

function clearFilters() {
  activeFilters.value = {
    models: [],
    colors: [],
    priceMin: 0,
    priceMax: Number.MAX_SAFE_INTEGER,
    priceActive: false,
    sort: 'default',
  }
}

// ── Fabric selection ───────────────────────────────────────────────
function onFabricSelect(fabric) {
  setSelectedFabric(fabric)
  fabricOpen.value = false
}

// ── Price helpers ──────────────────────────────────────────────────
function toPersian(str) {
  return String(str).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d])
}

function fmtToman(toman) {
  if (!toman || toman <= 0) return ''
  return toPersian(Math.round(toman).toLocaleString())
}

function hasMeaningfulValue(value) {
  if (value === null || value === undefined) return false
  const txt = String(value).trim()
  if (!txt) return false
  const normalized = txt
    .replace(/[۰-۹]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/[^\d.]/g, '')
  if (!normalized) return true
  const num = Number(normalized)
  if (Number.isFinite(num) && num <= 0) return false
  return true
}

function normalizeImageUrl(url) {
  if (!url) return ''
  return String(url).replace('/private/files/', '/files/')
}

// Fabric cost added to base price (toman)
function calcFabricAdded(meters) {
  if (!selectedFabric.value || !meters) return ''
  const added = Math.ceil((meters * selectedFabric.value.pricePerMeter) / 10) * 10
  if (!added) return ''
  return fmtToman(added) + ' تومان'
}

// Total = base(toman) + fabric_added
function calcTotal(baseToman, meters) {
  if (!selectedFabric.value || !baseToman || !meters) return ''
  const added = Math.ceil((meters * selectedFabric.value.pricePerMeter) / 10) * 10
  return fmtToman(baseToman + added) + ' تومان'
}


const heroStats = computed(() => [
  { label: 'مدل مبلمان', value: products.value.length },
  { label: 'نوع پارچه', value: clothGroups.value.length }
])
function getCoverImage(mod) {
  // 1. from tabFile images with cover tag
  if (mod.sofa_module_images?.length) {
    const cover = mod.sofa_module_images.find(i => i.cover)
    const img = cover ?? mod.sofa_module_images[0]
    if (img?.file_url) return normalizeImageUrl(img.file_url)
  }
  // 2. from module items' image field (i.image from tabItem)
  const firstItem = mod.sofa_module_items?.[0]
  if (firstItem?.images?.length) {
    const ci = firstItem.images.find(i => i.cover) ?? firstItem.images[0]
    if (ci?.file_url) return normalizeImageUrl(ci.file_url)
  }
  if (firstItem?.image) return normalizeImageUrl(firstItem.image)
  return ''
}

function getModulePrice(mod) {
  if (!mod.sofa_module_items?.length) return ''
  return mod.sofa_module_items.reduce((a, b) => b.Price > a.Price ? b : a).formatted_Price || ''
}

// Return base price in Toman (integer)
function getModulePriceRaw(mod) {
  if (!mod.sofa_module_items?.length) return 0
  return mod.sofa_module_items.reduce((a, b) => b.Price > a.Price ? b : a).Price || 0
}

function getFeature(mod) {
  return mod.sofa_module_items?.[0]?.module_feature || ''
}

function openModal(mod) { activeModal.value = mod }
function closeModal() { activeModal.value = null }
function openBundleModal(b) { activeBundleModal.value = b }

function navigateToProduct(mod) {
  const firstItem = mod.sofa_module_items?.[0]
  const targetName = firstItem?.item_name || `${mod.sofa_model || ''} ${mod.sofa_module_name || ''}`.trim()
  if (!targetName) return
  window.location.href = appendCustomerQuery(`/product/${encodeURIComponent(targetName)}?kind=sofa`)
}

function navigateToBundle(bundle) {
  if (!bundle.bundle_name) return
  const modelName = bundle.name || bundle.sofa_bundle_name || ''
  window.location.href = appendCustomerQuery(`/sofas/${encodeURIComponent(modelName)}?bundle=${encodeURIComponent(bundle.bundle_name)}`)
}
</script>

<style scoped>
.sofas-page {
  font-family: 'Peyda', 'IranSans', sans-serif;
  background: var(--bg-main);
  min-height: 100vh;
  direction: rtl;
  overflow-x: clip;
}

.sofas-main {
  margin: 0 auto;
  padding: 20px;
  overflow-x: clip;
}

.sofas-toolbar {
  position: sticky;
  top: calc(var(--header-sticky-offset, 82px) + env(safe-area-inset-top, 0px));
  z-index: 280;
  display: flex;
  direction: ltr;
  align-items: stretch;
  width: min(100%, 980px);
  max-width: calc(100vw - 48px);
  box-sizing: border-box;
  margin: 0 auto 14px;
  border: 1px solid color-mix(in srgb, var(--glass-border) 88%, #d2d7df 12%);
  border-radius: 999px;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-main) 90%, #f6f8fb 10%);
  backdrop-filter: blur(12px);
  box-shadow: 0 16px 34px rgba(34, 45, 62, 0.12);
}
.sofas-toolbar :deep(.ff-root) { flex: 1 1 50%; min-width: 0; width: auto; }
.sofas-toolbar :deep(.ff-trigger) {
  width: 100%;
  min-height: 64px;
  border: 0;
  border-radius: 999px 0 0 999px;
  padding: 0 18px;
  justify-content: center;
  gap: 10px;
  background: transparent;
  color: #182744;
  box-shadow: none;
}
.sofas-toolbar :deep(.ff-trigger:hover),
.sofas-toolbar :deep(.ff-trigger.active) {
  transform: none;
  background: rgba(24, 39, 68, 0.05);
  border-color: transparent;
  box-shadow: none;
}
.sofas-toolbar :deep(.ff-trigger-icon) { width: 22px; height: 22px; }
.sofas-toolbar :deep(.ff-trigger-label) { font-size: 16px; font-weight: 900; }
.sofas-toolbar :deep(.ff-trigger-count) { display: none; }

.fabric-tab-btn {
  flex: 1 1 50%;
  min-width: 0;
  display: inline-flex;
  flex-direction: row-reverse;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 64px;
  padding: 0 18px;
  background: transparent;
  color: #182744;
  border: 0;
  border-left: 1px solid color-mix(in srgb, var(--glass-border) 85%, #bfc6d1 15%);
  border-radius: 0 999px 999px 0;
  font-family: inherit;
  font-size: 16px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: none;
  transition: background 0.2s ease;
  white-space: nowrap;
}

.fabric-tab-btn > span:not(.fabric-color-dot) {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  direction: rtl;
}

.fabric-tab-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.fabric-tab-btn:hover {
  transform: none;
  background: rgba(24, 39, 68, 0.05);
}

.fabric-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent-orange);
  box-shadow: 0 0 0 4px rgba(var(--accent-orange-rgb, 255, 152, 0), 0.18);
  flex-shrink: 0;
}

.sofa-empty-state {
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  background: var(--glass-bg);
  color: var(--text-main);
  text-align: center;
  padding: 32px 20px;
  margin-top: 12px;
}

.sofa-empty-state p {
  margin: 0 0 14px;
  color: var(--text-dim);
}

.sofa-empty-state button {
  border: 1px solid var(--glass-border);
  background: var(--accent-brown);
  color: var(--accent-gold);
  border-radius: 999px;
  padding: 8px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.model-section { margin-bottom: 3rem; }

/* ── Main row: flex RTL — hero first = rightmost ── */
.model-row {
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
  gap: 30px;
  align-items: flex-start;
  width: 100%;
}

/* ── RIGHT col: hero (50%) ── */
.col-hero {
  flex-shrink: 0;
  width: 50%;
  height: stretch;
  overflow: hidden;
  border-radius: 30px;
}

.hero-img {
  width: 100%;
  height: 100%;
  max-height: 490px;
  object-fit: cover;
  display: block;
  border-radius: 30px;
}

/* ── LEFT col: fills remaining 50% ── */
.col-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0rem;
  height: fit-content;
  overflow: hidden;
}

/* top-bar: title + switch in one row */
.top-bar {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.6rem;
  padding-bottom: 0.5rem;
}

.center-header {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  flex-shrink: 0;
}

/* ── LEFT col: model name + info link ── */
.col-left {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: flex-start;
  padding-top: 0.3rem;
}

.model-title-row {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.model-name {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-main);
  margin: 0;
  white-space: nowrap;
}

.more-info-link {
  font-size: 0.75rem;
  color: var(--accent-gold);
  text-decoration: underline;
  white-space: nowrap;
}

/* ── Switch ── */
.switch-wrap {
  background: var(--bg-secondary);
  border-radius: 14px;
  padding: 0.55rem 0.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  width: fit-content;
}

.switch-pill {
  width: 26px;
  height: 50px;
  background: var(--glass-bg);
  border-radius: 13px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  padding-top: 3px;
}

.switch-ball {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 28px;
  height: 28px;
  background: var(--accent-brown);
  border-radius: 50%;
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  pointer-events: none;
  will-change: transform;
  flex-shrink: 0;
}

.switch-labels {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  line-height: 1.5;
}

.switch-label { font-size: 0.78rem; color: var(--text-dim); transition: color 0.2s; }
.switch-label.active { color: var(--text-main); font-weight: 700; }

/* ── Cards ── */
.col-cards { min-width: 0; }

.card-scroller {
  display: flex;
  flex-direction: row;
  padding: 0px 20px 0px 0px;
  gap: 0.8rem;
  overflow-x: auto;
  padding-bottom: 0.4rem;
  scrollbar-width: none;
}
.card-scroller::-webkit-scrollbar { display: none; }

.product-card {
  position: relative;
  flex: 0 0 auto;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  box-shadow: 0 6px 22px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.info-btn {
  position: absolute;
  top: 0.55rem;
  left: 0.55rem;
  background: rgba(255,255,255,0.82);
  border: none;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-dim);
  z-index: 2;
  padding: 0;
  transition: color 0.2s;
}
.info-btn:hover { color: var(--accent-gold); background: var(--bg-main); }

.card-img-wrap {
  overflow: hidden;
  line-height: 0;
}
.card-img {
  width: auto;
  height: 280px;
  max-width: 550px;
  min-width: 200px;
  object-fit: contain;
  display: block;
  transition: transform 0.3s;
  padding: 10px;
}
.product-card:hover .card-img { transform: scale(1.04); }
.card-img-placeholder { width: 200px; height: 280px; }

.card-info { padding: 0.6rem 0.85rem 0.8rem; text-align: right; }
.card-title { font-size: 0.85rem; font-weight: 800; color: var(--text-main); margin: 0 0 0.1rem; line-height: 1.3; }
.card-feature { font-size: 0.7rem; color: var(--text-dim); margin: 0 0 0.15rem; }

.card-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.3rem;
}
.spec-label {
  font-size: 0.65rem;
  background: var(--bg-secondary);
  color: var(--text-muted);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
}

.card-price { font-size: 0.8rem; color: var(--text-muted); margin: 0; }

.card-fabric-price {
  font-size: 0.72rem;
  color: var(--accent-orange);
  font-weight: 600;
  margin: 0.1rem 0 0;
  direction: ltr;
}

.card-total-price {
  font-size: 0.78rem;
  color: var(--accent-gold);
  background: var(--accent-brown);
  border-radius: 6px;
  padding: 0.15rem 0.4rem;
  margin-top: 0.2rem;
  display: inline-block;
}

/* (hero styles now in col-hero block above) */

/* ── Empty ── */
.empty-bundles { color: #ccc; font-size: 0.85rem; padding: 1rem; }

.fabric-overlay-bg {
  position: fixed;
  inset: 0;
  z-index: 99990;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(6px);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s;
}
.fabric-overlay-bg.active {
  opacity: 1;
  visibility: visible;
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-box {
  background: var(--bg-main);
  border: 1px solid var(--glass-border);
  border-radius: 1.3rem;
  padding: 1.6rem;
  max-width: 430px;
  width: 100%;
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
  direction: rtl;
}

.modal-close {
  position: absolute;
  top: 0.8rem;
  left: 0.9rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.modal-header { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.9rem; }
.modal-header h3 { font-size: 1.05rem; font-weight: 800; color: var(--text-main); margin: 0; }
.badge { background: var(--accent-brown); color: var(--accent-gold); border-radius: 6px; padding: 0.18rem 0.6rem; font-size: 0.75rem; }

.fabric-row { display: flex; gap: 0.6rem; margin-bottom: 0.9rem; flex-wrap: wrap; }
.fabric-chip { background: var(--bg-secondary); border: 1px solid var(--glass-border); border-radius: 9px; padding: 0.4rem 0.8rem; display: flex; flex-direction: column; align-items: center; }
.chip-label { font-size: 0.68rem; color: var(--text-dim); }
.chip-val { font-size: 0.85rem; font-weight: 700; color: var(--text-main); }

.item-list { list-style: none; margin: 0; padding: 0; }
.item-list li { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--glass-border); font-size: 0.85rem; gap: 0.5rem; color: var(--text-main); }
.item-list li:last-child { border-bottom: none; }
.item-qty { color: var(--text-dim); font-size: 0.8rem; flex-shrink: 0; }
.item-price { color: var(--accent-gold); font-weight: 600; flex-shrink: 0; }

/* ── Layout Stabilization ── */
.model-row {
  display: grid;
  grid-template-columns: minmax(320px, 42%) minmax(0, 1fr);
  gap: 24px;
  align-items: stretch;
}

.col-hero {
  width: auto;
  height: 100%;
  min-height: 360px;
}

.hero-img {
  width: 100%;
  height: 100%;
  max-height: 540px;
  object-fit: cover;
}

.col-center {
  gap: 10px;
  min-width: 0;
}

.top-bar {
  align-items: center;
  gap: 10px;
}

.model-name {
  white-space: normal;
}

.switch-pill {
  position: relative;
  width: 34px;
  height: 62px;
  padding-top: 0;
}

.switch-ball {
  top: 4px;
  right: 4px;
  width: 26px;
  height: 26px;
}

.card-scroller {
  padding: 0 0 4px;
  gap: 10px;
}

.product-card {
  min-width: 240px;
}

.card-img-wrap {
  width: 100%;
  height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-img {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  height: 100%;
  max-height: 210px;
  object-fit: contain;
  padding: 10px 12px;
}

.card-img-placeholder {
  width: 100%;
  height: 210px;
}

/* ── Mobile ── */
@media (max-width: 900px) {
  .model-row {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .col-hero {
    width: 100%;
    min-height: 220px;
    max-height: 340px;
    border-radius: 18px;
  }
  .hero-img { border-radius: 18px; }
  .product-card {
    min-width: 180px;
  }
  .card-img-wrap {
    height: 180px;
  }
  .card-img {
    height: 180px;
    max-height: 180px;
  }
  .card-img-placeholder { height: 180px; }
  .model-name { font-size: 1.3rem; }
  .top-bar {
    align-items: flex-start;
  }
  .sofas-toolbar {
    top: calc(var(--header-sticky-offset-mobile, 70px) + env(safe-area-inset-top, 0px));
    margin-bottom: 14px;
  }
  .sofas-toolbar :deep(.ff-trigger),
  .fabric-tab-btn {
    min-height: 50px;
    padding: 0 10px;
    font-size: 12px;
  }
  .sofas-toolbar :deep(.ff-trigger-icon),
  .fabric-tab-btn svg {
    width: 16px;
    height: 16px;
  }
  .fabric-color-dot { width: 8px; height: 8px; box-shadow: 0 0 0 2px rgba(var(--accent-orange-rgb, 255, 152, 0), 0.18); }
}

/* ── Refreshed Sofa Collection Layout ── */
.model-section {
  margin-bottom: 28px;
}

.model-shell {
  border: 1px solid var(--glass-border);
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0.6) 100%);
  backdrop-filter: blur(16px);
  padding: 18px;
}

.model-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 14px;
}

.model-heading {
  min-width: 0;
}

.model-name {
  margin: 0;
  font-size: 1.55rem;
  line-height: 1.3;
}

.model-meta {
  margin: 6px 0 0;
  font-size: 0.85rem;
  color: var(--text-dim);
  font-weight: 700;
}

.dot-divider {
  margin: 0 6px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-tabs {
  display: inline-flex;
  background: var(--bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.tab-btn {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--text-dim);
  font-family: inherit;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 8px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: var(--accent-brown);
  color: var(--accent-gold);
}

.model-row {
  display: grid;
  grid-template-columns: minmax(300px, 36%) minmax(0, 1fr);
  gap: 16px;
}

.col-center {
  overflow: hidden;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
  align-content: start;
}

.product-card {
  min-width: 0;
}

.card-img-wrap {
  height: 200px;
}

.card-img {
  max-height: 200px;
}

@media (max-width: 900px) {
  .model-shell {
    border-radius: 20px;
    padding: 14px;
  }

  .model-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 10px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .model-row {
    grid-template-columns: 1fr;
  }

  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  }
}


/* MYSITE-MANAGEMENT-VISUAL-STYLES:START */
img {
  position: relative;
}
/* MYSITE-MANAGEMENT-VISUAL-STYLES:END */
</style>
