<template>
  <header ref="headerRef" class="app-header" :class="{ scrolled: isScrolled }" dir="rtl">
    <div class="header-surface"></div>
    <div class="header-inner">
      <a href="/mysite" class="logo">
        <span class="logo-den">DEN</span>
        <span class="logo-room">ROOM</span>
      </a>

      <nav class="desktop-nav" aria-label="ناوبری اصلی">
        <div
          class="menu-wrap"
          @mouseenter="setMenu('shop')"
          @mouseleave="clearMenu"
        >
          <button
            class="menu-trigger"
            :class="{ active: isShopActive }"
            @click.prevent="toggleMenu('shop')"
            type="button"
          >
            فروشگاه
            <svg class="chevron" :class="{ open: openMenu === 'shop' }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          <transition name="menu-fade">
            <div v-if="openMenu === 'shop'" class="mega-panel">
              <div class="mega-grid">
                <section class="mega-col">
                  <h4>دسته‌بندی محصولات</h4>
                  <a
                    v-for="item in productLinks"
                    :key="item.url"
                    :href="item.url"
                    class="mega-item"
                  >
                    <span class="mega-badge">{{ item.badge }}</span>
                    <span class="mega-copy">
                      <strong>{{ item.label }}</strong>
                      <small>{{ item.sub }}</small>
                    </span>
                  </a>
                </section>

                <section class="mega-col">
                  <h4>کشف سریع</h4>
                  <a
                    v-for="item in shopExploreLinks"
                    :key="item.url"
                    :href="item.url"
                    class="mega-inline-link"
                  >
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.sub }}</small>
                  </a>
                </section>

                <section class="mega-feature-col">
                  <a class="feature-card feature-main" href="/mysite/shop-by-look">
                    <span>Shop by Look</span>
                    <strong>چیدمان آماده ببین</strong>
                    <small>محصولات داخل هر فضا را مستقیم انتخاب کن</small>
                  </a>
                  <a class="feature-card feature-soft" href="/mysite/projects">
                    <span>Project Cases</span>
                    <strong>پروژه‌های اجراشده</strong>
                    <small>نمونه اجراها با محصولات واقعی</small>
                  </a>
                </section>
              </div>
            </div>
          </transition>
        </div>

        <div
          class="menu-wrap"
          @mouseenter="setMenu('inspiration')"
          @mouseleave="clearMenu"
        >
          <button
            class="menu-trigger"
            :class="{ active: isInspirationActive }"
            @click.prevent="toggleMenu('inspiration')"
            type="button"
          >
            الهام و محتوا
            <svg class="chevron" :class="{ open: openMenu === 'inspiration' }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          <transition name="menu-fade">
            <div v-if="openMenu === 'inspiration'" class="mega-panel compact">
              <div class="compact-grid">
                <section>
                  <h4>الهام بصری</h4>
                  <a v-for="item in inspirationLinks" :key="item.url" :href="item.url" class="compact-link">
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.sub }}</small>
                  </a>
                </section>
                <section>
                  <h4>محتوا</h4>
                  <a v-for="item in contentLinks" :key="item.url" :href="item.url" class="compact-link">
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.sub }}</small>
                  </a>
                </section>
              </div>
            </div>
          </transition>
        </div>

        <div
          class="menu-wrap"
          @mouseenter="setMenu('service')"
          @mouseleave="clearMenu"
        >
          <button
            class="menu-trigger"
            :class="{ active: isServiceActive }"
            @click.prevent="toggleMenu('service')"
            type="button"
          >
            خدمات
            <svg class="chevron" :class="{ open: openMenu === 'service' }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          <transition name="menu-fade">
            <div v-if="openMenu === 'service'" class="mega-panel compact">
              <div class="compact-grid single">
                <section>
                  <h4>خدمات و حساب کاربری</h4>
                  <a v-for="item in serviceLinks" :key="item.url" :href="item.url" class="compact-link">
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.sub }}</small>
                  </a>
                </section>
              </div>
            </div>
          </transition>
        </div>

        <a class="quick-pill" href="/mysite/categories">همه دسته‌بندی‌ها</a>
      </nav>

      <div class="header-actions">
        <button class="action-btn" @click="isSearchOpen = true" aria-label="جستجو">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </button>

        <button class="action-btn" @click="toggleTheme" :aria-label="isDark ? 'تم روشن' : 'تم تاریک'">
          <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z" />
          </svg>
        </button>

        <button class="cart-pill" @click="isCartOpen = true" aria-label="سبد خرید">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round">
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4H6z" />
            <path d="M3 6h18" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
          <span>سبد</span>
          <i v-if="totalItems > 0">{{ totalItems }}</i>
        </button>

        <button class="hamburger" :class="{ open: mobileOpen }" @click="mobileOpen = !mobileOpen" aria-label="منو">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>

    <div class="mobile-overlay" :class="{ visible: mobileOpen }" @click="mobileOpen = false"></div>
    <aside class="mobile-sheet" :class="{ open: mobileOpen }" dir="rtl">
      <div class="sheet-head">
        <a href="/mysite" class="sheet-logo" @click="mobileOpen = false">DENROOM</a>
        <button class="sheet-close" @click="mobileOpen = false" aria-label="بستن">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <section class="sheet-section">
        <h5>دسته‌بندی محصولات</h5>
        <div class="sheet-grid">
          <a
            v-for="item in productLinks"
            :key="item.url"
            :href="item.url"
            class="sheet-grid-item"
            @click="mobileOpen = false"
          >
            <strong>{{ item.label }}</strong>
            <small>{{ item.sub }}</small>
          </a>
        </div>
      </section>

      <section class="sheet-section">
        <h5>الهام و محتوا</h5>
        <nav class="sheet-links">
          <a
            v-for="item in [...inspirationLinks, ...contentLinks]"
            :key="item.url"
            :href="item.url"
            @click="mobileOpen = false"
          >
            <strong>{{ item.label }}</strong>
            <small>{{ item.sub }}</small>
          </a>
        </nav>
      </section>

      <section class="sheet-section">
        <h5>خدمات</h5>
        <nav class="sheet-links">
          <a v-for="item in serviceLinks" :key="item.url" :href="item.url" @click="mobileOpen = false">
            <strong>{{ item.label }}</strong>
            <small>{{ item.sub }}</small>
          </a>
        </nav>
      </section>
    </aside>

    <SearchOverlay :is-open="isSearchOpen" @close="isSearchOpen = false" />
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useCart } from '../stores/cartStore'
import SearchOverlay from './SearchOverlay.vue'

const { totalItems, isCartOpen } = useCart()

const headerRef = ref(null)
const mobileOpen = ref(false)
const openMenu = ref('')
const isSearchOpen = ref(false)
const isScrolled = ref(false)
const isDark = ref(true)

const currentPath = computed(() => {
  const path = String(window.location.pathname || '/')
  return path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path
})

const productLinks = [
  { label: 'مبلمان', sub: 'کاناپه و مبل ماژولار', badge: 'SOFA', url: '/mysite/sofas' },
  { label: 'صندلی اپن', sub: 'کانتر و بار', badge: 'BAR', url: '/mysite/barstools' },
  { label: 'صندلی ناهارخوری', sub: 'Dining Chairs', badge: 'CHR', url: '/mysite/dining-chairs' },
  { label: 'میز ناهارخوری', sub: 'Dining Tables', badge: 'TBL', url: '/mysite/tables' },
  { label: 'میز جلو مبلی', sub: 'Coffee & Side', badge: 'CFE', url: '/mysite/coffee-tables' },
  { label: 'نیمکت', sub: 'Bench Collection', badge: 'BNH', url: '/mysite/benches' },
  { label: 'تخت خواب', sub: 'Bed Frames', badge: 'BED', url: '/mysite/beds' },
  { label: 'کوسن و تشکچه', sub: 'متعلقات پارچه‌ای', badge: 'ACC', url: '/mysite/cushions' },
  { label: 'کاتالوگ چاپی', sub: 'لیست کامل برای پرینت', badge: 'PRT', url: '/mysite/products-print' },
]

const shopExploreLinks = [
  { label: 'همه دسته‌بندی‌ها', sub: 'نمای کامل محصولات', url: '/mysite/categories' },
  { label: 'Special Edition', sub: 'مدل‌های محدود و لوکس', url: '/mysite/special-edition' },
  { label: 'Outlet', sub: 'قیمت ویژه و محدود', url: '/mysite/outlet' },
  { label: 'پارچه‌ها', sub: 'کالیته و رنگ پارچه', url: '/mysite/fabrics' },
  { label: 'Shop by Look', sub: 'خرید از روی چیدمان', url: '/mysite/shop-by-look' },
  { label: 'فوتوگالری', sub: 'الهام بصری پروژه‌ها', url: '/mysite/gallery' },
  { label: 'پروژه‌ها', sub: 'نمونه اجرای واقعی', url: '/mysite/projects' },
]

const inspirationLinks = [
  { label: 'Shop by Look', sub: 'چیدمان تعاملی', url: '/mysite/shop-by-look' },
  { label: 'پروژه‌ها', sub: 'خانه، رستوران، کافه', url: '/mysite/projects' },
  { label: 'فوتوگالری', sub: 'تصاویر الهام‌بخش', url: '/mysite/gallery' },
]

const contentLinks = [
  { label: 'بلاگ', sub: 'راهنمای خرید و دکوراسیون', url: '/mysite/blog' },
  { label: 'Special Edition', sub: 'نسخه‌های محدود', url: '/mysite/special-edition' },
  { label: 'Outlet', sub: 'قیمت‌های ویژه', url: '/mysite/outlet' },
  { label: 'سوالات متداول', sub: 'پاسخ سریع', url: '/mysite/faq' },
]

const serviceLinks = [
  { label: 'مشاوره', sub: 'مشاوره انتخاب محصول', url: '/mysite/consultation' },
  { label: 'درباره ما', sub: 'ماموریت، ارزش‌ها و تاریخچه', url: '/mysite/about' },
  { label: 'مدیریت مشتری', sub: 'پنل مشتری', url: '/mysite/dashboard' },
  { label: 'ذخیره‌شده‌ها', sub: 'لیست علاقه‌مندی', url: '/mysite/saved' },
  { label: 'ورود', sub: 'حساب کاربری', url: '/mysite/login' },
]

function hasPrefix(path) {
  const current = currentPath.value
  if (path === '/mysite') return current === '/mysite'
  return current === path || current.startsWith(`${path}/`)
}

const isShopActive = computed(() =>
  [
    '/mysite/categories',
    '/mysite/sofas',
    '/mysite/tables',
    '/mysite/coffee-tables',
    '/mysite/benches',
    '/mysite/barstools',
    '/mysite/dining-chairs',
    '/mysite/beds',
    '/mysite/cushions',
    '/mysite/fabrics',
    '/mysite/products-print',
    '/mysite/special-edition',
    '/mysite/outlet',
    '/mysite/product',
  ].some(hasPrefix)
)

const isInspirationActive = computed(() =>
  ['/mysite/shop-by-look', '/mysite/projects', '/mysite/gallery', '/mysite/blog', '/mysite/faq', '/mysite/special-edition', '/mysite/outlet'].some(hasPrefix)
)

const isServiceActive = computed(() =>
  ['/mysite/consultation', '/mysite/about', '/mysite/dashboard', '/mysite/saved', '/mysite/login'].some(hasPrefix)
)

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  try {
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  } catch (error) {
    // Ignore storage writes.
  }
}

function setMenu(key) {
  if (window.innerWidth <= 1080) return
  openMenu.value = key
}

function clearMenu() {
  openMenu.value = ''
}

function toggleMenu(key) {
  openMenu.value = openMenu.value === key ? '' : key
}

function onScroll() {
  isScrolled.value = window.scrollY > 14
}

function onKeydown(event) {
  if (event.key === 'Escape') {
    mobileOpen.value = false
    openMenu.value = ''
  }
}

function onDocumentClick(event) {
  if (!headerRef.value) return
  if (!headerRef.value.contains(event.target)) {
    openMenu.value = ''
  }
}

let initialTheme = document.documentElement.getAttribute('data-theme')
try {
  const storedTheme = localStorage.getItem('theme')
  if (storedTheme === 'dark' || storedTheme === 'light') {
    initialTheme = storedTheme
  }
} catch (error) {
  // Ignore storage reads.
}

if (initialTheme !== 'dark' && initialTheme !== 'light') {
  initialTheme = 'light'
}

isDark.value = initialTheme === 'dark'
document.documentElement.setAttribute('data-theme', initialTheme)

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onDocumentClick)
})
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 320;
  height: 74px;
  transition: height 0.28s ease;
}

.app-header.scrolled {
  height: 64px;
}

.header-surface {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--glass-bg) 92%, transparent);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid var(--glass-border);
}

.header-inner {
  position: relative;
  z-index: 2;
  width: min(1480px, 100%);
  height: 100%;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
}

.logo {
  text-decoration: none;
  display: inline-flex;
  align-items: baseline;
  gap: 3px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.logo-den {
  color: var(--text-main);
  font-size: 1.45rem;
}

.logo-room {
  color: var(--accent-gold);
  font-size: 1.45rem;
}

.desktop-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.menu-wrap {
  position: relative;
}

.menu-trigger {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  border-radius: 999px;
  height: 40px;
  padding: 0 14px;
  font-family: inherit;
  font-size: 0.86rem;
  font-weight: 760;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-trigger:hover {
  color: var(--text-main);
  border-color: var(--glass-border);
  background: var(--glass-bg);
}

.menu-trigger.active {
  color: var(--accent-gold);
}

.chevron {
  width: 13px;
  height: 13px;
  transition: transform 0.2s ease;
}

.chevron.open {
  transform: rotate(180deg);
}

.quick-pill {
  text-decoration: none;
  color: var(--accent-brown);
  background: var(--accent-gold);
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 800;
  font-size: 0.82rem;
  border: 1px solid color-mix(in srgb, var(--accent-gold) 80%, #000 20%);
}

.quick-pill:hover {
  filter: brightness(1.04);
}

.mega-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: min(920px, 88vw);
  border-radius: 22px;
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--bg-secondary) 86%, #fff 14%);
  box-shadow: 0 24px 68px rgba(0, 0, 0, 0.24);
  padding: 14px;
}

[data-theme='light'] .mega-panel {
  background: #fbf8f3;
}

.mega-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.95fr;
  gap: 12px;
}

.mega-col,
.mega-feature-col {
  background: color-mix(in srgb, var(--glass-bg) 90%, transparent);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 12px;
}

.mega-col h4,
.compact-grid h4 {
  margin: 0 0 8px;
  color: var(--accent-gold);
  font-size: 0.8rem;
  font-weight: 900;
}

.mega-item {
  text-decoration: none;
  display: flex;
  gap: 10px;
  align-items: center;
  border-radius: 12px;
  padding: 8px;
  border: 1px solid transparent;
}

.mega-item:hover {
  border-color: var(--glass-border);
  background: var(--glass-bg);
}

.mega-badge {
  width: 38px;
  height: 28px;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--glass-border) 85%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  color: var(--accent-gold);
  font-weight: 900;
  flex-shrink: 0;
}

.mega-copy strong {
  display: block;
  color: var(--text-main);
  font-size: 0.82rem;
}

.mega-copy small {
  display: block;
  color: var(--text-muted);
  font-size: 0.72rem;
  margin-top: 2px;
}

.mega-inline-link {
  text-decoration: none;
  display: grid;
  gap: 2px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 9px;
}

.mega-inline-link:hover {
  border-color: var(--glass-border);
  background: var(--glass-bg);
}

.mega-inline-link strong {
  font-size: 0.82rem;
  color: var(--text-main);
}

.mega-inline-link small {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.mega-feature-col {
  display: grid;
  gap: 8px;
}

.feature-card {
  text-decoration: none;
  border-radius: 14px;
  border: 1px solid transparent;
  padding: 11px;
  display: grid;
  gap: 3px;
  min-height: 98px;
}

.feature-card span {
  color: var(--text-muted);
  font-size: 0.7rem;
  letter-spacing: 0.05em;
}

.feature-card strong {
  color: var(--text-main);
  font-size: 0.89rem;
}

.feature-card small {
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.75;
}

.feature-main {
  background: linear-gradient(140deg, #e7b15d 0%, #f6d49f 100%);
}

.feature-main strong,
.feature-main small,
.feature-main span {
  color: #2f1d12;
}

.feature-soft {
  background: linear-gradient(150deg, rgba(242, 201, 126, 0.15) 0%, rgba(144, 114, 93, 0.08) 100%);
  border-color: var(--glass-border);
}

.mega-panel.compact {
  width: min(520px, 84vw);
}

.compact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.compact-grid.single {
  grid-template-columns: 1fr;
}

.compact-grid section {
  background: color-mix(in srgb, var(--glass-bg) 90%, transparent);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.compact-link {
  text-decoration: none;
  border-radius: 10px;
  border: 1px solid transparent;
  padding: 8px 9px;
  display: grid;
}

.compact-link:hover {
  border-color: var(--glass-border);
  background: var(--glass-bg);
}

.compact-link strong {
  color: var(--text-main);
  font-size: 0.82rem;
}

.compact-link small {
  color: var(--text-muted);
  font-size: 0.72rem;
  margin-top: 2px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.action-btn svg {
  width: 17px;
  height: 17px;
}

.action-btn:hover {
  border-color: color-mix(in srgb, var(--accent-gold) 44%, var(--glass-border));
}

.cart-pill {
  position: relative;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  border-radius: 999px;
  height: 38px;
  padding: 0 12px;
  font-family: inherit;
  font-size: 0.82rem;
  color: var(--text-main);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.cart-pill svg {
  width: 17px;
  height: 17px;
}

.cart-pill i {
  position: absolute;
  top: -6px;
  left: -6px;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gold);
  color: var(--accent-brown);
  font-style: normal;
  font-size: 0.65rem;
  font-weight: 900;
  border: 1px solid color-mix(in srgb, var(--accent-gold) 74%, #000 26%);
}

.hamburger {
  display: none;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 0;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
}

.hamburger span {
  display: block;
  width: 16px;
  height: 2px;
  border-radius: 4px;
  background: var(--text-main);
  transition: all 0.22s ease;
}

.hamburger.open span:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.hamburger.open span:nth-child(2) {
  opacity: 0;
}

.hamburger.open span:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
  z-index: 380;
}

.mobile-overlay.visible {
  opacity: 1;
  pointer-events: auto;
}

.mobile-sheet {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: min(390px, 92vw);
  background: var(--glass-bg);
  border-left: 1px solid var(--glass-border);
  transform: translateX(104%);
  transition: transform 0.24s ease;
  z-index: 390;
  overflow-y: auto;
  padding: 16px 14px 20px;
}

[data-theme='light'] .mobile-sheet {
  background: #faf7f2;
}

.mobile-sheet.open {
  transform: translateX(0);
}

.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.sheet-logo {
  text-decoration: none;
  color: var(--text-main);
  font-weight: 900;
  letter-spacing: 0.04em;
  font-size: 1.2rem;
}

.sheet-close {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.sheet-close svg {
  width: 16px;
  height: 16px;
}

.sheet-section {
  margin-top: 14px;
}

.sheet-section h5 {
  margin: 0 0 8px;
  color: var(--accent-gold);
  font-size: 0.78rem;
  font-weight: 900;
}

.sheet-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 7px;
}

.sheet-grid-item,
.sheet-links a {
  text-decoration: none;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  border-radius: 12px;
  padding: 9px 10px;
  display: grid;
  gap: 2px;
}

.sheet-grid-item strong,
.sheet-links strong {
  color: var(--text-main);
  font-size: 0.81rem;
}

.sheet-grid-item small,
.sheet-links small {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.sheet-links {
  display: grid;
  gap: 6px;
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.18s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.985);
}

@media (max-width: 1180px) {
  .quick-pill {
    display: none;
  }
}

@media (max-width: 1080px) {
  .desktop-nav {
    display: none;
  }

  .hamburger {
    display: inline-flex;
  }
}

@media (max-width: 720px) {
  .header-inner {
    gap: 8px;
  }

  .logo-den,
  .logo-room {
    font-size: 1.24rem;
  }

  .cart-pill span {
    display: none;
  }

  .cart-pill {
    width: 38px;
    padding: 0;
    justify-content: center;
  }
}

</style>
