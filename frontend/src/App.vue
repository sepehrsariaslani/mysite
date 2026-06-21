<template>
  <div class="app-layout" :class="{ 'app-layout--editor-focus': isEditorFocusPage }">
    <AdminHeader v-if="isAdminSection && !isEditorFocusPage" />
    <AppHeader v-else-if="!headerlessPages.includes(page) && !isEditorFocusPage" />
    
    <main class="app-main" :class="{ 'app-main-editor-focus': isEditorFocusPage }">
      <HomePage v-if="page === 'home'" />
      <SofaCollection v-else-if="page === 'sofas'" />
      <CategoriesPage v-else-if="page === 'categories'" />
      <BlogPage v-else-if="page === 'blog'" />
      <ConsultationPage v-else-if="page === 'consultation'" />
      <CooperationPage v-else-if="page === 'cooperation'" />
      <DealersPage v-else-if="page === 'dealers'" />
      <DownloadsPage v-else-if="page === 'downloads'" />
      <CustomProductsPage v-else-if="page === 'custom-products'" />
      <ProductPage v-else-if="page === 'product'" />
      <SofaPage v-else-if="page === 'sofa-model'" />
      
      <!-- New Specialized Detail Pages -->
      <SofaDetailsPage v-else-if="page === 'sofadetails'" />
      <SofaCollectionDetailsPage v-else-if="page === 'sofacollectiondetails'" />
      <BenchDetailsPage v-else-if="page === 'benchdetails'" />
      <ChairDetailsPage v-else-if="page === 'chairdetails'" />
      <BarstoolDetailsPage v-else-if="page === 'barstooldetails'" />
      <TableDetailsPage v-else-if="page === 'tabledetails'" />

      <GalleryPage v-else-if="page === 'gallery'" />
      <ShopByLookPage v-else-if="page === 'shop-by-look'" />
      <SpecialEditionPage v-else-if="page === 'special-edition'" />
      <SpecialEditionDetailPage v-else-if="page === 'special-edition-item'" />
      <OutletPage v-else-if="page === 'outlet'" />
      <OutletDetailPage v-else-if="page === 'outlet-item'" />
      <FaqPage v-else-if="page === 'faq'" />
      <AboutPage v-else-if="page === 'about'" />
      <ProjectsPage v-else-if="page === 'projects'" />
      <ProjectDetailsPage v-else-if="page === 'project-details'" />
      <FabricsPage v-else-if="page === 'fabrics'" />
      <SavedProductsPage v-else-if="page === 'saved'" />
      <CartPage v-else-if="page === 'cart'" />
      <LoginPage v-else-if="page === 'login'" />
      <DashboardPage v-else-if="page === 'dashboard'" />
      <ManagementPage v-else-if="page === 'management'" />
      <ManagementVisualEditorPage v-else-if="page === 'management-editor'" />
      <ManagementProductsPage v-else-if="page === 'management-products'" />
      <ManagementBlogPage v-else-if="page === 'management-blog'" />
      <ManagementSupportPage v-else-if="page === 'management-support'" />
      <ManagementAuditPage v-else-if="page === 'management-audit'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-overview'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-traffic'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-funnel'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-behavior'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-products'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-time'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-technical'" />
      <ManagementAnalyticsPage v-else-if="page === 'management-analytics-settings'" />
      <DiningChairsPage v-else-if="page === 'dining-chairs'" />
      <TablesPage v-else-if="page === 'tables'" />
      <CoffeeTablesPage v-else-if="page === 'coffee-tables'" />
      <CushionsPage v-else-if="page === 'cushions'" />
      <BenchesPage v-else-if="page === 'benches'" />
      <BedsPage v-else-if="page === 'beds'" />
      <ProductsPrintPage v-else-if="page === 'products-print'" />
      <BarstoolsPage v-else-if="page === 'barstools'" />
    </main>

    <button
      v-if="showSupportFab && !isEditorFocusPage"
      class="support-fab"
      type="button"
      @click="openSupportChatFab"
    >
      چت پشتیبانی
    </button>

    <button
      v-if="supportNotice && !isEditorFocusPage"
      class="support-toast"
      type="button"
      @click="openSupportNotice"
    >
      <strong>{{ supportNotice.title }}</strong>
      <span>{{ supportNotice.body }}</span>
    </button>

    <MobileBottomNav v-if="!isAdminSection && !mobileNavHiddenPages.includes(page)" />
    <AdminFooter v-if="isAdminSection && !isEditorFocusPage" />
    <AppFooter v-else-if="!isEditorFocusPage && !footerlessPages.includes(page)" />
    <CookieConsentBanner v-if="!isAdminSection && !footerlessPages.includes(page)" />
    <CartSidebar v-if="!isAdminSection && isCartOpen" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AdminHeader from './components/admin/AdminHeader.vue'
import AppFooter from './components/AppFooter.vue'
import AdminFooter from './components/admin/AdminFooter.vue'
import MobileBottomNav from './components/MobileBottomNav.vue'
import CartSidebar from './components/CartSidebar.vue'
import CookieConsentBanner from './components/CookieConsentBanner.vue'
import { useCart } from './stores/cartStore'
import { trackAnalyticsEvent, trackPageView } from './utils/analyticsTracker'
import { initPagePerformanceTracking } from './utils/pagePerformanceTracker'
import { fetchAndApplyRouteContentOverrides, stopRouteContentOverrideObserver } from './utils/contentOverrideApplier'
import { syncManagementAccessState } from './utils/managementAccess'
import HomePage from './pages/HomePage.vue'

const { isCartOpen } = useCart()
import BarstoolsPage from './pages/BarstoolsPage.vue'
import SofaCollection from './pages/SofaCollection.vue'
import CategoriesPage from './pages/CategoriesPage.vue'
import BlogPage from './pages/BlogPage.vue'
import ConsultationPage from './pages/ConsultationPage.vue'
import CooperationPage from './pages/CooperationPage.vue'
import DealersPage from './pages/DealersPage.vue'
import DownloadsPage from './pages/DownloadsPage.vue'
import CustomProductsPage from './pages/CustomProductsPage.vue'
import ProductPage from './pages/ProductPage.vue'
import SofaPage from './pages/SofaPage.vue'
import DiningChairsPage from './pages/DiningChairsPage.vue'
import TablesPage from './pages/TablesPage.vue'
import CoffeeTablesPage from './pages/CoffeeTablesPage.vue'
import CushionsPage from './pages/CushionsPage.vue'
import BenchesPage from './pages/BenchesPage.vue'
import BedsPage from './pages/BedsPage.vue'
import ProductsPrintPage from './pages/ProductsPrintPage.vue'

// New Specialized Detail Pages
import SofaDetailsPage from './pages/SofaDetailsPage.vue'
import SofaCollectionDetailsPage from './pages/SofaCollectionDetailsPage.vue'
import BenchDetailsPage from './pages/BenchDetailsPage.vue'
import ChairDetailsPage from './pages/ChairDetailsPage.vue'
import BarstoolDetailsPage from './pages/BarstoolDetailsPage.vue'
import TableDetailsPage from './pages/TableDetailsPage.vue'
import GalleryPage from './pages/GalleryPage.vue'
import ShopByLookPage from './pages/ShopByLookPage.vue'
import SpecialEditionPage from './pages/SpecialEditionPage.vue'
import SpecialEditionDetailPage from './pages/SpecialEditionDetailPage.vue'
import OutletPage from './pages/OutletPage.vue'
import OutletDetailPage from './pages/OutletDetailPage.vue'
import FaqPage from './pages/FaqPage.vue'
import AboutPage from './pages/AboutPage.vue'
import ProjectsPage from './pages/ProjectsPage.vue'
import ProjectDetailsPage from './pages/ProjectDetailsPage.vue'
import FabricsPage from './pages/FabricsPage.vue'
import SavedProductsPage from './pages/SavedProductsPage.vue'
import CartPage from './pages/CartPage.vue'
import LoginPage from './pages/LoginPage.vue'
import DashboardPage from './pages/DashboardPage.vue'
import ManagementPage from './pages/ManagementPage.vue'
import ManagementVisualEditorPage from './pages/ManagementVisualEditorPage.vue'
import ManagementProductsPage from './pages/ManagementProductsPage.vue'
import ManagementBlogPage from './pages/ManagementBlogPage.vue'
import ManagementSupportPage from './pages/ManagementSupportPage.vue'
import ManagementAuditPage from './pages/ManagementAuditPage.vue'
import ManagementAnalyticsPage from './pages/ManagementAnalyticsPage.vue'

const page = window._PAGE || 'barstools'
const isEditorFocusPage = page === 'management-editor'
const isAdminSection = page === 'management' || page === 'management-editor' || page === 'management-products' || page === 'management-blog' || page === 'management-support' || page === 'management-audit' || page.startsWith('management-analytics')
const immersiveProductPages = ['sofadetails', 'sofacollectiondetails', 'benchdetails', 'chairdetails', 'barstooldetails', 'tabledetails', 'project-details']
const headerlessPages = ['login', ...immersiveProductPages]
const footerlessPages = ['login', 'products-print', ...immersiveProductPages]
const mobileNavHiddenPages = [...footerlessPages]
const pageViewHandledLocally = new Set(['categories', 'product'])
const analyticsEnabledPage = !isAdminSection && !['login', 'products-print'].includes(page)
const showSupportFab = false
const supportNotice = ref(null)
let globalLinkTrackerBound = false
let supportRealtimeBound = false
let supportToastTimer = null

function isGuestUser() {
  return String(window?.frappe?.session?.user || 'Guest') === 'Guest'
}

function openSupportChatFab() {
  if (isGuestUser()) {
    window.location.href = `/login?next=${encodeURIComponent('/dashboard?tab=support_tickets&open_chat=1')}`
    return
  }
  window.location.href = '/dashboard?tab=support_tickets&open_chat=1'
}

function playSupportSound() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    const ctx = new AudioCtx()
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()
    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(880, ctx.currentTime)
    oscillator.connect(gain)
    gain.connect(ctx.destination)
    gain.gain.setValueAtTime(0.001, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2)
    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + 0.22)
  } catch (error) {
    // ignore unsupported browsers
  }
}

function openSupportNotice() {
  if (!supportNotice.value) return
  const route = supportNotice.value.route || '/dashboard?tab=support_tickets'
  window.location.href = route
}

function bindSupportRealtime() {
  if (supportRealtimeBound) return
  const rt = window?.frappe?.realtime
  if (!rt || typeof rt.on !== 'function') return
  rt.on('mysite_support_notification', (payload) => {
    supportNotice.value = {
      title: payload?.title || 'اعلان پشتیبانی',
      body: payload?.body || '',
      route: payload?.route || '/dashboard?tab=support_tickets',
    }
    if (payload?.play_sound) {
      playSupportSound()
    }
    if (supportToastTimer) {
      clearTimeout(supportToastTimer)
    }
    supportToastTimer = setTimeout(() => {
      supportNotice.value = null
    }, 6500)
  })
  supportRealtimeBound = true
}

function isWhatsAppLink(href) {
  const value = String(href || '').toLowerCase()
  return value.includes('wa.me') || value.includes('whatsapp.com') || value.startsWith('whatsapp:')
}

function onGlobalLinkClick(event) {
  if (!analyticsEnabledPage) return
  const anchor = event?.target?.closest?.('a[href]')
  if (!anchor) return

  const rawHref = String(anchor.getAttribute('href') || '').trim()
  if (!rawHref) return
  const href = rawHref.toLowerCase()
  const targetLabel = (anchor.textContent || '').trim().slice(0, 120)
  const commonPayload = {
    page_url: window.location.pathname + window.location.search,
    properties: {
      target: rawHref,
      label: targetLabel,
    },
  }

  if (href.startsWith('tel:')) {
    trackAnalyticsEvent('call_click', commonPayload)
    return
  }
  if (isWhatsAppLink(href)) {
    trackAnalyticsEvent('whatsapp_click', commonPayload)
    return
  }
  if (href.startsWith('mailto:')) {
    trackAnalyticsEvent('email_click', commonPayload)
  }
}

onMounted(async () => {
  if (isAdminSection) {
    syncManagementAccessState(window.management_boot || {})
    try {
      const response = await fetch('/api/method/mysite.api.can_access_management', {
        credentials: 'same-origin',
      })
      const payload = await response.json()
      syncManagementAccessState(payload || {})
      const allowed = !!(payload?.message?.allowed || payload?.allowed)
      if (!allowed) {
        window.location.replace('/login')
      } else if (!isGuestUser()) {
        bindSupportRealtime()
      }
    } catch (error) {
      window.location.replace('/login')
    }
    return
  }

  if (!['login', 'products-print'].includes(page)) {
    await fetchAndApplyRouteContentOverrides(window.location.pathname)
  }

  if (!analyticsEnabledPage) return

  initPagePerformanceTracking({ page })

  if (!pageViewHandledLocally.has(page)) {
    trackPageView({
      properties: {
        page,
      },
    })
  }

  if (!globalLinkTrackerBound) {
    document.addEventListener('click', onGlobalLinkClick, true)
    globalLinkTrackerBound = true
  }

  if (!isGuestUser()) {
    bindSupportRealtime()
  }
})

onBeforeUnmount(() => {
  if (globalLinkTrackerBound) {
    document.removeEventListener('click', onGlobalLinkClick, true)
    globalLinkTrackerBound = false
  }
  if (supportToastTimer) {
    clearTimeout(supportToastTimer)
    supportToastTimer = null
  }
  if (supportRealtimeBound && window?.frappe?.realtime && typeof window.frappe.realtime.off === 'function') {
    window.frappe.realtime.off('mysite_support_notification')
    supportRealtimeBound = false
  }
  stopRouteContentOverrideObserver()
})
</script>

<style>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  color: var(--text-main);
  transition: background-color 0.3s, color 0.3s;
}

.app-main {
  flex: 1;
}

.app-layout--editor-focus {
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background: #0f1217;
}

.app-main-editor-focus {
  height: 100%;
  overflow: hidden;
  padding-bottom: 0 !important;
}

.support-fab {
  position: fixed;
  left: 18px;
  bottom: 18px;
  z-index: 850;
  border: 1px solid rgba(238, 199, 120, 0.55);
  background: linear-gradient(135deg, rgba(30, 26, 18, 0.92), rgba(87, 66, 29, 0.92));
  color: #f6ddb0;
  border-radius: 999px;
  padding: 10px 14px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(14px);
}

.support-toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 900;
  width: min(360px, calc(100% - 36px));
  border: 1px solid rgba(238, 199, 120, 0.45);
  border-radius: 12px;
  padding: 10px 12px;
  text-align: right;
  color: #f7f2e6;
  background: rgba(20, 20, 20, 0.84);
  display: grid;
  gap: 4px;
  cursor: pointer;
}

.support-toast strong {
  font-size: 0.9rem;
}

.support-toast span {
  font-size: 0.82rem;
  opacity: 0.92;
}

/* Ensure fixed navigation doesn't overlap content on mobile if needed */
@media (max-width: 768px) {
  .app-main {
    padding-bottom: 80px; /* Space for MobileBottomNav */
  }
  .support-fab {
    left: 12px;
    bottom: 78px;
  }
  .support-toast {
    right: 12px;
    bottom: 134px;
  }
}
</style>
