<template>
  <nav class="mobile-bottom-nav" dir="rtl" aria-label="ناوبری موبایل">
    <div class="nav-glass"></div>
    <div class="nav-shimmer"></div>
    <div class="nav-container">

      <!-- مدیریت مشتری — سمت راست -->
      <a :href="dashUrl" class="nav-item" :class="{ active: currentPath === dashUrl }">
        <div class="icon-wrap">
          <span class="icon-svg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
              <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
            </svg>
          </span>
          <span class="icon-ripple"></span>
        </div>
        <span class="item-label">مدیریت</span>
        <span v-if="currentPath === dashUrl" class="active-dot"></span>
      </a>

      <!-- Shop by Look -->
      <a :href="shopByLookUrl" class="nav-item" :class="{ active: currentPath === shopByLookUrl }">
        <div class="icon-wrap">
          <span class="icon-svg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
              <rect x="3" y="3" width="7" height="9" rx="1.5"/>
              <rect x="14" y="3" width="7" height="5" rx="1.5"/>
              <rect x="14" y="12" width="7" height="9" rx="1.5"/>
              <rect x="3" y="16" width="7" height="5" rx="1.5"/>
            </svg>
          </span>
          <span class="icon-ripple"></span>
        </div>
        <span class="item-label">Shop by Look</span>
        <span v-if="currentPath === shopByLookUrl" class="active-dot"></span>
      </a>

      <!-- محصولات — وسط، بزرگ‌تر -->
      <a :href="shopUrl" class="nav-item nav-center" :class="{ active: currentPath === shopUrl }">
        <div class="center-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
            <rect width="7" height="7" x="3" y="3" rx="1.5"/>
            <rect width="7" height="7" x="14" y="3" rx="1.5"/>
            <rect width="7" height="7" x="14" y="14" rx="1.5"/>
            <rect width="7" height="7" x="3" y="14" rx="1.5"/>
          </svg>
        </div>
        <span class="item-label center-label">محصولات</span>
      </a>

      <!-- سبد خرید -->
      <button class="nav-item" @click="openCart">
        <div class="icon-wrap">
          <span class="icon-svg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
              <circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/>
              <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>
            </svg>
          </span>
          <span v-if="totalItems > 0" class="cart-dot">{{ totalItems }}</span>
          <span class="icon-ripple"></span>
        </div>
        <span class="item-label">سبد</span>
      </button>

      <!-- خانه — سمت چپ -->
      <a :href="homeUrl" class="nav-item" :class="{ active: currentPath === homeUrl || currentPath === '/mysite' }">
        <div class="icon-wrap">
          <span class="icon-svg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </span>
          <span class="icon-ripple"></span>
        </div>
        <span class="item-label">خانه</span>
        <span v-if="currentPath === homeUrl || currentPath === '/mysite'" class="active-dot"></span>
      </a>

    </div>

    <MobileMenuOverlay :isOpen="false" @close="() => {}" />
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import MobileMenuOverlay from './MobileMenuOverlay.vue'
import { useCart } from '../stores/cartStore'

const { totalItems, isCartOpen } = useCart()
const currentPath = computed(() => window.location.pathname)

const homeUrl    = '/mysite'
const shopByLookUrl = '/mysite/shop-by-look'
const shopUrl    = '/mysite/categories'
const dashUrl    = '/mysite/dashboard'

function openCart() {
  isCartOpen.value = true
}
</script>

<style scoped>
/* ════ Floating pill ════ */
.mobile-bottom-nav {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 440px;
  z-index: 1000;
  display: none;
}

.nav-glass {
  position: absolute; inset: 0;
  border-radius: 100px;
  background: var(--glass-bg);
  backdrop-filter: blur(32px) saturate(220%);
  -webkit-backdrop-filter: blur(32px) saturate(220%);
  border: 1px solid var(--glass-border);
  box-shadow:
    0 24px 64px rgba(0,0,0,0.35),
    inset 0 1px 0 rgba(255,255,255,0.12),
    0 0 0 0.5px rgba(255,255,255,0.05);
}
.nav-shimmer {
  position: absolute; inset: 0;
  border-radius: 100px;
  background: linear-gradient(110deg, rgba(255,255,255,0.08) 0%, transparent 45%, rgba(255,255,255,0.04) 100%);
  pointer-events: none;
}

/* ════ Container ════ */
.nav-container {
  position: relative; z-index: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 6px 8px;
  gap: 0;
}

/* ════ Nav item base ════ */
.nav-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  flex: 1;
  padding: 8px 4px;
  border-radius: 24px;
  text-decoration: none;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
  min-height: 54px;
  -webkit-tap-highlight-color: transparent;
  font-family: inherit;
}
.nav-item:hover { color: var(--text-main); }
.nav-item.active { color: var(--accent-gold); }
.nav-item:active { transform: scale(0.92); }

/* ════ Icon ════ */
.icon-wrap {
  position: relative;
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
}
.icon-svg {
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.3s cubic-bezier(0.16,1,0.3,1);
}
.icon-svg svg { width: 100%; height: 100%; }
.nav-item.active .icon-svg { transform: scale(1.12); }
.nav-item:active .icon-svg { transform: scale(0.86); }

.icon-ripple {
  position: absolute; inset: -6px;
  border-radius: 50%;
  background: var(--accent-gold);
  opacity: 0; transform: scale(0);
  transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
  pointer-events: none;
}
.nav-item.active .icon-ripple { opacity: 0.13; transform: scale(1); }

/* cart badge */
.cart-dot {
  position: absolute; top: -6px; left: -6px;
  background: var(--accent-gold); color: var(--accent-brown);
  font-size: 9.5px; font-weight: 900;
  min-width: 16px; height: 16px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 3px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  animation: dotAppear 0.4s cubic-bezier(0.16,1,0.3,1);
}

/* ════ Label ════ */
.item-label {
  font-size: 10px; font-weight: 800;
  white-space: nowrap; letter-spacing: 0.02em;
  opacity: 0.7; transition: all 0.3s;
}
.nav-item.active .item-label { opacity: 1; font-size: 10.5px; }

/* ════ Active dot ════ */
.active-dot {
  position: absolute; bottom: 4px; left: 50%;
  transform: translateX(-50%);
  width: 4px; height: 4px; border-radius: 50%;
  background: var(--accent-gold);
  box-shadow: 0 0 8px rgba(242,201,126,0.7);
  animation: dotAppear 0.4s cubic-bezier(0.16,1,0.3,1);
}
@keyframes dotAppear {
  from { transform: translateX(-50%) scale(0); opacity:0; }
  to   { transform: translateX(-50%) scale(1); opacity:1; }
}

/* ════ CENTER: Products button ════ */
.nav-center {
  flex: 0 0 auto;
  padding: 0 10px;
  margin: 0 2px;
  gap: 0;
}
.center-btn {
  width: 50px; height: 50px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--accent-gold) 0%, #e6a830 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(242,201,126,0.45), inset 0 1px 0 rgba(255,255,255,0.3);
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
  margin-bottom: 4px;
}
.center-btn svg { width: 22px; height: 22px; stroke: #503130; }
.nav-center:hover .center-btn { transform: translateY(-3px) scale(1.06); box-shadow: 0 12px 28px rgba(242,201,126,0.5); }
.nav-center:active .center-btn { transform: scale(0.92); }
.nav-center .center-label { font-size: 10px; font-weight: 800; color: var(--accent-gold); opacity: 0.9; margin-top: 2px; }

/* ════ Show only on mobile ════ */
@media (max-width: 768px) {
  .mobile-bottom-nav { display: block; }
}
</style>
