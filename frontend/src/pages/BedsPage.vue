<template>
  <div class="beds-page page" dir="rtl">
    <ProductHero
      title="سرویس خواب"
      description="ترکیب متفاوتی از راحتی و زیبایی برای اتاق خواب شما"
      :stats="heroStats"
    />

    <!-- Content Area -->
    <main class="content-scroll">
      <!-- Product Grid -->
      <div v-if="products.length" class="modules-grid">
        <div
          v-for="mod in products"
          :key="mod.id"
          class="module-card"
          @click="navigateToModel(mod)"
        >
          <div class="card-img-wrap">
            <img :src="getCoverImage(mod)" :alt="mod.name" class="card-img" />
          </div>
          <div class="card-info">
            <h3 class="card-title">{{ mod.name }}</h3>
            <p class="card-price">{{ getModulePrice(mod) }} تومان</p>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🛏️</div>
        <h3>محصولی یافت نشد</h3>
        <p>در حال حاضر محصولی در این دسته موجود نیست</p>
      </div>
    </main>

    <!-- Support FAB removed -->

    <!-- Mobile Bottom Nav -->
    <nav class="mobile-bottom-nav">
      <div class="nav-glass"></div>
      <div class="nav-shimmer"></div>
      <div class="nav-container">
        <a href="/dashboard" class="nav-item">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
          </svg>
          <span>مدیریت</span>
        </a>
        <a href="/shop-by-look" class="nav-item">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <span>Shop by Look</span>
        </a>
        <a href="/categories" class="nav-item nav-center">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          </svg>
          <span>محصولات</span>
        </a>
        <button class="nav-item" type="button">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
          </svg>
          <span>سبد</span>
        </button>
        <a href="/mysite" class="nav-item">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span>خانه</span>
        </a>
      </div>
    </nav>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <a href="/categories" class="footer-logo">
            <span class="logo-den">DEN</span><span class="logo-room">ROOM</span>
          </a>
          <p class="footer-desc">طراحی و تولید مبلمان با کیفیت برتر</p>
          <div class="footer-socials">
            <a href="#" aria-label="Instagram">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.5" fill="currentColor"/>
              </svg>
            </a>
            <a href="#" aria-label="Telegram">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m22 2-7 20-4-9-9-4 20-7z"/><path d="M22 2 11 13"/>
              </svg>
            </a>
            <a href="#" aria-label="WhatsApp">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
              </svg>
            </a>
          </div>
        </div>

        <div class="footer-col">
          <h4>محصولات</h4>
          <ul>
            <li><a href="/sofas">مبلمان</a></li>
            <li><a href="/barstools">صندلی اپن</a></li>
            <li><a href="/tables">میز ناهارخوری</a></li>
            <li><a href="/coffee-tables">میز جلو مبلی</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>خدمات مشتریان</h4>
          <ul>
            <li><a href="#">تماس با ما</a></li>
            <li><a href="/faq">سوالات متداول</a></li>
            <li><a href="#">پیگیری سفارش</a></li>
            <li><a href="#">بازگشت کالا</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>درباره ما</h4>
          <ul>
            <li><a href="#">درباره دن‌روم</a></li>
            <li><a href="/dealers">نمایندگان</a></li>
            <li><a href="/cooperation">همکاری با ما</a></li>
            <li><a href="/blog">بلاگ</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <form class="subscribe-form" @submit.prevent>
          <input type="email" placeholder="عضویت در خبرنامه..." />
          <button type="submit">تایید</button>
        </form>
        <p class="copyright">© 2024 DenRoom. تمامی حقوق محفوظ است.</p>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ProductHero from '../components/ProductHero.vue'

const products = ref(window.NestedBedProducts || [])
const clothGroups = ref(window.ClothGroups || [])


const heroStats = computed(() => [
  { label: 'مدل سرویس خواب', value: products.value.length },
  { label: 'نوع پارچه',      value: clothGroups.value.length },
])

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
  if (!val) return '—'
  return Math.round(val).toLocaleString('fa-IR')
}

const navigateToModel = (model) => {
  if (model.sofa_route) {
    window.location.href = `/${model.sofa_route}`
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  padding-bottom: 120px;
  font-family: 'Peyda', sans-serif;
}

/* Content */
.content-scroll { padding: 24px; }
.modules-grid {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding: 20px 0;
  scrollbar-width: none;
}
.modules-grid::-webkit-scrollbar { display: none; }

/* Cards */
.module-card {
  flex: 0 0 300px;
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: 0.3s;
}
.module-card:hover { transform: translateY(-8px); border-color: var(--accent-gold); }
.card-img-wrap { height: 200px; }
.card-img  { width: 100%; height: 100%; object-fit: cover; }
.card-info { padding: 20px; }
.card-title { font-weight: 800; margin-bottom: 8px; }
.card-price { color: var(--accent-orange); font-weight: 900; }

/* Empty State */
.empty-state { text-align: center; padding: 100px 24px; }
.empty-icon  { font-size: 5rem; margin-bottom: 24px; }
.empty-state h3 { font-size: 1.5rem; margin-bottom: 12px; }
.empty-state p  { opacity: 0.6; }

/* Support FAB */
.support-fab {
  position: fixed;
  bottom: 90px;
  left: 24px;
  background: var(--accent-brown);
  color: var(--accent-gold);
  border: none;
  padding: 14px 20px;
  border-radius: 50px;
  font-weight: 700;
  cursor: pointer;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Mobile Bottom Nav */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 200;
}
.nav-glass   { position: absolute; inset: 0; background: var(--glass-bg); backdrop-filter: blur(20px); }
.nav-shimmer { position: absolute; inset: 0; pointer-events: none; }
.nav-container {
  position: relative;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 0 16px;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: var(--text-main);
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.nav-item:hover { opacity: 1; }
.nav-center {
  background: var(--accent-brown);
  padding: 12px;
  border-radius: 50%;
  opacity: 1;
}

/* Footer */
.site-footer { padding: 60px 24px 24px; border-top: 1px solid var(--glass-border); }
.footer-inner {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}
.footer-logo { display: flex; align-items: baseline; gap: 2px; text-decoration: none; }
.logo-den  { font-size: 1.8rem; font-weight: 900; color: var(--text-main); }
.logo-room { font-size: 1rem; font-weight: 400; color: var(--accent-gold); }
.footer-desc { opacity: 0.7; margin: 16px 0; line-height: 1.6; font-size: 0.9rem; }
.footer-socials { display: flex; gap: 12px; }
.footer-socials a { color: var(--text-main); opacity: 0.7; transition: opacity 0.2s; }
.footer-socials a:hover { opacity: 1; }
.footer-col h4 { font-weight: 800; margin-bottom: 16px; }
.footer-col ul { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.footer-col a  { color: var(--text-main); text-decoration: none; opacity: 0.7; font-size: 0.9rem; transition: opacity 0.2s; }
.footer-col a:hover { opacity: 1; }
.footer-bottom { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.subscribe-form { display: flex; gap: 8px; }
.subscribe-form input {
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  font-family: inherit;
}
.subscribe-form button {
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  background: var(--accent-brown);
  color: var(--accent-gold);
  font-weight: 700;
  cursor: pointer;
}
.copyright { opacity: 0.5; font-size: 0.85rem; }

@media (max-width: 768px) {
  .hero-title { font-size: 2.5rem; }
  .module-card { flex: 0 0 250px; }
  .footer-inner { grid-template-columns: 1fr 1fr; }
  .footer-brand { grid-column: 1 / -1; }
  .footer-bottom { flex-direction: column; align-items: flex-start; }
}
</style>
