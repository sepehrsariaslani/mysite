<template>
  <div class="page" dir="rtl">
    <ProductHero
      title="نیمکت و پاف"
      description="مجموعه‌ای از نیمکت‌ها و پاف‌های مدرن برای خانه‌ای گرم و زیبا"
      :stats="heroStats"
    />

    <main class="products-main">
      <div class="products-toolbar">
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
        <button v-if="hasFabricItems" class="fabric-tab-btn" type="button" @click="fabricOpen = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5z"/>
            <path d="M4 9h16M9 4v16"/>
          </svg>
          <span>{{ selectedFabric ? 'پارچه: ' + selectedFabric.qualityName + (selectedFabric.colorName ? ' - ' + selectedFabric.colorName : '') : 'پارچه' }}</span>
          <span v-if="selectedFabric" class="fabric-color-dot"></span>
        </button>
      </div>

      <section v-if="filteredBodyColorModels.length > 0">
        <div class="section-header">
          <h2>نیمکت و پاف</h2>
          <span class="section-count">{{ filteredBodyColorModels.length }} مدل</span>
        </div>
        <div class="products-grid">
          <TableCard
            v-for="model in filteredBodyColorModels"
            :key="model.name"
            :model="model"
            product-kind="bench"
            :selected-fabric="selectedFabric"
            @open-fabric="fabricOpen = true"
          />
        </div>
      </section>

      <div v-if="filteredBodyColorModels.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
          <line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>
        </svg>
        <p>محصولی با این فیلترها یافت نشد</p>
        <button @click="clearFilters">پاک کردن فیلترها</button>
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TableCard from '../components/TableCard.vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import ProductHero from '../components/ProductHero.vue'
import FloatingFilter from '../components/FloatingFilter.vue'
import { useFabricStore } from '../stores/fabricStore'
import { buildFilterOptions, filterItems, sortItems } from '../utils/productFiltering'


const bodyColorModels = ref(window.BodyColorChairs || [])
const clothGroups = ref(window.ClothGroups || [])

const heroStats = computed(() => [
  { label: 'مدل محصول', value: bodyColorModels.value.length },
  { label: 'نوع پارچه', value: clothGroups.value.length },
])

const filterAdapter = {
  getName: (model) => model?.name || '',
  getColors: (model) => (model?.colors || []).map((color) => color?.name || ''),
  getPrices: (model) => (model?.colors || []).map((color) => color?.variant?.raw_price || 0),
}

const filterOptions = computed(() => {
  return buildFilterOptions(bodyColorModels.value, filterAdapter)
})

const activeFilters = ref({
  models: [],
  colors: [],
  priceMin: 0,
  priceMax: Number.MAX_SAFE_INTEGER,
  priceActive: false,
  sort: 'default',
})

const fabricOpen = ref(false)
const { selectedFabric, setSelectedFabric } = useFabricStore()

const hasFabricItems = computed(() => {
  return bodyColorModels.value.some((model) => model.odd_cloth > 0)
})

const filteredBodyColorModels = computed(() => {
  const filtered = filterItems(bodyColorModels.value, activeFilters.value, filterAdapter)
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

function onFabricSelect(fabric) {
  setSelectedFabric(fabric)
  fabricOpen.value = false
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  padding-bottom: 120px;
  position: relative;
  overflow-x: clip;
  font-family: 'Peyda', sans-serif;
}

.products-main { max-width: 1400px; margin: 0 auto; padding: 32px 24px 120px; position: relative; z-index: 1; overflow-x: clip; }
.products-toolbar {
  position: sticky;
  top: calc(var(--header-sticky-offset, 82px) + env(safe-area-inset-top, 0px));
  z-index: 280;
  display: flex;
  direction: ltr;
  align-items: stretch;
  width: min(100%, 980px);
  max-width: calc(100vw - 48px);
  box-sizing: border-box;
  margin: 0 auto 16px;
  border: 1px solid color-mix(in srgb, var(--glass-border) 88%, #d2d7df 12%);
  border-radius: 999px;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-main) 90%, #f6f8fb 10%);
  backdrop-filter: blur(12px);
  box-shadow: 0 16px 34px rgba(34, 45, 62, 0.12);
}
.products-toolbar :deep(.ff-root) { flex: 1 1 50%; min-width: 0; width: auto; }
.products-toolbar :deep(.ff-trigger) {
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
.products-toolbar :deep(.ff-trigger:hover),
.products-toolbar :deep(.ff-trigger.active) {
  transform: none;
  background: rgba(24, 39, 68, 0.05);
  border-color: transparent;
  box-shadow: none;
}
.products-toolbar :deep(.ff-trigger-icon) { width: 22px; height: 22px; }
.products-toolbar :deep(.ff-trigger-label) { font-size: 16px; font-weight: 900; }
.products-toolbar :deep(.ff-trigger-count) { display: none; }
.section-header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; margin-top: 40px; }
.section-header h2 { font-size: 24px; font-weight: 900; color: var(--text-main); }
.section-count { background: rgba(var(--accent-orange-rgb, 255, 152, 0), 0.1); color: var(--accent-orange); padding: 6px 16px; border-radius: 12px; font-size: 13px; font-weight: 800; border: 1px solid rgba(var(--accent-orange-rgb, 255, 152, 0), 0.2); }

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}
@media (max-width: 1100px) { .products-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .products-grid { grid-template-columns: 1fr; } }

.empty-state { text-align: center; padding: 80px 24px; color: #999; }
.empty-state svg { width: 64px; height: 64px; margin-bottom: 14px; }
.empty-state p { font-size: 16px; margin-bottom: 14px; color: var(--text-dim); }
.empty-state button { background: var(--accent-brown); color: var(--accent-gold); border: none; padding: 10px 24px; border-radius: 8px; font-family: inherit; font-size: 12px; cursor: pointer; }

/* ── Fabric Tab Button ── */
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
.fabric-tab-btn svg { width: 20px; height: 20px; flex-shrink: 0; }
.fabric-tab-btn:hover { transform: none; background: rgba(24, 39, 68, 0.05); }
.fabric-color-dot { width: 14px; height: 14px; border-radius: 50%; background: var(--accent-orange); box-shadow: 0 0 0 4px rgba(var(--accent-orange-rgb, 255, 152, 0), 0.18); flex-shrink: 0; }

.fabric-overlay-bg { position: fixed; inset: 0; z-index: 99990; background: rgba(0,0,0,0.56); backdrop-filter: blur(6px); opacity: 0; visibility: hidden; transition: all 0.25s; }
.fabric-overlay-bg.active { opacity: 1; visibility: visible; }

@media (max-width: 768px) {
  .products-toolbar {
    top: calc(var(--header-sticky-offset-mobile, 70px) + env(safe-area-inset-top, 0px));
    margin-bottom: 14px;
  }
  .products-toolbar :deep(.ff-trigger),
  .fabric-tab-btn {
    min-height: 50px;
    padding: 0 10px;
    font-size: 12px;
  }
  .products-toolbar :deep(.ff-trigger-icon),
  .fabric-tab-btn svg {
    width: 16px;
    height: 16px;
  }
  .fabric-color-dot { width: 8px; height: 8px; box-shadow: 0 0 0 2px rgba(var(--accent-orange-rgb, 255, 152, 0), 0.18); }
}
</style>
