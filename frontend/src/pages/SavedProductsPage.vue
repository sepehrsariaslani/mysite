<template>
  <div class="saved-page" dir="rtl">
    <header class="saved-header">
      <div class="inner">
        <h1>محصولات ذخیره‌شده</h1>
        <p>آیتم‌هایی که در گالری ذخیره کردی اینجا نمایش داده می‌شوند.</p>
      </div>
    </header>

    <main class="saved-main">
      <div v-if="savedItems.length" class="saved-grid">
        <article v-for="item in savedItems" :key="item.id" class="saved-card">
          <div class="img-wrap">
            <img :src="item.img" :alt="item.title" loading="lazy" />
          </div>
          <div class="content">
            <span class="tag">{{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="actions">
              <a :href="item.url" class="btn primary">مشاهده محصول</a>
              <button class="btn ghost" @click="removeItem(item.id)">حذف</button>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="empty">
        <h3>هنوز محصولی ذخیره نکردی</h3>
        <p>از صفحه گالری روی آیکن ذخیره بزن تا اینجا نمایش داده شود.</p>
        <a href="/mysite/gallery" class="back-btn">رفتن به گالری</a>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

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

const savedItems = ref(loadSavedProducts())

function removeItem(id) {
  savedItems.value = savedItems.value.filter(item => item.id !== id)
  try {
    localStorage.setItem(SAVED_KEY, JSON.stringify(savedItems.value))
  } catch (e) {
    // ignore storage failures
  }
}
</script>

<style scoped>
.saved-page { min-height: 100vh; background: var(--bg-main); color: var(--text-main); }
.saved-header { padding: 96px 20px 24px; }
.inner { max-width: 1200px; margin: 0 auto; }
.inner h1 { margin: 0 0 8px; font-size: 2rem; font-weight: 900; }
.inner p { margin: 0; color: var(--text-muted); }
.saved-main { max-width: 1200px; margin: 0 auto; padding: 0 20px 80px; }
.saved-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.saved-card { border: 1px solid var(--glass-border); background: var(--glass-bg); border-radius: 18px; overflow: hidden; }
.img-wrap { height: 240px; background: #f5f5f5; }
.img-wrap img { width: 100%; height: 100%; object-fit: contain; display: block; }
.content { padding: 14px; }
.tag { display: inline-block; font-size: 11px; font-weight: 700; background: rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 999px; }
.content h3 { margin: 10px 0 6px; font-size: 1.05rem; }
.content p { margin: 0 0 12px; color: var(--text-muted); font-size: 13px; line-height: 1.7; max-height: 44px; overflow: hidden; }
.actions { display: flex; gap: 8px; }
.btn { border: 1px solid var(--glass-border); border-radius: 10px; padding: 8px 12px; text-decoration: none; font-size: 13px; font-weight: 700; cursor: pointer; background: transparent; color: inherit; }
.btn.primary { background: var(--accent-gold); color: var(--accent-brown); border-color: var(--accent-gold); }
.btn.ghost { background: transparent; }
.empty { text-align: center; padding: 90px 20px; }
.back-btn { display: inline-block; margin-top: 12px; padding: 10px 16px; border-radius: 12px; text-decoration: none; background: var(--accent-gold); color: var(--accent-brown); font-weight: 800; }
@media (max-width: 980px) { .saved-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .saved-grid { grid-template-columns: 1fr; } }
</style>
