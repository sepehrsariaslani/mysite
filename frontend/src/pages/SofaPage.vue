<template>
  <div class="sofa-model-page" dir="rtl">
    <ProductHero
      :title="product.name || 'پیکربندی مبلمان'"
      description="ترکیب دلخواه خود را بسازید، رنگ چوب و پارچه را تنظیم کنید و یکجا به سبد اضافه کنید."
      :stats="heroStats"
    />

    <main class="content-scroll">
      <!-- Description Section -->
      <section class="description-section glass-card" v-if="product.description">
        <p class="description-text">{{ product.description }}</p>
      </section>

      <!-- Bundles Selection -->
      <div class="bundles-view" v-if="availableBundles.length">
        <div class="section-header">
          <h2 class="section-title">ست‌های پیشنهادی</h2>
          <span class="section-count">{{ availableBundles.length }} بسته آماده</span>
        </div>
        <div class="card-scroller custom-scrollbar">
          <div 
            v-for="bundle in availableBundles" 
            :key="bundle.name" 
            class="bundle-card product-card"
            @click="addBundleToStage(bundle)"
          >
            <div class="card-img-wrap">
              <img v-if="bundle.bundle_cover_photo" :src="bundle.bundle_cover_photo" :alt="bundle.sofa_bundle_display_name" class="card-img" />
              <div class="selection-indicator"><span>+</span></div>
            </div>
            <div class="card-info">
              <p class="card-title">{{ bundle.sofa_bundle_display_name || bundle.name }}</p>
              <p class="card-price">{{ bundle.bundle_formatted_price }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Modules Selection -->
      <div class="modules-view">
        <div class="section-header">
          <h2 class="section-title">انتخاب تکی اجزا</h2>
          <span class="section-count">{{ displayModules.length || 0 }} گزینه</span>
        </div>

        <div class="card-scroller custom-scrollbar">
          <div 
            v-for="mod in displayModules" 
            :key="mod.sofa_module_name" 
            class="product-card"
            @click="addModuleToStage(mod)"
          >
            <div class="card-img-wrap">
              <img v-if="getCoverImage(mod)" :src="getCoverImage(mod)" :alt="mod.sofa_module_name" class="card-img" />
              <div v-else class="card-img-placeholder"></div>
              <div class="selection-indicator">
                <span>+</span>
              </div>
            </div>
            <div class="card-info">
              <p class="card-title">{{ mod.sofa_module_name }}</p>
              <p class="card-price">{{ getModulePrice(mod) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Configuration Section -->
      <section class="config-section" v-if="stagedGroups.length > 0">
        <div class="section-header">
          <h2 class="section-title">پیکربندی انتخاب‌های شما</h2>
          <button class="clear-all" @click="stagedGroups = []">پاکسازی لیست</button>
        </div>

        <div class="staged-groups">
          <div v-for="(group, gIdx) in stagedGroups" :key="group.id" class="staged-group-box glass-card">
            <!-- Group Header (Bundle name or "Single Item") -->
            <div class="group-header">
              <div class="group-title-row">
                <span class="bundle-badge" v-if="group.isBundle">بسته</span>
                <span class="single-badge" v-else>جزء تکی</span>
                <h3>{{ group.name }}</h3>
                <button class="remove-group" @click="removeGroup(gIdx)">حذف این مورد</button>
              </div>
              
              <!-- Bulk Actions for Group -->
              <div class="bulk-config-bar" v-if="group.isBundle">
                <span class="bulk-label">تنظیم همگانی بسته:</span>
                <div class="bulk-actions">
                  <!-- Wood Bulk -->
                  <div class="bulk-select-wrap" v-if="group.commonWoodOptions.length > 1">
                    <select v-model="group.globalWood" @change="applyWoodToGroup(group)">
                      <option :value="null" disabled>رنگ چوب...</option>
                      <option v-for="w in group.commonWoodOptions" :key="w" :value="w">{{ w }}</option>
                    </select>
                  </div>
                  <!-- Fabric Bulk -->
                  <button v-if="group.items.some(i => i.odd_cloth)" class="bulk-fabric-btn" @click="openFabricForGroup(gIdx)">
                    {{ group.globalFabric ? group.globalFabric.colorName : 'انتخاب پارچه برای کل ست' }}
                  </button>
                </div>
              </div>
            </div>

            <div class="group-items">
              <div v-for="(item, iIdx) in group.items" :key="item.id" class="staged-item">
                <div class="item-inner">
                  <div class="item-visual">
                    <img :src="item.image" class="item-thumb" />
                  </div>

                  <div class="item-details">
                    <div class="item-top">
                      <div class="item-title-wrap">
                        <span class="module-name">{{ item.module_name }}</span>
                        <!-- Feature / Variant Selector -->
                        <div class="variant-picker" v-if="item.raw_mod.sofa_module_items.length > 1">
                          <select v-model="item.selectedItem" @change="syncItemDetails(item)">
                            <option v-for="v in item.raw_mod.sofa_module_items" :key="v.item_code" :value="v">
                              {{ v.module_feature || 'مدل پایه' }}
                            </option>
                          </select>
                        </div>
                      </div>
                      <span class="item-price">{{ fmtToman(calculateItemPrice(item)) }} تومان</span>
                    </div>

                    <div class="item-controls">
                      <!-- Wood -->
                      <div class="config-mini-row" v-if="item.all_wood_colors.length > 1">
                        <span class="mini-label">رنگ چوب:</span>
                        <div class="wood-pills">
                          <button v-for="w in item.all_wood_colors" :key="w" 
                            class="wood-pill" :class="{ active: item.selectedWood === w }"
                            @click="item.selectedWood = w">
                            {{ w }}
                          </button>
                        </div>
                      </div>

                      <!-- Fabric -->
                      <div class="config-mini-row" v-if="item.odd_cloth">
                        <span class="mini-label">انتخاب پارچه:</span>
                        <button class="fabric-trigger-mini" @click="openFabricForItem(gIdx, iIdx)">
                          <div class="fab-preview" v-if="item.selectedFabric">
                            <span class="dot" :style="{ background: item.selectedFabric.colorCode }"></span>
                            <span class="fab-name">{{ item.selectedFabric.colorName }} - {{ item.selectedFabric.qualityName }}</span>
                          </div>
                          <span v-else class="fab-placeholder">کلیک جهت انتخاب پارچه...</span>
                          <svg viewBox="0 0 20 20" fill="currentColor" width="14"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="empty-config" v-else>
        <div class="empty-icon">🛋️</div>
        <p>برای شروع طراحی مجموعه خود، از لیست بالا مبل‌ها یا ست‌های آماده را انتخاب کنید.</p>
      </div>
    </main>

    <!-- Global Config Action Bar -->
    <transition name="slide-up">
      <div class="action-bar" v-if="stagedGroups.length > 0">
        <div class="bar-content">
          <div class="price-summary">
            <span class="total-label">مبلغ قابل پرداخت کل:</span>
            <div class="total-value-wrap">
              <span class="total-value">{{ fmtToman(totalConfigPrice) }}</span>
              <span class="currency">تومان</span>
            </div>
          </div>
          <button class="add-all-btn" @click="addAllToCart" :disabled="!allConfigured">
            <span>{{ allConfigured ? 'افزودن به سبد خرید' : 'پیکربندی پارچه ناتمام است' }}</span>
            <svg v-if="allConfigured" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="20"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    </transition>

    <div class="fabric-overlay-bg" :class="{ active: fabricPickerOpen }" @click="fabricPickerOpen = false"></div>
    <FabricSidebar
      :open="fabricPickerOpen"
      :cloth-groups="clothGroups"
      @close="fabricPickerOpen = false"
      @select="onFabricSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCart } from '../stores/cartStore'
import FabricSidebar from '../components/FabricSidebar.vue'
import ProductHero from '../components/ProductHero.vue'


const product = ref(window.ProductDetails || { sofa_modules: [], sofa_bundles: [] })
const clothGroups = ref(window.ClothGroups || [])
const stagedGroups = ref([]) // Groups of items (Bundles or individual)
const fabricPickerOpen = ref(false)
const activeContext = ref({ gIdx: -1, iIdx: -1, forGroup: false })

const { addToCart, isCartOpen } = useCart()

const moduleTypeKeywords = ['مبل', 'باکس', 'نیمکت', 'پاف', 'میز جلومبلی', 'میز عسلی', 'کوسن', 'تشکچه']

const includesAnyKeyword = (text, keywords) => {
  const source = String(text || '')
  return keywords.some((kw) => source.includes(kw))
}

const moduleLooksLikeFurniture = (mod) => {
  const type = String(mod?.sofa_module_type || '')
  const moduleName = String(mod?.sofa_module_name || '')
  const fromItem = mod?.sofa_module_items?.some((it) =>
    includesAnyKeyword(it?.variant_of, moduleTypeKeywords)
  )
  return (
    includesAnyKeyword(type, moduleTypeKeywords) ||
    includesAnyKeyword(moduleName, moduleTypeKeywords) ||
    fromItem
  )
}

const displayModules = computed(() => {
  return (product.value.sofa_modules || []).filter((mod) => {
    if (!mod?.sofa_module_items?.length) return false
    return moduleLooksLikeFurniture(mod)
  })
})

const bundleUnitCount = (bundle) => {
  return (bundle?.sofa_bundle_table_items || []).reduce((sum, row) => {
    const qty = Number(row?.qty || 1)
    return sum + (Number.isFinite(qty) ? qty : 1)
  }, 0)
}

const availableBundles = computed(() => {
  return (product.value.sofa_bundles || []).filter((bundle) => bundleUnitCount(bundle) > 1)
})

const heroStats = computed(() => [
  { label: 'ماژول', value: displayModules.value.length },
  { label: 'بسته آماده', value: availableBundles.value.length },
  { label: 'گروه پارچه', value: clothGroups.value.length },
])

// ADD LOGIC
const addModuleToStage = (mod) => {
  const gId = Date.now()
  stagedGroups.value.unshift({
    id: gId,
    isBundle: false,
    name: mod.sofa_module_name,
    items: [createStagedItem(mod)]
  })
}

const addBundleToStage = (bundle) => {
  const gId = Date.now()
  const items = []
  const woodOptions = new Set()

  if (bundle.sofa_bundle_table_items) {
    bundle.sofa_bundle_table_items.forEach(bItem => {
      const mod = displayModules.value.find(m => m.sofa_module_name === bItem.module_name)
      if (mod) {
        for (let i = 0; i < (bItem.qty || 1); i++) {
          const sItem = createStagedItem(mod)
          items.push(sItem)
          sItem.all_wood_colors.forEach(w => woodOptions.add(w))
        }
      }
    })
  }

  stagedGroups.value.unshift({
    id: gId,
    isBundle: true,
    name: bundle.sofa_bundle_display_name || bundle.name,
    items: items,
    globalWood: null,
    globalFabric: null,
    commonWoodOptions: Array.from(woodOptions)
  })
}

const createStagedItem = (mod) => {
  const firstItem = mod.sofa_module_items?.[0]
  return {
    id: Math.random().toString(36).substr(2, 9),
    module_name: mod.sofa_module_name,
    raw_mod: mod,
    selectedItem: firstItem,
    image: getCoverImage(mod),
    odd_cloth: mod.sofa_odd_cloth || 0,
    all_wood_colors: firstItem?.all_wood_colors || [],
    selectedWood: firstItem?.all_wood_colors?.[0] || null,
    selectedFabric: null
  }
}

const removeGroup = (idx) => stagedGroups.value.splice(idx, 1)

// HELPER SYNC
const syncItemDetails = (item) => {
  item.image = item.selectedItem.image || getCoverImage(item.raw_mod)
  item.all_wood_colors = item.selectedItem.all_wood_colors || []
  if (!item.all_wood_colors.includes(item.selectedWood)) {
    item.selectedWood = item.all_wood_colors[0] || null
  }
}

const applyWoodToGroup = (group) => {
  if (!group.globalWood) return
  group.items.forEach(item => {
    if (item.all_wood_colors.includes(group.globalWood)) {
      item.selectedWood = group.globalWood
    }
  })
}

// FABRIC LOGIC
const openFabricForItem = (gIdx, iIdx) => {
  activeContext.value = { gIdx, iIdx, forGroup: false }
  fabricPickerOpen.value = true
}

const openFabricForGroup = (gIdx) => {
  activeContext.value = { gIdx, iIdx: -1, forGroup: true }
  fabricPickerOpen.value = true
}

const onFabricSelect = (fabric) => {
  const { gIdx, iIdx, forGroup } = activeContext.value
  if (gIdx === -1) return

  const group = stagedGroups.value[gIdx]
  if (forGroup) {
    group.globalFabric = fabric
    group.items.forEach(item => {
      if (item.odd_cloth) item.selectedFabric = fabric
    })
  } else {
    group.items[iIdx].selectedFabric = fabric
  }
  fabricPickerOpen.value = false
}

// PRICE CALC
const calculateItemPrice = (item) => {
  let total = item.selectedItem?.Price || 0
  if (item.selectedFabric && item.odd_cloth) {
    total += Math.ceil((item.odd_cloth * item.selectedFabric.pricePerMeter) / 10) * 10
  }
  return total
}

const totalConfigPrice = computed(() => {
  let total = 0
  stagedGroups.value.forEach(g => {
    g.items.forEach(i => total += calculateItemPrice(i))
  })
  return total
})

const allConfigured = computed(() => {
  return stagedGroups.value.every(g => 
    g.items.every(i => i.selectedFabric || !i.odd_cloth)
  )
})

const addAllToCart = () => {
  stagedGroups.value.forEach(g => {
    g.items.forEach(m => {
      const itemToCart = {
        name: m.selectedItem.item_name,
        item_code: m.selectedItem.item_code,
        type: 'sofa-unit',
        totalPrice: calculateItemPrice(m),
        image: m.image
      }
      const config = {
        qty: 1,
        image: m.image,
        attributes: {
          'رنگ چوب': m.selectedWood,
          'پارچه': m.selectedFabric ? `${m.selectedFabric.qualityName} - ${m.selectedFabric.colorName}` : null,
          'ویژگی': m.selectedItem.module_feature || 'پایه'
        }
      }
      addToCart(itemToCart, config)
    })
  })
  isCartOpen.value = true
  stagedGroups.value = []
}

// UI HELPERS
const getCoverImage = (mod) => {
  if (mod.sofa_module_images?.length) {
    const cover = mod.sofa_module_images.find(img => img.cover) || mod.sofa_module_images[0]
    return cover.file_url
  }
  return mod.sofa_module_items?.[0]?.image || ''
}

const getModulePrice = (mod) => {
  if (!mod.sofa_module_items?.length) return 'تماس بگیرید'
  const prices = mod.sofa_module_items.map(i => i.Price || 0)
  return fmtToman(Math.max(...prices))
}

const fmtToman = (val) => {
  if (!val) return '۰'
  return Math.round(val).toLocaleString('fa-IR')
}
</script>

<style scoped>
.sofa-model-page {
  background: var(--bg-main);
  min-height: 100vh;
  padding-bottom: 160px;
  color: var(--text-main);
  position: relative;
  overflow-x: hidden;
}

.content-scroll {
  max-width: 1400px;
  margin: 0 auto;
  padding: 18px 20px 0;
}

/* Description */
.description-section {
  margin: 0 0 32px;
  padding: 30px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 30px;
  position: relative;
  z-index: 2;
}

.description-text {
  line-height: 1.8;
  color: var(--text-muted);
  font-size: 1.1rem;
  font-weight: 500;
}

.section-header {
  padding: 0 24px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-main);
}

.section-count {
  font-size: 0.92rem;
  color: var(--text-dim);
  font-weight: 700;
}

.card-scroller {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 0 24px 6px;
  scrollbar-width: none;
}

.card-scroller::-webkit-scrollbar {
  display: none;
}

.product-card {
  flex: 0 0 240px;
  background: var(--glass-bg);
  backdrop-filter: blur(15px);
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.product-card:hover {
  transform: translateY(-8px);
  background: var(--glass-bg-hover);
  border-color: var(--accent-gold);
}

.card-img-wrap {
  position: relative;
  width: 100%;
  height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px 14px;
}

.card-img-placeholder {
  width: 100%;
  height: 100%;
  background: color-mix(in srgb, var(--bg-secondary) 80%, #ffffff 20%);
}

.selection-indicator { position: absolute; top: 15px; left: 15px; width: 40px; height: 40px; background: var(--accent-brown); backdrop-filter: blur(5px); color: var(--accent-gold); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 800; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }

.card-info { padding: 20px; }
.card-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 6px; }
.card-price { font-size: 1rem; color: var(--accent-orange); font-weight: 800; }

.config-section { margin-top: 50px; }
.staged-groups { padding: 0 20px; display: flex; flex-direction: column; gap: 40px; }
.staged-group-box {
  background: var(--bg-secondary);
  backdrop-filter: blur(30px);
  border: 1px solid var(--glass-border);
  border-radius: 40px;
  padding: 30px;
}

.group-header { margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid rgba(80, 49, 48, 0.08); }
.group-title-row { display: flex; align-items: center; gap: 15px; margin-bottom: 2rem; }
.bundle-badge, .single-badge { font-size: 0.75rem; font-weight: 900; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; letter-spacing: 1px; }
.bundle-badge { background: var(--accent-gold); color: var(--accent-brown); }
.single-badge { background: var(--accent-brown); color: var(--accent-gold); }

.remove-group { margin-right: auto; background: rgba(165, 97, 87, 0.1); color: #a56157; border: none; padding: 10px 20px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s; }
.remove-group:hover { background: #a56157; color: white; }

.bulk-config-bar { display: flex; align-items: center; gap: 24px; background: var(--glass-bg); padding: 16px 24px; border-radius: 24px; border: 1px dashed var(--glass-border); }
.bulk-label { font-size: 0.9rem; font-weight: 900; color: var(--text-main); white-space: nowrap; }
.bulk-actions { display: flex; gap: 16px; flex-wrap: wrap; }

.bulk-select-wrap select { background: var(--bg-main); border: 1px solid var(--glass-border); padding: 10px 20px; border-radius: 14px; font-weight: 700; color: var(--text-main); cursor: pointer; }
.bulk-fabric-btn { background: var(--accent-brown); color: var(--accent-gold); border: none; padding: 10px 24px; border-radius: 14px; font-weight: 700; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }

/* Staged Item */
.group-items { display: flex; flex-direction: column; gap: 2rem; }
.staged-item { border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 2rem; }
.staged-item:last-child { border: none; padding-bottom: 0; }

.item-inner { display: flex; gap: 32px; }
.item-thumb { width: 140px; height: 140px; border-radius: 28px; object-fit: cover; background: var(--bg-main); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }

.item-details { flex: 1; display: flex; flex-direction: column; gap: 1rem; }
.item-top { display: flex; justify-content: space-between; align-items: flex-start; }
.item-title-wrap { display: flex; flex-direction: column; gap: 8px; }
.module-name { font-size: 1.3rem; font-weight: 900; color: var(--text-main); }

.variant-picker select { background: var(--glass-bg); border: 1px solid var(--glass-border); padding: 6px 14px; border-radius: 12px; font-weight: 800; color: var(--text-main); font-size: 0.85rem; cursor: pointer; }

.item-price { font-size: 1.2rem; font-weight: 950; color: var(--accent-orange); }

.item-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.config-mini-row { display: flex; flex-direction: column; gap: 10px; }
.mini-label { font-size: 0.8rem; font-weight: 900; color: #888; text-transform: uppercase; letter-spacing: 1px; }

.wood-pills { display: flex; flex-wrap: wrap; gap: 8px; }
.wood-pill { padding: 8px 18px; border-radius: 12px; border: 1px solid var(--glass-border); background: var(--bg-main); color: var(--text-main); font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }
.wood-pill.active { background: var(--accent-brown); color: var(--accent-gold); border-color: var(--accent-brown); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }

.fabric-trigger-mini { background: var(--glass-bg); border: 1px solid var(--glass-border); padding: 12px 20px; border-radius: 16px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.3s; }
.fabric-trigger-mini:hover { border-color: #f2c97e; background: #fff; }

.fab-preview { display: flex; align-items: center; gap: 12px; }
.dot { width: 18px; height: 18px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.fab-name { font-weight: 800; color: var(--text-main); font-size: 0.9rem; }
.fab-placeholder { font-weight: 700; color: #aaa; font-size: 0.85rem; }

.clear-all {
  background: rgba(165, 97, 87, 0.12);
  border: 1px solid rgba(165, 97, 87, 0.28);
  color: #a56157;
  padding: 9px 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.empty-config {
  margin: 24px;
  padding: 30px 18px;
  border: 1px dashed var(--glass-border);
  border-radius: 24px;
  text-align: center;
  color: var(--text-dim);
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

/* Action Bar */
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 24px 20px calc(24px + env(safe-area-inset-bottom));
}

.bar-content {
  background: var(--bg-secondary);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: 40px;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.6);
}

.total-value { font-size: 2rem; font-weight: 900; color: var(--text-main); }

.add-all-btn {
  background: var(--accent-brown);
  color: var(--accent-gold);
  border: none;
  padding: 18px 32px;
  border-radius: 20px;
  font-weight: 800;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.6s; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); opacity: 0; }

.fabric-overlay-bg {
  position: fixed;
  inset: 0;
  z-index: 99990;
  background: rgba(0, 0, 0, 0.56);
  backdrop-filter: blur(6px);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s;
}

.fabric-overlay-bg.active {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 900px) {
  .bar-content { flex-direction: column; gap: 1.5rem; text-align: center; }
  .add-all-btn { width: 100%; }
}

@media (max-width: 600px) {
  .content-scroll { padding: 12px 12px 0; }
  .description-section { padding: 22px; border-radius: 24px; }
  .section-header { padding: 0 12px; }
  .card-scroller { padding: 0 12px 4px; gap: 10px; }
  .product-card { flex-basis: 190px; border-radius: 22px; }
  .card-img-wrap { height: 170px; }
  .staged-group-box { padding: 1.5rem; }
  .item-inner { flex-direction: column; gap: 20px; }
  .item-thumb { width: 100%; height: 200px; }
  .bulk-config-bar { flex-direction: column; align-items: stretch; }
}
</style>
