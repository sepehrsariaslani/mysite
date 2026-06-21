<template>
  <div class="shop-look-page" dir="rtl">
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">Shop by Look</p>
        <h1>الهام بگیر، دقیق انتخاب کن</h1>
        <p class="sub">
          روی نقطه‌ها بزن تا نام و قیمت محصول را ببینی. برای ورود به صفحه محصول، روی دکمه مشاهده محصول بزن.
        </p>
      </div>
      <div class="hero-controls">
        <label class="scene-search">
          <input
            v-model.trim="searchQuery"
            type="search"
            placeholder="جستجوی محصول (نام یا کد)"
            aria-label="جستجوی محصول در صحنه‌ها"
          />
        </label>
        <button
          v-if="searchQuery"
          type="button"
          class="clear-search"
          @click="searchQuery = ''"
        >
          پاک کردن
        </button>
        <div class="hero-filters">
          <button
            v-for="filter in filters"
            :key="filter.id"
            class="chip"
            :class="{ active: activeFilter === filter.id }"
            @click="activeFilter = filter.id"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="scenes" v-if="filteredScenes.length">
      <article v-for="scene in filteredScenes" :key="scene.id" class="scene-card">
        <header class="scene-head">
          <div>
            <h2>{{ scene.title }}</h2>
            <p class="scene-room">{{ scene.room_label }}</p>
          </div>
          <p class="scene-caption" v-if="scene.caption">{{ scene.caption }}</p>
        </header>

        <div class="scene-image-wrap" @click="closeAllSpots">
          <img
            v-if="sceneImage(scene) && !isSceneImageError(scene.id)"
            class="scene-image"
            :src="sceneImage(scene)"
            :alt="scene.title"
            loading="lazy"
            @error="markSceneImageError(scene.id)"
          />
          <div v-else class="scene-image-fallback">تصویر این صحنه در دسترس نیست</div>

          <div
            v-for="spot in scene.hotspots"
            :key="spot.id"
            class="hotspot"
            :style="{ left: `${spot.x_percent}%`, top: `${spot.y_percent}%` }"
            :class="{ open: isSpotOpen(scene.id, spot.id) }"
            role="button"
            tabindex="0"
            :aria-label="spot.label || spot.item_name"
            @mouseenter="openSpot(scene.id, spot.id)"
            @mouseleave="closeSpot(scene.id, spot.id)"
            @click.stop="onSpotClick($event, scene.id, spot.id)"
            @keydown.enter.prevent="onSpotClick($event, scene.id, spot.id)"
            @keydown.space.prevent="onSpotClick($event, scene.id, spot.id)"
          >
            <span class="dot"></span>
            <span class="pulse"></span>
            <div class="tooltip" @click.stop>
              <p class="tt-name">{{ spot.label || spot.item_name }}</p>
              <p class="tt-price">{{ formatPrice(displayPrice(spot)) }}</p>
              <a class="tt-cta" :href="appendCustomerQuery(spot.target_route)">مشاهده محصول</a>
            </div>
          </div>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <p v-if="searchQuery">
        برای «{{ searchQuery }}» صحنه‌ای پیدا نشد.
      </p>
      <p v-else>در این فیلتر هنوز صحنه‌ای منتشر نشده است.</p>
    </section>
  </div>
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

const scenes = ref(window.ShopByLookScenes || [])
const filters = ref(window.ShopByLookFilters || [{ id: 'all', label: 'همه' }])
const activeFilter = ref('all')
const searchQuery = ref('')

const selectedCustomer = ref(
  window.SelectedCustomer
    || (() => {
      try {
        return localStorage.getItem('mysite_selected_customer') || ''
      } catch (e) {
        return ''
      }
    })()
)

const { selectedFabric } = useFabricStore()

const activeSpotKey = ref('')
const imageErrorMap = ref({})

const isTouchDevice = (() => {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(hover: none)').matches || 'ontouchstart' in window
})()

const filteredScenes = computed(() => {
  const baseScenes = activeFilter.value === 'all'
    ? scenes.value
    : scenes.value.filter((scene) => scene.filter_id === activeFilter.value)
  const normalizedQuery = normalizeSearchText(searchQuery.value)
  if (!normalizedQuery) return baseScenes

  return baseScenes.filter((scene) => {
    const sceneHotspots = Array.isArray(scene.hotspots) ? scene.hotspots : []
    return sceneHotspots.some((spot) => spotMatchesQuery(spot, normalizedQuery))
  })
})

function normalizeSearchText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\u064a/g, 'ی')
    .replace(/\u0643/g, 'ک')
    .replace(/\s+/g, ' ')
    .trim()
}

function spotMatchesQuery(spot, query) {
  return [spot?.item_name, spot?.label, spot?.item_code]
    .some((field) => normalizeSearchText(field).includes(query))
}

function spotKey(sceneId, spotId) {
  return `${sceneId}::${spotId}`
}

function isSpotOpen(sceneId, spotId) {
  return activeSpotKey.value === spotKey(sceneId, spotId)
}

function openSpot(sceneId, spotId) {
  if (isTouchDevice) return
  activeSpotKey.value = spotKey(sceneId, spotId)
}

function closeSpot(sceneId, spotId) {
  if (isTouchDevice) return
  if (activeSpotKey.value === spotKey(sceneId, spotId)) {
    activeSpotKey.value = ''
  }
}

function onSpotClick(event, sceneId, spotId) {
  event.preventDefault()
  const key = spotKey(sceneId, spotId)
  activeSpotKey.value = activeSpotKey.value === key ? '' : key
}

function closeAllSpots() {
  activeSpotKey.value = ''
}

function sceneImage(scene) {
  return scene.cover_image || ''
}

function isSceneImageError(sceneId) {
  return !!imageErrorMap.value[sceneId]
}

function markSceneImageError(sceneId) {
  imageErrorMap.value = {
    ...imageErrorMap.value,
    [sceneId]: true,
  }
}

function appendCustomerQuery(route) {
  if (!route) return route
  if (!selectedCustomer.value) return route
  if (route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

function formatPrice(value) {
  const amount = toNumber(value)
  if (amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function getSpotFabricPrice(spot) {
  if (!selectedFabric.value) return 0
  const clothNeeds = resolveClothNeeds({
    odd_cloth: spot.odd_cloth,
    even_cloth: spot.even_cloth,
    minor_cloth: spot.minor_cloth,
  }, null)
  const meters = computeTotalFabricMeters(1, clothNeeds)
  return calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
}

function displayPrice(spot) {
  const base = toNumber(spot.base_price)
  const fabric = getSpotFabricPrice(spot)
  return calculatePriceWithFabric(base, fabric)
}
</script>

<style scoped>
.shop-look-page {
  min-height: 100vh;
  padding: 48px 24px 100px;
  background:
    radial-gradient(circle at 15% 5%, rgba(255, 201, 132, 0.2), transparent 32%),
    radial-gradient(circle at 84% 14%, rgba(149, 92, 51, 0.26), transparent 36%),
    var(--bg-main);
}

.hero {
  max-width: 1320px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 22px;
  flex-wrap: wrap;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  font-size: clamp(32px, 4vw, 54px);
  font-weight: 950;
  line-height: 1.1;
}

.sub {
  max-width: 680px;
  margin: 12px 0 0;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.8;
}

.hero-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.scene-search {
  flex: 1 1 320px;
  max-width: 420px;
}

.scene-search input {
  width: 100%;
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: var(--glass-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: 14px;
  font-weight: 700;
  padding: 10px 14px;
}

.scene-search input::placeholder {
  color: var(--text-muted);
}

.scene-search input:focus {
  outline: none;
  border-color: var(--accent-gold);
}

.clear-search {
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: transparent;
  color: var(--text-muted);
  font-family: inherit;
  font-size: 12px;
  font-weight: 800;
  padding: 9px 12px;
  cursor: pointer;
}

.clear-search:hover {
  color: var(--text-main);
  border-color: var(--glass-border-bright);
}

.hero-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: var(--glass-bg);
  color: var(--text-muted);
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  padding: 9px 16px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.chip:hover {
  color: var(--text-main);
  border-color: var(--glass-border-bright);
}

.chip.active {
  color: #3b281e;
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  box-shadow: 0 8px 18px rgba(242, 201, 126, 0.35);
}

.scenes {
  max-width: 1320px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.scene-card {
  border-radius: 28px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  overflow: hidden;
}

.scene-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 20px 20px 14px;
}

.scene-head h2 {
  margin: 0;
  font-size: 26px;
  font-weight: 900;
}

.scene-room {
  margin: 5px 0 0;
  font-size: 13px;
  color: var(--accent-gold);
  font-weight: 700;
}

.scene-caption {
  margin: 0;
  max-width: 540px;
  text-align: left;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.8;
}

.scene-image-wrap {
  position: relative;
  background: #f2eee8;
  aspect-ratio: 16 / 9;
  min-height: 320px;
}

.scene-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scene-image-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b5851;
  font-size: 14px;
  font-weight: 700;
  background:
    radial-gradient(circle at 20% 20%, rgba(255, 210, 144, 0.55), transparent 36%),
    radial-gradient(circle at 80% 80%, rgba(137, 89, 63, 0.3), transparent 42%),
    #ece5de;
}

.hotspot {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  z-index: 4;
}

.dot {
  position: absolute;
  inset: 5px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.95);
  background: rgba(57, 35, 24, 0.68);
}

.pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.55);
  animation: pulse 1.8s ease-out infinite;
}

.tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  right: 50%;
  transform: translateX(50%);
  width: 220px;
  border-radius: 14px;
  background: rgba(12, 9, 8, 0.9);
  color: #fff;
  text-align: right;
  padding: 10px;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.35);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.hotspot:hover .tooltip,
.hotspot.open .tooltip {
  opacity: 1;
  pointer-events: auto;
}

.tt-name {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
}

.tt-price {
  margin: 4px 0 8px;
  color: #ffe0a8;
  font-size: 12px;
  font-weight: 700;
}

.tt-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gold);
  color: #3d2b20;
  text-decoration: none;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 800;
}

.empty-state {
  max-width: 1320px;
  margin: 40px auto 0;
  border: 1px dashed var(--glass-border);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  color: var(--text-muted);
}

@keyframes pulse {
  0% { transform: scale(0.7); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}

@media (max-width: 768px) {
  .shop-look-page {
    padding: 24px 12px 90px;
  }

  .scene-search {
    flex-basis: 100%;
    max-width: none;
  }

  .scene-head {
    flex-direction: column;
    align-items: stretch;
  }

  .scene-caption {
    text-align: right;
  }

  .hotspot {
    width: 30px;
    height: 30px;
  }

  .scene-image-wrap {
    min-height: 240px;
  }

  .tooltip {
    width: 180px;
  }
}
</style>
