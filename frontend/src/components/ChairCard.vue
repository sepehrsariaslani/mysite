<template>
  <div class="chair-card" @click="goToProduct" dir="rtl">
    <!-- Info Button -->
    <div class="info-btn" @click.stop="showInfo = !showInfo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="8.01"/><line x1="12" y1="12" x2="12" y2="16"/>
      </svg>
    </div>
    
    <!-- Dimension Stickers -->
    <div class="dimension-stickers" v-if="hasMeaningfulValue(model.length) || hasMeaningfulValue(model.width) || hasMeaningfulValue(model.shape)">
      <span v-if="hasMeaningfulValue(model.length)" class="sticker">{{ model.length }}</span>
      <span v-if="hasMeaningfulValue(model.width)" class="sticker">{{ model.width }}</span>
      <span v-if="hasMeaningfulValue(model.shape)" class="sticker">{{ model.shape }}</span>
    </div>

    <!-- Info Tooltip -->
    <transition name="fade">
      <div v-if="showInfo" class="info-tooltip" @click.stop>
        <div class="info_row" v-if="hasMeaningfulValue(model.length)">
          <span>طول:</span>
          <strong>{{ model.length }}</strong>
        </div>
        <div class="info_row" v-if="hasMeaningfulValue(model.width)">
          <span>عرض:</span>
          <strong>{{ model.width }}</strong>
        </div>
        <div class="info_row" v-if="hasMeaningfulValue(model.shape)">
          <span>شکل:</span>
          <strong>{{ model.shape }}</strong>
        </div>
        <div class="info_row" v-if="model.odd_cloth">
          <span>پارچه مورد نیاز:</span>
          <strong>{{ model.odd_cloth }} متر</strong>
        </div>
      </div>
    </transition>

    <div class="card-body">
      <!-- Right Column: Image -->
      <div class="image-area">
        <img :src="model.image" :alt="model.name" loading="lazy" />
      </div>

      <!-- Left Column: Details -->
      <div class="color-price-list">
        <h3 class="model-name">{{ model.name }}</h3>
        <div 
          v-for="color in model.colors" 
          :key="color.name" 
          class="row-item"
        >
          <div class="price-col">
            <span v-if="getDisplayPrice(color) > 0" class="p-val">{{ formatToman(getDisplayPrice(color)) }}</span>
            <span v-else class="p-val contact">تماس بگیرید</span>
          </div>
          <span class="c-name">{{ color.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  calculateFabricPrice,
  calculatePriceWithFabric,
  computeTotalFabricMeters,
  resolveClothNeeds,
  toNumber
} from '../utils/fabricPricing'

const props = defineProps({
  model: { type: Object, required: true },
  productKind: { type: String, default: '' },
  selectedFabric: { type: Object, default: null }
})

const showInfo = ref(false)

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

function getSelectedCustomer() {
  try {
    return localStorage.getItem('mysite_selected_customer') || ''
  } catch (e) {
    return ''
  }
}

function formatToman(value) {
  return toNumber(value).toLocaleString('fa-IR')
}

function getBasePrice(color) {
  return toNumber(color?.variant?.raw_price) / 10
}

function getClothNeeds(color) {
  const variant = color?.variant || {}
  return resolveClothNeeds({
    odd_cloth: variant.odd_cloth ?? color?.odd_cloth,
    even_cloth: variant.even_cloth ?? color?.even_cloth,
    minor_cloth: variant.minor_cloth ?? color?.minor_cloth,
  }, props.model)
}

function getFabricMeters(color) {
  return computeTotalFabricMeters(1, getClothNeeds(color))
}

function getFabricPrice(color) {
  if (!props.selectedFabric) return 0
  return calculateFabricPrice(getFabricMeters(color), props.selectedFabric.pricePerMeter)
}

function hasFabricPrice(color) {
  return getFabricPrice(color) > 0
}

function getTotalPrice(color) {
  return calculatePriceWithFabric(getBasePrice(color), getFabricPrice(color))
}

function getDisplayPrice(color) {
  const base = getBasePrice(color)
  if (base <= 0) return 0
  return hasFabricPrice(color) ? getTotalPrice(color) : base
}

function goToProduct() {
  const customer = getSelectedCustomer()
  const kindQuery = props.productKind ? `&kind=${encodeURIComponent(props.productKind)}` : ''
  const customerQuery = customer ? `&customer=${encodeURIComponent(customer)}` : ''
  window.location.href = `/mysite/product?name=${encodeURIComponent(props.model.name)}${kindQuery}${customerQuery}`
}
</script>

<style scoped>
.chair-card {
  background: var(--glass-bg);
  border-radius: 24px;
  border: 1px solid var(--glass-border);
  padding: 20px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 240px;
  display: flex;
  flex-direction: column;
}

.chair-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(80, 49, 48, 0.1);
}

.model-name {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 15px 0;
  text-align: right;
  direction: rtl;
}

.info-btn {
  position: absolute;
  left: 20px;
  top: 20px;
  width: 28px;
  height: 28px;
  color: var(--text-main);
  opacity: 0.6;
  cursor: pointer;
  transition: 0.2s;
  z-index: 5;
}
.info-btn:hover { opacity: 1; }
.info-btn svg { width: 100%; height: 100%; }

.dimension-stickers {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-bottom: 15px;
}
.sticker {
  font-size: 10px;
  font-weight: 800;
  background: var(--bg-secondary);
  color: var(--text-dim);
  padding: 3px 10px;
  border-radius: 100px;
  border: 1px solid var(--glass-border);
}

.card-body {
  display: flex;
  gap: 15px;
  flex: 1;
}

.color-price-list {
  flex: 1;
  display: flex;
  direction: ltr;
  flex-direction: column;
  gap: 8px;
  padding-top: 10px;
}

.row-item {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  align-items: flex-start;
  font-size: 14px;
}

.c-name {
  color: var(--text-muted);
  font-weight: 500;
  white-space: nowrap;
  padding-top: 2px;
}

.price-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.p-val {
  color: #000;
  direction: ltr;
}

.p-val.contact {
  color: var(--text-dim);
  font-size: 12px;
  font-weight: 500;
}

.image-area {
  width: 180px;
  height: 220px;
  flex-shrink: 0;
}

.image-area img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.info-tooltip {
  position: absolute;
  top: 60px;
  right: 20px;
  left: 20px;
  background: var(--bg-secondary);
  backdrop-filter: blur(20px);
  padding: 15px;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  z-index: 10;
}

.info-title { font-size: 13px; font-weight: 800; color: var(--text-dim); margin-bottom: 5px; }
.info_row { display: flex; justify-content: space-between; font-size: 14px; color: var(--text-main); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 480px) {
  .image-area { width: 110px; height: 110px; }
  .model-name { font-size: 16px; }
}
</style>
