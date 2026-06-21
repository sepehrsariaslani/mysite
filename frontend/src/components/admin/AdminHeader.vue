<template>
  <div>
    <!-- ═══ Desktop Header ═══ -->
    <header class="admin-header" dir="rtl" v-if="!isMobile">
      <div class="admin-inner">
        <a href="/management" class="brand" aria-label="ناحیه مدیریت">
          <span class="badge">
            <LayoutDashboard :size="16" />
          </span>
          <span class="title">ناحیه مدیریت مای‌سایت</span>
        </a>

        <nav class="admin-nav" aria-label="ناوبری مدیریت">
          <a
            v-for="item in links"
            :key="item.href"
            :href="item.href"
            class="nav-link"
            :class="{ active: isActive(item.page) }"
          >
            <component :is="item.icon" :size="14" class="nav-icon" />
            {{ item.label }}
          </a>
        </nav>

        <div class="admin-actions">
          <a href="/mysite" class="action-link">
            <ArrowLeft :size="14" />
            <span>بازگشت به سایت</span>
          </a>
          <a href="/api/method/logout" class="action-link danger">
            <LogOut :size="14" />
            <span>خروج</span>
          </a>
        </div>
      </div>
    </header>

    <!-- ═══ Mobile Header ═══ -->
    <template v-else>
      <!-- Top Bar: hamburger + brand -->
      <header class="mobile-header" dir="rtl">
        <div class="mobile-top-bar">
          <button class="hamburger-btn" @click="showDrawer = !showDrawer" :class="{ open: showDrawer }">
            <Menu v-if="!showDrawer" :size="20" />
            <X v-else :size="20" />
          </button>
          <a href="/management" class="mobile-brand">
            <span class="mobile-brand-badge">
              <LayoutDashboard :size="16" />
            </span>
            <span class="mobile-brand-title">{{ activePageTitle }}</span>
          </a>
          <a href="/api/method/logout" class="mobile-logout" title="خروج">
            <LogOut :size="18" />
          </a>
        </div>
      </header>

      <!-- Drawer Overlay -->
      <div class="drawer-overlay" v-if="showDrawer" @click="showDrawer = false"></div>

      <!-- Side Drawer -->
      <aside class="mobile-drawer" :class="{ open: showDrawer }">
        <div class="drawer-header">
          <div class="drawer-brand">
            <div class="drawer-brand-icon">
              <LayoutDashboard :size="18" />
            </div>
            <div>
              <strong>دن‌روم</strong>
              <small>پنل مدیریت</small>
            </div>
          </div>
          <button class="drawer-close" @click="showDrawer = false">
            <X :size="18" />
          </button>
        </div>
        <nav class="drawer-nav">
          <a
            v-for="item in links"
            :key="item.href"
            :href="item.href"
            class="drawer-item"
            :class="{ active: isActive(item.page) }"
            @click="showDrawer = false"
          >
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
          </a>
        </nav>
        <div class="drawer-footer">
          <a class="drawer-back" href="/mysite">
            <ArrowLeft :size="14" />
            <span>بازگشت به سایت</span>
          </a>
          <a class="drawer-logout" href="/api/method/logout">
            <LogOut :size="14" />
            <span>خروج</span>
          </a>
        </div>
      </aside>

      <!-- Bottom Tab Bar - FIXED at bottom -->
      <nav class="bottom-tab-bar">
        <a
          v-for="tab in bottomTabs"
          :key="tab.id"
          :href="tab.href"
          class="tab-item"
          :class="{ active: isActive(tab.page) }"
        >
          <component :is="tab.icon" :size="20" />
          <span class="tab-label">{{ tab.label }}</span>
        </a>
      </nav>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { hasManagementCapability } from '../../utils/managementAccess'
import {
  LayoutDashboard, Menu, X, FileText, ShoppingBag, PenLine,
  MessageCircle, Search, BarChart3, ArrowLeft, LogOut
} from 'lucide-vue-next'

const page = window._PAGE || ''
const isMobile = ref(false)
const showDrawer = ref(false)

const allLinks = [
  { label: 'داشبورد مدیریت', href: '/management', page: 'management', capability: 'content.edit', icon: LayoutDashboard },
  { label: 'محصولات', href: '/management-products', page: 'management-products', capability: 'product.edit', icon: ShoppingBag },
  { label: 'بلاگ', href: '/management-blog', page: 'management-blog', capability: 'content.edit', icon: PenLine },
  { label: 'پشتیبانی', href: '/management-support', page: 'management-support', capability: 'support.manage', icon: MessageCircle },
  { label: 'ممیزی', href: '/management-audit', page: 'management-audit', capability: 'audit.view', icon: Search },
  { label: 'آنالیتیکس', href: '/management-analytics', page: 'management-analytics', capability: 'analytics.view', icon: BarChart3 },
]

const links = computed(() => allLinks.filter((item) => hasManagementCapability(item.capability)))

const bottomTabs = [
  { id: 'pages',     page: 'management',           icon: FileText,     label: 'صفحات',    href: '/management' },
  { id: 'products',  page: 'management-products',  icon: ShoppingBag,  label: 'محصولات',  href: '/management-products' },
  { id: 'blog',      page: 'management-blog',      icon: PenLine,      label: 'بلاگ',     href: '/management-blog' },
  { id: 'analytics', page: 'management-analytics',  icon: BarChart3,    label: 'آنالیتیکس', href: '/management-analytics' },
  { id: 'support',   page: 'management-support',   icon: MessageCircle, label: 'پشتیبانی', href: '/management-support' },
]

const activePageTitle = computed(() => {
  const link = allLinks.find(l => isActive(l.page))
  return link ? link.label : 'مدیریت'
})

function isActive(linkPage) {
  if (linkPage === 'management-analytics') return page.startsWith('management-analytics')
  if (linkPage === 'management') return page === 'management'
  return page === linkPage
}

function checkMobile() {
  isMobile.value = window.innerWidth <= 900
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
</script>

<style scoped>
/* ═══ Base ═══ */
.admin-header {
  position: sticky;
  top: 0;
  z-index: 420;
  border-bottom: 1px solid var(--admin-border);
  background: color-mix(in srgb, var(--admin-panel-bg) 88%, transparent);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
  overflow-x: hidden;
}

/* ═══ Desktop Inner ═══ */
.admin-inner {
  width: min(1400px, 100%);
  margin: 0 auto;
  padding: 12px 18px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  box-sizing: border-box;
  max-width: 100%;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  min-width: 0;
}

.badge {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  border: 1px solid color-mix(in srgb, var(--admin-border) 60%, #fff 40%);
  background: linear-gradient(135deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.title {
  color: var(--text-main);
  font-weight: 800;
  font-size: 0.92rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-nav {
  display: flex;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

.nav-link {
  text-decoration: none;
  color: var(--admin-text-soft);
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 0.8rem;
  font-weight: 700;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-link:hover {
  color: var(--text-main);
  border-color: var(--admin-border);
  background: var(--admin-chip-bg);
}

.nav-link.active {
  color: #fff;
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  border-color: transparent;
}

.admin-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action-link {
  text-decoration: none;
  border-radius: 10px;
  border: 1px solid var(--admin-border);
  color: var(--text-main);
  background: var(--admin-input-bg);
  padding: 7px 10px;
  font-size: 0.78rem;
  font-weight: 700;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.action-link:hover {
  border-color: var(--admin-tab-active-start);
}

.action-link.danger {
  border-color: color-mix(in srgb, #ef4444 55%, var(--admin-border) 45%);
  color: color-mix(in srgb, #ef4444 78%, var(--text-main) 22%);
}

/* ═══ Mobile Top Bar ═══ */
.mobile-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  gap: var(--space-2);
}

.hamburger-btn {
  width: var(--touch-min);
  height: var(--touch-min);
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}

.hamburger-btn:active {
  transform: scale(0.92);
  border-color: var(--accent-gold);
}

.mobile-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  flex: 1;
  min-width: 0;
}

.mobile-brand-badge {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mobile-brand-title {
  color: var(--text-main);
  font-weight: 800;
  font-size: var(--text-base);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mobile-logout {
  width: var(--touch-min);
  height: var(--touch-min);
  border: 1px solid color-mix(in srgb, #ef4444 40%, var(--admin-border) 60%);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  color: color-mix(in srgb, #ef4444 70%, var(--text-main) 30%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-out);
}

.mobile-logout:active {
  transform: scale(0.92);
}

/* ═══ Drawer ═══ */
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-overlay);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.mobile-drawer {
  position: fixed;
  top: 0;
  right: -300px;
  width: 280px;
  height: 100vh;
  height: 100dvh;
  z-index: var(--z-modal);
  background: var(--admin-bg);
  border-left: 1px solid var(--admin-border);
  display: grid;
  grid-template-rows: auto 1fr auto;
  transition: right var(--duration-slow) var(--ease-out);
  overflow: hidden;
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.2);
}

.mobile-drawer.open {
  right: 0;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border-bottom: 1px solid var(--admin-border);
}

.drawer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-brand strong {
  display: block;
  font-size: 0.85rem;
}

.drawer-brand small {
  color: var(--admin-text-soft);
  font-size: 10px;
}

.drawer-close {
  width: 32px;
  height: 32px;
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-nav {
  overflow-y: auto;
  padding: 8px 0;
  -webkit-overflow-scrolling: touch;
}

.drawer-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  text-decoration: none;
  color: var(--text-main);
  font-size: var(--text-base);
  font-weight: 600;
  transition: all var(--duration-fast) var(--ease-out);
  min-height: var(--touch-min);
}

.drawer-item:active {
  background: var(--admin-chip-bg);
  transform: scale(0.98);
}

.drawer-item.active {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}

.drawer-item svg {
  flex-shrink: 0;
}

.drawer-footer {
  border-top: 1px solid var(--admin-border);
  padding: 10px 14px;
  display: grid;
  gap: 6px;
}

.drawer-back,
.drawer-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  text-decoration: none;
  color: var(--admin-text-soft);
  font-size: 12px;
  font-weight: 600;
}

.drawer-logout {
  border-color: color-mix(in srgb, #ef4444 40%, var(--admin-border) 60%);
  color: color-mix(in srgb, #ef4444 70%, var(--text-main) 30%);
}

/* ═══ Mobile Header ═══ */
.mobile-header {
  position: sticky;
  top: 0;
  z-index: 420;
  background: color-mix(in srgb, var(--admin-panel-bg) 88%, transparent);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--admin-border);
  overflow-x: hidden;
  max-width: 100vw;
}

/* ═══ Bottom Tab Bar - FIXED at bottom of screen ═══ */
.bottom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky);
  display: flex;
  background: var(--admin-panel-bg);
  border-top: 1px solid var(--admin-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: var(--space-1) 0 calc(var(--space-1) + env(safe-area-inset-bottom, 0));
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-2) var(--space-1);
  text-decoration: none;
  color: var(--admin-text-soft);
  transition: all var(--duration-fast) var(--ease-out);
  min-width: 0;
  min-height: var(--touch-min);
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}

.tab-item:active {
  transform: scale(0.92);
}

.tab-item.active {
  color: var(--admin-tab-active-start);
}

.tab-item.active svg {
  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--admin-tab-active-start) 40%, transparent));
}

.tab-label {
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
  font-weight: 600;
}

/* ═══ Desktop responsive ═══ */
@media (max-width: 1100px) {
  .admin-inner {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .brand {
    justify-self: center;
  }

  .admin-nav,
  .admin-actions {
    justify-content: center;
  }
}

@media (max-width: 560px) {
  .admin-inner {
    padding: 10px;
  }

  .title {
    font-size: 0.84rem;
  }
}
</style>
