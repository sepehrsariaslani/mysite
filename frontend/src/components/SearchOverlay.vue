<template>
  <transition name="search-transition">
    <div v-if="isOpen" class="search-overlay" dir="rtl" @keydown.esc="close">
      <!-- Animated Liquid Background Elements -->
      <div class="background-blobs">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
      </div>
      
      <div class="overlay-content" @click.self="close">
        <div class="liquid-glass-container animate-search-in">
          <div class="search-header">
            <div class="search-input-wrapper">
              <div class="search-icon-glow">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </div>
              <input 
                ref="searchInput"
                v-model="query" 
                type="text" 
                placeholder="چیزی بنویسید (مثلاً: اورامان)..."
                @input="handleInput"
                autoFocus
              />
              <button v-if="query" class="clear-btn" @click="query = ''; results = null">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            <button class="close-btn" @click="close">
              <span>بستن</span>
              <div class="btn-glow"></div>
            </button>
          </div>

          <div class="search-body custom-scrollbar">
            <!-- Initial suggestions -->
            <div v-if="!query && !loading" class="initial-view">
              <h3 class="group-label">پرجستجوترین‌ها</h3>
              <div class="suggestion-tags">
                <button v-for="tag in ['اورامان', 'نیلپر', 'صندلی اپن', 'کنج', 'میز ناهارخوری']" 
                        :key="tag" @click="query = tag; handleInput()" class="tag-pill">
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="liquid-loader">
              <div class="pulse"></div>
              <span>در حال جستجو در کل سایت...</span>
            </div>

            <!-- Results -->
            <div v-if="results && !loading" class="results-layout">
              <!-- No Results -->
              <div v-if="!hasResults" class="empty-state">
                <div class="empty-glow"></div>
                <p>متأسفانه موردی برای «{{ query }}» پیدا نشد.</p>
              </div>

              <!-- Products Section -->
              <div v-if="results.items?.length" class="result-group">
                <h3 class="group-label">محصولات</h3>
                <div class="result-grid">
                  <a
                    v-for="item in results.items"
                    :key="item._grouped_key || `${item.name || item.item_name}-${item.kind || 'product'}`"
                    :href="resolveProductRoute(item)"
                    class="glass-result product-card"
                  >
                    <div class="img-wrap">
                      <img :src="item.image || '/assets/mysite/img/placeholder.png'" />
                    </div>
                    <div class="info">
                      <span class="name">{{ item.item_name }}</span>
                      <span class="category">
                        {{ item.item_group || 'محصول' }}
                        <template v-if="item.base_price > 0"> • {{ formatPrice(item.base_price) }}</template>
                      </span>
                      <span class="summary" v-if="item.summary">{{ item.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Collections Section -->
              <div v-if="results.models?.length" class="result-group">
                <h3 class="group-label">کالکشن‌ها</h3>
                <div class="result-grid">
                  <a v-for="model in results.models" :key="model.name" :href="model.route" class="glass-result collection-card">
                    <div class="img-wrap">
                      <img :src="model.sofa_main_photo || '/assets/mysite/img/placeholder.png'" />
                    </div>
                    <div class="info">
                      <span class="name">{{ model.sofa_model_name }}</span>
                      <span class="category">مجموعه مبلمان</span>
                      <span class="summary" v-if="model.summary">{{ model.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Projects Section -->
              <div v-if="results.projects?.length" class="result-group">
                <h3 class="group-label">پروژه‌ها</h3>
                <div class="result-grid">
                  <a v-for="project in results.projects" :key="project.name" :href="project.route" class="glass-result project-card">
                    <div class="img-wrap">
                      <img :src="project.image || '/assets/mysite/img/placeholder.png'" />
                    </div>
                    <div class="info">
                      <span class="name">{{ project.title }}</span>
                      <span class="category">
                        {{ project.project_type_label || 'پروژه' }}
                        <template v-if="project.location"> • {{ project.location }}</template>
                      </span>
                      <span class="summary" v-if="project.summary">{{ project.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Gallery Section -->
              <div v-if="results.gallery?.length" class="result-group">
                <h3 class="group-label">گالری</h3>
                <div class="result-grid">
                  <a v-for="entry in results.gallery" :key="entry.name" :href="entry.route" class="glass-result gallery-card">
                    <div class="img-wrap">
                      <img :src="entry.image || '/assets/mysite/img/placeholder.png'" />
                    </div>
                    <div class="info">
                      <span class="name">{{ entry.title }}</span>
                      <span class="category">
                        {{ entry.category || 'گالری محصولات' }}
                        <template v-if="entry.base_price > 0"> • {{ formatPrice(entry.base_price) }}</template>
                      </span>
                      <span class="summary" v-if="entry.summary">{{ entry.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Pages Section -->
              <div v-if="results.pages?.length" class="result-group">
                <h3 class="group-label">صفحات سایت</h3>
                <div class="result-grid">
                  <a v-for="page in results.pages" :key="page.route" :href="page.route" class="glass-result page-card">
                    <div class="img-wrap page-icon-wrap">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="4" y="3" width="16" height="18" rx="2"></rect>
                        <line x1="8" y1="8" x2="16" y2="8"></line>
                        <line x1="8" y1="12" x2="16" y2="12"></line>
                        <line x1="8" y1="16" x2="13" y2="16"></line>
                      </svg>
                    </div>
                    <div class="info">
                      <span class="name">{{ page.title }}</span>
                      <span class="category">صفحه</span>
                      <span class="summary" v-if="page.summary">{{ page.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Blog Section -->
              <div v-if="results.posts?.length" class="result-group">
                <h3 class="group-label">بلاگ</h3>
                <div class="result-grid">
                  <a v-for="post in results.posts" :key="post.name" :href="post.route || '/blog'" class="glass-result blog-card">
                    <div class="img-wrap">
                      <img :src="post.meta_image || '/assets/mysite/img/placeholder.png'" />
                    </div>
                    <div class="info">
                      <span class="name">{{ post.title }}</span>
                      <span class="category">{{ post.blog_category || 'وبلاگ دن‌روم' }}</span>
                      <span class="summary" v-if="post.summary">{{ post.summary }}</span>
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const query = ref('')
const results = ref(null)
const loading = ref(false)
const searchInput = ref(null)

const hasResults = computed(() => {
  if (!results.value) return false
  return (results.value.items?.length || 0) + 
         (results.value.models?.length || 0) + 
         (results.value.posts?.length || 0) +
         (results.value.projects?.length || 0) +
         (results.value.gallery?.length || 0) +
         (results.value.pages?.length || 0) > 0
})

let debounceTimeout = null

function getSelectedCustomer() {
  if (window.SelectedCustomer) return window.SelectedCustomer
  try {
    return localStorage.getItem('mysite_selected_customer') || ''
  } catch (e) {
    return ''
  }
}

function buildSearchUrl() {
  const base = `/api/method/mysite.www.mysite.product.search_everything?query=${encodeURIComponent(query.value)}`
  const customer = getSelectedCustomer()
  if (!customer) return base
  return `${base}&customer=${encodeURIComponent(customer)}`
}

function formatPrice(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function resolveProductRoute(item) {
  const route = String(item?.route || '').trim()
  if (route) return route
  const name = String(item?.item_name || item?.name || '').trim()
  if (!name) return '/products'
  const kind = String(item?.kind || '').trim()
  let fallback = `/product?name=${encodeURIComponent(name)}`
  if (kind) fallback += `&kind=${encodeURIComponent(kind)}`
  return fallback
}

const handleInput = () => {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  
  if (!query.value || query.value.trim().length < 2) {
    results.value = null
    loading.value = false
    return
  }

  loading.value = true
  debounceTimeout = setTimeout(async () => {
    try {
      trackAnalyticsEvent('site_search', {
        properties: {
          query: query.value,
          source: 'search_overlay'
        }
      })
      const resp = await fetch(buildSearchUrl())
      const data = await resp.json()
      results.value = data.message
    } catch (e) {
      console.error('Search failed:', e)
    } finally {
      loading.value = false
    }
  }, 400)
}

const close = () => {
  query.value = ''
  results.value = null
  emit('close')
}

watch(() => props.isOpen, (val) => {
  if (val) {
    nextTick(() => searchInput.value?.focus())
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Background Blobs for Liquid Feel */
.background-blobs {
  position: absolute;
  inset: 0;
  background: var(--bg-footer);
  backdrop-filter: blur(40px);
  overflow: hidden;
}

.blob {
  position: absolute;
  filter: blur(80px);
  border-radius: 50%;
  opacity: 0.4;
  animation: moveBlob 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}

.blob-1 { width: 400px; height: 400px; background: var(--accent-gold); top: -100px; left: -100px; }
.blob-2 { width: 500px; height: 500px; background: var(--accent-brown); bottom: -100px; right: -100px; animation-duration: 25s; }
.blob-3 { width: 300px; height: 300px; background: var(--accent-orange); top: 30%; right: 20%; animation-duration: 18s; }

@keyframes moveBlob {
  from { transform: translate(0, 0) rotate(0deg); }
  to { transform: translate(100px, 50px) rotate(90deg); }
}

.overlay-content {
  width: 100%;
  height: 100%;
  display: flex;
  padding: 40px;
  justify-content: center;
  z-index: 2;
}

.liquid-glass-container {
  width: 100%;
  max-width: 1000px;
  height: min-content;
  max-height: 85vh;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 40px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* Header Section */
.search-header {
  padding: 32px 40px;
  display: flex;
  align-items: center;
  gap: 32px;
  border-bottom: 1px solid var(--glass-border);
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
}

.search-icon-glow {
  color: var(--accent-gold);
  filter: drop-shadow(0 0 8px var(--accent-gold));
  width: 28px;
}

.search-input-wrapper input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-main);
  font-family: inherit;
  letter-spacing: -0.5px;
}

.search-input-wrapper input:focus { outline: none; }
.search-input-wrapper input::placeholder { color: var(--text-dim); }

.clear-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  padding: 12px 28px;
  border-radius: 20px;
  color: var(--text-main);
  font-weight: 800;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.close-btn:hover { background: var(--glass-bg-hover); border-color: var(--accent-gold); }

/* Body Section */
.search-body {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

.group-label {
  font-size: 0.95rem;
  font-weight: 900;
  color: var(--accent-gold);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 24px;
  opacity: 0.9;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.tag-pill {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  padding: 12px 24px;
  border-radius: 100px;
  color: var(--text-main);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-pill:hover {
  background: var(--accent-gold);
  color: var(--accent-brown);
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(242, 201, 126, 0.2);
}

/* Results Layout */
.results-layout { display: flex; flex-direction: column; gap: 56px; }

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.glass-result {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 28px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 20px;
  text-decoration: none;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.glass-result:hover {
  background: var(--glass-bg-hover);
  border-color: var(--accent-gold);
  transform: translateX(-10px);
}

.img-wrap {
  width: 80px;
  height: 80px;
  background: var(--table-bg);
  border-radius: 20px;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.img-wrap img { max-width: 100%; max-height: 100%; object-fit: contain; }
.page-icon-wrap svg {
  width: 30px;
  height: 30px;
  color: var(--text-main);
  opacity: 0.8;
}

.info { display: flex; flex-direction: column; gap: 4px; }
.info .name { color: var(--text-main); font-weight: 800; font-size: 1.1rem; }
.info .category { color: var(--text-dim); font-size: 0.85rem; }
.info .summary {
  color: var(--text-dim);
  font-size: 0.78rem;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Loader */
.liquid-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 24px;
}

.pulse {
  width: 60px;
  height: 60px;
  background: var(--accent-gold);
  border-radius: 50%;
  animation: liquidPulse 1.5s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
  filter: blur(10px);
  opacity: 0.6;
}

@keyframes liquidPulse {
  from { transform: scale(0.8); border-radius: 50% 40% 60% 45% / 45% 60% 40% 55%; }
  to { transform: scale(1.2); border-radius: 40% 60% 45% 55% / 60% 45% 55% 40%; }
}

/* Animations */
.animate-search-in {
  animation: searchIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes searchIn {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.search-transition-enter-active, .search-transition-leave-active { transition: all 0.5s ease; }
.search-transition-enter-from, .search-transition-leave-to { opacity: 0; }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--accent-gold); }

/* Mobile */
@media (max-width: 768px) {
  .overlay-content { padding: 0; }
  .liquid-glass-container { max-height: 100vh; border-radius: 0; border: none; }
  .search-input-wrapper input { font-size: 1.3rem; }
  .search-header { padding: 20px; }
  .result-grid { grid-template-columns: 1fr; }
}
</style>
