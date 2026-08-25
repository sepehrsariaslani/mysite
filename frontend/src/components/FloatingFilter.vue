<template>
  <div class="ff-root" dir="rtl">
    <button class="ff-trigger" :class="{ active: open }" @click="open = !open" :aria-label="triggerLabel">
      <svg class="ff-trigger-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="4" y1="7" x2="20" y2="7" />
        <line x1="4" y1="12" x2="20" y2="12" />
        <line x1="4" y1="17" x2="20" y2="17" />
        <circle cx="9" cy="7" r="2.5" />
        <circle cx="15" cy="12" r="2.5" />
        <circle cx="12" cy="17" r="2.5" />
      </svg>
      <span class="ff-trigger-label">{{ triggerLabel }}</span>
      <span v-if="activeCount > 0" class="ff-trigger-count">{{ toPersian(activeCount) }}</span>
    </button>

    <Teleport to="body">
      <transition name="overlay-fade">
        <button v-if="open" class="ff-overlay" type="button" aria-label="بستن فیلتر" @click="open = false"></button>
      </transition>

      <transition :name="drawerTransitionName">
        <aside v-if="open" class="ff-drawer" :class="drawerModeClass" dir="rtl">
          <header class="ff-head">
            <div class="ff-head-brand">
              <div class="ff-avatar">◎</div>
              <div>
                <p class="ff-sub">online</p>
                <h3>مرتب‌سازی و فیلتر</h3>
              </div>
            </div>
            <button class="ff-close" type="button" @click="open = false" aria-label="بستن">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </header>

          <div class="ff-body">
            <section class="ff-section">
              <div class="ff-title-row">
                <h4>مرتب‌سازی</h4>
              </div>
              <div class="ff-select-wrap">
                <select v-model="state.sort">
                  <option v-for="option in sortOptions" :key="option.id" :value="option.id">
                    {{ option.label }}
                  </option>
                </select>
                <span class="ff-select-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </span>
              </div>
            </section>

            <section class="ff-section">
              <div class="ff-title-row">
                <h4>مدل</h4>
                <span class="ff-mini" v-if="state.models.length">{{ toPersian(state.models.length) }} انتخاب</span>
              </div>

              <div class="ff-search-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="7.5" />
                  <line x1="16.7" y1="16.7" x2="21" y2="21" />
                </svg>
                <input v-model.trim="modelSearch" type="text" placeholder="جستجوی مدل..." />
              </div>

              <div class="ff-list">
                <button
                  v-for="option in visibleModelOptions"
                  :key="option.value"
                  type="button"
                  class="ff-radio-row"
                  :class="{ selected: state.models.includes(option.value) }"
                  @click="toggleModel(option.value)"
                >
                  <span class="ff-radio">
                    <span></span>
                  </span>
                  <span>{{ option.name }}</span>
                </button>
              </div>

              <button
                v-if="filteredModelOptions.length > modelSliceLimit"
                type="button"
                class="ff-more-link"
                @click="showAllModels = !showAllModels"
              >
                {{ showAllModels ? 'نمایش کمتر' : `+${toPersian(filteredModelOptions.length - modelSliceLimit)} بیشتر` }}
              </button>
            </section>

            <section class="ff-section">
              <button class="ff-title-row ff-collapse-btn" type="button" @click="advancedOpen = !advancedOpen">
                <h4>شرایط</h4>
                <svg :class="{ open: advancedOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              <div v-show="advancedOpen" class="ff-advanced-grid">
                <div class="ff-field">
                  <label>بازه سریع قیمت</label>
                  <div class="ff-select-wrap">
                    <select v-model="state.priceBand" @change="onPriceBandChange">
                      <option v-for="option in priceBandOptions" :key="option.id" :value="option.id">
                        {{ option.label }}
                      </option>
                    </select>
                    <span class="ff-select-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
                        <polyline points="6 9 12 15 18 9" />
                      </svg>
                    </span>
                  </div>
                </div>

                <div class="ff-field">
                  <label>بازه دقیق قیمت</label>
                  <div class="ff-range-head">
                    <span>{{ formatPrice(state.priceMin) }}</span>
                    <span>تا</span>
                    <span>{{ formatPrice(state.priceMax) }}</span>
                  </div>
                  <div class="ff-slider-wrap">
                    <div class="ff-track"></div>
                    <div class="ff-active-track" :style="rangeStyle"></div>
                    <input
                      type="range"
                      class="ff-slider"
                      :min="safeMin"
                      :max="safeMax"
                      :step="safeStep"
                      :value="state.priceMin"
                      @input="onMinInput"
                    />
                    <input
                      type="range"
                      class="ff-slider"
                      :min="safeMin"
                      :max="safeMax"
                      :step="safeStep"
                      :value="state.priceMax"
                      @input="onMaxInput"
                    />
                  </div>
                </div>

                <div class="ff-field">
                  <label>رنگ / پوشش</label>
                  <div class="ff-color-list">
                    <button
                      v-for="option in visibleColorOptions"
                      :key="option.value"
                      type="button"
                      class="ff-color-item"
                      :class="{ selected: state.colors.includes(option.value) }"
                      @click="toggleColor(option.value)"
                    >
                      <span class="ff-swatch" :style="colorStyle(option.value)"></span>
                      <span>{{ option.name }}</span>
                    </button>
                  </div>
                  <button
                    v-if="normalizedColors.length > colorSliceLimit"
                    type="button"
                    class="ff-more-link"
                    @click="showAllColors = !showAllColors"
                  >
                    {{ showAllColors ? 'نمایش کمتر' : `+${toPersian(normalizedColors.length - colorSliceLimit)} بیشتر` }}
                  </button>
                </div>
              </div>
            </section>

            <section v-if="activeTags.length" class="ff-active-tags">
              <button
                v-for="tag in activeTags"
                :key="`${tag.type}-${tag.value}`"
                type="button"
                class="ff-tag"
                @click="removeTag(tag)"
              >
                <span>{{ tag.label }}</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </section>
          </div>

          <footer class="ff-footer">
            <button class="ff-reset-btn" type="button" @click="resetFilters">پاک‌کردن</button>
            <button class="ff-apply-btn" type="button" @click="applyFilters">اعمال فیلتر</button>
          </footer>
        </aside>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  availableModels: { type: Array, default: () => [] },
  availableColors: { type: Array, default: () => [] },
  minBound: { type: Number, default: 0 },
  maxBound: { type: Number, default: 100000000 },
  step: { type: Number, default: 1000000 },
  triggerLabel: { type: String, default: 'مرتب‌سازی و فیلتر' },
})

const emit = defineEmits(['apply', 'reset'])

const open = ref(false)
const advancedOpen = ref(true)
const showAllModels = ref(false)
const showAllColors = ref(false)
const modelSearch = ref('')
const modelSliceLimit = 4
const colorSliceLimit = 6
const isMobile = ref(false)

const state = reactive({
  sort: 'default',
  models: [],
  colors: [],
  priceMin: 0,
  priceMax: 0,
  priceBand: 'all',
})

const boundState = reactive({
  min: 0,
  max: 0,
})

const sortOptions = [
  { id: 'default', label: 'مرتب‌سازی پیش‌فرض' },
  { id: 'price-low', label: 'ارزان‌ترین' },
  { id: 'price-high', label: 'گران‌ترین' },
  { id: 'name-asc', label: 'نام (الف تا ی)' },
]

const drawerModeClass = computed(() => (isMobile.value ? 'is-mobile' : 'is-desktop'))
const drawerTransitionName = computed(() => (isMobile.value ? 'sheet-slide' : 'sidebar-slide'))

const normalizedModels = computed(() =>
  (props.availableModels || [])
    .map((raw) => {
      if (typeof raw === 'string') {
        const value = raw.trim()
        return { value, name: value }
      }
      const value = String(raw?.value || raw?.name || '').trim()
      const name = String(raw?.name || raw?.value || '').trim()
      return { value, name: name || value }
    })
    .filter((entry) => entry.value && entry.name)
)

const normalizedColors = computed(() =>
  (props.availableColors || [])
    .map((raw) => {
      if (typeof raw === 'string') {
        const value = raw.trim()
        return { value, name: value }
      }
      const value = String(raw?.value || raw?.name || '').trim()
      const name = String(raw?.name || raw?.value || '').trim()
      return { value, name: name || value }
    })
    .filter((entry) => entry.value && entry.name)
)

const filteredModelOptions = computed(() => {
  const query = modelSearch.value.trim()
  if (!query) return normalizedModels.value
  return normalizedModels.value.filter((item) => item.name.includes(query) || item.value.includes(query))
})

const visibleModelOptions = computed(() => {
  if (showAllModels.value) return filteredModelOptions.value
  return filteredModelOptions.value.slice(0, modelSliceLimit)
})

const visibleColorOptions = computed(() => {
  if (showAllColors.value) return normalizedColors.value
  return normalizedColors.value.slice(0, colorSliceLimit)
})

const safeStep = computed(() => {
  const numeric = Number(props.step || 0)
  return Number.isFinite(numeric) && numeric > 0 ? numeric : 1000000
})

const safeMin = computed(() => boundState.min)
const safeMax = computed(() => boundState.max)

const activeCount = computed(() => {
  let count = 0
  if (state.sort !== 'default') count += 1
  if (state.models.length) count += 1
  if (state.colors.length) count += 1
  if (state.priceMin !== boundState.min || state.priceMax !== boundState.max) count += 1
  return count
})

const activeTags = computed(() => {
  const tags = []
  state.models.forEach((value) => {
    const target = normalizedModels.value.find((m) => m.value === value)
    tags.push({ type: 'model', value, label: target?.name || value })
  })
  state.colors.forEach((value) => {
    const target = normalizedColors.value.find((c) => c.value === value)
    tags.push({ type: 'color', value, label: target?.name || value })
  })
  if (state.priceMin !== boundState.min || state.priceMax !== boundState.max) {
    tags.push({
      type: 'price',
      value: 'range',
      label: `قیمت: ${toPersian(formatPriceNumeric(state.priceMin))} تا ${toPersian(formatPriceNumeric(state.priceMax))}`,
    })
  }
  return tags
})

const priceBandOptions = computed(() => {
  if (boundState.max <= boundState.min) {
    return [{ id: 'all', label: 'همه قیمت‌ها' }]
  }

  const span = boundState.max - boundState.min
  const cutOne = roundToStep(boundState.min + span * 0.33)
  const cutTwo = roundToStep(boundState.min + span * 0.66)

  const lowEnd = clampToBounds(cutOne)
  const midEnd = clampToBounds(Math.max(cutTwo, lowEnd + safeStep.value))

  return [
    { id: 'all', label: 'همه قیمت‌ها' },
    { id: 'low', label: `تا ${shortToman(lowEnd)}` },
    { id: 'mid', label: `${shortToman(lowEnd)} تا ${shortToman(midEnd)}` },
    { id: 'high', label: `بالاتر از ${shortToman(midEnd)}` },
    { id: 'custom', label: 'سفارشی' },
  ]
})

const rangeStyle = computed(() => {
  const span = safeMax.value - safeMin.value
  if (span <= 0) {
    return { right: '0%', width: '100%' }
  }
  const fromRight = ((safeMax.value - state.priceMax) / span) * 100
  const toRight = ((safeMax.value - state.priceMin) / span) * 100
  return {
    right: `${fromRight}%`,
    width: `${Math.max(0, toRight - fromRight)}%`,
  }
})

watch(
  () => [props.minBound, props.maxBound, props.step],
  () => {
    const [nextMin, nextMax] = normalizeBounds(props.minBound, props.maxBound)
    boundState.min = nextMin
    boundState.max = nextMax

    if (state.priceMin === 0 && state.priceMax === 0) {
      state.priceMin = nextMin
      state.priceMax = nextMax
      state.priceBand = 'all'
      return
    }

    state.priceMin = clampToBounds(state.priceMin)
    state.priceMax = clampToBounds(state.priceMax)
    ensurePriceOrder()
    syncBandWithRange()
  },
  { immediate: true }
)

watch(
  () => normalizedModels.value.map((item) => item.value),
  (allowedValues) => {
    const allowed = new Set(allowedValues)
    state.models = state.models.filter((value) => allowed.has(value))
  }
)

watch(
  () => normalizedColors.value.map((item) => item.value),
  (allowedValues) => {
    const allowed = new Set(allowedValues)
    state.colors = state.colors.filter((value) => allowed.has(value))
  }
)

onMounted(() => {
  syncViewportMode()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', syncViewportMode, { passive: true })
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', syncViewportMode)
  }
})

function syncViewportMode() {
  if (typeof window === 'undefined') {
    isMobile.value = false
    return
  }
  isMobile.value = window.innerWidth <= 900
}

function onMinInput(event) {
  const raw = Number(event?.target?.value || boundState.min)
  state.priceMin = clampToBounds(raw)
  ensurePriceOrder()
  syncBandWithRange()
}

function onMaxInput(event) {
  const raw = Number(event?.target?.value || boundState.max)
  state.priceMax = clampToBounds(raw)
  ensurePriceOrder()
  syncBandWithRange()
}

function ensurePriceOrder() {
  if (state.priceMin > state.priceMax) {
    const keep = state.priceMin
    state.priceMin = state.priceMax
    state.priceMax = keep
  }

  if (state.priceMax - state.priceMin < safeStep.value) {
    if (state.priceMax + safeStep.value <= boundState.max) {
      state.priceMax += safeStep.value
    } else if (state.priceMin - safeStep.value >= boundState.min) {
      state.priceMin -= safeStep.value
    }
  }

  state.priceMin = clampToBounds(state.priceMin)
  state.priceMax = clampToBounds(state.priceMax)
}

function onPriceBandChange() {
  const selected = state.priceBand
  if (selected === 'custom') return
  if (selected === 'all') {
    state.priceMin = boundState.min
    state.priceMax = boundState.max
    return
  }

  const span = boundState.max - boundState.min
  const cutOne = clampToBounds(roundToStep(boundState.min + span * 0.33))
  const cutTwo = clampToBounds(roundToStep(boundState.min + span * 0.66))
  const mid = Math.max(cutTwo, cutOne + safeStep.value)

  if (selected === 'low') {
    state.priceMin = boundState.min
    state.priceMax = cutOne
  } else if (selected === 'mid') {
    state.priceMin = cutOne
    state.priceMax = mid
  } else if (selected === 'high') {
    state.priceMin = mid
    state.priceMax = boundState.max
  }

  ensurePriceOrder()
}

function syncBandWithRange() {
  if (state.priceMin === boundState.min && state.priceMax === boundState.max) {
    state.priceBand = 'all'
    return
  }

  const span = boundState.max - boundState.min
  if (span <= 0) {
    state.priceBand = 'all'
    return
  }

  const cutOne = clampToBounds(roundToStep(boundState.min + span * 0.33))
  const cutTwo = clampToBounds(roundToStep(boundState.min + span * 0.66))
  const mid = Math.max(cutTwo, cutOne + safeStep.value)

  if (state.priceMin === boundState.min && state.priceMax === cutOne) {
    state.priceBand = 'low'
    return
  }
  if (state.priceMin === cutOne && state.priceMax === mid) {
    state.priceBand = 'mid'
    return
  }
  if (state.priceMin === mid && state.priceMax === boundState.max) {
    state.priceBand = 'high'
    return
  }
  state.priceBand = 'custom'
}

function toggleModel(value) {
  const idx = state.models.indexOf(value)
  if (idx >= 0) {
    state.models.splice(idx, 1)
    return
  }
  state.models.push(value)
}

function toggleColor(value) {
  const idx = state.colors.indexOf(value)
  if (idx >= 0) {
    state.colors.splice(idx, 1)
    return
  }
  state.colors.push(value)
}

function removeTag(tag) {
  if (tag.type === 'model') {
    state.models = state.models.filter((value) => value !== tag.value)
    return
  }
  if (tag.type === 'color') {
    state.colors = state.colors.filter((value) => value !== tag.value)
    return
  }
  if (tag.type === 'price') {
    state.priceMin = boundState.min
    state.priceMax = boundState.max
    state.priceBand = 'all'
  }
}

function applyFilters() {
  emit('apply', {
    models: [...state.models],
    colors: [...state.colors],
    priceMin: state.priceMin,
    priceMax: state.priceMax,
    priceActive: state.priceMin !== boundState.min || state.priceMax !== boundState.max,
    sort: state.sort,
  })
  open.value = false
}

function resetFilters() {
  state.sort = 'default'
  state.models = []
  state.colors = []
  state.priceMin = boundState.min
  state.priceMax = boundState.max
  state.priceBand = 'all'
  modelSearch.value = ''
  showAllModels.value = false
  showAllColors.value = false
  emit('reset')
  open.value = false
}

function normalizeBounds(minValue, maxValue) {
  const min = Number(minValue)
  const max = Number(maxValue)
  const safeMinValue = Number.isFinite(min) ? min : 0
  const safeMaxValue = Number.isFinite(max) ? max : safeMinValue
  return [Math.min(safeMinValue, safeMaxValue), Math.max(safeMinValue, safeMaxValue)]
}

function roundToStep(value) {
  if (!safeStep.value) return Math.round(value)
  return Math.round(value / safeStep.value) * safeStep.value
}

function clampToBounds(value) {
  const raw = Number(value)
  if (!Number.isFinite(raw)) return boundState.min
  return Math.min(boundState.max, Math.max(boundState.min, raw))
}

function shortToman(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return '۰'
  if (amount >= 1_000_000) {
    const mil = amount / 1_000_000
    return `${toPersian(mil.toLocaleString('fa-IR', { maximumFractionDigits: 1 }))} میلیون`
  }
  return `${toPersian(amount.toLocaleString('fa-IR'))} تومان`
}

function formatPrice(value) {
  return `${toPersian(formatPriceNumeric(value))} تومان`
}

function formatPriceNumeric(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return '۰'
  return amount.toLocaleString('fa-IR')
}

function toPersian(value) {
  return String(value).replace(/\d/g, (digit) => '۰۱۲۳۴۵۶۷۸۹'[Number(digit)])
}

function colorStyle(name) {
  const map = {
    'رنگ مشکی': 'background:linear-gradient(135deg,#1b1b1b,#3a3a3a)',
    'مشکی': 'background:linear-gradient(135deg,#1b1b1b,#3a3a3a)',
    'رنگ بژ': 'background:linear-gradient(135deg,#f5f1e8,#e8ddcc)',
    'بژ': 'background:linear-gradient(135deg,#f5f1e8,#e8ddcc)',
    'رنگ سفید': 'background:linear-gradient(135deg,#ffffff,#ececec);border:1px solid rgba(80,49,48,0.2)',
    'سفید': 'background:linear-gradient(135deg,#ffffff,#ececec);border:1px solid rgba(80,49,48,0.2)',
    'آبکاری نقره‌ای': 'background:linear-gradient(135deg,#d4d4d4,#f1f1f1)',
    'آبکاری طلایی': 'background:linear-gradient(135deg,#f6cd70,#d7a64a)',
    'آبکاری پی‌وی‌دی': 'background:linear-gradient(135deg,#2b2b2b,#4c4c4c)',
  }
  return map[name] || 'background:linear-gradient(135deg,#d0cbc4,#b8aa96)'
}
</script>

<style scoped>
.ff-root {
  position: relative;
  z-index: 100;
  width: fit-content;
  font-family: 'Peyda', sans-serif;
}

.ff-trigger {
  min-height: 46px;
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  padding: 12px 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  color: var(--text-main);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.22);
  cursor: pointer;
  transition: 0.3s cubic-bezier(0.19, 1, 0.22, 1);
  white-space: nowrap;
}

.ff-trigger:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-hover);
  border-color: var(--accent-gold);
}

.ff-trigger.active {
  background: var(--glass-bg-hover);
}

.ff-trigger-icon {
  width: 18px;
  height: 18px;
}

.ff-trigger-label {
  font-size: 13px;
  font-weight: 800;
  line-height: 1.1;
}

.ff-trigger-count {
  min-width: 21px;
  height: 21px;
  padding: 0 6px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--accent-orange) 24%, #fff 76%);
  color: var(--accent-brown);
  font-size: 11px;
  font-weight: 900;
}

.ff-overlay {
  position: fixed;
  inset: 0;
  z-index: 99990;
  border: 0;
  background: rgba(0, 0, 0, 0.56);
  backdrop-filter: blur(6px);
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

.ff-drawer {
  position: fixed;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--bg-main);
  box-shadow: -4px 0 40px rgba(0, 0, 0, 0.2);
  z-index: 100000;
  display: flex;
  flex-direction: column;
}

.ff-drawer.is-desktop {
  top: 0;
  left: 0;
  width: min(420px, 94vw);
  height: 100vh;
  border-radius: 0 30px 30px 0;
}

.ff-drawer.is-mobile {
  left: 0;
  right: 0;
  bottom: 0;
  width: auto;
  height: min(76svh, 720px);
  max-height: 76svh;
  border-radius: 22px 22px 0 0;
}

.sidebar-slide-enter-active,
.sidebar-slide-leave-active,
.sheet-slide-enter-active,
.sheet-slide-leave-active {
  transition: transform 0.24s ease, opacity 0.24s ease;
}

.sidebar-slide-enter-from,
.sidebar-slide-leave-to {
  opacity: 0;
  transform: translateX(-36px);
}

.sheet-slide-enter-from,
.sheet-slide-leave-to {
  opacity: 0;
  transform: translateY(24px);
}

.ff-head {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--glass-border);
  background: var(--bg-footer);
  color: var(--text-main);
}

.ff-head-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ff-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid var(--glass-border);
  box-shadow: none;
  font-size: 18px;
}

.ff-sub {
  margin: 0 0 2px;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 780;
  text-transform: lowercase;
}

.ff-head h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 18px;
  font-weight: 700;
}

.ff-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.ff-close svg {
  width: 15px;
  height: 15px;
}

.ff-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: grid;
  gap: 10px;
}

.ff-section {
  border-radius: 22px;
  border: 1px solid var(--glass-border);
  background:
    linear-gradient(160deg, color-mix(in srgb, var(--glass-bg) 70%, #fff 30%), color-mix(in srgb, var(--glass-bg) 95%, transparent));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 12px;
}

.ff-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.ff-title-row h4 {
  margin: 0;
  color: var(--text-main);
  font-size: 20px;
  font-weight: 920;
}

.ff-mini {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 780;
}

.ff-select-wrap {
  position: relative;
}

.ff-select-wrap select {
  width: 100%;
  height: 46px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--glass-bg) 72%, #fff 28%);
  color: var(--text-main);
  font-family: inherit;
  font-size: 14px;
  font-weight: 760;
  padding: 0 14px 0 52px;
  appearance: none;
}

.ff-select-icon {
  position: absolute;
  left: 6px;
  top: 5px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent-brown) 84%, #000 16%);
  color: var(--accent-gold);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 6px 14px rgba(24, 15, 10, 0.24);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.ff-select-icon svg {
  width: 15px;
  height: 15px;
}

.ff-search-wrap {
  position: relative;
  margin-bottom: 8px;
}

.ff-search-wrap svg {
  position: absolute;
  right: 12px;
  top: 50%;
  width: 15px;
  height: 15px;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.ff-search-wrap input {
  width: 100%;
  height: 42px;
  border-radius: 13px;
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--glass-bg) 72%, #fff 28%);
  padding: 0 36px 0 10px;
  color: var(--text-main);
  font-family: inherit;
  font-size: 13px;
  font-weight: 710;
}

.ff-list {
  display: grid;
  gap: 6px;
}

.ff-radio-row {
  border: 0;
  background: transparent;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 32px;
  font-family: inherit;
  font-size: 15px;
  font-weight: 740;
  text-align: right;
  cursor: pointer;
}

.ff-radio {
  width: 21px;
  height: 21px;
  border-radius: 50%;
  border: 2px solid color-mix(in srgb, var(--glass-border-bright) 75%, #fff 25%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ff-radio span {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: transparent;
}

.ff-radio-row.selected .ff-radio {
  border-color: var(--text-main);
}

.ff-radio-row.selected .ff-radio span {
  background: var(--text-main);
}

.ff-more-link {
  border: 0;
  background: transparent;
  color: #2c67df;
  font-family: inherit;
  font-size: 13px;
  font-weight: 800;
  width: fit-content;
  margin-top: 4px;
  cursor: pointer;
}

.ff-collapse-btn {
  width: 100%;
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.ff-collapse-btn svg {
  width: 15px;
  height: 15px;
  color: var(--text-main);
  transition: transform 0.2s ease;
}

.ff-collapse-btn svg.open {
  transform: rotate(180deg);
}

.ff-advanced-grid {
  display: grid;
  gap: 12px;
}

.ff-field {
  display: grid;
  gap: 6px;
}

.ff-field label {
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 790;
}

.ff-range-head {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 760;
}

.ff-slider-wrap {
  position: relative;
  height: 34px;
}

.ff-track,
.ff-active-track {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 5px;
  border-radius: 999px;
}

.ff-track {
  inset: 0;
  background: color-mix(in srgb, var(--glass-border) 80%, #fff 20%);
}

.ff-active-track {
  background: linear-gradient(90deg, #e4b66d 0%, #b68449 100%);
}

.ff-slider {
  position: absolute;
  inset: 0;
  margin: 0;
  width: 100%;
  background: transparent;
  pointer-events: none;
  appearance: none;
}

.ff-slider::-webkit-slider-thumb {
  appearance: none;
  pointer-events: auto;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #4f3427;
  box-shadow: 0 2px 7px rgba(40, 24, 16, 0.2);
  cursor: pointer;
}

.ff-slider::-moz-range-thumb {
  pointer-events: auto;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #4f3427;
  box-shadow: 0 2px 7px rgba(40, 24, 16, 0.2);
  cursor: pointer;
}

.ff-color-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.ff-color-item {
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--glass-bg) 70%, #fff 30%);
  border-radius: 12px;
  padding: 6px 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-main);
  font-family: inherit;
  font-size: 12px;
  font-weight: 740;
  text-align: right;
  cursor: pointer;
}

.ff-color-item.selected {
  border-color: color-mix(in srgb, var(--accent-gold) 60%, var(--glass-border-bright) 40%);
  background: color-mix(in srgb, var(--accent-gold) 22%, var(--glass-bg) 78%);
}

.ff-swatch {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ff-active-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ff-tag {
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--glass-bg) 72%, #fff 28%);
  color: var(--text-main);
  border-radius: 999px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 770;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  cursor: pointer;
}

.ff-tag svg {
  width: 11px;
  height: 11px;
}

.ff-footer {
  padding: 10px 12px 12px;
  border-top: 1px solid var(--glass-border);
  background: linear-gradient(180deg, transparent, color-mix(in srgb, var(--glass-bg) 72%, #fff 28%));
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.ff-reset-btn,
.ff-apply-btn {
  height: 46px;
  border-radius: 999px;
  border: 0;
  font-family: inherit;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
}

.ff-reset-btn {
  color: var(--text-main);
  background: color-mix(in srgb, var(--glass-bg) 68%, #fff 32%);
  border: 1px solid var(--glass-border);
}

.ff-apply-btn {
  color: var(--accent-gold);
  background: linear-gradient(120deg, #1f1511 0%, #4f3328 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    0 10px 18px rgba(28, 17, 12, 0.28);
}

@media (max-width: 900px) {
  .ff-root {
    width: 100%;
  }

  .ff-trigger {
    width: 100%;
    justify-content: center;
  }

  .ff-head {
    padding: 14px 16px;
    border-radius: 22px 22px 0 0;
  }
}
</style>
