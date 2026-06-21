<template>
  <div class="product-page" dir="rtl">
    <!-- Liquid Background Blobs -->
    <div class="liquid-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <!-- Top Nav -->
    <header class="product-header">
      <GlassButton variant="ghost" class="header-btn" icon-only @click="goBack">
        <template #icon>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#503130" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </template>
      </GlassButton>
      <div class="header-center">
        <div class="glass-label-pill">{{ product.category_name || 'محصول' }}</div>
      </div>
      <div style="position: relative;">
        <GlassButton variant="ghost" class="header-btn" icon-only @click="isCartOpen = true">
          <template #icon>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#503130" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </template>
        </GlassButton>
        <span class="cart-badge" v-if="totalItems > 0">{{ totalItems }}</span>
      </div>
    </header>

    <main class="content-scrollable">
      <!-- Mega Full-width Gallery -->
      <div class="mega-gallery">

          <div class="gallery-inner" @click="openLightbox">
          <img :src="getImageUrl(activeImage)" class="mega-img" />
        </div>

        <!-- Thumbnail Nav -->
        <div class="gallery-thumbnails">
          <div 
            v-for="(img, idx) in product.images" 
            :key="idx" 
            class="thumb-tile"
            :class="{ active: idx === activeImageIndex }"
            @click="activeImageIndex = idx"
          >
            <img :src="getImageUrl(img)" />
          </div>
        </div>
      </div>

      <!-- Main Content Tab System -->
      <div class="product-info-sheet">
        <!-- Tab Bar -->
        <div class="tab-system-header">
          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'details' }"
            @click="setActiveTab('details')"
          >اطلاعات</button>
          
          <!-- Profile Badge style floating element -->
          <div class="header-action-pill">
            <div class="glass-pill">
              <i class="pi pi-heart"></i>
            </div>
          </div>

          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'reviews' }"
            @click="setActiveTab('reviews')"
          >دیدگاه‌ها ({{ reviewCount }})</button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'questions' }"
            @click="setActiveTab('questions')"
          >پرسش‌ها</button>
        </div>

        <div class="tab-content-area">
          <!-- Details Tab -->
          <div v-if="activeTab === 'details'" class="animate-fade-in">
            <div class="header-right">
        <Breadcrumbs :crumbs="breadcrumbs" />
        <h1 class="product-title">{{ product.parent_model_name || product.display_name || product.name }}</h1>
        <p class="product-module-name" v-if="product.type === 'sofa-unit'">{{ product.module }}</p>
        <p class="product-category" v-else>{{ product.category_name }}</p>
      </div>
            <div class="rating-v-row">
                <div class="stars">⭐⭐⭐⭐☆</div>
                <span class="rating-text">۴.۸ (۱۰۸ نظر)</span>
              </div>
            

            <!-- Quick Specs Grid -->
            <div class="quick-specs-grid">
              <div class="q-spec">
                <div class="q-icon">📐</div>
                <div class="q-label">{{ product.length ? product.length + ' سم' : 'بررسی طول' }}</div>
              </div>
              <div class="q-spec">
                <div class="q-icon">📏</div>
                <div class="q-label">{{ product.width ? product.width + ' سم' : 'بررسی عرض' }}</div>
              </div>
              <div class="q-spec">
                <div class="q-icon">📏</div>
                <div class="q-label">{{ displayedHeight || 'بررسی ارتفاع' }}</div>
              </div>
              <div class="q-spec">
                <div class="q-icon">🧵</div>
                <div class="q-label">{{ hasFabricRequirement ? totalCalculatedFabric + ' متر' : 'بدون نیاز به پارچه' }}</div>
              </div>
            </div>

            <p class="product-long-description">{{ sampleDescription }}</p>

            <!-- Configuration Section -->
            <div class="configuration-section">
              <!-- Dynamic Attributes (Height, Width, etc.) -->
              <div 
                v-for="attr in selectableAttributes" 
                :key="attr.name" 
                class="config-item"
              >
                <div class="item-label">انتخاب {{ attr.name }}</div>
                <div class="attr-selector">
                  <div 
                    v-for="opt in attr.options" 
                    :key="opt" 
                    class="attr-option"
                    :class="{ active: currentAttributes[attr.name] === opt }"
                    @click="updateAttribute(attr.name, opt)"
                  >
                    {{ cleanAttrValue(opt) }}
                  </div>
                </div>
              </div>
              
              <!-- Module Switcher (Sofa Units) -->
              <div class="config-item" v-if="product.type === 'sofa-unit' && modelModules.length > 1">
                <div class="item-label">تغییر ماژول</div>
                <div class="attr-selector">
                  <div 
                    v-for="mod in modelModules" 
                    :key="mod.sofa_module_name" 
                    class="attr-option"
                    :class="{ active: mod.sofa_module_name === product.module }"
                    @click="switchToModule(mod)"
                  >
                    {{ mod.sofa_module_name }}
                  </div>
                </div>
              </div>

              <!-- Quantity (Chair Only) -->
              <div class="config-item" v-if="product.type === 'barstool'">
                <div class="item-label">تعداد</div>
                <div class="quantity-input-wrap">
                  <button type="button" @click="quantity > 1 ? quantity-- : null">-</button>
                  <input type="number" v-model.number="quantity" min="1" />
                  <button type="button" @click="quantity++">+</button>
                </div>
              </div>

              <!-- Fabric Selection -->
              <div class="config-item fabric-section-mobile" v-if="hasFabricRequirement">
                <div class="item-label">انتخاب پارچه</div>
                <button
                  class="fabric-selector-trigger"
                  :class="{ warning: showFabricWarning }"
                  @click="fabricOpen = true"
                >
                  <div v-if="selectedFabric" class="selected-fabric">
                    <img v-if="selectedFabric.image" :src="getImageUrl(selectedFabric.image)" />
                    <div class="fab-info">
                      <span class="fab-name">{{ selectedFabric.qualityName }}</span>
                      <span class="fab-color">{{ selectedFabric.colorName }}</span>
                    </div>
                  </div>
                  <span v-else>انتخاب پارچه</span>
                </button>
                <button type="button" class="fabric-self-send-link" @click="selfSendFabric = !selfSendFabric">
                  {{ selfSendFabric ? 'پارچه توسط شما ارسال نمی‌شود' : 'پارچه را خودم ارسال می‌کنم' }}
                </button>
              </div>

              <!-- Modules (Sofa Only) -->
              <div class="config-group" v-if="product.type === 'sofa'">
                <div class="item-label">ماژول‌های مبل</div>
                <div class="modules-grid-premium">
                  <div 
                    v-for="mod in product.modules" 
                    :key="mod.sofa_module_name"
                    class="module-card-liquid"
                    :class="{ active: checkIsSofaModuleSelected(mod) }"
                    @click="addModule(mod)"
                  >
                    <div class="mod-img"><img :src="getModuleImage(mod)" /></div>
                    <div class="mod-body">
                      <div class="n">{{ mod.sofa_module_name }}</div>
                      <div class="p">{{ formatPrice(getModuleBasePrice(mod)) }} تومان</div>
                    </div>
                    <div class="mod-status">{{ checkIsSofaModuleSelected(mod) ? '✓' : '+' }}</div>
                  </div>
                </div>

                <!-- Selected Modules Summary -->
                <div class="selected-summary-box" v-if="selectedModules.length">
                  <div class="item-label">خلاصه انتخاب‌ها</div>
                  <div class="selected-modules-list">
                    <div v-for="(mod, idx) in selectedModules" :key="idx" class="selected-mod-item liquid-glass-inner">
                      <div class="mod-mini-img"><img :src="getModuleImage(mod)" /></div>
                      <div class="mod-mini-info">
                        <div class="n">{{ mod.sofa_module_name }}</div>
                        <div class="p">{{ formatPrice(getModuleBasePrice(mod)) }} تومان</div>
                      </div>
                      <button type="button" class="remove-btn" @click="removeModule(idx)">×</button>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <!-- Similar Products -->
            <div class="similar-products-mobile" v-if="similarProducts.length">
              <div class="item-label">محصولات مشابه</div>
              <div class="similar-scroll">
                <div 
                  v-for="p in similarProducts" 
                  :key="p.name" 
                  class="similar-mini-card liquid-glass-inner"
                  @click="goToProduct(p.route)"
                >
                  <img :src="p.image" />
                  <div class="n">{{ p.name }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Reviews Tab -->
          <div v-if="activeTab === 'reviews'" class="animate-fade-in reviews-tab">
            <ProductFeedbackPanel
              feedback-type="review"
              :model-name="feedbackModelName"
              :item-code="product.item_code || product.name"
              @count-change="(count) => { reviewCount = count }"
            />
          </div>

          <!-- Questions Tab -->
          <div v-if="activeTab === 'questions'" class="animate-fade-in reviews-tab">
            <ProductFeedbackPanel
              feedback-type="question"
              :model-name="feedbackModelName"
              :item-code="product.item_code || product.name"
            />
          </div>
        </div>
      </div>
    </main>

    <!-- Sticky Bottom CTA -->
    <div class="sticky-cta-bar">
      <div class="cta-glass-container">
        <div class="price-display">
          <span class="p-label">قیمت نهایی</span>
          <span class="p-amount">{{ totalCalculatedPrice }} تومان</span>
        </div>
        <GlassButton variant="primary" class="main-action-btn" @click="handleAddToCart">
          افزودن به سبد
        </GlassButton>
      </div>
    </div>

    <!-- Lightbox Overlay -->
    <transition name="fade">
      <div class="lightbox-overlay" v-if="showLightbox" @click="showLightbox = false">
        <button type="button" class="close-lightbox" @click="showLightbox = false">×</button>
        <div class="lightbox-content" @click.stop v-if="product.images?.length">
          <img :src="getImageUrl(product.images[lightboxImageIndex])" />
        </div>
        <div class="lightbox-nav">
           <div 
            v-for="(img, idx) in product.images" 
            :key="idx" 
            class="nav-dot"
            :class="{ active: idx === lightboxImageIndex }"
            @click="lightboxImageIndex = idx"
          ></div>
        </div>
      </div>
    </transition>

    <!-- Overlays & Modals -->
    <div class="fabric-overlay" :class="{ active: fabricOpen }" @click="fabricOpen = false"></div>
    <FabricSidebar
      :open="fabricOpen"
      :cloth-groups="clothGroups"
      :selected-fabric="selectedFabric"
      @close="fabricOpen = false"
      @select="onFabricSelect"
    />

    <!-- Fabric Warning Modal -->
    <transition name="fade">
      <div class="modal-overlay" v-if="showFabricWarningModal" @click="showFabricWarningModal = false">
        <div class="modal-card liquid-glass-card" @click.stop>
          <h3>انتخاب پارچه</h3>
          <p>شما پارچه‌ای انتخاب نکرده‌اید. این بدان معناست که پارچه را خودتان برای ما ارسال می‌کنید. آیا تایید می‌کنید؟</p>
          <div class="modal-actions">
            <GlassButton variant="secondary" @click="showFabricWarningModal = false; fabricOpen = true">خیر، انتخاب پارچه</GlassButton>
            <GlassButton variant="primary" @click="confirmSelfSendFabric">بله، تایید می‌شود</GlassButton>
          </div>
        </div>
      </div>
    </transition>

    <!-- Self-Send Fabric Meter Modal -->
    <transition name="fade">
      <div class="modal-overlay" v-if="showMeterInputModal" @click="showMeterInputModal = false">
        <div class="modal-card liquid-glass-card" @click.stop>
          <h3>متراژ پارچه</h3>
          <p>لطفاً متراژ پارچه‌ای که ارسال می‌کنید را وارد کنید (به متر):</p>
          <div class="meter-input">
            <input type="number" v-model.number="selfSendMeters" min="0.5" step="0.5" />
            <span>متر</span>
          </div>
          <div class="modal-actions">
            <GlassButton variant="primary" @click="addToCartWithSelfSend">ادامه خرید</GlassButton>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import GlassButton from '../components/GlassButton.vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import ProductFeedbackPanel from '../components/ProductFeedbackPanel.vue'
import { useCart } from '../stores/cartStore'
import { useFabricStore } from '../stores/fabricStore'
import { getAnalyticsSessionId, trackAnalyticsEvent } from '../utils/analyticsTracker'
import {
  calculateFabricPrice,
  computeTotalFabricMeters,
  resolveClothNeeds,
  toNumber
} from '../utils/fabricPricing'

// --- Data ---
const product = ref(window.ProductDetails || { modules: [] })
const clothGroups = ref(window.ClothGroups || [])
const similarProducts = ref(window.SimilarProducts || [])
const activeImageIndex = ref(0)
const selectedModules = ref([])
const selectedWood = ref('')
const selectedBodyColor = ref('')
const quantity = ref(1)
const { selectedFabric, setSelectedFabric } = useFabricStore()

const siblings = ref(window.Siblings || [])
const selectableAttributes = ref(window.SelectableAttributes || [])
const currentAttributes = ref({})
const selectedHeight = computed(() => currentAttributes.value['ارتفاع'] || '')

// --- Mobile Redesign State ---
const activeTab = ref('details') // 'details' | 'reviews' | 'questions'
const reviewCount = ref(0)
const feedbackModelName = computed(() => {
  return (
    product.value.parent_model_name
    || product.value.attributes?.['مدل محصول']
    || product.value.display_name
    || product.value.name
    || ''
  )
})
const showLightbox = ref(false)
const lightboxImageIndex = ref(0)
const pageEnterEpoch = Date.now()

const breadcrumbs = computed(() => {
  const list = []
  if (product.value.type === 'barstool') {
    list.push({ label: 'صندلی‌های بار', route: '/barstools' })
  } else if (product.value.parent_model_name) {
    list.push({ label: 'مبلمان', route: '/sofas' })
    list.push({ label: product.value.parent_model_name, route: `/${product.value.parent_model_route}` })
  }
  list.push({ label: product.value.display_name || product.value.name })
  return list
})

const modelModules = ref(window.ProductDetails?.parent_sofa_modules || [])
const isSofaContext = computed(() =>
  product.value.type === 'sofa' || product.value.type === 'sofa-unit' || !!product.value.parent_model_name
)

const buildProductRoute = (itemName) => {
  if (!itemName) return ''
  const base = `/product/${encodeURIComponent(itemName)}`
  return isSofaContext.value ? `${base}?kind=sofa` : base
}

const switchToModule = (mod) => {
  const firstItem = mod.sofa_module_items?.[0]
  if (firstItem?.item_name) {
    window.location.href = buildProductRoute(firstItem.item_name)
  }
}

const sampleDescription = computed(() => {
  return product.value.description || `این محصول با ترکیبی از سبک مدرن میان‌قرنی و راحتی بی‌نظیر، انتخابی ایده‌آل برای دکوراسیون منزل شماست. بدنه ارگونومیک و استفاده از متریال با کیفیت از ویژگی‌های بارز این مدل می‌باشد.`
})

const readVariantAttribute = (variant, attrName) => {
  if (!variant || !variant.attributes) return ''
  return variant.attributes[attrName] || ''
}

const findVariantByAttributes = (attrs) => {
  const variants = Array.isArray(siblings.value) ? siblings.value : []
  if (!variants.length) return null

  const effectiveEntries = Object.entries(attrs || {}).filter(([, value]) => {
    return value !== undefined && value !== null && String(value).trim() !== ''
  })

  if (!effectiveEntries.length) return variants[0]
  return variants.find((variant) =>
    effectiveEntries.every(([key, value]) => readVariantAttribute(variant, key) === value)
  ) || null
}

const cleanAttrValue = (v) => {
  if (!v) return ''
  return v.toString().replace('ارتفاع', '').replace('سانتی متر', '').replace('سم', '').trim()
}

// --- UI State ---
const fabricOpen = ref(false)
const showFabricWarningModal = ref(false)
const showMeterInputModal = ref(false)
const selfSendFabric = ref(false)
const selfSendMeters = ref(0)
const showFabricWarning = ref(false)

// --- Cart Store ---
const { addToCart, totalItems, isCartOpen } = useCart()

// --- Computed ---
const getImageUrl = (img) => {
  if (!img) return ''
  // Safety check for startsWith
  const imgStr = String(img)
  return imgStr.startsWith('http') || imgStr.startsWith('/') ? imgStr : `/files/${imgStr}`
}

const activeImage = computed(() => {
  const imgs = product.value.images || []
  if (imgs.length === 0) return ''
  return imgs[activeImageIndex.value] || ''
})

const displayedHeight = computed(() => selectedHeight.value || product.value.height || '')
const availableWoodColors = computed(() => product.value.all_wood_colors || [])
const availableBodyColors = computed(() => product.value.all_body_colors || [])
const hasHeightAttribute = computed(() =>
  selectableAttributes.value.some((attr) => attr?.name === 'ارتفاع' && Array.isArray(attr.options) && attr.options.length > 0)
)
const activeBarstoolVariant = computed(() => {
  if (product.value.type !== 'barstool') return null

  const attrs = { ...currentAttributes.value }
  if (selectedWood.value) attrs['رنگ چوب'] = selectedWood.value
  if (selectedBodyColor.value) attrs['رنگ بدنه'] = selectedBodyColor.value

  const exact = findVariantByAttributes(attrs)
  if (exact) return exact

  if (selectedHeight.value) {
    const byHeight = findVariantByAttributes({ 'ارتفاع': selectedHeight.value })
    if (byHeight) return byHeight
  }

  if (selectedWood.value) {
    const byWood = findVariantByAttributes({ 'رنگ چوب': selectedWood.value })
    if (byWood) return byWood
  }
  if (selectedBodyColor.value) {
    const byBody = findVariantByAttributes({ 'رنگ بدنه': selectedBodyColor.value })
    if (byBody) return byBody
  }

  return Array.isArray(siblings.value) && siblings.value.length ? siblings.value[0] : null
})
const barstoolClothNeeds = computed(() => resolveClothNeeds(activeBarstoolVariant.value, product.value))
const activeBarstoolUnitPrice = computed(() => {
  if (product.value.type !== 'barstool') return 0
  const variantPrice = toNumber(activeBarstoolVariant.value?.raw_price)
  if (variantPrice > 0) return variantPrice
  return toNumber(product.value.price)
})

const totalCalculatedFabric = computed(() => {
  if (product.value.type === 'barstool') {
    return computeTotalFabricMeters(quantity.value, barstoolClothNeeds.value)
  }
  let total = 0
  selectedModules.value.forEach(mod => {
    total += toNumber(mod.sofa_odd_cloth) + toNumber(mod.sofa_minor_cloth)
  })
  return total * quantity.value
})
const hasFabricRequirement = computed(() => totalCalculatedFabric.value > 0 || toNumber(product.value.fabric_needed) > 0)

const totalCalculatedPrice = computed(() => {
  let basePrice = 0
  if (product.value.type === 'barstool') {
    basePrice = activeBarstoolUnitPrice.value * quantity.value
  } else {
    selectedModules.value.forEach(mod => {
      basePrice += toNumber(mod.sofa_module_items?.[0]?.Price)
    })
    basePrice = basePrice * quantity.value
  }

  let fabricPrice = 0
  if (selectedFabric.value && !selfSendFabric.value) {
    const meters = totalCalculatedFabric.value
    fabricPrice = calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
  }

  return (basePrice + fabricPrice).toLocaleString('fa-IR')
})

const analyticsModelName = computed(() => {
  return (
    product.value.parent_model_name
    || product.value.attributes?.['مدل محصول']
    || product.value.display_name
    || product.value.name
    || ''
  )
})

// --- Methods ---
const goBack = () => window.history.back()
const formatPrice = (p) => p ? p.toLocaleString('fa-IR') : '۰'
const openLightbox = () => {
  showLightbox.value = true
  lightboxImageIndex.value = activeImageIndex.value
  trackAnalyticsEvent('product_images_open', {
    session_id: getAnalyticsSessionId(),
    model_name: analyticsModelName.value,
    product_id: product.value.item_code || product.value.name || '',
    item_group: product.value.type || '',
    properties: {
      image_index: activeImageIndex.value,
      image_count: (product.value.images || []).length
    }
  })
}
const setActiveTab = (tab) => {
  activeTab.value = tab
  if (tab === 'reviews' || tab === 'questions') {
    trackAnalyticsEvent('product_reviews_open', {
      session_id: getAnalyticsSessionId(),
      model_name: analyticsModelName.value,
      product_id: product.value.item_code || product.value.name || '',
      item_group: product.value.type || '',
      properties: { tab }
    })
  }
}
const selectWoodColor = (color) => {
  selectedWood.value = color
  currentAttributes.value['رنگ چوب'] = color
}
const selectBodyColor = (color) => {
  selectedBodyColor.value = color
  currentAttributes.value['رنگ بدنه'] = color
}
const updateAttribute = (attrName, value) => {
  currentAttributes.value[attrName] = value

  if (product.value.type === 'barstool') {
    if (attrName === 'رنگ چوب') selectedWood.value = value
    if (attrName === 'رنگ بدنه') selectedBodyColor.value = value
    return
  }

  // Find sibling that matches all current attributes
  const match = siblings.value.find(s => {
    return Object.entries(currentAttributes.value).every(([k, v]) => s.attributes?.[k] === v)
  })
  
  if (match) {
    const targetRoute = match.route || buildProductRoute(match.item_name)
    goToProduct(targetRoute)
  }
}

const goToProduct = (route) => {
  if (!route) return
  window.location.href = route
}

const getModuleImage = (mod) => {
  if (mod.sofa_module_images?.length) return mod.sofa_module_images[0].file_url
  return mod.sofa_module_items?.[0]?.image || ''
}

const getModuleBasePrice = (mod) => mod.sofa_module_items?.[0]?.Price || 0

const checkIsSofaModuleSelected = (mod) => 
  selectedModules.value.some(m => m.sofa_module_name === mod.sofa_module_name)

const addModule = (mod) => {
  selectedModules.value.push(JSON.parse(JSON.stringify(mod)))
}

const removeModule = (idx) => {
  selectedModules.value.splice(idx, 1)
}

const onFabricSelect = (fabric) => {
  setSelectedFabric(fabric)
  fabricOpen.value = false
  selfSendFabric.value = false
  showFabricWarning.value = false
}

const handleAddToCart = () => {
  if (product.value.type === 'barstool' && hasHeightAttribute.value && !selectedHeight.value) {
    window.alert('لطفاً ابتدا ارتفاع صندلی اپن را انتخاب کنید.')
    return
  }

  // If self-send fabric was already confirmed, skip warning
  if (selfSendFabric.value) {
    showFabricWarning.value = false
    onAddToCart()
    return
  }

  const needsFabric = totalCalculatedFabric.value > 0
  const fabricSatisfied = !needsFabric || selectedFabric.value

  if (fabricSatisfied) {
    showFabricWarning.value = false
    onAddToCart()
    return
  }

  // Show warning only if fabric is needed AND not selected
  showFabricWarning.value = true
  showFabricWarningModal.value = true
}

const confirmSelfSendFabric = () => {
  showFabricWarning.value = false
  showFabricWarningModal.value = false
  selfSendMeters.value = totalCalculatedFabric.value
  showMeterInputModal.value = true
}

const addToCartWithSelfSend = () => {
  selfSendFabric.value = true
  showMeterInputModal.value = false
  onAddToCart()
}

const onAddToCart = () => {
  let activeItemCode = product.value.item_code 
  const parentLineId = `line-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  
  if (product.value.type === 'barstool' && activeBarstoolVariant.value?.item_code) {
    activeItemCode = activeBarstoolVariant.value.item_code
  }

  // 1. Add Product Item
  const config = {
    wood: selectedWood.value,
    body: selectedBodyColor.value,
    height: selectedHeight.value,
    item_code: activeItemCode,
    modules: selectedModules.value.map(m => m.sofa_module_name),
    qty: quantity.value,
    image: activeImage.value,
    line_id: parentLineId
  }
  
  let rawBasePrice = 0
  if (product.value.type === 'barstool') {
    rawBasePrice = activeBarstoolUnitPrice.value * quantity.value
  } else {
    selectedModules.value.forEach(m => {
      rawBasePrice += toNumber(m.sofa_module_items?.[0]?.Price)
    })
    rawBasePrice = rawBasePrice * quantity.value
  }

  addToCart(product.value, {
    ...config,
    name: product.value.name,
    totalPrice: rawBasePrice
  })

  // 2. Add Fabric Item
  if (selfSendFabric.value) {
    const fabricItem = {
      name: 'پارچه ارسالی توسط مشتری',
      type: 'fabric',
      price: 0,
      image: '',
      qty: 1,
      config: {
        meters: selfSendMeters.value || totalCalculatedFabric.value,
        note: 'پارچه را خودتان ارسال می‌کنید',
        parent_line_id: parentLineId,
        meta: {
          linked_item_code: activeItemCode,
          fabric_role: 'self-send'
        },
        totalPrice: 0
      }
    }
    addToCart(fabricItem, fabricItem.config)
  } else if (selectedFabric.value) {
    const meters = totalCalculatedFabric.value
    const fabricPrice = calculateFabricPrice(meters, selectedFabric.value.pricePerMeter)
    const fabricItem = {
      name: `پارچه ${selectedFabric.value.qualityName} (${selectedFabric.value.colorName})`,
      type: 'fabric',
      price: fabricPrice,
      image: selectedFabric.value.image,
      qty: 1,
      config: {
        meters,
        quality: selectedFabric.value.qualityName,
        color: selectedFabric.value.colorName,
        parent_line_id: parentLineId,
        meta: {
          linked_item_code: activeItemCode,
          fabric_role: 'main'
        },
        totalPrice: fabricPrice
      }
    }
    addToCart(fabricItem, fabricItem.config)
  }
  
  isCartOpen.value = true
}

const isColorAttribute = (attrName) => {
  const normalized = String(attrName || '').trim()
  return normalized === 'رنگ چوب' || normalized === 'رنگ بدنه' || normalized.includes('رنگ')
}

const getColorHex = (name) => {
  const label = String(name || '')
  const map = {
    'مشکی': '#212121',
    'زغالی': '#2B2B2B',
    'طوسی': '#9E9E9E',
    'سفید': '#F7F7F2',
    'کرم': '#E8DCC8',
    'بژ': '#DCC7A1',
    'عسلی': '#C98A3D',
    'طلایی': '#C9A227',
    'فندقی': '#6B4A2B',
    'گردویی': '#5A3C27',
    'قهوه': '#6F4E37',
    'نقره': '#B0B7C3',
    'خودرنگ': '#CFAE7B',
    'طبیعی': '#CFAE7B'
  }
  for (const key in map) {
    if (label.includes(key)) return map[key]
  }
  return '#8D6E63'
}

const isDarkColorName = (name) => {
  const label = String(name || '')
  return ['مشکی', 'زغالی', 'گردویی', 'فندقی', 'قهوه'].some((token) => label.includes(token))
}

const getColorVisual = (name) => {
  const label = String(name || '')
  if (label.includes('خودرنگ') || label.includes('طبیعی')) {
    return 'linear-gradient(135deg, #e6cfaa 0%, #c89a62 45%, #8b5a2b 100%)'
  }
  return getColorHex(label)
}

const getAttrOptionStyle = (attrName, optionValue, isActive) => {
  if (!isColorAttribute(attrName) || !isActive) return null

  const colorName = String(optionValue || '')
  const darkTone = isDarkColorName(colorName)
  const borderColor = colorName.includes('سفید')
    ? '#BDBDBD'
    : darkTone
      ? 'rgba(255,255,255,0.45)'
      : 'rgba(60,35,18,0.35)'

  return {
    background: getColorVisual(colorName),
    color: darkTone ? '#F9F7F2' : '#2D2019',
    borderColor,
    boxShadow: '0 12px 20px rgba(0,0,0,0.16)'
  }
}

const computeScrollDepth = () => {
  const scrollTop = window.scrollY || window.pageYOffset || 0
  const totalScrollable = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1)
  return Math.max(0, Math.min(100, Math.round((scrollTop / totalScrollable) * 100)))
}

let leaveTracked = false
const trackProductPageLeave = () => {
  if (leaveTracked) return
  leaveTracked = true
  trackAnalyticsEvent('page_view', {
    session_id: getAnalyticsSessionId(),
    model_name: analyticsModelName.value,
    product_id: product.value.item_code || product.value.name || '',
    item_group: product.value.type || '',
    time_spent_seconds: Math.max(1, Math.round((Date.now() - pageEnterEpoch) / 1000)),
    scroll_depth: computeScrollDepth(),
    properties: {
      page: 'product',
      tab: activeTab.value
    }
  })
}

onMounted(() => {
  // Initialize current attributes from product
  if (product.value.attributes) {
    currentAttributes.value = { ...product.value.attributes }
  } else if (siblings.value.length) {
    // Fallback: find this product in siblings to get its attributes
    const self = siblings.value.find(s => s.item_name === product.value.name || s.item_code === product.value.item_code)
    if (self) currentAttributes.value = { ...self.attributes }
  }

  if (currentAttributes.value['رنگ چوب']) {
    selectedWood.value = currentAttributes.value['رنگ چوب']
  }
  if (currentAttributes.value['رنگ بدنه']) {
    selectedBodyColor.value = currentAttributes.value['رنگ بدنه']
  }
  if (!selectedWood.value && availableWoodColors.value.length) selectedWood.value = availableWoodColors.value[0]
  if (!selectedBodyColor.value && availableBodyColors.value.length) selectedBodyColor.value = availableBodyColors.value[0]
  if (selectedWood.value && !currentAttributes.value['رنگ چوب']) currentAttributes.value['رنگ چوب'] = selectedWood.value
  if (selectedBodyColor.value && !currentAttributes.value['رنگ بدنه']) currentAttributes.value['رنگ بدنه'] = selectedBodyColor.value

  trackAnalyticsEvent('product_view', {
    session_id: getAnalyticsSessionId(),
    model_name: analyticsModelName.value,
    product_id: product.value.item_code || product.value.name || '',
    item_group: product.value.type || '',
    amount: Number(product.value.price || 0),
    properties: { page_type: window.PageType || '' }
  })

  window.addEventListener('beforeunload', trackProductPageLeave)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', trackProductPageLeave)
  trackProductPageLeave()
})
</script>

<style scoped>
.product-page {
  min-height: 100vh;
  background: var(--bg-main);
  position: relative;
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
  color: var(--text-main);
}

.liquid-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: var(--blob-opacity);
  animation: float 20s infinite alternate;
}

.blob-1 {
  width: 600px;
  height: 600px;
  background: var(--blob-1);
  top: -200px;
  right: -100px;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: var(--blob-2);
  bottom: -100px;
  left: -100px;
  animation-delay: -5s;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background: var(--blob-3);
  top: 40%;
  left: 30%;
  animation-delay: -10s;
}

@keyframes float {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(50px, 50px) scale(1.1); }
}

/* Header - Floating over mega gallery */
.product-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.header-btn {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(15px);
  border: 1px solid var(--glass-border) !important;
  border-radius: 16px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-main);
}

.glass-label-pill {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  padding: 8px 18px;
  border-radius: 100px;
  font-weight: 700;
  font-size: 14px;
  border: 1px solid var(--glass-border);
  color: var(--text-main);
}
.cart-badge {
  position: absolute; top: -5px; right: -5px; width: 20px; height: 20px;
  background: #ff5252; color: #fff; font-size: 10px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 900;
  border: 2px solid #fff;
}

/* Mega Gallery - Full View Inspiration */
.mega-gallery { 
  position: relative; height: 75vh; width: 100%; z-index: 1; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: transparent;
}
.gallery-inner { width: 100%; height: 80%; display: flex; align-items: center; justify-content: center; padding: 20px; }
.mega-img { max-width: 100%; max-height: 100%; object-fit: contain; transform: translateY(-20px); }

/* Vertical Swatches (Floating Left) */
.vertical-config-sidebar {
  position: absolute; left: 24px; top: 120px; z-index: 20;
  display: flex; flex-direction: column; gap: 16px;
}
.swatch-vertical-track { display: flex; flex-direction: column; gap: 12px; }
.swatch-dot {
  width: 24px; height: 24px; border-radius: 50%; cursor: pointer;
  border: 2px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  transition: all 0.3s; position: relative;
}
.swatch-dot.active { transform: scale(1.4); border-color: #503130; box-shadow: 0 8px 15px rgba(0,0,0,0.15); }
.swatch-dot .tooltip {
  position: absolute; left: 35px; top: 50%; transform: translateY(-50%);
  background: #1a1a1a; color: white; padding: 4px 8px; border-radius: 6px;
  font-size: 10px; visibility: hidden; opacity: 0; white-space: nowrap; transition: 0.2s;
}
.swatch-dot:hover .tooltip { visibility: visible; opacity: 1; }

/* Thumbnails sitting at the bottom of the gallery */
.gallery-thumbnails {
  position: absolute; bottom: 100px; left: 0; right: 0;
  display: flex; justify-content: center; gap: 12px; z-index: 10;
}
.thumb-tile {
  width: 48px; height: 48px; border-radius: 12px; background: rgba(255,255,255,0.6);
  backdrop-filter: blur(10px); padding: 4px; border: 2.5px solid transparent;
  transition: 0.3s; cursor: pointer;
}
.thumb-tile img { width: 100%; height: 100%; object-fit: contain; }
.thumb-tile.active { border-color: #503130; transform: translateY(-5px); }

/* Main Content Info Sheet */
.product-info-sheet {
  position: relative;
  z-index: 30;
  margin-top: -60px;
  background: var(--bg-main);
  backdrop-filter: blur(40px) saturate(180%);
  border-radius: 50px 50px 0 0;
  min-height: 50vh;
  padding-bottom: 140px;
  border-top: 1px solid var(--glass-border);
  box-shadow: 0 -30px 60px rgba(0, 0, 0, 0.2);
}

/* Tab Switcher - Apple Style */
.tab-system-header {
  display: grid; grid-template-columns: 1fr 80px 1fr; align-items: center;
  padding: 10px 20px; border-bottom: 1px solid #F0F0F0;
}
.tab-btn {
  background: none;
  border: none;
  font-family: inherit;
  font-size: 16px;
  font-weight: 800;
  color: var(--text-dim);
  cursor: pointer;
  transition: 0.3s;
  padding: 20px 0;
}
.tab-btn.active { color: var(--text-main); }

.floating-heart-container { display: flex; justify-content: center; position: relative; bottom: 20px; }
.heart-glass-circle {
  width: 56px; height: 56px; border-radius: 50%; background: #FFF;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1); border: 4px solid #FBFBFB;
}

.tab-content-area { padding: 32px 24px; }

/* Title Section */
.product-title { font-size: 28px; font-weight: 900; color: var(--text-main); margin-bottom: 4px; }
.product-category { font-size: 14px; font-weight: 700; color: var(--text-dim); margin-bottom: 20px; }
.product-module-name { font-size: 14px; font-weight: 700; color: var(--accent-orange); margin-bottom: 20px; }
.rating-v-row { display: flex; align-items: center; gap: 8px; margin-bottom: 24px; }
.rating-text { font-size: 13px; color: var(--text-dim); font-weight: 600; }

/* Quick Specs Grid (Technical look) */
.quick-specs-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 32px;
}
.q-spec {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 16px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: transform 0.3s;
}
.q-spec:active { transform: scale(0.95); }
.q-icon { font-size: 20px; }
.q-label { font-size: 11px; color: var(--text-dim); font-weight: 700; text-align: center; }

.product-long-description {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-muted);
  font-weight: 500;
  margin-bottom: 40px;
}

/* Config Items */
.configuration-section { display: flex; flex-direction: column; gap: 32px; }
.config-item { display: flex; flex-direction: column; gap: 14px; }
.item-label { font-size: 12px; font-weight: 900; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; }

.attr-selector { display: flex; flex-wrap: wrap; gap: 10px; }
.attr-option {
  padding: 12px 20px;
  border-radius: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: 0.3s;
  font-weight: 700;
  font-size: 14px;
  color: var(--text-main);
}
.attr-option.active { background: var(--accent-brown); color: var(--accent-gold); border-color: var(--accent-brown); }

.quantity-input-wrap {
  display: flex; align-items: center; gap: 20px; background: #F8F8F8;
  width: fit-content; padding: 6px 16px; border-radius: 100px; border: 1px solid #EEE;
}
.quantity-input-wrap button { background: none; border: none; font-size: 24px; font-weight: 300; color: #503130; cursor: pointer; }
.quantity-input-wrap input { width: 40px; text-align: center; border: none; background: none; font-weight: 900; font-size: 18px; }

/* Fabric Section Mobile */
.fabric-section-mobile { margin-top: 20px; }
.fabric-selector-trigger {
  padding: 16px 20px !important; display: flex; justify-content: space-between; align-items: center; cursor: pointer;
}
.fabric-selector-trigger.warning { border-color: #ff5252; box-shadow: 0 0 10px rgba(255,82,82,0.1); }
.selected-fabric { display: flex; align-items: center; gap: 16px; }
.selected-fabric img { width: 50px; height: 50px; border-radius: 14px; object-fit: cover; }
.fab-info { display: flex; flex-direction: column; gap: 2px; }
.fab-name { font-size: 15px; font-weight: 900; color: var(--text-main); }
.fab-color { font-size: 11px; color: var(--text-dim); }
.fabric-self-send-link {
  margin-top: 10px;
  border: none;
  background: transparent;
  color: var(--text-dim);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-align: right;
  padding: 0;
}
.fabric-self-send-link:hover { color: var(--text-main); }
.placeholder { font-size: 14px; font-weight: 800; color: var(--text-dim); }
.arrow { color: var(--text-main); font-weight: 900; font-size: 20px; }

/* Sofa Specifics */
.modules-grid-premium { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.module-card-liquid {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 16px; position: relative; transition: 0.3s; cursor: pointer;
}
.module-card-liquid.active { border-color: white; background: rgba(255, 255, 255, 0.1); transform: translateY(-4px); }
.mod-img { width: 100%; height: 100px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; margin-bottom: 12px; }
.mod-img img { width: 100%; height: 100%; object-fit: contain; }
.mod-body .n { font-size: 14px; font-weight: 700; color: white; }
.mod-body .p { font-size: 11px; color: #ff9800; font-weight: 800; margin-top: 2px; }
.mod-status {
  position: absolute; bottom: 16px; left: 16px; width: 28px; height: 28px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: #F0F0F0; font-size: 14px; transition: 0.3s;
}
.module-card-liquid.active .mod-status { background: #503130; color: #FFF; }

.selected-summary-box { 
  margin-top: 32px; padding: 20px; background: #FAFAFA; border-radius: 24px; border: 2px dashed #EEE;
}
.selected-modules-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.selected-mod-item { border-radius: 16px; display: flex; align-items: center; gap: 12px; padding: 12px !important; }
.mod-mini-img { width: 50px; height: 50px; border-radius: 8px; background: white; overflow: hidden; }
.mod-mini-img img { width: 100%; height: 100%; object-fit: contain; }
.mod-mini-info .n { font-size: 13px; font-weight: 800; }
.mod-mini-info .p { font-size: 11px; color: #503130; font-weight: 700; }
.remove-btn { 
  margin-right: auto; width: 24px; height: 24px; border-radius: 50%;
  border: none; background: rgba(255,82,82,0.1); color: #ff5252;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
}

/* Reviews List */
.review-stats { text-align: center; margin-bottom: 32px; }
.review-stats .avg { font-size: 48px; font-weight: 900; color: #1a1a1a; }
.review-stats .total { font-size: 13px; color: #AAA; font-weight: 600; }
.reviews-list { display: flex; flex-direction: column; gap: 16px; }
.review-card { padding: 20px !important; border-radius: 20px; }
.r-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.review-card .user { font-weight: 800; font-size: 15px; }
.r-text { font-size: 14px; line-height: 1.7; color: #555; margin: 0 0 12px 0; }
.r-date { font-size: 11px; color: #AAA; font-weight: 600; }

/* Similar Products */
.similar-products-mobile { margin-top: 64px; }
.similar-scroll { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 10px; scrollbar-width: none; }
.similar-mini-card { flex-shrink: 0; width: 120px; cursor: pointer; }
.similar-mini-card img { width: 100%; height: 120px; border-radius: 20px; object-fit: cover; background: #F8F8F8; margin-bottom: 8px; }
.similar-mini-card .n { font-size: 13px; font-weight: 800; text-align: center; color: #333; }

/* Sticky Cta Bar */
.sticky-cta-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 10px 14px calc(10px + env(safe-area-inset-bottom));
  pointer-events: none;
}

.cta-glass-container {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
}
.price-display { display: flex; flex-direction: column; }
.price-display .p-amount { font-size: 18px; font-weight: 900; color: var(--text-main); }
.price-display .p-label { font-size: 10px; font-weight: 800; color: var(--text-dim); text-align: left; }
.main-action-btn { background: var(--accent-brown) !important; color: var(--accent-gold) !important; padding: 12px 24px; border-radius: 14px; font-weight: 900; font-size: 13px; }

/* Lightbox */
.lightbox-overlay {
  position: fixed; inset: 0; z-index: 2000; background: rgba(255,255,255,0.9);
  backdrop-filter: blur(25px); display: flex; flex-direction: column;
}
.close-lightbox { position: absolute; top: 24px; right: 24px; font-size: 32px; background: none; border: none; cursor: pointer; color: #1a1a1a; z-index: 10; }
.lightbox-content { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px; }
.lightbox-content img { max-width: 100%; max-height: 100%; object-fit: contain; }
.lightbox-nav { display: flex; justify-content: center; gap: 8px; padding-bottom: 40px; }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s cubic-bezier(0.19, 1, 0.22, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.animate-fade-in { animation: fadeIn 0.4s both; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.liquid-glass-inner {
  background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.8);
  box-shadow: inset 0 2px 5px rgba(0,0,0,0.01); backdrop-filter: blur(15px);
  border-radius: 24px;
}

/* Fabric Overlays */
.fabric-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.1); backdrop-filter: blur(10px); z-index: 998; display: none; }
.fabric-overlay.active { display: block; }

/* Modal styles for fabric skip */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(15px);
  display: flex; align-items: center; justify-content: center; z-index: 3000; padding: 24px;
}
.modal-card { max-width: 400px; width: 100%; padding: 32px; text-align: center; }
.modal-card h3 { margin: 0 0 16px; font-size: 20px; font-weight: 900; }
.modal-card p { font-size: 14px; color: #666; line-height: 1.7; margin-bottom: 24px; }
.modal-actions { display: flex; flex-direction: column; gap: 12px; }
.meter-input { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 24px; }
.meter-input input {
  width: 80px; padding: 12px; border-radius: 12px; border: 1px solid #EEE;
  font-size: 20px; text-align: center; font-weight: 900; background: #F8F8F8;
}
</style>
