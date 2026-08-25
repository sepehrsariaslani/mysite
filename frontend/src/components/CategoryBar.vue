<template>
  <section v-if="renderedCategories.length" class="cat-shell" dir="rtl" aria-label="دسته بندی محصولات">
    <div class="cat-bar-wrap">
      <div class="cat-bar-scroll">
        <div class="cat-bar">
          <a
            v-for="cat in renderedCategories"
            :key="cat.id"
            :href="cat.url"
            class="cat-item"
            :class="{ active: cat.activeResolved }"
          >
            <div class="cat-img-wrap">
              <img :src="cat.image" :alt="cat.name" loading="lazy" />
            </div>
            <span class="cat-name">{{ cat.name }}</span>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const FALLBACK_CATEGORIES = [
  { id: 'sofa', name: 'مبلمان', url: '/mysite/sofas', image: '/assets/mysite/frontend/images/cat-sofa.png' },
  { id: 'dining-chair', name: 'صندلی ناهارخوری', url: '/mysite/dining-chairs', image: '/assets/mysite/frontend/images/cat-dining-chair.png' },
  { id: 'open-chair', name: 'صندلی اپن', url: '/mysite/barstools', image: '/assets/mysite/frontend/images/cat-open-chair.png' },
  { id: 'dining-table', name: 'میز ناهارخوری', url: '/mysite/tables', image: '/assets/mysite/frontend/images/cat-dining-table.png' },
  { id: 'coffee-table', name: 'میز جلو مبلی و عسلی', url: '/mysite/coffee-tables', image: '/assets/mysite/frontend/images/cat-coffee-table.png' },
  { id: 'cushions', name: 'کوسن و تشکچه', url: '/mysite/cushions', image: '/assets/mysite/frontend/images/cat-bench.png' },
  { id: 'bench', name: 'نیمکت', url: '/mysite/benches', image: '/assets/mysite/frontend/images/cat-bench.png' },
  { id: 'bed', name: 'سرویس خواب', url: '/mysite/beds', image: '/assets/mysite/frontend/images/cat-bed.png' },
]

const props = defineProps({
  categories: {
    type: Array,
    default: () => [],
  },
})

const currentPath = computed(() => {
  if (typeof window === 'undefined') return ''
  const path = String(window.location?.pathname || '')
  if (!path) return ''
  return path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path
})

function normalizePath(path) {
  const value = String(path || '').trim()
  if (!value) return ''
  return value.endsWith('/') && value.length > 1 ? value.slice(0, -1) : value
}

function resolveActive(cat) {
  if (cat.active === true) return true
  const target = normalizePath(cat.url)
  if (!target || !currentPath.value) return false
  return currentPath.value === target || currentPath.value.startsWith(`${target}/`)
}

const renderedCategories = computed(() => {
  const source = Array.isArray(props.categories) && props.categories.length ? props.categories : FALLBACK_CATEGORIES
  return source
    .map((cat, idx) => ({
      id: cat?.id || `cat-${idx}`,
      name: String(cat?.name || '').trim(),
      url: String(cat?.url || '/mysite/categories').trim(),
      image: String(cat?.image || '/assets/mysite/frontend/images/cat-sofa.png').trim(),
      active: Boolean(cat?.active),
    }))
    .filter((cat) => cat.name)
    .map((cat) => ({
      ...cat,
      activeResolved: resolveActive(cat),
    }))
})
</script>

<style scoped>
.cat-shell {
  position: relative;
  width: 100%;
  padding: 0 18px;
  margin-top: -8px;
  z-index: 12;
}

.cat-bar-wrap {
  width: min(1280px, 100%);
  margin: 0 auto;
  border: 1px solid color-mix(in srgb, var(--glass-border) 84%, transparent);
  border-radius: 24px;
  background: linear-gradient(140deg, color-mix(in srgb, var(--glass-bg) 90%, transparent), color-mix(in srgb, var(--bg-secondary) 86%, transparent));
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 42px rgba(16, 25, 40, 0.12);
}

.cat-bar-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 14px;
}

.cat-bar-scroll::-webkit-scrollbar {
  display: none;
}

.cat-bar {
  display: flex;
  gap: 10px;
  width: max-content;
  min-width: 100%;
  justify-content: center;
}

.cat-item {
  width: 112px;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  text-decoration: none;
  padding: 10px 8px;
  border-radius: 18px;
  border: 1px solid transparent;
  transition: transform 0.22s ease, background 0.22s ease, border-color 0.22s ease;
}

.cat-img-wrap {
  width: 94px;
  height: 88px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--glass-bg) 88%, transparent);
  border: 1px solid color-mix(in srgb, var(--glass-border) 78%, transparent);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  overflow: hidden;
}

.cat-img-wrap img {
  width: 88%;
  height: 90%;
  object-fit: contain;
  object-position: bottom center;
  transition: transform 0.25s ease;
}

.cat-name {
  font-size: 12px;
  line-height: 1.5;
  font-weight: 700;
  color: var(--text-main);
  text-align: center;
  max-width: 100%;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cat-item:hover {
  transform: translateY(-3px);
  border-color: var(--glass-border);
  background: color-mix(in srgb, var(--glass-bg-hover) 82%, transparent);
}

.cat-item:hover .cat-img-wrap img {
  transform: scale(1.06);
}

.cat-item.active {
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent-brown) 94%, transparent), color-mix(in srgb, var(--accent-brown) 84%, black 16%));
  border-color: color-mix(in srgb, var(--accent-gold) 75%, transparent);
}

.cat-item.active .cat-img-wrap {
  background: color-mix(in srgb, var(--accent-gold) 22%, var(--glass-bg) 78%);
  border-color: color-mix(in srgb, var(--accent-gold) 65%, transparent);
}

.cat-item.active .cat-name {
  color: var(--accent-gold);
}

@media (max-width: 700px) {
  .cat-shell {
    padding: 0 10px;
  }

  .cat-bar-wrap {
    border-radius: 18px;
  }

  .cat-bar-scroll {
    padding: 10px;
  }

  .cat-bar {
    justify-content: flex-start;
  }

  .cat-item {
    width: 92px;
    min-height: 120px;
    border-radius: 14px;
    gap: 8px;
    padding: 8px 6px;
  }

  .cat-img-wrap {
    width: 74px;
    height: 70px;
    border-radius: 12px;
  }

  .cat-name {
    font-size: 11px;
  }
}
</style>
