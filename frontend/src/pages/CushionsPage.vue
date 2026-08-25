<template>
  <div class="page" dir="rtl">
    <ProductHero
      title="کوسن و تشکچه"
      description="بر اساس مدل و سایز انتخاب کن، بعد بسته تکی/دوتایی/سه‌تایی رو بردار"
      :stats="heroStats"
    />

    <main class="products-main">
      <section v-if="groups.length > 0">
        <div class="section-header">
          <h2>مدل‌های قابل سفارش</h2>
          <span class="section-count">{{ groups.length }} گروه</span>
        </div>

        <div class="products-grid">
          <article v-for="group in groups" :key="groupKey(group)" class="cushion-card">
            <div class="card-image-wrap">
              <img v-if="group.image" :src="group.image" :alt="group.display_name || group.name" class="card-image" />
              <div v-else class="card-image-placeholder">بدون تصویر</div>
            </div>

            <div class="card-body">
              <h3 class="card-title">{{ group.display_name || group.name }}</h3>
              <p class="card-subtitle" v-if="group.size">سایز: {{ group.size }}</p>

              <div class="pack-list">
                <button
                  v-for="opt in group.options"
                  :key="`${groupKey(group)}-${opt.item_code}-${opt.name}`"
                  class="pack-row"
                  @click="goToOption(opt)"
                >
                  <span class="pack-name">{{ opt.name || 'تکی' }}</span>
                  <span class="pack-price">{{ formatToman(optionFinalPrice(opt)) }} تومان</span>
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <div v-if="groups.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
          <line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>
        </svg>
        <p>محصولی برای نمایش وجود ندارد</p>
      </div>
    </main>

    <button class="fabric-fab" @click="fabricOpen = true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5z"/>
        <path d="M4 9h16M9 4v16"/>
      </svg>
      <span>{{ selectedFabric ? `${selectedFabric.qualityName} - ${selectedFabric.colorName}` : 'انتخاب پارچه' }}</span>
    </button>

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
import ProductHero from '../components/ProductHero.vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import { useFabricStore } from '../stores/fabricStore'
import {
  calculateFabricPrice,
  computeTotalFabricMeters,
  resolveClothNeeds,
  toNumber,
} from '../utils/fabricPricing'

const groups = ref(window.CushionGroups || window.BodyColorChairs || [])
const clothGroups = ref(window.ClothGroups || [])
const fabricOpen = ref(false)
const { selectedFabric, setSelectedFabric } = useFabricStore()

const getCachedCustomer = () => {
  try {
    return localStorage.getItem('mysite_selected_customer') || ''
  } catch (e) {
    return ''
  }
}
const selectedCustomer = ref(window.SelectedCustomer || getCachedCustomer())


const heroStats = computed(() => [
  { label: 'گروه کوسن', value: groups.value.length },
  {
    label: 'گزینه بسته',
    value: groups.value.reduce((sum, group) => sum + (group.options?.length || 0), 0),
  },
  { label: 'نوع پارچه', value: clothGroups.value.length },
])

const groupKey = (group) => `${group.variant_of || ''}-${group.cushion_type || ''}-${group.size || ''}-${group.name || ''}`

function formatToman(value) {
  return Math.round(toNumber(value || 0)).toLocaleString('fa-IR')
}

function appendCustomerQuery(route) {
  if (!route || !selectedCustomer.value) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

function optionFabricMeters(opt) {
  const needs = resolveClothNeeds(opt, opt)
  return computeTotalFabricMeters(1, needs)
}

function optionFinalPrice(opt) {
  const basePrice = toNumber(opt.price_toman || (toNumber(opt.raw_price) / 10))
  if (!selectedFabric.value) return basePrice

  const meters = optionFabricMeters(opt)
  const fabricPrice = calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
  return basePrice + fabricPrice
}

function goToOption(opt) {
  const targetName = opt.item_name || opt.item_code
  if (!targetName) return
  window.location.href = appendCustomerQuery(`/mysite/product/${encodeURIComponent(targetName)}?kind=sofa`)
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
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
}

.products-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px 120px;
  position: relative;
  z-index: 1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  margin-top: 40px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 900;
  color: var(--text-main);
}

.section-count {
  background: rgba(var(--accent-orange-rgb, 255, 152, 0), 0.1);
  color: var(--accent-orange);
  padding: 6px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  border: 1px solid rgba(var(--accent-orange-rgb, 255, 152, 0), 0.2);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 48px;
}

.cushion-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 22px;
  overflow: hidden;
}

.card-image-wrap {
  height: 220px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
}

.card-image-placeholder {
  color: var(--text-dim);
  font-size: 13px;
}

.card-body {
  padding: 14px;
  display: grid;
  gap: 10px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
  color: var(--text-main);
}

.card-subtitle {
  margin: 0;
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

.pack-list {
  display: grid;
  gap: 8px;
}

.pack-row {
  width: 100%;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: #fff;
  color: var(--text-main);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  cursor: pointer;
  font-family: inherit;
}

.pack-row:hover {
  border-color: var(--accent-gold);
  background: rgba(255, 255, 255, 0.92);
}

.pack-name {
  font-size: 13px;
  font-weight: 800;
}

.pack-price {
  font-size: 13px;
  font-weight: 900;
  color: var(--accent-orange);
}

.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: #999;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  color: var(--text-dim);
}

.fabric-fab {
  position: fixed;
  bottom: 100px;
  right: 24px;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  color: var(--text-main);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  transition: 0.3s cubic-bezier(0.19, 1, 0.22, 1);
}

.fabric-fab svg {
  width: 22px;
  height: 22px;
}

.fabric-fab:hover {
  transform: translateY(-5px);
  background: var(--glass-bg-hover);
  border-color: var(--accent-gold);
}

.fabric-overlay-bg {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s;
}

.fabric-overlay-bg.active {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 1100px) {
  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .products-grid {
    grid-template-columns: 1fr;
  }

  .card-image-wrap {
    height: 180px;
  }
}
</style>
