<template>
  <div class="page" dir="rtl">
    <ProductHero
      title="پارچه‌ها"
      description="ابتدا کالیته را انتخاب کن، سپس رنگ پارچه مناسب را بردار و برای کل مسیر خرید ذخیره کن"
      :stats="heroStats"
    />

    <main class="fabrics-main">
      <section class="selected-summary" v-if="selectedFabricResolved">
        <div class="summary-image">
          <img
            v-if="selectedFabricResolved.image"
            :src="selectedFabricResolved.image"
            :alt="selectedFabricResolved.name"
          />
          <div v-else class="summary-placeholder">پارچه</div>
        </div>
        <div class="summary-content">
          <p class="summary-label">پارچه انتخابی فعال</p>
          <h3>{{ selectedFabricResolved.quality }} - {{ selectedFabricResolved.name }}</h3>
          <p class="summary-meta">
            <span v-if="selectedFabricResolved.code">کد: {{ selectedFabricResolved.code }}</span>
            <span v-if="selectedFabricResolved.formatted_price">{{ selectedFabricResolved.formatted_price }} تومان / متر</span>
          </p>
        </div>
        <button class="clear-btn" @click="clearSelectedFabric">پاک کردن انتخاب</button>
      </section>

      <section v-if="!selectedQuality" class="qualities-section">
        <div class="filters-panel quality-search-panel">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              v-model="qualitySearch"
              type="text"
              placeholder="جستجو در نام کالیته..."
            />
          </div>
        </div>

        <div class="section-head">
          <h2>انتخاب کالیته پارچه</h2>
          <span class="section-count">{{ filteredQualityCards.length }} کالیته</span>
        </div>

        <div class="qualities-grid" v-if="filteredQualityCards.length">
          <article
            v-for="quality in filteredQualityCards"
            :key="quality.name"
            class="quality-card"
          >
            <button class="quality-card-action" @click="openQuality(quality.name)">
              <div class="quality-image-wrap">
                <img v-if="quality.image" :src="quality.image" :alt="quality.name" loading="lazy" />
                <div v-else class="quality-image-placeholder">{{ quality.name.slice(0, 2) }}</div>
              </div>
              <div class="quality-content">
                <h3>{{ quality.name }}</h3>
                <p>{{ quality.variantCount }} رنگ موجود</p>
                <p class="quality-codes">{{ quality.codeCount }} کد</p>
              </div>
            </button>
          </article>
        </div>

        <div v-else class="empty-state">
          <p>کالیته‌ای با عبارت جستجوی فعلی پیدا نشد.</p>
        </div>
      </section>

      <section v-else>
        <div class="quality-toolbar">
          <button class="back-btn" @click="goBackToQualities">بازگشت به کالیته‌ها</button>
          <div class="quality-toolbar-title">
            <p>کالیته انتخاب‌شده</p>
            <h2>{{ selectedQuality }}</h2>
          </div>
        </div>

        <section class="filters-panel">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              v-model="colorSearch"
              type="text"
              placeholder="جستجو در نام رنگ یا کد..."
            />
          </div>

          <div class="chips-wrap">
            <div class="chip-group">
              <span class="chip-label">کد رنگ</span>
              <button class="chip" :class="{ active: activeCode === 'all' }" @click="activeCode = 'all'">همه</button>
              <button
                v-for="code in selectedQualityCodeOptions"
                :key="code"
                class="chip"
                :class="{ active: activeCode === code }"
                @click="activeCode = code"
              >
                {{ code }}
              </button>
            </div>
          </div>
        </section>

        <div class="section-head">
          <h2>رنگ‌های کالیته {{ selectedQuality }}</h2>
          <span class="section-count">{{ filteredFabrics.length }} رنگ</span>
        </div>

        <div class="fabrics-grid" v-if="filteredFabrics.length">
          <article
            v-for="fabric in filteredFabrics"
            :key="fabric.id"
            class="fabric-card"
            :class="{ selected: isSelectedFabric(fabric) }"
          >
            <div class="fabric-image-wrap">
              <img v-if="fabric.image" :src="fabric.image" :alt="fabric.name" loading="lazy" />
              <div v-else class="fabric-image-placeholder">{{ (fabric.code || '').slice(0, 3) || 'پارچه' }}</div>
            </div>

            <div class="fabric-content">
              <div class="fabric-top-meta">
                <span class="fabric-quality">{{ fabric.quality }}</span>
                <span v-if="fabric.code" class="fabric-code">کد {{ fabric.code }}</span>
              </div>
              <h3 class="fabric-name">{{ fabric.name }}</h3>
              <p class="fabric-price">{{ fabric.formatted_price || '۰' }} تومان / متر</p>
            </div>

            <button
              class="pick-btn"
              :class="{ selected: isSelectedFabric(fabric) }"
              @click="selectFabric(fabric)"
            >
              {{ isSelectedFabric(fabric) ? 'انتخاب شده' : 'انتخاب پارچه' }}
            </button>
          </article>
        </div>

        <div v-else class="empty-state">
          <p>رنگی با فیلترهای فعلی برای این کالیته پیدا نشد.</p>
        </div>
      </section>

      <section class="related-section" v-if="selectedQuality">
        <div class="section-head">
          <h2>محصولات مرتبط با پارچه</h2>
          <span class="section-count">{{ filteredRelatedProducts.length }} محصول</span>
        </div>

        <div class="related-hint" v-if="!selectedFabricInCurrentQuality">
          <p>برای دقت بیشتر، یک رنگ از همین کالیته انتخاب کن. فعلاً محصولات پارچه‌خور عمومی نمایش داده می‌شوند.</p>
        </div>

        <div class="related-hint" v-else-if="selectedSpecificProducts.length === 0">
          <p>برای این پارچه ارتباط مستقیم پروژه‌ای پیدا نشد؛ محصولات پارچه‌خور عمومی نمایش داده می‌شوند.</p>
        </div>

        <div class="chip-group related-colors" v-if="relatedColorOptions.length">
          <span class="chip-label">فیلتر رنگ محصول</span>
          <button class="chip" :class="{ active: activeRelatedColor === 'all' }" @click="activeRelatedColor = 'all'">همه</button>
          <button
            v-for="color in relatedColorOptions"
            :key="color"
            class="chip"
            :class="{ active: activeRelatedColor === color }"
            @click="activeRelatedColor = color"
          >
            {{ color }}
          </button>
        </div>

        <div class="related-grid" v-if="filteredRelatedProducts.length">
          <a
            v-for="product in filteredRelatedProducts"
            :key="`${product.item_code}-${product.route}`"
            class="related-card"
            :href="product.route"
          >
            <div class="related-image-wrap">
              <img v-if="product.image" :src="product.image" :alt="product.item_name" loading="lazy" />
              <div v-else class="related-image-placeholder">محصول</div>
            </div>
            <div class="related-content">
              <h3>{{ product.item_name }}</h3>
              <p class="related-price">{{ formatToman(product.base_price) }} تومان</p>
              <div class="related-colors-list" v-if="product.colors?.length">
                <span v-for="color in product.colors" :key="`${product.item_code}-${color}`">{{ color }}</span>
              </div>
            </div>
          </a>
        </div>

        <div v-else class="empty-state">
          <p>محصول مرتبطی برای نمایش وجود ندارد.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import ProductHero from '../components/ProductHero.vue'
import { useFabricStore } from '../stores/fabricStore'

const clothGroups = ref(window.ClothGroups || [])
const fabrics = ref(window.Fabrics || [])
const filterMeta = ref(window.FabricFilterMeta || {})
const fallbackRelatedProducts = ref(window.FabricRelatedProducts || [])
const projectLinks = ref(window.FabricProjectLinks || {})

const qualitySearch = ref('')
const colorSearch = ref('')
const selectedQuality = ref('')
const activeCode = ref('all')
const activeRelatedColor = ref('all')

const { selectedFabric, setSelectedFabric, clearSelectedFabric } = useFabricStore()


const heroStats = computed(() => [
  { label: 'کالیته', value: qualityOptions.value.length },
  { label: 'رنگ پارچه', value: codeOptions.value.length },
  { label: 'محصول مرتبط', value: fallbackRelatedProducts.value.length },
])

const qualityOptions = computed(() => {
  const fromBoot = Array.isArray(filterMeta.value.qualities) ? filterMeta.value.qualities : []
  if (fromBoot.length) return fromBoot
  return Array.from(new Set(fabrics.value.map((f) => f.quality).filter(Boolean))).sort()
})

const codeOptions = computed(() => {
  const fromBoot = Array.isArray(filterMeta.value.codes) ? filterMeta.value.codes : []
  if (fromBoot.length) return fromBoot
  return Array.from(new Set(fabrics.value.map((f) => f.code).filter(Boolean))).sort()
})

const qualityCards = computed(() => {
  if (Array.isArray(clothGroups.value) && clothGroups.value.length) {
    return clothGroups.value
      .map((group) => {
        const variants = Array.isArray(group.clothvariants) ? group.clothvariants : []
        const codeSet = new Set(
          variants
            .map((v) => String(v.code || '').trim())
            .filter(Boolean)
        )

        const sampleImage = group.sample_image || variants.find((v) => v.image)?.image || ''

        return {
          name: String(group.name || '').trim(),
          image: sampleImage,
          variantCount: variants.length,
          codeCount: codeSet.size,
        }
      })
      .filter((g) => g.name)
      .sort((a, b) => a.name.localeCompare(b.name, 'fa'))
  }

  const map = new Map()
  for (const fabric of fabrics.value) {
    const quality = String(fabric.quality || '').trim()
    if (!quality) continue

    if (!map.has(quality)) {
      map.set(quality, {
        name: quality,
        image: fabric.image || '',
        variantCount: 0,
        codes: new Set(),
      })
    }

    const row = map.get(quality)
    row.variantCount += 1
    if (fabric.code) row.codes.add(String(fabric.code).trim())
    if (!row.image && fabric.image) row.image = fabric.image
  }

  return Array.from(map.values())
    .map((row) => ({
      name: row.name,
      image: row.image,
      variantCount: row.variantCount,
      codeCount: row.codes.size,
    }))
    .sort((a, b) => a.name.localeCompare(b.name, 'fa'))
})

const filteredQualityCards = computed(() => {
  const q = qualitySearch.value.trim().toLowerCase()
  if (!q) return qualityCards.value

  return qualityCards.value.filter((quality) => {
    const text = [quality.name, quality.variantCount, quality.codeCount]
      .map((v) => String(v || '').toLowerCase())
      .join(' ')
    return text.includes(q)
  })
})

const fabricsInSelectedQuality = computed(() => {
  if (!selectedQuality.value) return []
  return fabrics.value.filter((f) => f.quality === selectedQuality.value)
})

const selectedQualityCodeOptions = computed(() => {
  const set = new Set(
    fabricsInSelectedQuality.value
      .map((f) => String(f.code || '').trim())
      .filter(Boolean)
  )
  return Array.from(set).sort()
})

const filteredFabrics = computed(() => {
  if (!selectedQuality.value) return []

  const q = colorSearch.value.trim().toLowerCase()
  return fabricsInSelectedQuality.value.filter((fabric) => {
    if (activeCode.value !== 'all' && fabric.code !== activeCode.value) return false
    if (!q) return true

    const haystack = [fabric.name, fabric.item_name, fabric.code, fabric.item_code]
      .map((v) => String(v || '').toLowerCase())
      .join(' ')

    return haystack.includes(q)
  })
})

const selectedItemCode = computed(() => {
  if (selectedFabric.value?.itemCode) {
    return String(selectedFabric.value.itemCode).trim()
  }

  const quality = String(selectedFabric.value?.qualityName || '').trim()
  const color = String(selectedFabric.value?.colorName || '').trim()
  if (!quality || !color) return ''

  const match = fabrics.value.find((fabric) => {
    return fabric.quality === quality && [fabric.name, fabric.item_name].includes(color)
  })
  return match?.item_code || ''
})

const selectedFabricResolved = computed(() => {
  const itemCode = selectedItemCode.value
  if (!itemCode) return null
  return fabrics.value.find((fabric) => fabric.item_code === itemCode) || null
})

const selectedFabricInCurrentQuality = computed(() => {
  if (!selectedFabricResolved.value || !selectedQuality.value) return false
  return selectedFabricResolved.value.quality === selectedQuality.value
})

const selectedSpecificProducts = computed(() => {
  if (!selectedFabricInCurrentQuality.value) return []

  const code = selectedItemCode.value
  if (!code) return []

  const rows = projectLinks.value?.[code]
  return Array.isArray(rows) ? rows : []
})

const mergedRelatedProducts = computed(() => {
  const merged = []
  const seen = new Set()

  for (const row of [...selectedSpecificProducts.value, ...fallbackRelatedProducts.value]) {
    const key = String(row?.item_code || row?.id || row?.item_name || '')
    if (!key || seen.has(key)) continue
    seen.add(key)
    merged.push(row)
  }

  return merged
})

const relatedColorOptions = computed(() => {
  const set = new Set()
  mergedRelatedProducts.value.forEach((row) => {
    ;(row.colors || []).forEach((c) => {
      const color = String(c || '').trim()
      if (color) set.add(color)
    })
  })
  return Array.from(set).sort()
})

const filteredRelatedProducts = computed(() => {
  if (activeRelatedColor.value === 'all') return mergedRelatedProducts.value
  return mergedRelatedProducts.value.filter((row) => (row.colors || []).includes(activeRelatedColor.value))
})

watch(selectedQuality, (nextQuality) => {
  if (nextQuality && !qualityOptions.value.includes(nextQuality)) {
    selectedQuality.value = ''
    syncQualityInQuery('')
    return
  }

  activeCode.value = 'all'
  colorSearch.value = ''
  activeRelatedColor.value = 'all'
  syncQualityInQuery(nextQuality)
})

function readInitialQuality() {
  const params = new URLSearchParams(window.location.search)
  const fromQuery = params.get('quality') || ''
  const quality = String(fromQuery).trim()
  if (quality && qualityOptions.value.includes(quality)) return quality
  return ''
}

function syncQualityInQuery(quality) {
  const url = new URL(window.location.href)
  if (quality) {
    url.searchParams.set('quality', quality)
  } else {
    url.searchParams.delete('quality')
  }

  const target = `${url.pathname}${url.search ? `?${url.searchParams.toString()}` : ''}${url.hash}`
  window.history.replaceState({}, '', target)
}

function openQuality(qualityName) {
  selectedQuality.value = String(qualityName || '').trim()
}

function goBackToQualities() {
  selectedQuality.value = ''
}

function formatToman(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return 'تماس بگیرید'
  return amount.toLocaleString('fa-IR')
}

function isSelectedFabric(fabric) {
  return !!fabric && !!selectedItemCode.value && fabric.item_code === selectedItemCode.value
}

function selectFabric(fabric) {
  if (!fabric) return

  setSelectedFabric({
    qualityName: fabric.quality || '',
    colorName: fabric.name || fabric.item_name || '',
    pricePerMeter: Number(fabric.price_per_meter || 0),
    formattedPrice: fabric.formatted_price || '',
    image: fabric.image || fabric.sample_image || '',
    itemCode: fabric.item_code || '',
    code: fabric.code || '',
  })
}

selectedQuality.value = readInitialQuality()
</script>

<style scoped>
* { box-sizing: border-box; }

.page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  padding-bottom: 120px;
  position: relative;
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
}

.fabrics-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px 120px;
  display: grid;
  gap: 24px;
}

.filters-panel {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 16px;
  display: grid;
  gap: 14px;
}

.search-box {
  position: relative;
}

.search-box svg {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-dim);
}

.search-box input {
  width: 100%;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 12px 42px 12px 12px;
  font-family: inherit;
  color: var(--text-main);
  font-size: 14px;
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-gold);
}

.chips-wrap {
  display: grid;
  gap: 12px;
}

.chip-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.chip-label {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-dim);
  margin-left: 4px;
}

.chip {
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  color: var(--text-main);
  border-radius: 999px;
  padding: 7px 14px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.chip:hover {
  border-color: var(--accent-gold);
}

.chip.active {
  border-color: var(--accent-gold);
  color: var(--accent-gold);
  background: color-mix(in srgb, var(--accent-gold) 12%, transparent);
}

.selected-summary {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  align-items: center;
  background: var(--glass-bg);
  border: 1px solid color-mix(in srgb, var(--accent-gold) 40%, var(--glass-border));
  border-radius: 20px;
  padding: 12px;
}

.summary-image {
  width: 72px;
  height: 72px;
  border-radius: 14px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--glass-border);
}

.summary-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.summary-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-dim);
}

.summary-content h3 {
  margin: 0;
  font-size: 18px;
}

.summary-label {
  margin: 0 0 6px;
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

.summary-meta {
  margin: 8px 0 0;
  display: flex;
  gap: 14px;
  font-size: 13px;
  color: var(--text-muted);
}

.clear-btn {
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 10px 14px;
  color: var(--text-main);
  font-family: inherit;
  cursor: pointer;
}

.section-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.section-head h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.section-count {
  font-size: 12px;
  font-weight: 800;
  color: var(--accent-orange);
  border: 1px solid color-mix(in srgb, var(--accent-orange) 28%, transparent);
  background: color-mix(in srgb, var(--accent-orange) 10%, transparent);
  border-radius: 999px;
  padding: 6px 12px;
}

.qualities-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.quality-card {
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  overflow: hidden;
  background: var(--glass-bg);
}

.quality-card-action {
  width: 100%;
  border: none;
  background: transparent;
  padding: 0;
  color: inherit;
  cursor: pointer;
  text-align: right;
}

.quality-image-wrap {
  aspect-ratio: 1;
  background: var(--bg-secondary);
}

.quality-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.quality-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 900;
  color: var(--text-dim);
}

.quality-content {
  padding: 12px;
  border-top: 1px solid var(--glass-border);
}

.quality-content h3 {
  margin: 0;
  font-size: 18px;
}

.quality-content p {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--text-dim);
}

.quality-codes {
  color: var(--accent-gold) !important;
  font-weight: 800;
}

.quality-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 10px;
}

.back-btn {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 14px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
}

.quality-toolbar-title p {
  margin: 0;
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

.quality-toolbar-title h2 {
  margin: 4px 0 0;
  font-size: 28px;
}

.fabrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.fabric-card {
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  background: var(--glass-bg);
  overflow: hidden;
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.fabric-card.selected {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 50%, transparent);
}

.fabric-image-wrap {
  aspect-ratio: 1;
  background: var(--bg-secondary);
}

.fabric-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fabric-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 900;
  color: var(--text-dim);
}

.fabric-content {
  padding: 10px;
}

.fabric-top-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}

.fabric-quality {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-main);
}

.fabric-code {
  font-size: 11px;
  color: var(--text-dim);
}

.fabric-name {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
  min-height: 36px;
}

.fabric-price {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--accent-gold);
  font-weight: 800;
}

.pick-btn {
  border: none;
  border-top: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-main);
  font-family: inherit;
  font-size: 13px;
  font-weight: 800;
  padding: 10px;
  cursor: pointer;
}

.pick-btn.selected {
  color: var(--accent-gold);
}

.related-section {
  margin-top: 8px;
}

.related-colors {
  margin-bottom: 14px;
}

.related-hint {
  margin-bottom: 14px;
  font-size: 13px;
  color: var(--text-muted);
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.related-card {
  text-decoration: none;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  border-radius: 18px;
  overflow: hidden;
  color: var(--text-main);
  transition: 0.2s ease;
}

.related-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-gold);
}

.related-image-wrap {
  aspect-ratio: 4 / 3;
  background: var(--bg-secondary);
}

.related-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--text-dim);
  font-weight: 800;
}

.related-content {
  padding: 10px;
}

.related-content h3 {
  margin: 0;
  font-size: 15px;
  min-height: 40px;
}

.related-price {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--accent-gold);
  font-weight: 900;
}

.related-colors-list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.related-colors-list span {
  font-size: 11px;
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  padding: 3px 8px;
  color: var(--text-dim);
}

.empty-state {
  border: 1px dashed var(--glass-border);
  border-radius: 16px;
  padding: 26px;
  text-align: center;
  color: var(--text-dim);
}

@media (max-width: 1200px) {
  .qualities-grid,
  .fabrics-grid,
  .related-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 920px) {
  .qualities-grid,
  .fabrics-grid,
  .related-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .selected-summary {
    grid-template-columns: auto 1fr;
  }

  .clear-btn {
    grid-column: 1 / -1;
    width: 100%;
  }

  .quality-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 580px) {
  .qualities-grid,
  .fabrics-grid,
  .related-grid {
    grid-template-columns: 1fr;
  }

  .section-head h2 {
    font-size: 20px;
  }

  .quality-toolbar-title h2 {
    font-size: 22px;
  }
}
</style>
