<template>
  <div class="mobile-nav-wrapper">
    <!-- ═══ Top Header ═══ -->
    <header class="mobile-top-bar">
      <div class="mobile-brand">
        <div class="mobile-brand-icon">
          <component :is="brandIconComponent" :size="18" />
        </div>
        <div class="mobile-brand-text">
          <strong>{{ brandTitle }}</strong>
          <small>{{ brandSubtitle }}</small>
        </div>
      </div>
      <button class="hamburger-btn" @click="showDrawer = !showDrawer" :class="{ open: showDrawer }">
        <Menu v-if="!showDrawer" :size="20" />
        <X v-else :size="20" />
      </button>
    </header>

    <!-- ═══ Drawer Overlay ═══ -->
    <div class="drawer-overlay" v-if="showDrawer" @click="showDrawer = false"></div>

    <!-- ═══ Side Drawer ═══ -->
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
        <div class="drawer-section">مدیریت محتوا</div>
        <a class="drawer-item" href="/management" @click="showDrawer = false">
          <FileText :size="18" />
          <span>مدیریت صفحات</span>
        </a>
        <a class="drawer-item" href="/management-products" @click="showDrawer = false">
          <ShoppingBag :size="18" />
          <span>مدیریت محصولات</span>
        </a>
        <a class="drawer-item" href="/management-blog" @click="showDrawer = false">
          <PenLine :size="18" />
          <span>مدیریت بلاگ</span>
        </a>
        <a class="drawer-item" href="/management-support" @click="showDrawer = false">
          <MessageCircle :size="18" />
          <span>پشتیبانی</span>
        </a>
        <div class="drawer-section">گزارش‌ها</div>
        <a class="drawer-item" href="/management-analytics" @click="showDrawer = false">
          <BarChart3 :size="18" />
          <span>آنالیتیکس</span>
        </a>
        <a class="drawer-item" href="/management-analytics-traffic" @click="showDrawer = false">
          <TrendingUp :size="18" />
          <span>ترافیک</span>
        </a>
        <a class="drawer-item" href="/management-analytics-products" @click="showDrawer = false">
          <Package :size="18" />
          <span>گزارش محصولات</span>
        </a>
        <a class="drawer-item" href="/management-analytics-funnel" @click="showDrawer = false">
          <Filter :size="18" />
          <span>فانل تبدیل</span>
        </a>
        <div class="drawer-section">سیستم</div>
        <a class="drawer-item" href="/management-audit" @click="showDrawer = false">
          <Search :size="18" />
          <span>حسابرسی</span>
        </a>
        <a class="drawer-item" href="/management-analytics-settings" @click="showDrawer = false">
          <Settings :size="18" />
          <span>تنظیمات رهگیری</span>
        </a>
      </nav>
      <div class="drawer-footer">
        <a class="drawer-back" href="/">
          <ArrowRight :size="14" />
          <span>بازگشت به سایت</span>
        </a>
      </div>
    </aside>

    <!-- ═══ Bottom Tab Bar ═══ -->
    <nav class="bottom-tab-bar">
      <a
        v-for="tab in bottomTabs"
        :key="tab.id"
        :href="tab.href"
        class="tab-item"
        :class="{ active: activeTab === tab.id }"
      >
        <component :is="tab.iconComponent" :size="20" />
        <span class="tab-label">{{ tab.label }}</span>
      </a>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Menu, X, LayoutDashboard, FileText, ShoppingBag, PenLine,
  MessageCircle, BarChart3, TrendingUp, Package, Filter,
  Search, Settings, ArrowRight, Image, Palette
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: { type: String, default: 'pages' },
  brandTitle: { type: String, default: 'مدیریت صفحات' },
  brandSubtitle: { type: String, default: 'سازنده داخلی' },
  brandIcon: { type: String, default: 'FileText' }
})

const showDrawer = ref(false)

const iconMap = {
  FileText, ShoppingBag, PenLine, MessageCircle, BarChart3,
  TrendingUp, Package, Filter, Search, Settings, Image, Palette, LayoutDashboard
}

const brandIconComponent = iconMap[props.brandIcon] || FileText

const bottomTabs = [
  { id: 'pages',     iconComponent: FileText,     label: 'صفحات',    href: '/management' },
  { id: 'products',  iconComponent: ShoppingBag,  label: 'محصولات',  href: '/management-products' },
  { id: 'blog',      iconComponent: PenLine,      label: 'بلاگ',     href: '/management-blog' },
  { id: 'analytics', iconComponent: BarChart3,    label: 'آنالیتیکس', href: '/management-analytics' },
  { id: 'support',   iconComponent: MessageCircle, label: 'پشتیبانی', href: '/management-support' },
]
</script>

<style scoped>
/* ═══ Wrapper ═══ */
.mobile-nav-wrapper {
  display: none;
}

/* ═══ Top Bar ═══ */
.mobile-top-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--admin-panel-bg);
  border-bottom: 1px solid var(--admin-border);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.mobile-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mobile-brand-text strong {
  display: block;
  font-size: 0.85rem;
  line-height: 1.3;
}

.mobile-brand-text small {
  color: var(--admin-text-soft);
  font-size: 10px;
}

/* ═══ Hamburger (now icon-based) ═══ */
.hamburger-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.hamburger-btn:hover {
  border-color: var(--accent-gold);
}

/* ═══ Drawer Overlay ═══ */
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 199;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ═══ Side Drawer ═══ */
.mobile-drawer {
  position: fixed;
  top: 0;
  right: -300px;
  width: 280px;
  height: 100vh;
  z-index: 200;
  background: var(--admin-bg);
  border-left: 1px solid var(--admin-border);
  display: grid;
  grid-template-rows: auto 1fr auto;
  transition: right 0.3s ease;
  overflow: hidden;
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

.drawer-section {
  padding: 12px 14px 6px;
  font-size: 11px;
  color: var(--admin-text-soft);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.drawer-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 13px;
  transition: background 0.15s;
}

.drawer-item:hover,
.drawer-item:active {
  background: var(--admin-chip-bg);
}

.drawer-item svg {
  flex-shrink: 0;
  color: var(--admin-text-soft);
}

.drawer-footer {
  border-top: 1px solid var(--admin-border);
  padding: 10px 14px;
}

.drawer-back {
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
}

/* ═══ Bottom Tab Bar ═══ */
.bottom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  background: var(--admin-panel-bg);
  border-top: 1px solid var(--admin-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 4px 0 calc(4px + env(safe-area-inset-bottom, 0));
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 6px 2px;
  text-decoration: none;
  color: var(--admin-text-soft);
  transition: color 0.15s;
  min-width: 0;
}

.tab-item.active {
  color: var(--admin-tab-active-start);
}

.tab-label {
  font-size: 9px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
}

/* ═══ Show only on mobile/tablet ═══ */
@media (max-width: 1020px) {
  .mobile-nav-wrapper {
    display: block;
  }
}
</style>
