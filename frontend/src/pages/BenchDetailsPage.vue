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
      <!-- Hero Section: Gallery + Config -->
      <div class="hero-composite-container">
        <!-- Mega Full-width Gallery -->
        <div class="mega-gallery">

          <div class="gallery-inner" @click="showLightbox = true; lightboxImageIndex = activeImageIndex">
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

        <!-- Purchase Config Panel -->
        <div class="product-config-panel">
            <div class="config-header">
                <Breadcrumbs :crumbs="breadcrumbs" />
                <h1 class="product-title">{{ product.parent_model_name || product.display_name || product.name }}</h1>
                <p class="product-category">{{ product.category_name }}</p>
                <div class="rating-simple">
                    <span class="stars">⭐⭐⭐⭐☆</span>
                    <span class="count">(۱۰۸ نظر)</span>
                </div>
            </div>

            <!-- Configuration Section -->
            <div class="configuration-section">
              <!-- Dynamic Attributes (Color, Length, etc.) -->
              <div 
                v-for="attr in selectableAttributes" 
                :key="attr.name" 
                class="config-item"
              >
                <div class="item-label">انتخاب {{ attr.name }}</div>
                <div class="attr-selector">
                  <div 
                    v-for="opt in getAttrOptions(attr)" 
                    :key="opt" 
                    class="attr-option"
                    :class="{ active: currentAttributes[attr.name] === opt, disabled: !isAttrOptionEnabled(attr.name, opt), 'is-color-attr': isColorAttribute(attr.name) }"
                    :style="getAttrOptionStyle(attr.name, opt, currentAttributes[attr.name] === opt)"
                    @click="isAttrOptionEnabled(attr.name, opt) && updateAttribute(attr.name, opt)"
                  >
                    {{ cleanAttrValue(opt) }}
                  </div>
                </div>
              </div>

              <!-- Fabric Selection -->
              <div class="config-item fabric-section-mobile" v-if="hasFabricRequirement">
                <!-- Minor Fabric Selection -->
                <div v-if="product.minor_cloth > 0" style="margin-bottom: 12px;">
                  <div class="item-label">انتخاب پارچه جزیی</div>
                  <div 
                    class="fabric-selector-trigger liquid-glass-inner"
                    @click="openFabricPicker('minor')"
                  >
                    <div v-if="selectedMinorFabric" class="selected-fabric">
                      <img :src="getImageUrl(selectedMinorFabric.image)" />
                      <div class="fab-info">
                        <span class="fab-name">{{ selectedMinorFabric.qualityName }}</span>
                        <span class="fab-color">{{ selectedMinorFabric.colorName }}</span>
                      </div>
                    </div>
                    <div v-else class="placeholder">انتخاب پارچه جزیی...</div>
                    <span class="arrow">›</span>
                  </div>
                </div>

                <!-- Main Fabric Selection -->
                <div class="item-label">انتخاب پارچه اصلی</div>
                <div 
                  class="fabric-selector-trigger liquid-glass-inner"
                  @click="openFabricPicker('main')"
                >
                  <div v-if="selectedMainFabric" class="selected-fabric">
                    <img :src="getImageUrl(selectedMainFabric.image)" />
                    <div class="fab-info">
                      <span class="fab-name">{{ selectedMainFabric.qualityName }}</span>
                      <span class="fab-color">{{ selectedMainFabric.colorName }}</span>
                    </div>
                  </div>
                  <div v-else class="placeholder">لطفاً پارچه را انتخاب کنید</div>
                  <span class="arrow">›</span>
                </div>
              </div>
              
              <!-- Quantity -->
              <div class="config-item">
                <div class="item-label">تعداد</div>
                <div class="quantity-input-wrap">
                  <button type="button" @click="quantity > 1 ? quantity-- : null">-</button>
                  <input type="number" v-model.number="quantity" min="1" />
                  <button type="button" @click="quantity++">+</button>
                </div>
              </div>
            </div>
        </div>
      </div>

      <!-- Informational Sections (Tabs) -->
      <div class="product-details-container">
        <!-- Tab Bar -->
        <div class="details-tab-bar">
          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'intro' }"
            @click="activeTab = 'intro'"
          >معرفی</button>
          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'specs' }"
            @click="activeTab = 'specs'"
          >مشخصات</button>
          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'reviews' }"
            @click="activeTab = 'reviews'"
          >دیدگاه‌ها ({{ reviewCount }})</button>
          <button 
            type="button"
            class="tab-btn" 
            :class="{ active: activeTab === 'questions' }"
            @click="activeTab = 'questions'"
          >پرسش‌ها</button>
        </div>

        <div class="details-content-area">
          <!-- Intro -->
          <div v-if="activeTab === 'intro'" class="tab-pane">
            <h2>معرفی محصول</h2>
            <p>{{ sampleDescription }}</p>
          </div>

          <!-- Specs -->
          <div v-if="activeTab === 'specs'" class="tab-pane">
             <h2>مشخصات فنی</h2>
             <div class="specs-grid">
               <div class="spec-row" v-if="product.length"><span>طول</span><span>{{ product.length }} سم</span></div>
               <div class="spec-row" v-if="product.width"><span>عرض</span><span>{{ product.width }} سم</span></div>
               <div class="spec-row" v-if="product.height"><span>ارتفاع</span><span>{{ product.height }} سم</span></div>
               <div class="spec-row" v-if="hasFabricRequirement"><span>نیاز به پارچه</span><span>{{ totalCalculatedFabric }} متر</span></div>
               <div class="spec-row" v-if="product.weight"><span>وزن</span><span>{{ product.weight }} کیلوگرم</span></div>
             </div>
             <ProductFeatureTable :rows="product.feature_rows || []" />
          </div>

          <!-- Reviews -->
          <div v-if="activeTab === 'reviews'" class="tab-pane">
            <ProductFeedbackPanel
              feedback-type="review"
              :model-name="feedbackModelName"
              :item-code="product.item_code || product.name"
              @count-change="(count) => { reviewCount = count }"
            />
          </div>

          <!-- Questions -->
          <div v-if="activeTab === 'questions'" class="tab-pane">
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
        <GlassButton variant="primary" class="main-action-btn" :disabled="!canAddToCart" @click="handleAddToCart">
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
      :selected-fabric="activeFabricType === 'main' ? selectedMainFabric : selectedMinorFabric"
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
import { ref, computed, onMounted, watch } from 'vue'
import GlassButton from '../components/GlassButton.vue'
import FabricSidebar from '../components/FabricSidebar.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import ProductFeedbackPanel from '../components/ProductFeedbackPanel.vue'
import ProductFeatureTable from '../components/ProductFeatureTable.vue'
import { useCart } from '../stores/cartStore'
import { useFabricStore } from '../stores/fabricStore'
import { useVariantConfigurator } from '../composables/useVariantConfigurator'
import {
  calculateFabricPrice,
  computeMainFabricMeters,
  computeMinorFabricMeters,
  resolveClothNeeds,
  toNumber
} from '../utils/fabricPricing'

// --- Data ---
const product = ref(window.ProductDetails || {})
const clothGroups = ref(window.ClothGroups || [])
const similarProducts = ref(window.SimilarProducts || [])
const activeImageIndex = ref(0)
const selectedWood = ref('')
const selectedBodyColor = ref('')
const { selectedFabric: persistedFabric, setSelectedFabric: setPersistedFabric } = useFabricStore()
const selectedMainFabric = ref(persistedFabric.value ? { ...persistedFabric.value } : null)
const selectedMinorFabric = ref(null)
const quantity = ref(1)
const selectedCustomer = ref(window.SelectedCustomer || '')

const variantSchema = computed(() => product.value.attribute_schema || product.value.selectable_attributes || [])
const variantList = computed(() => product.value.variants || [])
const {
  selectedAttributes: currentAttributes,
  currentVariant: currentMatchedVariant,
  selectableAttributes,
  isSelectionComplete,
  isOptionEnabled,
  setAttribute,
  initializeSelection,
} = useVariantConfigurator({
  variants: variantList,
  attributeSchema: variantSchema
})

// --- Mobile Redesign State ---
const activeTab = ref('intro') // 'intro', 'specs', 'reviews', 'questions'
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

const breadcrumbs = computed(() => {
  const list = []
  list.push({ label: 'نیمکت و پاف', route: '/mysite/benches' })
  list.push({ label: product.value.display_name || product.value.name })
  return list
})

const sampleDescription = computed(() => {
  return product.value.description || `این محصول با ترکیبی از سبک مدرن میان‌قرنی و راحتی بی‌نظیر، انتخابی ایده‌آل برای دکوراسیون منزل شماست. بدنه ارگونومیک و استفاده از متریال با کیفیت از ویژگی‌های بارز این مدل می‌باشد.`
})

const cleanAttrValue = (v) => {
  if (!v) return ''
  return v.toString().replace('ارتفاع', '').replace('سانتی متر', '').replace('سم', '').trim()
}

// --- UI State ---
const fabricOpen = ref(false)
const activeFabricType = ref('main') // 'main' or 'minor'
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

const availableWoodColors = computed(() => product.value.all_wood_colors || [])
const availableBodyColors = computed(() => product.value.all_body_colors || [])
const currentClothNeeds = computed(() => resolveClothNeeds(currentMatchedVariant.value, product.value))

const totalCalculatedFabricMain = computed(() => {
  return computeMainFabricMeters(quantity.value, currentClothNeeds.value)
})

const totalCalculatedFabricMinor = computed(() => {
  return computeMinorFabricMeters(quantity.value, currentClothNeeds.value)
})

const totalCalculatedFabric = computed(() => {
  return totalCalculatedFabricMain.value + totalCalculatedFabricMinor.value
})
const hasFabricRequirement = computed(() => totalCalculatedFabric.value > 0)

const totalCalculatedPrice = computed(() => {
  let basePrice = toNumber(currentMatchedVariant.value ? currentMatchedVariant.value.raw_price : product.value.price)
  basePrice = basePrice * quantity.value
  let fabricPrice = 0
  
  if (selectedMainFabric.value && totalCalculatedFabricMain.value > 0) {
    fabricPrice += calculateFabricPrice(totalCalculatedFabricMain.value, selectedMainFabric.value.pricePerMeter)
  }
  if (selectedMinorFabric.value && totalCalculatedFabricMinor.value > 0) {
    fabricPrice += calculateFabricPrice(totalCalculatedFabricMinor.value, selectedMinorFabric.value.pricePerMeter)
  }
  
  return (basePrice + fabricPrice).toLocaleString('fa-IR')
})
const canAddToCart = computed(() => isSelectionComplete.value && !!currentMatchedVariant.value)

// --- Methods ---
const goBack = () => window.history.back()
const formatPrice = (p) => p ? p.toLocaleString('fa-IR') : '۰'
const updateAttribute = (attrName, value) => setAttribute(attrName, value)
const isAttrOptionEnabled = (attrName, option) => isOptionEnabled(attrName, option)
const getAttrOptions = (attr) => attr.options || []
const appendCustomerQuery = (route) => {
  if (!route || !selectedCustomer.value) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

const goToProduct = (route) => {
  if (!route) return
  window.location.href = appendCustomerQuery(route)
}

const getModuleImage = (mod) => ''
const getModuleBasePrice = (mod) => 0
const checkIsSofaModuleSelected = (mod) => false
const addModule = (mod) => {}
const removeModule = (idx) => {}

const openFabricPicker = (type) => {
  activeFabricType.value = type
  fabricOpen.value = true
}

const onFabricSelect = (fabric) => {
  if (activeFabricType.value === 'main') {
    selectedMainFabric.value = fabric
  } else {
    selectedMinorFabric.value = fabric
  }
  setPersistedFabric(fabric)
  fabricOpen.value = false
  selfSendFabric.value = false
}

const handleAddToCart = () => {
  const needsMain = currentClothNeeds.value.odd > 0
  const needsMinor = currentClothNeeds.value.minor > 0

  if (needsMain && !selectedMainFabric.value && !selfSendFabric.value) {
    showFabricWarningModal.value = true
    return
  }
  if (needsMinor && !selectedMinorFabric.value && !selfSendFabric.value) {
    showFabricWarningModal.value = true
    return
  }
  
  onAddToCart()
}

const confirmSelfSendFabric = () => {
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
  let activeItemCode = currentMatchedVariant.value ? currentMatchedVariant.value.item_code : product.value.name
  let rawBasePrice = toNumber(currentMatchedVariant.value ? currentMatchedVariant.value.raw_price : product.value.price)
  const parentLineId = `line-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

  // 1. Add Product Item
  const config = {
    ...currentAttributes.value,
    item_code: activeItemCode,
    qty: quantity.value,
    image: activeImage.value,
    line_id: parentLineId
  }
  
  rawBasePrice = rawBasePrice * quantity.value

  addToCart(product.value, {
    ...config,
    name: product.value.name,
    totalPrice: rawBasePrice,
    display_title: `${product.value.category_name} ${product.value.name} (${Object.values(currentAttributes.value).join('-')})`
  })

  // 2. Add Fabric Items
  if (totalCalculatedFabric.value > 0 || selfSendFabric.value) {
    // Main Fabric
    if (selectedMainFabric.value && totalCalculatedFabricMain.value > 0) {
      const meters = totalCalculatedFabricMain.value
      const price = calculateFabricPrice(meters, selectedMainFabric.value.pricePerMeter)
      const fabricItem = {
        name: `پارچه ${selectedMainFabric.value.qualityName} (${selectedMainFabric.value.colorName}) - بدنه`,
        type: 'fabric',
        price,
        image: selectedMainFabric.value.image,
        qty: 1,
        config: {
          meters,
          quality: selectedMainFabric.value.qualityName,
          color: selectedMainFabric.value.colorName,
          parent_line_id: parentLineId,
          meta: {
            linked_item_code: activeItemCode,
            fabric_role: 'main'
          },
          totalPrice: price
        }
      }
      addToCart(fabricItem, fabricItem.config)
    }

    // Minor Fabric
    if (selectedMinorFabric.value && totalCalculatedFabricMinor.value > 0) {
      const meters = totalCalculatedFabricMinor.value
      const price = calculateFabricPrice(meters, selectedMinorFabric.value.pricePerMeter)
      const fabricItem = {
        name: `پارچه ${selectedMinorFabric.value.qualityName} (${selectedMinorFabric.value.colorName}) - جزیی`,
        type: 'fabric',
        price,
        image: selectedMinorFabric.value.image,
        qty: 1,
        config: {
          meters,
          quality: selectedMinorFabric.value.qualityName,
          color: selectedMinorFabric.value.colorName,
          parent_line_id: parentLineId,
          meta: {
            linked_item_code: activeItemCode,
            fabric_role: 'minor'
          },
          totalPrice: price
        }
      }
      addToCart(fabricItem, fabricItem.config)
    }

    // Self Sent Fabric (Bulk)
    if (selfSendFabric.value) {
      const fabricItem = {
        name: 'پارچه ارسالی توسط مشتری',
        type: 'fabric',
        price: 0,
        image: '',
        qty: 1,
        config: {
          meters: selfSendMeters.value,
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
    }
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

onMounted(() => {
  initializeSelection()
  if (!selectedMainFabric.value && persistedFabric.value) {
    selectedMainFabric.value = { ...persistedFabric.value }
  }
})

watch(
  () => currentAttributes.value,
  (attrs) => {
    selectedWood.value = attrs['رنگ چوب'] || ''
    selectedBodyColor.value = attrs['رنگ بدنه'] || ''
  },
  { immediate: true, deep: true }
)
</script>

<style scoped>
.product-page {
  min-height: 100vh;
  background: var(--bg-main);
  position: relative;
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
  color: var(--text-main);
  overflow-y: auto;
}

@media (min-width: 1024px) {
  .product-page {
    height: auto;
    overflow-y: auto;
  }
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

@media (min-width: 1024px) {
  .liquid-bg {
    opacity: 0.6;
  }
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

@media (min-width: 1024px) {
  .product-header {
    padding: 30px 50px;
    background: linear-gradient(to bottom, rgba(255,255,255,0.8), transparent);
    backdrop-filter: blur(10px);
    position: fixed;
  }
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

/* Base Content Scrollable */
.content-scrollable {
  height: 100%;
  overflow-y: auto;
  scroll-snap-type: y proximity;
  scroll-behavior: smooth;
}

@media (min-width: 1024px) {
  .content-scrollable {
    display: block;
    padding-top: 0;
  }
  .hero-composite-container {
    display: flex;
    height: 100vh;
    width: 100%;
  }
}

/* Mega Gallery - Full View Inspiration */
.mega-gallery { 
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 70vh; 
  z-index: 1; 
  overflow: hidden;
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center;
  background: var(--bg-main);
}
.gallery-inner { width: 100%; height: 80%; display: flex; align-items: center; justify-content: center; padding: 20px; }
.mega-img { max-width: 100%; max-height: 100%; object-fit: contain; }

@media (min-width: 1024px) {
  .mega-gallery {
    position: relative;
    flex: 1;
    height: 100vh;
    margin: 0;
    padding-top: 80px;
    background: rgba(255,255,255,0.2);
  }
  .gallery-inner {
    height: 70%;
  }
  .mega-img {
    transform: none;
    max-width: 85%;
  }
  .gallery-thumbnails {
    bottom: 50px;
  }
  .vertical-config-sidebar {
    left: 40px;
    top: 50%;
    transform: translateY(-50%);
  }
}

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

/* Configuration Panel (Right Column on Desktop) */
.product-config-panel {
  position: relative;
  z-index: 10;
  margin-top: 70vh;
  background: var(--bg-main);
  backdrop-filter: blur(40px) saturate(180%);
  border-radius: 40px 40px 0 0;
  min-height: 20vh;
  padding: 40px 24px 80px;
  border-top: 1px solid var(--glass-border);
  box-shadow: 0 -20px 40px rgba(0, 0, 0, 0.1);
}

@media (max-width: 1024px) {
  .product-config-panel {
    scroll-snap-align: start;
    animation: panel-hop-in 680ms cubic-bezier(0.2, 0.9, 0.24, 1.05) both;
    will-change: transform, opacity;
  }
}

@keyframes panel-hop-in {
  0% {
    opacity: 0;
    transform: translateY(64px) scale(0.98);
  }
  58% {
    opacity: 1;
    transform: translateY(-12px) scale(1.01);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (min-width: 1024px) {
  .product-config-panel {
    width: 550px;
    height: 100vh;
    overflow-y: auto;
    margin-top: 0;
    border-radius: 0;
    border-top: none;
    border-right: 1px solid var(--glass-border);
    background: rgba(255, 255, 255, 0.7);
    padding: 140px 50px 200px;
  }
}

.config-header { margin-bottom: 40px; }
.product-title { font-size: 2.8rem; font-weight: 950; margin: 15px 0 5px; color: var(--text-main); line-height: 1.1; }
.product-category { font-size: 1.1rem; color: var(--accent-gold); font-weight: 800; opacity: 0.9; }
.rating-simple { display: flex; align-items: center; gap: 10px; margin-top: 10px; font-size: 0.9rem; }

/* Informational Container (Below Hero) */
.product-details-container {
  background: #FFF;
  padding: 40px 0 120px;
  position: relative;
  z-index: 11;
  margin-top: 0;
  min-height: 80vh; /* Ensure it reaches footer on short content */
}

.details-tab-bar {
  display: flex;
  justify-content: center;
  gap: 40px;
  border-bottom: 1px solid #EEE;
  margin-bottom: 50px;
  padding: 0 20px;
}

.tab-btn {
  padding: 15px 5px;
  font-family: inherit;
  font-size: 1.1rem;
  font-weight: 800;
  color: #999;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn.active {
  color: var(--accent-brown);
  border-bottom-color: var(--accent-gold);
}

.details-content-area {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 30px;
}

.tab-pane h2 { font-size: 2rem; font-weight: 900; margin-bottom: 25px; color: var(--text-main); }
.tab-pane p { line-height: 2; font-size: 1.15rem; color: #555; text-align: justify; }

.specs-grid { display: flex; flex-direction: column; gap: 15px; }
.spec-row { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px dashed #DDD; }
.spec-row span:first-child { font-weight: 900; color: #777; }
.spec-row span:last-child { font-weight: 700; color: var(--text-main); }

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

@media (min-width: 1024px) {
  .quick-specs-grid {
    grid-template-columns: repeat(2, 1fr);
  }
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
.attr-option.disabled { opacity: 0.45; cursor: not-allowed; }

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
  z-index: 4000;
  padding: 20px 24px calc(24px + env(safe-area-inset-bottom));
  pointer-events: none; /* Allow clicking through the bar area */
}

.cta-glass-container {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  pointer-events: auto; /* Re-enable clicks for the actual pill */
}
.price-display { display: flex; flex-direction: column; }
.price-display .p-amount { font-size: 26px; font-weight: 900; color: var(--text-main); }
.price-display .p-label { font-size: 11px; font-weight: 800; color: var(--text-dim); text-align: left; }
.main-action-btn { background: var(--accent-brown) !important; color: var(--accent-gold) !important; padding: 18px 40px; border-radius: 20px; font-weight: 900; }

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
