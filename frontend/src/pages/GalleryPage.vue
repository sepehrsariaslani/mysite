<template>
  <div class="gallery-page" dir="rtl">

    <!-- Blobs -->
    <div class="liquid-bg">
      <div class="blob b1"></div>
      <div class="blob b2"></div>
      <div class="blob b3"></div>
    </div>

    <!-- ── Header ── -->
    <header class="gallery-header">
      <div class="gh-inner">
        <div class="gh-text">
          <span class="gh-eyebrow">کالکشن اینسپیره</span>
          <h1 class="gh-title">گالری <span class="gold">دن‌روم</span></h1>
          <p class="gh-sub">ایده بگیر، انتخاب کن، بساز</p>
        </div>

        <div class="gallery-toolbar">
          <div class="search-pill">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="search" type="text" placeholder="جستجو در گالری..." />
          </div>
          <div class="filter-chips">
            <button
              v-for="f in filters" :key="f.id"
              class="chip" :class="{ active: activeFilter === f.id }"
              @click="activeFilter = f.id"
            >{{ f.label }}</button>
          </div>
        </div>
      </div>
    </header>

    <!-- ── Masonry Grid ── -->
    <main class="gallery-main">
      <div class="masonry">
        <div
          v-for="(item, i) in filteredItems"
          :key="item.id"
          class="masonry-item"
          :class="item.size"
          @click="openModal(item)"
        >
          <div class="card-glass"></div>
          <div class="card-img-wrap">
            <img :src="item.img" :alt="item.title" loading="lazy" />
            <div class="card-overlay"></div>
          </div>

          <span class="card-tag">{{ item.category }}</span>

          <div class="card-content">
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-desc">{{ item.desc }}</p>
            <a :href="item.url" class="card-cta" @click.stop>
              <span>مشاهده محصول</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
          </div>

          <button class="save-btn" @click.stop="toggleSave(item.id)" :class="{ saved: saved.has(item.id) }">
            <svg width="16" height="16" viewBox="0 0 24 24" :fill="saved.has(item.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="filteredItems.length === 0" class="empty">
        <div class="empty-icon">🔍</div>
        <h3>نتیجه‌ای یافت نشد</h3>
        <p>فیلتر دیگری را امتحان کنید</p>
      </div>
    </main>

    <!-- ── Lightbox Modal ── -->
    <transition name="modal">
      <div v-if="modalItem" class="modal-wrap" @click.self="modalItem = null">
        <div class="modal-card">
          <div class="modal-glass"></div>
          <button class="modal-close" @click="modalItem = null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="modal-img-wrap">
            <img :src="modalItem.img" :alt="modalItem.title" />
          </div>
          <div class="modal-info">
            <span class="modal-tag">{{ modalItem.category }}</span>
            <h2 class="modal-title">{{ modalItem.title }}</h2>
            <p class="modal-desc">{{ modalItem.desc }}</p>
            <a :href="modalItem.url" class="modal-btn">
              مشاهده و سفارش
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const activeFilter = ref('all')
const modalItem = ref(null)
const SAVED_KEY = 'denroom_saved_products'

function loadSavedProducts() {
  try {
    const raw = localStorage.getItem(SAVED_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch (e) {
    return []
  }
}

function persistSavedProducts(list) {
  try {
    localStorage.setItem(SAVED_KEY, JSON.stringify(list))
  } catch (e) {
    // ignore storage failures
  }
}

const savedProducts = ref(loadSavedProducts())
const saved = ref(new Set(savedProducts.value.map(p => p.id)))

function openModal(item) { modalItem.value = item }
function toggleSave(id) {
  const s = new Set(saved.value)
  if (s.has(id)) {
    s.delete(id)
    savedProducts.value = savedProducts.value.filter(p => p.id !== id)
  } else {
    s.add(id)
    const item = items.value.find(i => i.id === id)
    if (item) {
      savedProducts.value = [item, ...savedProducts.value.filter(p => p.id !== id)]
    }
  }
  saved.value = s
  persistSavedProducts(savedProducts.value)
}

// ── داده از server (gallery.py → window) ──
// اگر window._GALLERY_ITEMS خالی بود، آرایه خالی برمی‌گردونه
const filters = ref(
  (window._GALLERY_FILTERS && window._GALLERY_FILTERS.length)
    ? window._GALLERY_FILTERS
    : [{ id: 'all', label: 'همه' }]
)

const items = ref(
  (window._GALLERY_ITEMS && window._GALLERY_ITEMS.length)
    ? window._GALLERY_ITEMS
    : []
)

const filteredItems = computed(() => {
  let r = items.value
  if (activeFilter.value !== 'all')
    r = r.filter(i => i.filter === activeFilter.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i =>
      String(i.title || '').toLowerCase().includes(q) ||
      String(i.category || '').toLowerCase().includes(q)
    )
  }
  return r
})
</script>

<style scoped>
.gallery-page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  font-family: 'Peyda', sans-serif;
  padding-bottom: 120px;
  position: relative;
  overflow-x: hidden;
}

.liquid-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.blob { position: absolute; border-radius: 50%; filter: blur(90px); opacity: var(--blob-opacity); }
.b1 { width: 500px; height: 500px; background: var(--blob-1); top: -100px; right: -150px; animation: bf 18s infinite alternate; }
.b2 { width: 600px; height: 600px; background: var(--blob-2); bottom: 0; left: -150px; animation: bf 22s 2s infinite alternate; }
.b3 { width: 400px; height: 400px; background: var(--blob-3); top: 40%; left: 30%; animation: bf 15s 1s infinite alternate; }
@keyframes bf { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(30px,40px) scale(1.1); } }

.gallery-header { position: relative; z-index: 2; padding: 100px 24px 40px; }
.gh-inner { max-width: 1300px; margin: 0 auto; }
.gh-eyebrow {
  display: inline-block; font-size: 11px; font-weight: 900; letter-spacing: 0.2em;
  color: var(--accent-gold); text-transform: uppercase;
  background: var(--glass-bg); padding: 5px 14px;
  border-radius: 100px; border: 1px solid var(--glass-border); margin-bottom: 16px;
}
.gh-title { font-size: clamp(2.4rem, 6vw, 4rem); font-weight: 950; margin: 0 0 10px; line-height: 1.1; }
.gold { color: var(--accent-gold); }
.gh-sub { font-size: 1.1rem; color: var(--text-muted); font-weight: 600; margin-bottom: 40px; }

.gallery-toolbar { display: flex; flex-direction: column; gap: 16px; }
.search-pill {
  display: flex; align-items: center; gap: 12px;
  background: var(--glass-bg); border: 1px solid var(--glass-border);
  border-radius: 100px; padding: 10px 20px; max-width: 480px;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.search-pill:focus-within { border-color: var(--accent-gold); box-shadow: 0 0 0 3px rgba(242,201,126,0.12); }
.search-pill svg { color: var(--text-muted); flex-shrink: 0; }
.search-pill input { flex: 1; border: none; background: none; outline: none; font-size: 14px; font-family: inherit; font-weight: 600; color: var(--text-main); }
.search-pill input::placeholder { color: var(--text-muted); }

.filter-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip {
  background: var(--glass-bg); border: 1px solid var(--glass-border);
  color: var(--text-muted); font-size: 13px; font-weight: 700;
  padding: 7px 18px; border-radius: 100px; cursor: pointer;
  transition: all 0.25s; font-family: inherit;
}
.chip:hover { color: var(--text-main); border-color: var(--glass-border-bright); }
.chip.active { background: var(--accent-gold); color: var(--accent-brown); border-color: var(--accent-gold); box-shadow: 0 4px 14px rgba(242,201,126,0.35); }

.gallery-main { position: relative; z-index: 2; max-width: 100%; margin: 0 auto; padding: 0 20px; }
.masonry { columns: 5; column-gap: 16px; }

.masonry-item {
  position: relative; break-inside: avoid; margin-bottom: 16px;
  border-radius: 22px; overflow: hidden; cursor: pointer;
  transition: transform 0.4s cubic-bezier(0.16,1,0.3,1), box-shadow 0.4s;
}
.masonry-item:hover { transform: translateY(-6px); box-shadow: 0 30px 70px rgba(0,0,0,0.3); }

.masonry-item.tall   .card-img-wrap { height: 380px; }
.masonry-item.normal .card-img-wrap { height: 260px; }
.masonry-item.wide   .card-img-wrap { height: 220px; }

.card-glass {
  position: absolute; inset: 0; border: 1px solid var(--glass-border);
  border-radius: inherit; pointer-events: none; z-index: 3;
  background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, transparent 50%);
}
.card-img-wrap { width: 100%; position: relative; overflow: hidden; background: var(--glass-bg); }
.card-img-wrap img { width: 100%; height: 100%; object-fit: contain; background: #f5f5f5; transition: transform 0.7s cubic-bezier(0.16,1,0.3,1); display: block; }
.masonry-item:hover .card-img-wrap img { transform: scale(1.07); }

.card-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(10,10,10,0.85) 0%, rgba(10,10,10,0.1) 55%, transparent 100%);
  transition: opacity 0.4s; opacity: 0.5;
}
.masonry-item:hover .card-overlay { opacity: 1; }

.card-tag {
  position: absolute; top: 14px; right: 14px;
  background: rgba(10,10,10,0.55); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15); color: rgba(255,255,255,0.9);
  font-size: 11px; font-weight: 800; letter-spacing: 0.05em;
  padding: 4px 12px; border-radius: 100px; z-index: 4;
}

.card-content {
  position: absolute; bottom: 0; left: 0; right: 0;
  z-index: 4; padding: 20px 18px;
  opacity: 0; transform: translateY(12px);
  transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
}
.masonry-item:hover .card-content { opacity: 1; transform: translateY(0); }
.card-title { font-size: 15px; font-weight: 900; color: #fff; margin: 0 0 4px; }
.card-desc { font-size: 12px; color: rgba(255,255,255,0.75); margin: 0 0 12px; font-weight: 600; }

.card-cta {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(242,201,126,0.2); backdrop-filter: blur(8px);
  border: 1px solid rgba(242,201,126,0.5); color: var(--accent-gold);
  font-size: 12px; font-weight: 900; padding: 7px 14px;
  border-radius: 100px; text-decoration: none; transition: background 0.2s;
}
.card-cta:hover { background: rgba(242,201,126,0.35); }

.save-btn {
  position: absolute; top: 14px; left: 14px; z-index: 5;
  width: 34px; height: 34px; border-radius: 10px;
  background: rgba(10,10,10,0.5); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15); color: rgba(255,255,255,0.7);
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  opacity: 0; transform: scale(0.8); transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}
.masonry-item:hover .save-btn { opacity: 1; transform: scale(1); }
.save-btn.saved { color: var(--accent-gold); border-color: rgba(242,201,126,0.5); background: rgba(242,201,126,0.15); }
.save-btn:hover { transform: scale(1.1) !important; }

.empty { text-align: center; padding: 80px 24px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty h3 { font-size: 1.4rem; font-weight: 900; margin-bottom: 8px; }
.empty p { color: var(--text-muted); font-weight: 600; }

.modal-wrap {
  position: fixed; inset: 0; z-index: 900;
  background: rgba(0,0,0,0.72); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.modal-card {
  position: relative; background: var(--bg-secondary, #140807);
  border-radius: 28px; overflow: hidden; max-width: 800px; width: 100%;
  max-height: 90vh; display: flex; flex-direction: row;
  border: 1px solid var(--glass-border); box-shadow: 0 50px 120px rgba(0,0,0,0.6);
}
.modal-glass { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%); pointer-events: none; }
.modal-close {
  position: absolute; top: 16px; left: 16px; z-index: 10;
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.modal-close:hover { background: rgba(255,80,80,0.25); color: #ff5050; }
.modal-img-wrap { width: 55%; flex-shrink: 0; position: relative; overflow: hidden; }
.modal-img-wrap img { width: 100%; height: 100%; object-fit: contain; background: #f5f5f5; }
.modal-info { flex: 1; padding: 40px 32px; display: flex; flex-direction: column; justify-content: center; gap: 16px; overflow-y: auto; }
.modal-tag {
  display: inline-block; font-size: 11px; font-weight: 900; letter-spacing: 0.1em;
  color: var(--accent-gold); background: rgba(242,201,126,0.1);
  padding: 4px 12px; border-radius: 100px; border: 1px solid rgba(242,201,126,0.3);
}
.modal-title { font-size: 1.8rem; font-weight: 950; margin: 0; line-height: 1.2; }
.modal-desc { color: var(--text-muted); font-weight: 600; line-height: 1.7; margin: 0; }
.modal-btn {
  display: inline-flex; align-items: center; gap: 10px;
  background: var(--accent-gold); color: var(--accent-brown);
  font-weight: 900; font-size: 15px; padding: 14px 28px;
  border-radius: 100px; text-decoration: none; margin-top: 8px;
  transition: all 0.3s; align-self: flex-start;
  box-shadow: 0 8px 24px rgba(242,201,126,0.4);
}
.modal-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(242,201,126,0.5); }

.modal-enter-active { transition: all 0.4s cubic-bezier(0.16,1,0.3,1); }
.modal-leave-active { transition: all 0.25s ease-in; }
.modal-enter-from { opacity: 0; transform: scale(0.92); }
.modal-leave-to   { opacity: 0; transform: scale(0.95); }

@media (max-width: 1100px) { .masonry { columns: 3; } }
@media (max-width: 768px) {
  .masonry { columns: 2; }
  .gallery-header { padding: 80px 16px 30px; }
  .modal-card { flex-direction: column; max-height: 85vh; }
  .modal-img-wrap { width: 100%; height: 240px; flex-shrink: 0; }
  .modal-info { padding: 24px 20px; }
  .modal-title { font-size: 1.4rem; }
}
@media (max-width: 480px) { .masonry { columns: 1; } }
</style>
