<template>
  <section class="sbl-preview" dir="rtl" v-if="cards.length">
    <div class="head">
      <div>
        <p class="eyebrow">Shop by Look</p>
        <h2>انتخاب سریع از چیدمان واقعی</h2>
      </div>
      <a :href="allLooksRoute" class="view-all">مشاهده همه</a>
    </div>

    <div class="grid">
      <article v-for="scene in cards" :key="scene.id" class="card">
        <img class="card-image" :src="scene.cover_image || firstSpotImage(scene)" :alt="scene.title" loading="lazy" />

        <div
          v-for="spot in scene.hotspots"
          :key="spot.id"
          class="hotspot"
          :style="{ left: `${spot.x_percent}%`, top: `${spot.y_percent}%` }"
          role="button"
          tabindex="0"
        >
          <span class="dot"></span>
          <div class="tooltip">
            <p class="name">{{ spot.label || spot.item_name }}</p>
            <p class="price">{{ formatPrice(displayPrice(spot)) }}</p>
            <a :href="appendCustomerQuery(spot.target_route)">مشاهده</a>
          </div>
        </div>

        <div class="meta">
          <strong>{{ scene.title }}</strong>
          <span>{{ scene.room_label }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useFabricStore } from '../stores/fabricStore'
import {
  calculateFabricPrice,
  calculatePriceWithFabric,
  computeTotalFabricMeters,
  resolveClothNeeds,
  toNumber,
} from '../utils/fabricPricing'

const props = defineProps({
  scenes: { type: Array, default: () => [] },
  selectedCustomer: { type: String, default: '' },
})

const { selectedFabric } = useFabricStore()

const localCustomer = ref(
  props.selectedCustomer
    || window.SelectedCustomer
    || (() => {
      try {
        return localStorage.getItem('mysite_selected_customer') || ''
      } catch (e) {
        return ''
      }
    })()
)

const cards = computed(() => (props.scenes || []).slice(0, 6))

const allLooksRoute = computed(() => {
  const base = '/mysite/shop-by-look'
  if (!localCustomer.value) return base
  return `${base}?customer=${encodeURIComponent(localCustomer.value)}`
})

function appendCustomerQuery(route) {
  if (!route) return route
  if (!localCustomer.value) return route
  if (route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(localCustomer.value)}`
}

function formatPrice(value) {
  const amount = toNumber(value)
  if (amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function displayPrice(spot) {
  const base = toNumber(spot.base_price)
  if (!selectedFabric.value) return base

  const clothNeeds = resolveClothNeeds({
    odd_cloth: spot.odd_cloth,
    even_cloth: spot.even_cloth,
    minor_cloth: spot.minor_cloth,
  }, null)
  const meters = computeTotalFabricMeters(1, clothNeeds)
  const fabric = calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
  return calculatePriceWithFabric(base, fabric)
}

function firstSpotImage(scene) {
  return (scene.hotspots && scene.hotspots[0] && scene.hotspots[0].item_image) || ''
}
</script>

<style scoped>
.sbl-preview {
  --preview-surface: var(--home-surface-strong, rgba(255, 255, 255, 0.78));
  --preview-surface-soft: var(--home-surface, rgba(255, 255, 255, 0.6));
  --preview-border: var(--home-border, rgba(120, 85, 57, 0.2));
  --preview-border-strong: var(--home-border-strong, rgba(120, 85, 57, 0.32));
  --preview-text-main: var(--home-text-main, var(--text-main));
  --preview-text-muted: var(--home-text-muted, var(--text-muted));
  --preview-accent: var(--home-accent, var(--accent-gold));
  --preview-accent-strong: var(--home-accent-strong, #7b4f34);
  --preview-shadow: var(--home-shadow, 0 20px 52px rgba(71, 45, 27, 0.12));
  max-width: var(--home-shell-max, 1320px);
  margin: var(--home-space-lg, 72px) auto 0;
  padding: 0 var(--home-inline-pad, 24px);
  position: relative;
  z-index: 1;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 14px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--preview-accent-strong);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.head h2 {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  font-weight: 930;
  color: var(--preview-text-main);
}

.view-all {
  text-decoration: none;
  color: #fff8ee;
  background: var(--preview-accent-strong);
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 800;
  border: 1px solid transparent;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.view-all:hover {
  transform: translateY(-2px);
  box-shadow: var(--preview-shadow);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.card {
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  border: 1px solid var(--preview-border);
  background: var(--preview-surface);
  min-height: 280px;
  box-shadow: var(--preview-shadow);
}

.card-image {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 280px;
  object-fit: cover;
}

.hotspot {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
}

.dot {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--preview-accent-strong) 74%, #000 26%);
  border: 2px solid #fff;
}

.tooltip {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  bottom: calc(100% + 8px);
  right: 50%;
  transform: translateX(50%);
  width: 170px;
  padding: 8px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--preview-accent-strong) 72%, #000 28%);
  color: #fff9ef;
  text-align: right;
  transition: opacity 0.2s ease;
}

.hotspot:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
}

.name {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
}

.price {
  margin: 4px 0 7px;
  color: #ffe4b6;
  font-size: 11px;
  font-weight: 700;
}

.tooltip a {
  display: inline-flex;
  text-decoration: none;
  color: #fff8ee;
  background: var(--preview-accent-strong);
  border-radius: 8px;
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 800;
}

.meta {
  position: absolute;
  inset: auto 10px 10px 10px;
  background: color-mix(in srgb, var(--preview-surface-soft) 85%, #000 15%);
  color: var(--preview-text-main);
  border-radius: 12px;
  padding: 8px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.meta strong {
  font-size: 13px;
  font-weight: 800;
}

.meta span {
  font-size: 11px;
  color: var(--preview-accent-strong);
  font-weight: 700;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 680px) {
  .sbl-preview {
    padding: 0 12px;
    margin-top: 56px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .head {
    align-items: flex-start;
    flex-direction: column;
  }

  .hotspot {
    width: 22px;
    height: 22px;
  }

  .dot {
    inset: 3px;
  }
}
</style>
