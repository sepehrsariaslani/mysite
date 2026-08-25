<template>
  <header class="admin-header" dir="rtl">
    <div class="admin-inner">
      <a href="/mysite/management" class="brand" aria-label="ناحیه مدیریت">
        <span class="badge">مد</span>
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
          {{ item.label }}
        </a>
      </nav>

      <div class="admin-actions">
        <button class="theme-toggle" @click="toggleTheme" :aria-label="`تغییر تم به ${nextThemeLabel}`">
          <span>{{ isDark ? '🌙' : '☀️' }}</span>
          <span>{{ currentThemeLabel }}</span>
        </button>
        <a href="/mysite" class="action-link">بازگشت به سایت</a>
        <a href="/api/method/logout" class="action-link danger">خروج</a>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { hasManagementCapability } from '../../utils/managementAccess'

const page = window._PAGE || ''
const allLinks = [
  { label: 'داشبورد مدیریت', href: '/mysite/management', page: 'management', capability: 'content.edit' },
  { label: 'محصولات', href: '/mysite/management-products', page: 'management-products', capability: 'product.edit' },
  { label: 'بلاگ', href: '/mysite/management-blog', page: 'management-blog', capability: 'content.edit' },
  { label: 'پشتیبانی', href: '/mysite/management-support', page: 'management-support', capability: 'support.manage' },
  { label: 'ممیزی', href: '/mysite/management-audit', page: 'management-audit', capability: 'audit.view' },
  { label: 'آنالیتیکس مدیریت', href: '/mysite/management-analytics', page: 'management-analytics', capability: 'analytics.view' },
]
const links = computed(() => allLinks.filter((item) => hasManagementCapability(item.capability)))

const themeMode = ref('light')
const isDark = computed(() => themeMode.value === 'dark')
const currentThemeLabel = computed(() => (isDark.value ? 'تیره' : 'روشن'))
const nextThemeLabel = computed(() => (isDark.value ? 'روشن' : 'تیره'))

function isActive(linkPage) {
  if (linkPage === 'management-analytics') return page.startsWith('management-analytics')
  return page === linkPage
}

function resolveInitialTheme() {
  const attrTheme = document.documentElement.getAttribute('data-theme')
  if (attrTheme === 'dark' || attrTheme === 'light') return attrTheme

  try {
    const stored = localStorage.getItem('theme')
    if (stored === 'dark' || stored === 'light') return stored
  } catch (error) {
    // Ignore storage errors.
  }

  try {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    return prefersDark ? 'dark' : 'light'
  } catch (error) {
    return 'light'
  }
}

function applyTheme(mode, persist = true) {
  const normalized = mode === 'dark' ? 'dark' : 'light'
  themeMode.value = normalized
  document.documentElement.setAttribute('data-theme', normalized)
  if (!persist) return
  try {
    localStorage.setItem('theme', normalized)
  } catch (error) {
    // Ignore storage errors.
  }
}

function toggleTheme() {
  applyTheme(isDark.value ? 'light' : 'dark')
}

onMounted(() => {
  applyTheme(resolveInitialTheme(), false)
})
</script>

<style scoped>
.admin-header {
  position: sticky;
  top: 0;
  z-index: 420;
  border-bottom: 1px solid var(--admin-border);
  background: color-mix(in srgb, var(--admin-panel-bg) 88%, transparent);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
}

.admin-inner {
  width: min(1400px, 100%);
  margin: 0 auto;
  padding: 12px 18px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
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
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.08em;
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
  gap: 8px;
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

.theme-toggle {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  padding: 7px 10px;
  font-family: inherit;
  font-size: 0.78rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.theme-toggle:hover {
  border-color: var(--admin-tab-active-start);
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
}

.action-link:hover {
  border-color: var(--admin-tab-active-start);
}

.action-link.danger {
  border-color: color-mix(in srgb, #ef4444 55%, var(--admin-border) 45%);
  color: color-mix(in srgb, #ef4444 78%, var(--text-main) 22%);
}

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

  .theme-toggle span:last-child {
    display: none;
  }
}
</style>
