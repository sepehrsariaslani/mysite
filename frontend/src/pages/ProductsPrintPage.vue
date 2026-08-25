<template>
  <div class="print-page" dir="rtl">
    <header class="toolbar no-print">
      <div class="toolbar-copy">
        <h1>کاتالوگ چاپی محصولات</h1>
        <p>
          طراحی کارت‌ها هماهنگ با صفحات محصول
          <span v-if="selectedPriceList">| لیست قیمت: {{ selectedPriceList }}</span>
        </p>
      </div>

      <div class="toolbar-actions">
        <label class="price-list-picker">
          <span>لیست قیمت</span>
          <select v-model="activePriceList">
            <option value="">پیش‌فرض</option>
            <option v-for="pl in availablePriceLists" :key="pl" :value="pl">{{ pl }}</option>
          </select>
        </label>
        <button class="ghost-btn" :disabled="!canApplyPriceList" @click="applyPriceList">اعمال لیست</button>
        <button class="ghost-btn" @click="fabricOpen = true">انتخاب پارچه</button>
        <div class="selected-fabric" v-if="selectedFabric">
          <span class="fabric-name">{{ selectedFabric.qualityName }} - {{ selectedFabric.colorName }}</span>
        </div>
        <button class="print-btn" @click="startPrint">پرینت</button>
      </div>
    </header>

    <main class="catalog-main">
      <section
        v-for="section in visibleSections"
        :key="section.id"
        class="category-section"
        :class="`section-${layoutForSection(section.id)}`"
      >
        <div class="section-head">
          <h2>{{ section.title }}</h2>
          <span>{{ section.items?.length || 0 }} محصول</span>
        </div>

        <article
          v-for="item in section.items"
          :key="item.key"
          class="product-card"
          :class="[`layout-${layoutForSection(section.id)}`, `kind-${item.kind || 'standard'}`]"
        >
          <template v-if="layoutForSection(section.id) === 'chair'">
            <div class="card-chair-body">
              <div class="card-chair-image">
                <img v-if="item.image" :src="item.image" :alt="item.name" loading="lazy" />
                <div v-else class="image-empty">بدون تصویر</div>
              </div>
              <div class="card-chair-content">
                <h3>{{ item.name }}</h3>
                <div class="meta-row">
                  <span class="kind-chip">{{ kindLabel(item.kind) }}</span>
                  <span v-if="dimensionsText(item)" class="meta-chip">{{ dimensionsText(item) }}</span>
                  <span v-if="itemClothMeters(item) > 0" class="meta-chip">پارچه: {{ formatMeters(itemClothMeters(item)) }} متر</span>
                </div>
                <div class="chair-price-table" v-if="item.priceRows?.length">
                  <div class="chair-price-head">
                    <span>با پارچه</span>
                    <span>زیرکار</span>
                    <span>گزینه</span>
                  </div>
                  <div v-for="row in item.priceRows" :key="`${item.key}-${row.label}`" class="chair-price-line">
                    <span class="with-fabric">{{ renderPrice(finalRowPrice(row)) }}</span>
                    <span class="underwork">{{ renderPrice(row.basePriceToman) }}</span>
                    <span class="row-label">{{ row.label || 'مدل پایه' }}</span>
                  </div>
                </div>
                <p v-else class="empty-price">قیمت ثبت نشده است</p>
              </div>
            </div>
          </template>

          <template v-else-if="layoutForSection(section.id) === 'table'">
            <div class="card-table-image-wrap">
              <img v-if="item.image" :src="item.image" :alt="item.name" loading="lazy" />
              <div v-else class="image-empty">بدون تصویر</div>
            </div>
            <div class="card-table-meta">
              <h3>{{ item.name }}</h3>
              <div class="meta-row">
                <span class="kind-chip">{{ kindLabel(item.kind) }}</span>
                <span v-if="dimensionsText(item)" class="meta-chip">{{ dimensionsText(item) }}</span>
                <span v-if="itemClothMeters(item) > 0" class="meta-chip">پارچه: {{ formatMeters(itemClothMeters(item)) }} متر</span>
              </div>
            </div>
            <div class="price-list compact">
              <div v-if="item.priceRows?.length" v-for="row in item.priceRows" :key="`${item.key}-${row.label}`" class="price-row">
                <span class="row-label">{{ row.label || 'مدل پایه' }}</span>
                <div class="dual-prices">
                  <span class="underwork">زیرکار: {{ renderPrice(row.basePriceToman) }}</span>
                  <span class="with-fabric">با پارچه: {{ renderPrice(finalRowPrice(row)) }}</span>
                </div>
              </div>
              <p v-else class="empty-price">قیمت ثبت نشده است</p>
            </div>
          </template>

          <template v-else-if="layoutForSection(section.id) === 'sofa'">
            <div class="card-sofa-image-wrap">
              <img v-if="item.image" :src="item.image" :alt="item.name" loading="lazy" />
              <div v-else class="image-empty">بدون تصویر</div>
            </div>
            <div class="card-sofa-meta">
              <h3>{{ item.name }}</h3>
              <div class="meta-row">
                <span class="kind-chip">{{ kindLabel(item.kind) }}</span>
                <span v-if="dimensionsText(item)" class="meta-chip">{{ dimensionsText(item) }}</span>
                <span v-if="itemClothMeters(item) > 0" class="meta-chip">پارچه: {{ formatMeters(itemClothMeters(item)) }} متر</span>
              </div>
            </div>
            <div class="price-list">
              <div v-if="item.priceRows?.length" v-for="row in item.priceRows" :key="`${item.key}-${row.label}`" class="price-row sofa-row">
                <span class="row-label">{{ row.label || 'مدل پایه' }}</span>
                <div class="dual-prices">
                  <span class="underwork">زیرکار: {{ renderPrice(row.basePriceToman) }}</span>
                  <span class="with-fabric">با پارچه: {{ renderPrice(finalRowPrice(row)) }}</span>
                </div>
                <span class="cloth-meter" v-if="toNumber(row.clothMeters) > 0">پارچه: {{ formatMeters(row.clothMeters) }} متر</span>
              </div>
              <p v-else class="empty-price">قیمت ثبت نشده است</p>
            </div>
          </template>

          <template v-else-if="layoutForSection(section.id) === 'cushion'">
            <div class="card-cushion-wrap">
              <div class="card-cushion-image">
                <img v-if="item.image" :src="item.image" :alt="item.name" loading="lazy" />
                <div v-else class="image-empty">بدون تصویر</div>
              </div>
              <div class="card-cushion-body">
                <h3>{{ item.name }}</h3>
                <div class="meta-row">
                  <span class="kind-chip">{{ kindLabel(item.kind) }}</span>
                  <span v-if="dimensionsText(item)" class="meta-chip">{{ dimensionsText(item) }}</span>
                </div>
                <div class="price-list cushion-list">
                  <div v-if="item.priceRows?.length" v-for="row in item.priceRows" :key="`${item.key}-${row.label}`" class="price-row cushion-row">
                    <span class="row-label">{{ row.label || 'بسته' }}</span>
                    <div class="dual-prices">
                      <span class="underwork">زیرکار: {{ renderPrice(row.basePriceToman) }}</span>
                      <span class="with-fabric">با پارچه: {{ renderPrice(finalRowPrice(row)) }}</span>
                    </div>
                  </div>
                  <p v-else class="empty-price">قیمت ثبت نشده است</p>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="card-bed-wrap">
              <div class="card-bed-image">
                <img v-if="item.image" :src="item.image" :alt="item.name" loading="lazy" />
                <div v-else class="image-empty">بدون تصویر</div>
              </div>
              <div class="card-bed-content">
                <h3>{{ item.name }}</h3>
                <div class="meta-row">
                  <span class="kind-chip">{{ kindLabel(item.kind) }}</span>
                  <span v-if="dimensionsText(item)" class="meta-chip">{{ dimensionsText(item) }}</span>
                </div>
                <div class="price-list">
                  <div v-if="item.priceRows?.length" v-for="row in item.priceRows" :key="`${item.key}-${row.label}`" class="price-row">
                    <span class="row-label">{{ row.label || 'مدل پایه' }}</span>
                    <div class="dual-prices">
                      <span class="underwork">زیرکار: {{ renderPrice(row.basePriceToman) }}</span>
                      <span class="with-fabric">با پارچه: {{ renderPrice(finalRowPrice(row)) }}</span>
                    </div>
                  </div>
                  <p v-else class="empty-price">قیمت ثبت نشده است</p>
                </div>
              </div>
            </div>
          </template>
        </article>
      </section>

      <div v-if="!visibleSections.length" class="empty-page">
        <p>داده‌ای برای نمایش وجود ندارد.</p>
      </div>
    </main>

    <div class="fabric-overlay-bg no-print" :class="{ active: fabricOpen }" @click="fabricOpen = false"></div>
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
import { computed, ref } from 'vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import { useFabricStore } from '../stores/fabricStore'
import { calculateFabricPrice, calculatePriceWithFabric, toNumber } from '../utils/fabricPricing'

const sections = ref(window.PrintCatalogSections || [])
const clothGroups = ref(window.ClothGroups || [])
const selectedPriceList = ref(window.SelectedPriceList || '')

const fabricOpen = ref(false)
const { selectedFabric, setSelectedFabric } = useFabricStore()

const kindMap = {
  module: 'ماژول',
  bundle: 'بسته',
  standard: 'محصول',
}

const visibleSections = computed(() => (sections.value || []).filter((section) => (section.items || []).length > 0))

function layoutForSection(sectionId) {
  if (sectionId === 'sofas') return 'sofa'
  if (sectionId === 'dining-chairs' || sectionId === 'barstools') return 'chair'
  if (sectionId === 'benches') return 'sofa'
  if (sectionId === 'tables' || sectionId === 'coffee-tables') return 'table'
  if (sectionId === 'cushions') return 'cushion'
  if (sectionId === 'beds') return 'bed'
  return 'table'
}

function kindLabel(kind) {
  return kindMap[kind] || 'محصول'
}

function formatToman(value) {
  return Math.round(toNumber(value || 0)).toLocaleString('fa-IR')
}

function renderPrice(value) {
  const n = toNumber(value || 0)
  if (n <= 0) return 'تماس بگیرید'
  return formatToman(n)
}

function formatMeters(value) {
  const n = toNumber(value || 0)
  if (!n) return '0'
  if (Number.isInteger(n)) return String(n)
  return n.toLocaleString('fa-IR', { maximumFractionDigits: 2 })
}

function dimensionsText(item) {
  const d = item?.dimensions || {}
  const parts = []
  if (d.size) parts.push(`سایز: ${d.size}`)
  if (d.length) parts.push(`طول: ${d.length}`)
  if (d.width) parts.push(`عرض: ${d.width}`)
  if (d.height) parts.push(`ارتفاع: ${d.height}`)
  if (d.shape) parts.push(`شکل: ${d.shape}`)
  if (d.diameter) parts.push(`قطر: ${d.diameter}`)
  return parts.join(' | ')
}

function itemClothMeters(item) {
  if (!item?.priceRows?.length) return 0
  return item.priceRows.reduce((max, row) => Math.max(max, toNumber(row?.clothMeters || 0)), 0)
}

function finalRowPrice(row) {
  const base = Math.max(0, toNumber(row?.basePriceToman || 0))
  if (!base) return 0
  if (!selectedFabric.value) return base
  const meters = Math.max(0, toNumber(row?.clothMeters || 0))
  if (!meters) return base
  const fabricPrice = calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
  return calculatePriceWithFabric(base, fabricPrice)
}

function onFabricSelect(fabric) {
  setSelectedFabric(fabric)
  fabricOpen.value = false
}

const availablePriceLists = ref(window.AvailablePriceLists || [])
const activePriceList = ref(selectedPriceList.value || '')

const canApplyPriceList = computed(() => {
  return (activePriceList.value || '') !== (selectedPriceList.value || '')
})

function applyPriceList() {
  const url = new URL(window.location.href)
  if (activePriceList.value) url.searchParams.set('price_list', activePriceList.value)
  else url.searchParams.delete('price_list')
  window.location.href = url.toString()
}

function startPrint() {
  window.print()
}
</script>

<style scoped>
.print-page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  font-family: 'Peyda', sans-serif;
}

.toolbar {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--bg-main) 94%, #fff 6%);
  backdrop-filter: blur(10px);
}

.toolbar-copy h1 {
  margin: 0;
  font-size: 25px;
  font-weight: 900;
}

.toolbar-copy p {
  margin: 4px 0 0;
  color: var(--text-dim);
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.ghost-btn,
.print-btn {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.ghost-btn:disabled {
  opacity: 0.45;
  cursor: default;
}

.price-list-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 6px 10px;
  background: var(--glass-bg);
}

.price-list-picker span {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

.price-list-picker select {
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-main);
  font-family: inherit;
  font-size: 12px;
  padding: 6px 8px;
  min-width: 180px;
}

.print-btn {
  background: var(--accent-brown);
  color: var(--accent-gold);
  border-color: var(--accent-brown);
}

.selected-fabric {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 8px 12px;
}

.fabric-name {
  font-size: 12px;
  font-weight: 700;
}

.catalog-main {
  max-width: 1240px;
  margin: 0 auto;
  padding: 20px 16px 52px;
}

.category-section {
  margin-bottom: 34px;
  break-inside: avoid-page;
  page-break-inside: avoid;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  border-bottom: 2px solid var(--glass-border);
  padding-bottom: 10px;
}

.section-head h2 {
  margin: 0;
  font-size: 25px;
  font-weight: 900;
}

.section-head span {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 800;
}

.product-card {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  margin: 0 auto 14px;
  break-inside: avoid-page;
  page-break-inside: avoid;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.kind-chip,
.meta-chip {
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  color: var(--text-main);
}

.kind-chip {
  font-weight: 900;
  background: color-mix(in srgb, var(--accent-gold) 18%, #fff 82%);
}

.price-list {
  display: grid;
  gap: 8px;
}

.price-row {
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.68);
  padding: 10px;
  display: grid;
  gap: 5px;
}

.row-label {
  font-size: 13px;
  font-weight: 900;
  color: var(--text-main);
}

.dual-prices {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.underwork,
.with-fabric {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-main);
}

.with-fabric {
  color: var(--accent-orange);
}

.cloth-meter {
  font-size: 11px;
  color: var(--text-dim);
}

.empty-price,
.empty-page p {
  margin: 0;
  color: var(--text-dim);
  font-size: 13px;
}

.image-empty {
  color: var(--text-dim);
  font-size: 11px;
}

/* Chair-like cards (Dining chairs / Barstools) */
.layout-chair {
  border-radius: 24px;
  padding: 18px;
  width: min(980px, 100%);
}

.card-chair-body {
  display: flex;
  gap: 15px;
}

.card-chair-image {
  width: 180px;
  height: 220px;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-chair-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-chair-content {
  flex: 1;
}

.card-chair-content h3 {
  margin: 0 0 10px;
  font-size: 19px;
  font-weight: 900;
}

.chair-price-table {
  display: grid;
  gap: 6px;
}

.chair-price-head,
.chair-price-line {
  display: grid;
  grid-template-columns: 1fr 1fr 1.2fr;
  align-items: center;
  gap: 10px;
}

.chair-price-head {
  border-bottom: 1px dashed var(--glass-border);
  padding-bottom: 4px;
}

.chair-price-head span {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 800;
}

.chair-price-line {
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 10px;
}

/* Table-like cards (tables / coffee / benches) */
.layout-table {
  border-radius: 28px;
  padding: 20px;
  width: min(760px, 100%);
}

.card-table-image-wrap {
  width: 100%;
  height: 280px;
  border-radius: 18px;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.card-table-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-table-meta h3 {
  margin: 0 0 10px;
  font-size: 21px;
  font-weight: 900;
}

/* Sofa-like cards */
.layout-sofa {
  border-radius: 24px;
  padding: 14px;
  width: min(900px, 100%);
}

.card-sofa-image-wrap {
  height: 220px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.card-sofa-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-sofa-meta h3 {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 900;
}

.sofa-row {
  background: color-mix(in srgb, var(--accent-gold) 10%, #fff 90%);
}

/* Cushion-like cards */
.layout-cushion {
  border-radius: 22px;
  padding: 12px;
  width: min(860px, 100%);
}

.card-cushion-wrap {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 12px;
}

.card-cushion-image {
  height: 180px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-cushion-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-cushion-body h3 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 900;
}

.cushion-list .price-row {
  border-radius: 12px;
  background: #fff;
}

.cushion-row .row-label {
  color: var(--accent-brown);
}

/* Bed-like cards */
.layout-bed {
  border-radius: 24px;
  padding: 14px;
  width: min(900px, 100%);
}

.card-bed-wrap {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 12px;
}

.card-bed-image {
  height: 190px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-bed-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-bed-content h3 {
  margin: 0 0 10px;
  font-size: 21px;
  font-weight: 900;
}

.fabric-overlay-bg {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s;
}

.fabric-overlay-bg.active {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 980px) {
  .toolbar {
    position: static;
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .price-list-picker {
    width: 100%;
    justify-content: space-between;
  }

  .price-list-picker select {
    min-width: 0;
    width: 58%;
  }

  .card-chair-body,
  .card-cushion-wrap,
  .card-bed-wrap {
    display: grid;
    grid-template-columns: 1fr;
  }

  .card-chair-image,
  .card-cushion-image,
  .card-bed-image,
  .card-table-image-wrap {
    width: 100%;
    height: 220px;
  }

  .chair-price-head,
  .chair-price-line {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}

@media print {
  @page {
    size: A4;
    margin: 11mm;
  }

  :global(.app-header),
  :global(.mobile-bottom-nav),
  :global(.app-footer),
  :global(.cart-sidebar),
  :global(.fabric-sidebar),
  .no-print,
  .fabric-overlay-bg {
    display: none !important;
  }

  :global(body),
  .print-page {
    background: #fff !important;
    color: #000 !important;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }

  .catalog-main {
    max-width: none;
    margin: 0;
    padding: 0;
  }

  .category-section {
    margin-bottom: 7mm;
    break-inside: avoid-page;
    page-break-inside: avoid;
  }

  .section-head {
    margin-bottom: 3mm;
    break-after: avoid;
    page-break-after: avoid;
    border-bottom-color: #d5d5d5;
  }

  .section-head h2 {
    font-size: 18px;
  }

  .product-card {
    box-shadow: none !important;
    border-color: #d6d6d6 !important;
    background: #fff !important;
    margin-bottom: 3.5mm;
    break-inside: avoid-page;
    page-break-inside: avoid;
  }

  .layout-chair,
  .layout-table,
  .layout-sofa,
  .layout-cushion,
  .layout-bed {
    width: 100% !important;
    border-radius: 7px;
    padding: 3mm;
  }

  .card-chair-image,
  .card-cushion-image,
  .card-bed-image,
  .card-table-image-wrap,
  .card-sofa-image-wrap {
    height: 30mm;
  }

  .card-chair-body,
  .card-cushion-wrap,
  .card-bed-wrap {
    display: grid;
    grid-template-columns: 30mm 1fr;
    gap: 3mm;
  }

  .card-table-meta h3,
  .card-sofa-meta h3,
  .card-bed-content h3,
  .card-cushion-body h3,
  .card-chair-content h3 {
    font-size: 13px;
    margin-bottom: 2mm;
  }

  .price-list {
    gap: 2mm;
  }

  .price-row {
    padding: 2mm;
    border-radius: 4px;
    border-color: #d8d8d8;
    background: #fff !important;
  }

  .row-label,
  .underwork,
  .with-fabric,
  .cloth-meter,
  .meta-chip,
  .kind-chip {
    font-size: 10px;
  }
}
</style>
