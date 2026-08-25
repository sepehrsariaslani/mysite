<template>
  <div class="categories-page" dir="rtl">
    <!-- Liquid Background -->
    <div class="liquid-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <!-- Header Section -->
    <header class="page-header animate-fade-down">
      <div class="header-glass-card">
        <h1 class="page-title">کالکشن‌های <span class="highlight">دن‌روم</span></h1>
        <p class="page-subtitle">دنیایی از طراحی مدرن برای تمام بخش‌های خانه شما</p>
        
        <!-- Premium Search Box -->
        <div class="premium-search-wrap">
          <div class="search-inner glass-morph">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="نام محصول یا دسته‌بندی را جستجو کنید..." 
              autocomplete="off"
            >
          </div>
        </div>
      </div>
    </header>

    <!-- Filters Area -->
    <div class="filter-section animate-fade-up">
      <div class="filter-glass-dock">
        <button 
          v-for="filter in filters" 
          :key="filter.id"
          class="glass-pill"
          :class="{ active: activeFilter === filter.id }"
          @click="activeFilter = filter.id"
        >
          {{ filter.name }}
        </button>
      </div>
    </div>

    <!-- Grid Layout -->
    <main class="grid-section">
      <div v-if="filteredCategories.length" class="glass-grid">
        <a 
          v-for="(cat, idx) in filteredCategories" 
          :key="cat.id"
          :href="`/mysite/${cat.route}`"
          class="cat-tile-link animate-scroll"
          :style="{ transitionDelay: (idx * 0.05) + 's' }"
        >
          <div class="cat-tile liquid-glass-card">
            <div class="tile-img-wrap">
              <img :src="cat.image" :alt="cat.name" class="tile-img" />
              <div class="tile-overlay"></div>
            </div>
            <div class="tile-content">
              <div class="tile-meta">
                <span class="tile-count">{{ cat.count }} محصول</span>
                <span v-if="cat.tag" class="tile-tag">{{ cat.tag }}</span>
              </div>
              <h2 class="tile-name">{{ cat.name }}</h2>
              <div class="tile-action">
                <span>بررسی محصولات</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="18">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
            </div>
          </div>
        </a>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state glass-card">
        <div class="empty-icon">📂</div>
        <h3>نتیجه‌ای یافت نشد</h3>
        <p>جستجوی دیگری را امتحان کنید.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

const categories = ref(window.Categories || [])
const searchQuery = ref('')
const activeFilter = ref('all')

const filters = [
  { id: 'all', name: 'همه دسته‌ها' },
  { id: 'furniture', name: 'مبلمان' },
  { id: 'chairs', name: 'صندلی' },
  { id: 'tables', name: 'میز' },
  { id: 'accessories', name: 'اکسسوری' }
]

const filteredCategories = computed(() => {
  let result = categories.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c => c.name.toLowerCase().includes(q))
  }
  if (activeFilter.value !== 'all') {
    result = result.filter(c => (c.type || c.id) === activeFilter.value)
  }
  return result
})

onMounted(() => {
  trackAnalyticsEvent('page_view', {
    page_url: '/mysite/categories',
    properties: { page: 'categories' }
  })

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('in-view')
    })
  }, { threshold: 0.1 })
  document.querySelectorAll('.animate-scroll').forEach(el => observer.observe(el))
})

watch(activeFilter, (value) => {
  trackAnalyticsEvent('category_filter_apply', {
    item_group: value || '',
    properties: { filter: value || 'all' }
  })
})

let searchTimer = null
watch(searchQuery, (value) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    if (!String(value || '').trim()) return
    trackAnalyticsEvent('site_search', {
      properties: {
        query: String(value || '').trim(),
        page: 'categories'
      }
    })
  }, 450)
})
</script>

<style scoped>
.categories-page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  padding-bottom: 120px;
  position: relative;
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
}

/* Background Blobs */
.liquid-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: var(--blob-opacity); }
.blob-1 { width: 500px; height: 500px; background: var(--blob-1); top: -100px; left: -100px; }
.blob-2 { width: 600px; height: 600px; background: var(--blob-2); bottom: -100px; right: -100px; }

/* Header */
.page-header {
  padding: 120px 24px 60px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.header-glass-card {
  max-width: 800px;
  margin: 0 auto;
  background: var(--glass-bg);
  backdrop-filter: blur(40px);
  padding: 60px 40px;
  border-radius: 40px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 20px 50px rgba(0,0,0,0.1);
}

.page-title { font-size: 3.5rem; font-weight: 900; color: var(--text-main); margin-bottom: 16px; }
.highlight { color: var(--accent-gold); }
.page-subtitle { font-size: 1.1rem; color: var(--text-muted); font-weight: 500; margin-bottom: 40px; }

/* Search Box */
.premium-search-wrap { max-width: 500px; margin: 0 auto; }
.search-inner {
  display: flex;
  align-items: center;
  padding: 6px 20px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  transition: 0.3s;
}
.search-inner:focus-within { border-color: var(--accent-gold); transform: translateY(-2px); }

.search-icon { width: 24px; color: var(--text-dim); margin-left: 14px; }
.search-inner input {
  flex: 1;
  border: none; background: none;
  padding: 14px 0; font-size: 1rem;
  font-family: inherit; font-weight: 600;
  color: var(--text-main); outline: none;
}
.search-inner input::placeholder { color: var(--text-dim); }

/* Filter Dock */
.filter-section {
  position: sticky; top: 100px;
  z-index: 100;
  display: flex; justify-content: center;
  padding: 0 24px; margin-bottom: 60px;
}
.filter-glass-dock {
  background: var(--bg-secondary);
  backdrop-filter: blur(20px);
  padding: 8px;
  border-radius: 20px;
  display: flex; gap: 8px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}
.glass-pill {
  border: none; background: none;
  padding: 10px 24px; border-radius: 14px;
  font-size: 14px; font-weight: 700;
  color: var(--text-muted); cursor: pointer;
  transition: 0.3s;
}
.glass-pill.active { background: var(--accent-gold); color: var(--accent-brown); font-weight: 800; }
.glass-pill:hover:not(.active) { background: var(--glass-bg-hover); color: var(--text-main); }

/* Grid */
.grid-section { max-width: 1400px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }
.glass-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 32px;
}

.cat-tile-link { text-decoration: none; display: block; }
.cat-tile {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-radius: 40px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  transition: 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  height: 100%;
}
.cat-tile-link:hover .cat-tile { transform: translateY(-12px); border-color: var(--accent-gold); box-shadow: 0 40px 80px rgba(0,0,0,0.2); }

.tile-img-wrap { height: 260px; position: relative; overflow: hidden; background: #fafafa; }
.tile-img { width: 100%; height: 100%; object-fit: cover; transition: 0.8s; }
.cat-tile-link:hover .tile-img { transform: scale(1.1); }
.tile-overlay { position: absolute; inset: 0; background: linear-gradient(to top, var(--bg-footer) 0%, transparent 60%); }

.tile-content { padding: 32px; text-align: right; color: var(--text-main); }
.tile-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.tile-count { font-size: 12px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; }
.tile-tag { background: var(--accent-orange); color: white; padding: 4px 12px; border-radius: 8px; font-size: 11px; font-weight: 900; }

.tile-name { font-size: 1.8rem; font-weight: 900; color: var(--text-main); margin-bottom: 24px; transition: 0.3s; }
.cat-tile-link:hover .tile-name { color: var(--accent-gold); }

.tile-action {
  display: flex; align-items: center; gap: 8px;
  font-weight: 800; color: var(--text-main); font-size: 14px;
}
.tile-action svg { transition: 0.3s; }
.cat-tile-link:hover .tile-action svg { transform: translateX(-6px); }

/* States */
.empty-state { padding: 80px 40px; text-align: center; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 20px 60px rgba(0,0,0,0.05); }
.empty-icon { font-size: 48px; margin-bottom: 20px; }
.empty-state h3 { font-size: 1.5rem; font-weight: 950; color: var(--text-main); }

/* Animations */
.animate-fade-down { opacity: 0; transform: translateY(-20px); animation: fadeDown 0.8s forwards; }
@keyframes fadeDown { to { opacity: 1; transform: translateY(0); } }

.animate-fade-up { opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s 0.2s forwards; }
@keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }

.animate-scroll { opacity: 0; transform: translateY(40px); transition: 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-scroll.in-view { opacity: 1; transform: translateY(0); }

/* Mobile */
@media (max-width: 768px) {
  .header-glass-card { padding: 40px 20px; border-radius: 30px; }
  .page-title { font-size: 2.2rem; }
  .grid-section { padding: 0 16px; }
  .glass-grid { grid-template-columns: 1fr; }
  .filter-glass-dock { overflow-x: auto; max-width: 100%; white-space: nowrap; padding: 4px; }
  .glass-pill { padding: 8px 16px; font-size: 12px; }
}
</style>
