<template>
  <div class="sofa-collection-page" dir="rtl">
    <header class="hero">
      <img v-if="product.images?.[0]" :src="product.images[0]" :alt="product.name" class="hero-image" />
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <Breadcrumbs :crumbs="breadcrumbs" light />
        <h1 class="hero-title">{{ product.name }}</h1>
        <p class="hero-subtitle">طراحی ترکیب نهایی با انتخاب ماژول، رنگ چوب و پارچه</p>
        <div class="hero-stats">
          <span class="stat-chip">{{ displayPrimaryModules.length }} ماژول اصلی</span>
          <span class="stat-chip">{{ displayAccessoryModules.length }} کوسن/تشکچه</span>
          <span class="stat-chip">{{ displayBundles.length }} بسته آماده</span>
          <span class="stat-chip">{{ clothGroups.length }} گروه پارچه</span>
        </div>
      </div>
    </header>

    <main class="workspace">
      <section class="library-panel">
        <div class="panel-head">
          <div>
            <h2>کتابخانه اجزا</h2>
            <p>از بسته آماده یا ماژول تکی انتخاب کن و به لیست نهایی اضافه کن.</p>
          </div>
          <div class="library-tabs">
            <button
              class="tab-btn"
              :class="{ active: libraryTab === 'modules' }"
              @click="libraryTab = 'modules'"
            >
              ماژول‌ها
            </button>
            <button
              class="tab-btn"
              :class="{ active: libraryTab === 'cushions' }"
              @click="libraryTab = 'cushions'"
            >
              کوسن‌ها
            </button>
            <button
              class="tab-btn"
              :class="{ active: libraryTab === 'bundles' }"
              @click="libraryTab = 'bundles'"
            >
              بسته‌ها
            </button>
          </div>
        </div>

        <div v-if="libraryTab === 'modules'" class="module-library-stack">
          <div class="module-section">
            <h3 class="module-section-title">ماژول‌های اصلی</h3>
            <div class="library-grid">
              <article
                v-for="mod in displayPrimaryModules"
                :key="mod.sofa_module_name"
                class="library-card"
              >
                <div class="library-card-image" @click="addModuleToStage(mod)">
                  <img v-if="getCoverImage(mod)" :src="getCoverImage(mod)" :alt="mod.sofa_module_name" class="thumb" />
                  <div v-else class="thumb-placeholder">بدون تصویر</div>
                </div>
                <div class="library-card-body">
                  <h3>{{ mod.sofa_module_name }}</h3>
                  <div class="spec-row">
                    <span v-if="hasMeaningfulValue(mod.sofa_length)">طول: {{ mod.sofa_length }}</span>
                    <span v-if="hasMeaningfulValue(mod.sofa_width)">عرض: {{ mod.sofa_width }}</span>
                    <span v-if="hasMeaningfulValue(mod.sofa_shape)">{{ mod.sofa_shape }}</span>
                  </div>
                  <p class="card-price">{{ getModulePrice(mod) }} تومان</p>
                  <div class="card-actions">
                    <button class="secondary-btn" @click="goToSofaUnit(mod)">جزئیات</button>
                    <button class="primary-btn" @click="addModuleToStage(mod)">افزودن</button>
                  </div>
                </div>
              </article>
            </div>
            <div v-if="!displayPrimaryModules.length" class="empty-library">ماژول اصلی برای نمایش وجود ندارد.</div>
          </div>
        </div>

        <div v-else-if="libraryTab === 'cushions'" class="module-library-stack">
          <div class="module-section">
            <h3 class="module-section-title">کوسن و تشکچه</h3>
            <div class="library-grid">
              <article
                v-for="mod in displayAccessoryModules"
                :key="`acc-${mod.sofa_module_name}`"
                class="library-card accessory-card"
              >
                <div class="library-card-image" @click="addModuleToStage(mod)">
                  <img v-if="getCoverImage(mod)" :src="getCoverImage(mod)" :alt="mod.sofa_module_name" class="thumb" />
                  <div v-else class="thumb-placeholder">بدون تصویر</div>
                </div>
                <div class="library-card-body">
                  <h3>{{ mod.sofa_module_name }}</h3>
                  <div class="spec-row">
                    <span v-if="hasMeaningfulValue(mod.sofa_length)">طول: {{ mod.sofa_length }}</span>
                    <span v-if="hasMeaningfulValue(mod.sofa_width)">عرض: {{ mod.sofa_width }}</span>
                    <span v-if="hasMeaningfulValue(mod.sofa_shape)">{{ mod.sofa_shape }}</span>
                  </div>
                  <p class="card-price">{{ getModulePrice(mod) }} تومان</p>
                  <div class="card-actions">
                    <button class="secondary-btn" @click="goToSofaUnit(mod)">جزئیات</button>
                    <button class="primary-btn" @click="addModuleToStage(mod)">افزودن</button>
                  </div>
                </div>
              </article>
            </div>
            <div v-if="!displayAccessoryModules.length" class="empty-library">کوسن یا تشکچه‌ای برای نمایش وجود ندارد.</div>
          </div>
        </div>

        <div v-else class="library-grid">
          <article
            v-for="bundle in displayBundles"
            :key="bundle.bundle_name || bundle.name"
            class="library-card"
          >
            <div class="library-card-image" @click="addBundleToStage(bundle)">
              <img v-if="bundle.bundle_cover_photo" :src="bundle.bundle_cover_photo" :alt="bundle.sofa_bundle_display_name" class="thumb" />
              <div v-else class="thumb-placeholder">بدون تصویر</div>
            </div>
            <div class="library-card-body">
              <h3>{{ bundle.sofa_bundle_display_name || bundle.name }}</h3>
              <div class="spec-row">
                <span>تعداد آیتم: {{ bundleUnitCount(bundle) }}</span>
                <span v-if="bundle.total_fabric">پارچه: {{ bundle.total_fabric }} متر</span>
              </div>
              <p class="card-price">{{ bundle.bundle_formatted_price }} تومان</p>
              <div class="card-actions">
                <button class="primary-btn" @click="addBundleToStage(bundle)">افزودن بسته</button>
              </div>
            </div>
          </article>
          <div v-if="!displayBundles.length" class="empty-library">بسته‌ای برای نمایش وجود ندارد.</div>
        </div>
      </section>

      <aside class="stage-panel">
        <div class="panel-head stage-head">
          <div>
            <h2>پیکربندی نهایی</h2>
            <p>همین‌جا همه انتخاب‌ها را کنترل و یکجا به سبد اضافه کن.</p>
          </div>
          <button class="secondary-btn" :disabled="!stagedGroups.length" @click="stagedGroups = []">پاکسازی</button>
        </div>

        <div v-if="!stagedGroups.length" class="empty-stage">
          <strong>هنوز چیزی انتخاب نشده</strong>
          <span>از ستون سمت چپ یک ماژول یا بسته انتخاب کن.</span>
        </div>

        <div v-else class="stage-groups">
          <section v-for="(group, gIdx) in stagedGroups" :key="group.id" class="group-card">
            <div class="group-header">
              <div class="group-title-wrap">
                <span class="group-tag" :class="group.isBundle ? 'bundle' : 'single'">
                  {{ group.isBundle ? 'بسته' : 'تکی' }}
                </span>
                <h3>{{ group.name }}</h3>
              </div>
              <button class="danger-btn" @click="removeGroup(gIdx)">حذف</button>
            </div>

            <div class="group-bulk" v-if="group.isBundle">
              <div class="bulk-control" v-if="getGroupWoodOptions(group).length > 1">
                <label>رنگ چوب همگانی</label>
                <select v-model="group.globalWood" @change="applyWoodToGroup(group)">
                  <option value="" disabled>انتخاب رنگ چوب</option>
                  <option v-for="w in getGroupWoodOptions(group)" :key="w" :value="w">{{ w }}</option>
                </select>
              </div>
              <button
                v-if="group.items.some(i => i.odd_cloth)"
                class="secondary-btn"
                @click="openFabricForGroup(gIdx, 'main')"
              >
                {{
                  group.globalMainFabric
                    ? `پارچه اصلی ست: ${group.globalMainFabric.colorName}`
                    : 'پارچه اصلی یکسان برای کل بسته'
                }}
              </button>
              <button
                v-if="group.items.some(i => i.minor_cloth)"
                class="secondary-btn"
                @click="openFabricForGroup(gIdx, 'minor')"
              >
                {{
                  group.globalMinorFabric
                    ? `پارچه جزیی ست: ${group.globalMinorFabric.colorName}`
                    : 'پارچه جزیی یکسان برای کل بسته'
                }}
              </button>
            </div>

            <div class="group-items">
              <article v-for="(item, iIdx) in group.items" :key="item.id" class="stage-item">
                <img :src="item.image" class="stage-thumb" :alt="item.module_name" />
                <div class="stage-item-main">
                  <div class="stage-item-top">
                    <strong>{{ item.module_name }}</strong>
                    <span class="item-price">{{ fmtToman(calculateItemPrice(item)) }} تومان</span>
                  </div>

                  <div class="stage-item-controls">
                    <div
                      v-for="attr in getItemAttributeControls(item)"
                      :key="`${item.id}-${attr.key}`"
                      class="control"
                    >
                      <label>{{ attr.label }}</label>
                      <div class="chip-list">
                        <button
                          v-for="opt in attr.options"
                          :key="`${attr.key}-${opt}`"
                          class="chip"
                          :class="{ active: item.variantAttributes[attr.key] === opt }"
                          @click="selectItemAttribute(group, item, attr.key, opt)"
                        >
                          {{ formatAttributeOption(attr.key, opt) }}
                        </button>
                      </div>
                    </div>

                    <div class="control" v-if="item.all_wood_colors.length">
                      <label>رنگ چوب</label>
                      <div class="chip-list">
                        <button
                          v-for="w in item.all_wood_colors"
                          :key="w"
                          class="chip"
                          :class="{ active: item.selectedWood === w }"
                          @click="item.selectedWood = w"
                        >
                          {{ w }}
                        </button>
                      </div>
                    </div>

                    <div class="control" v-if="item.odd_cloth">
                      <label>پارچه اصلی</label>
                      <button class="fabric-selector-trigger" @click="openFabricForItem(gIdx, iIdx, 'main')">
                        <div v-if="item.selectedMainFabric" class="selected-fabric">
                          <img v-if="item.selectedMainFabric.image" :src="item.selectedMainFabric.image" />
                          <div class="fab-info">
                            <span class="fab-name">{{ item.selectedMainFabric.qualityName }}</span>
                            <span class="fab-color">{{ item.selectedMainFabric.colorName }}</span>
                          </div>
                        </div>
                        <span v-else class="placeholder">انتخاب پارچه اصلی</span>
                        <span class="arrow">›</span>
                      </button>
                    </div>

                    <div class="control" v-if="item.minor_cloth">
                      <label>پارچه جزیی</label>
                      <button class="fabric-selector-trigger" @click="openFabricForItem(gIdx, iIdx, 'minor')">
                        <div v-if="item.selectedMinorFabric" class="selected-fabric">
                          <img v-if="item.selectedMinorFabric.image" :src="item.selectedMinorFabric.image" />
                          <div class="fab-info">
                            <span class="fab-name">{{ item.selectedMinorFabric.qualityName }}</span>
                            <span class="fab-color">{{ item.selectedMinorFabric.colorName }}</span>
                          </div>
                        </div>
                        <span v-else class="placeholder">انتخاب پارچه جزیی</span>
                        <span class="arrow">›</span>
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </section>
        </div>

        <div class="checkout-box" v-if="stagedGroups.length">
          <div class="total-row">
            <span>مبلغ کل</span>
            <strong>{{ fmtToman(totalConfigPrice) }} تومان</strong>
          </div>
          <button class="checkout-btn" :disabled="!allConfigured" @click="addAllToCart">
            {{ allConfigured ? 'افزودن همه به سبد خرید' : 'پارچه برخی آیتم‌ها ناقص است' }}
          </button>
        </div>
      </aside>
    </main>

    <FabricSidebar
      :open="fabricPickerOpen"
      :cloth-groups="clothGroups"
      :selected-fabric="activeSelectedFabric"
      @close="fabricPickerOpen = false"
      @select="onFabricSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCart } from '../stores/cartStore'
import { useFabricStore } from '../stores/fabricStore'
import { toNumber, calculateFabricPrice } from '../utils/fabricPricing'
import FabricSidebar from '../components/FabricSidebar.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'

const product = ref(window.ProductDetails || { sofa_modules: [], sofa_bundles: [] })
const breadcrumbs = computed(() => [
  { label: 'مبلمان', route: '/sofas' },
  { label: product.value.name }
])

const clothGroups = ref(window.ClothGroups || [])
const stagedGroups = ref([])
const fabricPickerOpen = ref(false)
const activeContext = ref({ gIdx: -1, iIdx: -1, forGroup: false, role: 'main' })
const selectedCustomer = ref(window.SelectedCustomer || '')
const bundlePrefill = ref(window.BundlePrefill || '')
const libraryTab = ref('modules')
const { selectedFabric: persistedFabric, setSelectedFabric: setPersistedFabric } = useFabricStore()

const { addToCart, isCartOpen } = useCart()

const variantAttributeDefs = [
  { key: 'body_color', label: 'رنگ بدنه' },
  { key: 'module_feature', label: 'ویژگی ماژول' },
  { key: 'module_shape', label: 'شکل' },
  { key: 'module_length', label: 'طول' },
  { key: 'module_width', label: 'عرض' },
  { key: 'module_height', label: 'ارتفاع' },
  { key: 'module_diameter', label: 'قطر' }
]

const appendCustomerQuery = (route) => {
  if (!route || !selectedCustomer.value) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

const hasMeaningfulValue = (value) => {
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

const normalizeImageUrl = (url) => {
  if (!url) return ''
  return String(url).replace('/private/files/', '/files/')
}

const normalizeText = (value) => String(value || '').trim().replace(/\s+/g, ' ').toLowerCase()

const toEnglishDigits = (value) => String(value || '').replace(/[۰-۹]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))

const parseBundleQty = (value) => {
  const normalized = toEnglishDigits(value).replace(/[^\d.-]/g, '')
  const qty = Number(normalized)
  if (!Number.isFinite(qty) || qty <= 0) return 1
  return Math.max(1, Math.round(qty))
}

const isCushionLikeText = (value) => {
  const txt = String(value || '')
  return txt.includes('کوسن') || txt.includes('تشکچه')
}

const cloneFabric = (fabric) => (fabric ? { ...fabric } : null)

const buildFabricObject = (group, variant) => {
  if (!group || !variant) return null
  return {
    qualityName: group.name,
    colorName: variant.name || variant.item_name || '',
    pricePerMeter: toNumber(variant.Price || 0),
    formattedPrice: variant.formatted_Price || '',
    image: normalizeImageUrl(variant.image || group.sample_image || '')
  }
}

const getFallbackFabric = () => {
  for (const group of clothGroups.value || []) {
    const variant = group?.clothvariants?.[0]
    if (variant) return buildFabricObject(group, variant)
  }
  return null
}

const ensureDefaultMainFabric = () => {
  if (persistedFabric.value) return cloneFabric(persistedFabric.value)
  const fallback = getFallbackFabric()
  if (fallback) {
    setPersistedFabric(fallback)
    return cloneFabric(fallback)
  }
  return null
}

const displayModules = computed(() => {
  return (product.value.sofa_modules || []).filter((mod) => mod?.sofa_module_items?.length)
})

const isAccessoryModule = (mod) => {
  const type = String(mod?.sofa_module_type || '')
  const name = String(mod?.sofa_module_name || '')
  return type.includes('کوسن') || type.includes('تشکچه') || name.includes('کوسن') || name.includes('تشکچه')
}

const displayPrimaryModules = computed(() => displayModules.value.filter((mod) => !isAccessoryModule(mod)))
const displayAccessoryModules = computed(() => displayModules.value.filter((mod) => isAccessoryModule(mod)))

const bundleUnitCount = (bundle) => {
  return (bundle?.sofa_bundle_table_items || []).reduce((sum, row) => {
    const qty = Number(row?.qty || 1)
    return sum + (Number.isFinite(qty) ? qty : 1)
  }, 0)
}

const displayBundles = computed(() => {
  return (product.value.sofa_bundles || []).filter((bundle) => bundleUnitCount(bundle) > 1)
})

const defaultWoodColor = computed(() => {
  const explicit = (product.value.all_wood_colors || [])
    .map((val) => String(val || '').trim())
    .find(Boolean)
  if (explicit) return explicit

  for (const mod of displayModules.value) {
    for (const item of mod.sofa_module_items || []) {
      const colors = item.all_wood_colors?.length ? item.all_wood_colors : (item.wood_color ? [item.wood_color] : [])
      for (const color of colors) {
        const normalized = String(color || '').trim()
        if (normalized) return normalized
      }
    }
  }
  return ''
})

const getPreferredWood = (options = []) => {
  const list = Array.isArray(options) ? options.filter(Boolean) : []
  if (!list.length) return null
  if (defaultWoodColor.value && list.includes(defaultWoodColor.value)) return defaultWoodColor.value
  return list[0]
}

const activeSelectedFabric = computed(() => {
  const { gIdx, iIdx, forGroup, role } = activeContext.value
  if (gIdx < 0) return persistedFabric.value
  const group = stagedGroups.value[gIdx]
  if (!group) return persistedFabric.value

  if (forGroup) {
    if (role === 'minor') return group.globalMinorFabric || persistedFabric.value
    return group.globalMainFabric || persistedFabric.value
  }

  const targetItem = group.items?.[iIdx]
  if (!targetItem) return persistedFabric.value
  if (role === 'minor') return targetItem.selectedMinorFabric || persistedFabric.value
  return targetItem.selectedMainFabric || persistedFabric.value
})

const goToSofaUnit = (mod) => {
  const firstItem = mod.sofa_module_items?.[0]
  if (!firstItem?.item_name) return
  window.location.href = appendCustomerQuery(`/product/${encodeURIComponent(firstItem.item_name)}?kind=sofa`)
}

const resolveModuleImage = (mod) => {
  if (mod?.sofa_module_images?.length) {
    const cover = mod.sofa_module_images.find((img) => img.cover) || mod.sofa_module_images[0]
    if (cover?.file_url) return normalizeImageUrl(cover.file_url)
  }
  const firstItem = mod?.sofa_module_items?.[0]
  if (firstItem?.images?.length) {
    const cover = firstItem.images.find((img) => img.cover) || firstItem.images[0]
    if (cover?.file_url) return normalizeImageUrl(cover.file_url)
  }
  if (firstItem?.image) return normalizeImageUrl(firstItem.image)
  return ''
}

const resolveSelectedItemImage = (mod, selectedItem) => {
  if (selectedItem?.images?.length) {
    const cover = selectedItem.images.find((img) => img.cover) || selectedItem.images[0]
    if (cover?.file_url) return normalizeImageUrl(cover.file_url)
  }
  if (selectedItem?.image) return normalizeImageUrl(selectedItem.image)
  return resolveModuleImage(mod)
}

const getVariantAttrRaw = (variant, key) => {
  if (!variant) return null
  if (key === 'body_color') return variant.body_color || variant.module_color || null
  return variant[key] ?? null
}

const getVariantAttrValue = (variant, key) => {
  const raw = getVariantAttrRaw(variant, key)
  if (raw === null || raw === undefined) return ''
  return String(raw).trim()
}

const isValidVariantValue = (key, value) => {
  if (!value) return false
  if (['module_length', 'module_width', 'module_height', 'module_diameter'].includes(key)) {
    return hasMeaningfulValue(value)
  }
  return true
}

const matchesVariantAttributes = (variant, attrs) => {
  return variantAttributeDefs.every((def) => {
    const selected = attrs?.[def.key]
    if (!selected) return true
    return getVariantAttrValue(variant, def.key) === selected
  })
}

const getAttributeOptions = (item, key, attrs = item.variantAttributes || {}) => {
  const variants = item.raw_mod?.sofa_module_items || []
  const options = []
  variants.forEach((variant) => {
    const compatible = variantAttributeDefs.every((def) => {
      if (def.key === key) return true
      const selected = attrs?.[def.key]
      if (!selected) return true
      return getVariantAttrValue(variant, def.key) === selected
    })
    if (!compatible) return
    const val = getVariantAttrValue(variant, key)
    if (!isValidVariantValue(key, val)) return
    if (!options.includes(val)) options.push(val)
  })
  return options
}

const refreshVariantAttributes = (item, preferredKey = '') => {
  if (!item.variantAttributes) item.variantAttributes = {}
  const next = { ...item.variantAttributes }

  variantAttributeDefs.forEach((def) => {
    const options = getAttributeOptions(item, def.key, next)
    const current = next[def.key]
    if (current && options.includes(current)) return

    if (options.length === 1) {
      next[def.key] = options[0]
      return
    }

    if (preferredKey && def.key === preferredKey && options.length) {
      if (options.includes(current)) return
      next[def.key] = options[0]
      return
    }

    next[def.key] = ''
  })

  item.variantAttributes = next
}

const findBestMatchingVariant = (item, preferredKey = '') => {
  const variants = item.raw_mod?.sofa_module_items || []
  if (!variants.length) return null

  let match = variants.find((variant) => matchesVariantAttributes(variant, item.variantAttributes))
  if (match) return match

  if (preferredKey && item.variantAttributes?.[preferredKey]) {
    const preferred = item.variantAttributes[preferredKey]
    match = variants.find((variant) => getVariantAttrValue(variant, preferredKey) === preferred)
    if (match) return match
  }

  return variants[0]
}

const collectWoodOptions = (item, selectedItem) => {
  const variants = item.raw_mod?.sofa_module_items || []
  const bodyColor = getVariantAttrValue(selectedItem, 'body_color')
  const scoped = bodyColor
    ? variants.filter((variant) => getVariantAttrValue(variant, 'body_color') === bodyColor)
    : variants

  const source = scoped.length ? scoped : variants
  const woods = new Set()
  source.forEach((variant) => {
    const values = variant.all_wood_colors?.length
      ? variant.all_wood_colors
      : (variant.wood_color ? [variant.wood_color] : [])
    values.forEach((value) => {
      const normalized = String(value || '').trim()
      if (normalized) woods.add(normalized)
    })
  })
  return Array.from(woods)
}

const resolveItemClothNeeds = (item) => {
  const selected = item?.selectedItem || {}
  const moduleLevel = item?.raw_mod || {}
  return {
    odd: Math.max(0, toNumber(selected.odd_cloth ?? moduleLevel.sofa_odd_cloth)),
    even: Math.max(0, toNumber(selected.even_cloth ?? moduleLevel.sofa_even_cloth)),
    minor: Math.max(0, toNumber(selected.minor_cloth ?? moduleLevel.sofa_minor_cloth))
  }
}

const applyDefaultSelectionsToItem = (item, { force = false } = {}) => {
  if (!item) return

  const fallbackFabric = ensureDefaultMainFabric()
  if (item.odd_cloth > 0) {
    if (force || !item.selectedMainFabric) {
      item.selectedMainFabric = cloneFabric(fallbackFabric)
    }
  } else {
    item.selectedMainFabric = null
  }

  if (item.minor_cloth > 0) {
    if (force || !item.selectedMinorFabric) {
      item.selectedMinorFabric = cloneFabric(fallbackFabric)
    }
  } else {
    item.selectedMinorFabric = null
  }

  if (!item.all_wood_colors?.includes(item.selectedWood)) {
    item.selectedWood = getPreferredWood(item.all_wood_colors)
  }
}

const createStagedItem = (mod, preferredItemCode = '') => {
  const variants = mod?.sofa_module_items || []
  if (!variants.length) return null

  const preferredCode = normalizeText(preferredItemCode)
  const firstItem = preferredCode
    ? (
        variants.find((variant) => {
          const code = normalizeText(variant?.item_code)
          const name = normalizeText(variant?.item_name || variant?.display_name)
          return code === preferredCode || name === preferredCode
        }) || variants[0]
      )
    : variants[0]

  if (!firstItem) return null

  const staged = {
    id: Math.random().toString(36).slice(2, 10),
    module_name: mod.sofa_module_name,
    raw_mod: mod,
    selectedItem: firstItem,
    image: resolveSelectedItemImage(mod, firstItem),
    odd_cloth: Math.max(0, toNumber(mod.sofa_odd_cloth || 0)),
    even_cloth: Math.max(0, toNumber(mod.sofa_even_cloth || 0)),
    minor_cloth: Math.max(0, toNumber(mod.sofa_minor_cloth || 0)),
    all_wood_colors: [],
    selectedWood: null,
    selectedMainFabric: null,
    selectedMinorFabric: null,
    variantAttributes: {}
  }

  variantAttributeDefs.forEach((def) => {
    const val = getVariantAttrValue(firstItem, def.key)
    staged.variantAttributes[def.key] = isValidVariantValue(def.key, val) ? val : ''
  })

  refreshVariantAttributes(staged)
  const matched = findBestMatchingVariant(staged)
  if (matched) staged.selectedItem = matched
  syncItemDetails(staged)
  applyDefaultSelectionsToItem(staged)
  return staged
}

const getItemAttributeControls = (item) => {
  return variantAttributeDefs
    .map((def) => ({
      ...def,
      options: getAttributeOptions(item, def.key)
    }))
    .filter((def) => def.options.length > 1)
}

const formatAttributeOption = (key, value) => {
  if (!value) return ''
  if (key === 'body_color') return value
  return value
}

const selectItemAttribute = (group, item, key, value) => {
  if (!item?.variantAttributes) item.variantAttributes = {}
  item.variantAttributes[key] = value
  refreshVariantAttributes(item, key)
  const matched = findBestMatchingVariant(item, key)
  if (matched) item.selectedItem = matched
  syncItemDetails(item)

  if (
    group?.isBundle &&
    group.globalWood &&
    item.all_wood_colors.includes(group.globalWood) &&
    (!item.selectedWood || !item.all_wood_colors.includes(item.selectedWood))
  ) {
    item.selectedWood = group.globalWood
  }
  if (group?.isBundle && group.globalMainFabric && item.odd_cloth > 0 && !item.selectedMainFabric) {
    item.selectedMainFabric = cloneFabric(group.globalMainFabric)
  }
  if (group?.isBundle && group.globalMinorFabric && item.minor_cloth > 0 && !item.selectedMinorFabric) {
    item.selectedMinorFabric = cloneFabric(group.globalMinorFabric)
  }
}

const addModuleToStage = (mod) => {
  const item = createStagedItem(mod)
  if (!item) return

  const group = {
    id: Date.now() + Math.random(),
    isBundle: false,
    name: mod.sofa_module_name,
    items: [item]
  }
  applyDefaultSelectionsToGroup(group, { force: true })
  stagedGroups.value.unshift(group)
}

const findModuleForBundleItem = (bItem) => {
  const moduleNameKey = normalizeText(bItem?.module_name)
  const itemCodeKey = normalizeText(bItem?.item_code)
  const itemNameKey = normalizeText(bItem?.item_name || bItem?.display_name)

  return displayModules.value.find((mod) => {
    const modNameKey = normalizeText(mod?.sofa_module_name)
    if (
      moduleNameKey &&
      (
        modNameKey === moduleNameKey ||
        modNameKey.includes(moduleNameKey) ||
        moduleNameKey.includes(modNameKey)
      )
    ) {
      return true
    }

    return (mod?.sofa_module_items || []).some((variant) => {
      const variantCodeKey = normalizeText(variant?.item_code)
      const variantNameKey = normalizeText(variant?.item_name || variant?.display_name)
      if (itemCodeKey && variantCodeKey === itemCodeKey) return true
      if (
        itemNameKey &&
        (
          variantNameKey === itemNameKey ||
          variantNameKey.includes(itemNameKey) ||
          itemNameKey.includes(variantNameKey)
        )
      ) {
        return true
      }
      return false
    })
  })
}

const createStagedItemFromBundleItem = (bItem) => {
  const itemName = String(bItem?.item_name || bItem?.display_name || bItem?.item_code || 'آیتم بسته').trim()
  const moduleName = String(bItem?.module_name || bItem?.display_name || itemName).trim()
  const image = normalizeImageUrl(bItem?.image || '')
  const rawPrice = Math.max(0, toNumber(bItem?.Price || bItem?.raw_price || 0))
  const odd = Math.max(0, toNumber(bItem?.odd_cloth || bItem?.cushion_cloth || 0))
  const even = Math.max(0, toNumber(bItem?.even_cloth || 0))
  const minor = Math.max(0, toNumber(bItem?.minor_cloth || 0))
  const moduleType = String(
    bItem?.variant_of ||
    (isCushionLikeText(itemName) || isCushionLikeText(moduleName) ? 'کوسن' : 'ماژول')
  ).trim()

  const fallbackModule = {
    sofa_module_name: moduleName,
    sofa_module_type: moduleType,
    sofa_odd_cloth: odd,
    sofa_even_cloth: even,
    sofa_minor_cloth: minor,
    sofa_module_items: [{
      item_name: itemName,
      item_code: bItem?.item_code || itemName,
      display_name: bItem?.display_name || itemName,
      image,
      images: image ? [{ file_url: image, cover: true }] : [],
      Price: rawPrice,
      raw_price: rawPrice,
      odd_cloth: odd,
      even_cloth: even,
      minor_cloth: minor,
      all_wood_colors: [],
      wood_color: '',
      body_color: '',
      module_feature: '',
      module_shape: '',
      module_length: '',
      module_width: '',
      module_height: '',
      module_diameter: '',
    }],
  }

  return createStagedItem(fallbackModule, bItem?.item_code || itemName)
}

const addBundleToStage = (bundle) => {
  const gId = Date.now() + Math.random()
  const items = []

  ;(bundle.sofa_bundle_table_items || []).forEach((bItem) => {
    const mod = findModuleForBundleItem(bItem)
    const qty = parseBundleQty(bItem?.qty)
    const preferredCode = bItem?.item_code || bItem?.item_name || ''

    for (let i = 0; i < qty; i += 1) {
      let staged = null
      if (mod) {
        staged = createStagedItem(mod, preferredCode)
      }
      if (!staged) {
        staged = createStagedItemFromBundleItem(bItem)
      }
      if (staged) items.push(staged)
    }
  })

  if (!items.length) return

  const group = {
    id: gId,
    isBundle: true,
    name: bundle.sofa_bundle_display_name || bundle.name,
    items,
    globalWood: '',
    globalMainFabric: null,
    globalMinorFabric: null
  }
  applyDefaultSelectionsToGroup(group, { force: true })
  stagedGroups.value.unshift(group)
}

const removeGroup = (idx) => stagedGroups.value.splice(idx, 1)

const syncItemDetails = (item) => {
  refreshVariantAttributes(item)
  const matched = findBestMatchingVariant(item)
  if (matched) {
    item.selectedItem = matched
  }

  item.image = resolveSelectedItemImage(item.raw_mod, item.selectedItem)
  item.all_wood_colors = collectWoodOptions(item, item.selectedItem)

  const clothNeeds = resolveItemClothNeeds(item)
  item.odd_cloth = clothNeeds.odd
  item.even_cloth = clothNeeds.even
  item.minor_cloth = clothNeeds.minor

  variantAttributeDefs.forEach((def) => {
    const current = item.variantAttributes?.[def.key]
    if (current) return
    const value = getVariantAttrValue(item.selectedItem, def.key)
    if (isValidVariantValue(def.key, value)) {
      item.variantAttributes[def.key] = value
    }
  })

  applyDefaultSelectionsToItem(item)
}

const getGroupWoodOptions = (group) => {
  const options = new Set()
  ;(group?.items || []).forEach((item) => {
    ;(item.all_wood_colors || []).forEach((wood) => {
      if (wood) options.add(wood)
    })
  })
  return Array.from(options)
}

const applyWoodToGroup = (group) => {
  if (!group.globalWood) return
  group.items.forEach((item) => {
    if (item.all_wood_colors.includes(group.globalWood)) {
      item.selectedWood = group.globalWood
    }
  })
}

const applyDefaultSelectionsToGroup = (group, { force = false } = {}) => {
  if (!group?.items?.length) return

  const defaultFabric = ensureDefaultMainFabric()
  const hasMainFabricItems = group.items.some((item) => item.odd_cloth > 0)
  const hasMinorFabricItems = group.items.some((item) => item.minor_cloth > 0)

  if (group.isBundle) {
    if (hasMainFabricItems) {
      if (force || !group.globalMainFabric) {
        group.globalMainFabric = cloneFabric(defaultFabric)
      }
    } else {
      group.globalMainFabric = null
    }

    if (hasMinorFabricItems) {
      if (force || !group.globalMinorFabric) {
        group.globalMinorFabric = cloneFabric(defaultFabric)
      }
    } else {
      group.globalMinorFabric = null
    }

    const woodOptions = getGroupWoodOptions(group)
    if (woodOptions.length) {
      if (force || !group.globalWood || !woodOptions.includes(group.globalWood)) {
        group.globalWood = getPreferredWood(woodOptions)
      }
    } else {
      group.globalWood = ''
    }
  }

  group.items.forEach((item) => {
    applyDefaultSelectionsToItem(item, { force })

    if (group.isBundle) {
      if (group.globalWood && item.all_wood_colors.includes(group.globalWood)) {
        item.selectedWood = group.globalWood
      }
      if (item.odd_cloth > 0 && group.globalMainFabric && (force || !item.selectedMainFabric)) {
        item.selectedMainFabric = cloneFabric(group.globalMainFabric)
      }
      if (item.minor_cloth > 0 && group.globalMinorFabric && (force || !item.selectedMinorFabric)) {
        item.selectedMinorFabric = cloneFabric(group.globalMinorFabric)
      }
    }
  })
}

const applyFabricToGroup = (group, role, fabric) => {
  if (!group) return

  if (role === 'minor') {
    group.globalMinorFabric = cloneFabric(fabric)
    group.items.forEach((item) => {
      if (item.minor_cloth > 0) {
        item.selectedMinorFabric = cloneFabric(fabric)
      }
    })
    return
  }

  group.globalMainFabric = cloneFabric(fabric)
  group.items.forEach((item) => {
    if (item.odd_cloth > 0) {
      item.selectedMainFabric = cloneFabric(fabric)
    }
  })
}

const openFabricForItem = (gIdx, iIdx, role = 'main') => {
  activeContext.value = { gIdx, iIdx, forGroup: false, role }
  fabricPickerOpen.value = true
}

const openFabricForGroup = (gIdx, role = 'main') => {
  activeContext.value = { gIdx, iIdx: -1, forGroup: true, role }
  fabricPickerOpen.value = true
}

const onFabricSelect = (fabric) => {
  const { gIdx, iIdx, forGroup, role } = activeContext.value
  if (gIdx === -1) return

  const normalized = cloneFabric(fabric)
  if (normalized && role === 'main') {
    setPersistedFabric(normalized)
  }

  const group = stagedGroups.value[gIdx]
  if (!group) {
    fabricPickerOpen.value = false
    return
  }

  if (forGroup) {
    applyFabricToGroup(group, role, normalized)
  } else if (group.items?.[iIdx]) {
    const item = group.items[iIdx]
    if (role === 'minor' && item.minor_cloth > 0) {
      item.selectedMinorFabric = cloneFabric(normalized)
    } else if (role === 'main' && item.odd_cloth > 0) {
      item.selectedMainFabric = cloneFabric(normalized)
    }
  }

  fabricPickerOpen.value = false
}

const calculateItemPrice = (item) => {
  let total = toNumber(item.selectedItem?.raw_price || item.selectedItem?.Price || 0)
  if (item.selectedMainFabric && item.odd_cloth > 0) {
    total += calculateFabricPrice(item.odd_cloth, item.selectedMainFabric.pricePerMeter)
  }
  if (item.selectedMinorFabric && item.minor_cloth > 0) {
    total += calculateFabricPrice(item.minor_cloth, item.selectedMinorFabric.pricePerMeter)
  }
  return total
}

const totalConfigPrice = computed(() => {
  let total = 0
  stagedGroups.value.forEach((group) => {
    group.items.forEach((item) => {
      total += calculateItemPrice(item)
    })
  })
  return total
})

const allConfigured = computed(() => {
  return stagedGroups.value.every((group) => group.items.every((item) => {
    const mainOk = item.odd_cloth <= 0 || !!item.selectedMainFabric
    const minorOk = item.minor_cloth <= 0 || !!item.selectedMinorFabric
    return mainOk && minorOk
  }))
})

const formatFabricLabel = (fabric) => {
  if (!fabric) return null
  return `${fabric.qualityName} - ${fabric.colorName}`
}

const addFabricLineToCart = ({ itemCode, parentLineId, fabric, meters, role }) => {
  if (!fabric || meters <= 0) return
  const price = calculateFabricPrice(meters, fabric.pricePerMeter)
  if (price <= 0) return

  addToCart(
    {
      name: `پارچه ${fabric.qualityName} (${fabric.colorName}) - ${role === 'minor' ? 'جزیی' : 'اصلی'}`,
      type: 'fabric',
      price,
      image: fabric.image,
      qty: 1
    },
    {
      meters,
      quality: fabric.qualityName,
      color: fabric.colorName,
      parent_line_id: parentLineId,
      meta: {
        linked_item_code: itemCode,
        fabric_role: role
      },
      totalPrice: price
    }
  )
}

const addAllToCart = () => {
  stagedGroups.value.forEach((group) => {
    group.items.forEach((item) => {
      const parentLineId = `line-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
      const basePrice = toNumber(item.selectedItem?.raw_price || item.selectedItem?.Price || 0)
      const itemCode = item.selectedItem?.item_code || item.module_name

      addToCart(
        {
          name: item.selectedItem?.item_name || item.module_name,
          item_code: itemCode,
          type: 'sofa-unit',
          totalPrice: basePrice,
          image: item.image
        },
        {
          qty: 1,
          image: item.image,
          item_code: itemCode,
          line_id: parentLineId,
          totalPrice: basePrice,
          attributes: {
            'رنگ چوب': item.selectedWood,
            'رنگ بدنه': item.selectedItem.body_color || null,
            'پارچه اصلی': formatFabricLabel(item.selectedMainFabric),
            'پارچه جزیی': formatFabricLabel(item.selectedMinorFabric),
            'ویژگی': item.selectedItem.module_feature || 'پایه',
            'شکل': item.selectedItem.module_shape || null,
            'طول': hasMeaningfulValue(item.selectedItem.module_length) ? item.selectedItem.module_length : null,
            'عرض': hasMeaningfulValue(item.selectedItem.module_width) ? item.selectedItem.module_width : null,
            'ارتفاع': hasMeaningfulValue(item.selectedItem.module_height) ? item.selectedItem.module_height : null,
            'قطر': hasMeaningfulValue(item.selectedItem.module_diameter) ? item.selectedItem.module_diameter : null
          }
        }
      )

      addFabricLineToCart({
        itemCode,
        parentLineId,
        fabric: item.selectedMainFabric,
        meters: item.odd_cloth,
        role: 'main'
      })
      addFabricLineToCart({
        itemCode,
        parentLineId,
        fabric: item.selectedMinorFabric,
        meters: item.minor_cloth,
        role: 'minor'
      })
    })
  })

  isCartOpen.value = true
  stagedGroups.value = []
}

const getCoverImage = (mod) => resolveModuleImage(mod)

const getModulePrice = (mod) => {
  if (!mod.sofa_module_items?.length) return '۰'
  const prices = mod.sofa_module_items.map((i) => i.raw_price || i.Price || 0)
  return fmtToman(Math.max(...prices))
}

const fmtToman = (val) => {
  if (!val) return '۰'
  return Math.round(val).toLocaleString('fa-IR')
}

onMounted(() => {
  ensureDefaultMainFabric()

  if (!bundlePrefill.value) return
  const targetBundle = displayBundles.value.find((bundle) => bundle.bundle_name === bundlePrefill.value)
  if (targetBundle) {
    libraryTab.value = 'bundles'
    addBundleToStage(targetBundle)
  }
})
</script>

<style scoped>
.sofa-collection-page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  padding-bottom: 40px;
}

.hero {
  position: relative;
  min-height: 320px;
  border-bottom: 1px solid var(--glass-border);
  overflow: hidden;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(20, 18, 16, 0.78), rgba(40, 35, 31, 0.54));
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 26px 20px 34px;
}

.hero-title {
  margin: 14px 0 8px;
  font-size: clamp(1.8rem, 3.5vw, 2.8rem);
  font-weight: 900;
  color: #fff;
}

.hero-subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.95rem;
  font-weight: 500;
}

.hero-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.stat-chip {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #fff;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.8rem;
  font-weight: 700;
}

.workspace {
  max-width: 1200px;
  margin: 0 auto;
  padding: 22px 20px 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
}

.library-panel,
.stage-panel {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 16px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--text-main);
}

.panel-head p {
  margin: 6px 0 0;
  color: var(--text-dim);
  font-size: 0.85rem;
}

.library-tabs {
  display: inline-flex;
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.tab-btn {
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--text-dim);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 7px 14px;
  cursor: pointer;
}

.tab-btn.active {
  background: var(--accent-brown);
  color: var(--accent-gold);
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.module-library-stack {
  display: grid;
  gap: 16px;
}

.module-section {
  display: grid;
  gap: 10px;
}

.module-section-title {
  margin: 0;
  font-size: 0.92rem;
  color: var(--text-main);
  font-weight: 850;
}

.library-card {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.library-card.accessory-card {
  background: rgba(248, 244, 236, 0.8);
}

.library-card-image {
  cursor: pointer;
  height: 170px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
}

.thumb-placeholder {
  color: var(--text-dim);
  font-size: 0.85rem;
}

.library-card-body {
  padding: 12px;
}

.library-card-body h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.45;
}

.spec-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  color: var(--text-dim);
  font-size: 0.72rem;
  font-weight: 700;
}

.card-price {
  margin: 10px 0 0;
  font-size: 0.95rem;
  color: var(--accent-orange);
  font-weight: 800;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.primary-btn,
.secondary-btn,
.danger-btn,
.checkout-btn {
  font-family: inherit;
  border: none;
  cursor: pointer;
}

.primary-btn,
.secondary-btn,
.danger-btn {
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 0.78rem;
  font-weight: 700;
}

.primary-btn {
  background: var(--accent-brown);
  color: var(--accent-gold);
}

.secondary-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.danger-btn {
  background: rgba(163, 51, 51, 0.12);
  color: #a33333;
}

.empty-library {
  grid-column: 1 / -1;
  border: 1px dashed var(--glass-border);
  border-radius: 14px;
  padding: 18px;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.86rem;
}

.stage-head {
  margin-bottom: 10px;
}

.empty-stage {
  border: 1px dashed var(--glass-border);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--text-dim);
  font-size: 0.85rem;
}

.empty-stage strong {
  color: var(--text-main);
}

.stage-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 55vh;
  overflow: auto;
  padding-right: 2px;
}

.group-card {
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.45);
  padding: 12px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.group-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.group-title-wrap h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-tag {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 0.7rem;
  font-weight: 800;
}

.group-tag.bundle {
  background: rgba(176, 134, 57, 0.16);
  color: #8f6a2a;
}

.group-tag.single {
  background: rgba(80, 49, 48, 0.14);
  color: #503130;
}

.group-bulk {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: end;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px dashed var(--glass-border);
  border-radius: 12px;
}

.bulk-control {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bulk-control label {
  font-size: 0.72rem;
  color: var(--text-dim);
  font-weight: 700;
}

.bulk-control select,
.control select {
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  background: #fff;
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.78rem;
  padding: 7px 10px;
}

.group-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stage-item {
  display: flex;
  gap: 10px;
  border: 1px solid rgba(80, 49, 48, 0.08);
  border-radius: 12px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.65);
}

.stage-thumb {
  width: 84px;
  height: 84px;
  object-fit: contain;
  border-radius: 10px;
  background: #fff;
  border: 1px solid var(--glass-border);
}

.stage-item-main {
  flex: 1;
  min-width: 0;
}

.stage-item-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.stage-item-top strong {
  color: var(--text-main);
  font-size: 0.87rem;
  font-weight: 800;
}

.item-price {
  color: var(--accent-orange);
  font-size: 0.82rem;
  font-weight: 800;
  white-space: nowrap;
}

.stage-item-controls {
  margin-top: 8px;
  display: grid;
  gap: 7px;
}

.control {
  display: grid;
  gap: 5px;
}

.control label {
  color: var(--text-dim);
  font-size: 0.7rem;
  font-weight: 700;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  border: 1px solid var(--glass-border);
  background: #fff;
  color: var(--text-main);
  border-radius: 999px;
  padding: 5px 10px;
  font-family: inherit;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}

.chip.active {
  background: var(--accent-brown);
  border-color: var(--accent-brown);
  color: var(--accent-gold);
}

.fabric-selector-trigger {
  width: 100%;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: #fff;
  color: var(--text-main);
  min-height: 48px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-family: inherit;
  cursor: pointer;
}

.selected-fabric {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.selected-fabric img {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  object-fit: cover;
  border: 1px solid var(--glass-border);
}

.fab-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.fab-name {
  color: var(--text-main);
  font-size: 0.78rem;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fab-color {
  color: var(--text-dim);
  font-size: 0.7rem;
  font-weight: 700;
}

.placeholder {
  color: var(--text-dim);
  font-size: 0.75rem;
  font-weight: 700;
}

.arrow {
  color: var(--text-dim);
  font-size: 1rem;
  font-weight: 800;
  line-height: 1;
}

.checkout-box {
  margin-top: 12px;
  border-top: 1px solid var(--glass-border);
  padding-top: 12px;
  display: grid;
  gap: 10px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.86rem;
  color: var(--text-main);
}

.total-row strong {
  font-size: 1.05rem;
  color: var(--accent-brown);
}

.checkout-btn {
  width: 100%;
  border-radius: 12px;
  background: var(--accent-brown);
  color: var(--accent-gold);
  font-size: 0.88rem;
  font-weight: 800;
  padding: 11px 12px;
}

.checkout-btn:disabled {
  background: #b8b0ac;
  color: #f2efe9;
  cursor: default;
}

@media (min-width: 1024px) {
  .workspace {
    grid-template-columns: minmax(0, 1fr) 430px;
    align-items: start;
  }

  .library-panel {
    padding: 18px;
  }

  .stage-panel {
    position: sticky;
    top: 18px;
    max-height: calc(100vh - 36px);
    display: flex;
    flex-direction: column;
  }

  .stage-groups {
    max-height: none;
    flex: 1;
  }
}

@media (max-width: 680px) {
  .hero {
    min-height: 260px;
  }

  .hero-content {
    padding: 20px 14px 24px;
  }

  .workspace {
    padding: 14px;
    gap: 12px;
  }

  .library-panel,
  .stage-panel {
    border-radius: 16px;
    padding: 12px;
  }

  .panel-head {
    flex-direction: column;
    align-items: stretch;
  }

  .library-tabs {
    width: fit-content;
  }

  .library-grid {
    grid-template-columns: 1fr;
  }

  .stage-item {
    flex-direction: column;
  }

  .stage-thumb {
    width: 100%;
    height: 150px;
  }
}
</style>
