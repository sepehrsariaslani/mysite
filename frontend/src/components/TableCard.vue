<template>
  <div class="table-card" @click="goToProduct" dir="rtl">
    <!-- Info Button (Floating) -->
    <div class="info-btn" @click.stop="showInfo = !showInfo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="8.01"/><line x1="12" y1="12" x2="12" y2="16"/>
      </svg>
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

    <!-- 1. Top Image -->
    <div class="image-area">
      <img :src="model.image" :alt="model.name" loading="lazy" />
    </div>

    <!-- 2. Meta Info Row (Model Name & Stickers) -->
    <div class="meta-row">
      <h3 class="model-name">{{ model.name }}</h3>
      
      <div class="dimension-stickers">
        <span v-if="hasMeaningfulValue(model.size)" class="sticker size">{{ model.size }}</span>
        <span v-if="hasMeaningfulValue(model.length)" class="sticker">{{ model.length }}</span>
        <span v-if="hasMeaningfulValue(model.width)" class="sticker">{{ model.width }}</span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- 3. Options List (Colors & Prices) -->
    <div class="options-list">
      <div 
        v-for="color in model.colors" 
        :key="color.name" 
        class="option-row"
      >
        <span class="c-name">{{ color.name }}</span>
        <div class="price-col">
          <span class="p-val" v-if="getDisplayPrice(color) > 0">{{ formatToman(getDisplayPrice(color)) }}</span>
          <span class="p-val contact" v-else>تماس بگیرید</span>
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
.table-card {
  background: var(--glass-bg);
  border-radius: 28px;
  border: 1px solid var(--glass-border);
  padding: 24px;
  position: relative;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.table-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.1);
  border-color: var(--accent-gold);
}

/* Info Tooltip */
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
.info_row { display: flex; justify-content: space-between; font-size: 14px; color: var(--text-main); margin-bottom: 4px; }

/* Image Area */
.image-area {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-area img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.6s ease;
}
.table-card:hover .image-area img {
  transform: scale(1.05);
}

/* Meta Row */
.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.model-name {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0;
}

.dimension-stickers {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.sticker {
  font-size: 11px;
  font-weight: 800;
  background: var(--bg-secondary);
  color: var(--text-dim);
  padding: 4px 10px;
  border-radius: 100px;
  border: 1px solid var(--glass-border);
  white-space: nowrap;
}
.sticker.size {
  background: rgba(var(--accent-gold-rgb, 212, 175, 55), 0.1);
  color: var(--accent-gold);
  border-color: rgba(var(--accent-gold-rgb, 212, 175, 55), 0.3);
}

.divider {
  height: 1px;
  background: linear-gradient(to left, var(--glass-border), transparent);
  margin: 4px 0;
}

/* Options List */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 14px;
}

.c-name {
  color: var(--text-main);
  font-weight: 800;
  font-size: 15px;
}

.price-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.p-val {
  color: #000;
  font-weight: 900;
  direction: ltr;
}
.p-val.contact {
  color: var(--text-dim);
  font-weight: 500;
  font-size: 13px;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 480px) {
  .image-area { height: 200px; }
  .model-name { font-size: 18px; }
  .table-card { padding: 16px; }
}
</style>
