<template>
  <div class="projects-page" dir="rtl">
    <header class="projects-hero">
      <div class="hero-text">
        <p class="eyebrow">Customer Projects</p>
        <h1>پروژه‌های اجراشده دن‌روم</h1>
        <p class="sub">نمونه پروژه‌های واقعی با محصولات اجرا شده، همراه با جزئیات کامل هر پروژه.</p>
      </div>

      <div class="hero-controls">
        <label class="search-box">
          <input v-model.trim="searchQuery" type="search" placeholder="جستجوی پروژه..." />
        </label>

        <div class="chips">
          <button
            v-for="filter in filters"
            :key="filter.id"
            class="chip"
            :class="{ active: activeFilter === filter.id }"
            @click="activeFilter = filter.id"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
    </header>

    <main class="projects-main" v-if="filteredProjects.length">
      <article v-for="project in filteredProjects" :key="project.id" class="project-card">
        <div class="cover-wrap">
          <img v-if="project.cover_image" :src="project.cover_image" :alt="project.title" class="cover-image" />
          <div v-else class="cover-fallback">بدون تصویر</div>
          <div class="cover-glow"></div>
        </div>

        <div class="project-body">
          <div class="project-meta">
            <span class="meta-pill">{{ project.project_type_label }}</span>
            <span v-if="project.location" class="meta-pill ghost">{{ project.location }}</span>
            <span v-if="project.project_date" class="meta-pill ghost">{{ formatDate(project.project_date) }}</span>
          </div>

          <h2 class="project-title">{{ project.title }}</h2>
          <p v-if="project.short_description" class="project-desc">{{ project.short_description }}</p>

          <div class="used-products" v-if="project.preview_products?.length">
            <div class="thumbs">
              <img
                v-for="item in project.preview_products.slice(0, 5)"
                :key="item.id"
                :src="item.image"
                :alt="item.item_name"
                class="thumb"
              />
            </div>
            <span class="count">{{ project.product_count }} محصول استفاده‌شده</span>
          </div>

          <a :href="buildProjectRoute(project)" class="open-btn">
            مشاهده جزئیات پروژه
          </a>
        </div>
      </article>
    </main>

    <section v-else class="empty-state">
      <p>پروژه‌ای با این فیلتر یا جستجو پیدا نشد.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const projects = ref(window.Projects || [])
const filters = ref(window.ProjectFilters || [{ id: 'all', label: 'همه' }])
const activeFilter = ref('all')
const searchQuery = ref('')

const selectedCustomer = ref(
  window.SelectedCustomer
    || (() => {
      try {
        return localStorage.getItem('mysite_selected_customer') || ''
      } catch (e) {
        return ''
      }
    })()
)

const filteredProjects = computed(() => {
  const byFilter = activeFilter.value === 'all'
    ? projects.value
    : projects.value.filter((project) => project.filter_id === activeFilter.value)

  const query = normalize(searchQuery.value)
  if (!query) return byFilter

  return byFilter.filter((project) => {
    const searchable = [
      project.title,
      project.project_type_label,
      project.location,
      project.customer_name,
      ...(project.products || []).map((item) => item.item_name),
    ].map(normalize).join(' ')
    return searchable.includes(query)
  })
})

function normalize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\u064a/g, 'ی')
    .replace(/\u0643/g, 'ک')
    .replace(/\s+/g, ' ')
    .trim()
}

function buildProjectRoute(project) {
  const route = project?.route || ''
  if (!route || !selectedCustomer.value || route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

function formatDate(dateText) {
  if (!dateText) return ''
  try {
    return new Date(dateText).toLocaleDateString('fa-IR')
  } catch (e) {
    return dateText
  }
}
</script>

<style scoped>
.projects-page {
  min-height: 100vh;
  padding: 44px 24px 100px;
  background:
    radial-gradient(circle at 10% 5%, rgba(255, 203, 135, 0.2), transparent 30%),
    radial-gradient(circle at 90% 16%, rgba(145, 93, 60, 0.22), transparent 34%),
    var(--bg-main);
}

.projects-hero {
  max-width: 1320px;
  margin: 0 auto 28px;
  display: grid;
  gap: 14px;
  border-radius: 24px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 18px;
}

.eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 900;
  color: var(--accent-gold);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(30px, 4.2vw, 54px);
  line-height: 1.08;
  font-weight: 950;
}

.sub {
  margin: 10px 0 0;
  color: var(--text-muted);
  max-width: 700px;
  font-size: 15px;
  line-height: 1.9;
}

.hero-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-box {
  width: min(420px, 100%);
}

.search-box input {
  width: 100%;
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: var(--glass-bg);
  color: var(--text-main);
  font-size: 14px;
  font-family: inherit;
  padding: 10px 14px;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-gold);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: var(--glass-bg);
  color: var(--text-muted);
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  padding: 9px 16px;
  cursor: pointer;
}

.chip.active {
  color: #3b281e;
  background: var(--accent-gold);
  border-color: var(--accent-gold);
}

.projects-main {
  max-width: 1320px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 18px;
}

.project-card {
  display: grid;
  grid-template-rows: auto 1fr;
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  overflow: hidden;
  background: var(--glass-bg);
  transition: transform 0.22s ease, border-color 0.22s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  border-color: var(--glass-border-bright);
}

.cover-wrap {
  position: relative;
  min-height: 250px;
  background: #e8dfd6;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-glow {
  position: absolute;
  inset: auto 0 0;
  height: 40%;
  background: linear-gradient(to top, rgba(15, 11, 10, 0.55), transparent);
  pointer-events: none;
}

.cover-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #6f5f56;
  font-weight: 700;
}

.project-body {
  padding: 18px;
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 10px;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-pill {
  border-radius: 999px;
  background: rgba(242, 201, 126, 0.24);
  border: 1px solid rgba(242, 201, 126, 0.35);
  color: var(--accent-gold);
  font-size: 11px;
  font-weight: 800;
  padding: 5px 10px;
}

.meta-pill.ghost {
  color: var(--text-muted);
  border-color: var(--glass-border);
  background: rgba(255, 255, 255, 0.03);
}

.project-title {
  margin: 0;
  font-size: clamp(24px, 2.4vw, 32px);
  line-height: 1.3;
  font-weight: 900;
}

.project-desc {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.8;
  font-size: 13px;
}

.used-products {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px dashed var(--glass-border);
  padding-top: 10px;
}

.thumbs {
  display: flex;
  align-items: center;
}

.thumb {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.7);
  margin-left: -10px;
  background: #d8cec4;
}

.count {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.open-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border-radius: 10px;
  background: var(--accent-gold);
  color: #3d2b20;
  font-size: 13px;
  font-weight: 900;
  padding: 10px 14px;
  transition: transform 0.2s ease;
}

.open-btn:hover {
  transform: translateY(-1px);
}

.empty-state {
  max-width: 1320px;
  margin: 22px auto 0;
  padding: 24px;
  border: 1px dashed var(--glass-border);
  border-radius: 18px;
  color: var(--text-muted);
  text-align: center;
}

@media (max-width: 1024px) {
  .projects-main {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .projects-page {
    padding: 24px 12px 90px;
  }

  .cover-wrap {
    min-height: 220px;
  }

  .projects-hero {
    padding: 14px;
  }
}
</style>
