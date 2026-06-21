<template>
  <section class="projects-preview" dir="rtl" v-if="cards.length">
    <div class="head">
      <div>
        <p class="eyebrow">Projects</p>
        <h2>پروژه‌های منتخب مشتریان</h2>
      </div>
      <a :href="allProjectsRoute" class="view-all">مشاهده همه</a>
    </div>

    <div class="grid">
      <article v-for="project in cards" :key="project.id" class="card">
        <a :href="projectRoute(project)" class="cover-link">
          <img :src="project.cover_image" :alt="project.title" class="cover" />
          <span class="type-pill">{{ project.project_type_label }}</span>
        </a>

        <div class="body">
          <h3>{{ project.title }}</h3>
          <p class="desc" v-if="project.short_description">{{ project.short_description }}</p>
          <div class="meta-row">
            <span class="meta" v-if="project.location">{{ project.location }}</span>
            <span class="meta">{{ project.product_count }} محصول</span>
          </div>

          <div class="thumbs" v-if="project.preview_products?.length">
            <img
              v-for="item in project.preview_products.slice(0, 5)"
              :key="item.id"
              :src="item.image"
              :alt="item.item_name"
              class="thumb"
            />
          </div>

          <a :href="projectRoute(project)" class="open-btn">ورود به پروژه</a>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  projects: { type: Array, default: () => [] },
  selectedCustomer: { type: String, default: '' },
})

const localCustomer = ref(
  props.selectedCustomer
    || window.SelectedCustomer
    || (() => {
      try {
        return localStorage.getItem('mysite_selected_customer') || ''
      } catch (e) {
        return ''
      }
    })()
)

const cards = computed(() => (props.projects || []).slice(0, 6))

const allProjectsRoute = computed(() => {
  const base = '/projects'
  if (!localCustomer.value) return base
  return `${base}?customer=${encodeURIComponent(localCustomer.value)}`
})

function appendCustomerQuery(route) {
  if (!route || !localCustomer.value || route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(localCustomer.value)}`
}

function projectRoute(project) {
  return appendCustomerQuery(project?.route || '')
}
</script>

<style scoped>
.projects-preview {
  --preview-surface: var(--home-surface-strong, rgba(255, 255, 255, 0.78));
  --preview-surface-soft: var(--home-surface, rgba(255, 255, 255, 0.6));
  --preview-border: var(--home-border, rgba(120, 85, 57, 0.2));
  --preview-border-strong: var(--home-border-strong, rgba(120, 85, 57, 0.32));
  --preview-text-main: var(--home-text-main, var(--text-main));
  --preview-text-muted: var(--home-text-muted, var(--text-muted));
  --preview-accent: var(--home-accent, var(--accent-gold));
  --preview-accent-strong: var(--home-accent-strong, #7b4f34);
  --preview-shadow: var(--home-shadow, 0 20px 52px rgba(71, 45, 27, 0.12));
  max-width: var(--home-shell-max, 1320px);
  margin: var(--home-space-lg, 72px) auto 0;
  padding: 0 var(--home-inline-pad, 24px);
  position: relative;
  z-index: 1;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 14px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--preview-accent-strong);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.head h2 {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  font-weight: 930;
  color: var(--preview-text-main);
}

.view-all {
  text-decoration: none;
  color: #fff8ee;
  background: var(--preview-accent-strong);
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 800;
  border: 1px solid transparent;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.view-all:hover {
  transform: translateY(-2px);
  box-shadow: var(--preview-shadow);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.card {
  border-radius: 22px;
  border: 1px solid var(--preview-border);
  overflow: hidden;
  background: var(--preview-surface);
  box-shadow: var(--preview-shadow);
}

.cover-link {
  display: block;
  position: relative;
}

.cover {
  width: 100%;
  height: 250px;
  object-fit: cover;
}

.type-pill {
  position: absolute;
  right: 10px;
  top: 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--preview-accent-strong) 66%, #000 34%);
  border: 1px solid rgba(255, 255, 255, 0.24);
  color: #fbe2ba;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 800;
}

.body {
  padding: 12px;
  display: grid;
  gap: 8px;
}

.body h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  line-height: 1.4;
}

.desc {
  margin: 0;
  color: var(--preview-text-muted);
  font-size: 13px;
  line-height: 1.7;
}

.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.meta {
  font-size: 12px;
  color: var(--preview-text-muted);
  font-weight: 700;
}

.thumbs {
  display: flex;
  align-items: center;
  padding-top: 4px;
}

.thumb {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--preview-surface);
  margin-left: -9px;
}

.open-btn {
  display: inline-flex;
  justify-content: center;
  text-decoration: none;
  border-radius: 8px;
  background: var(--preview-accent-strong);
  color: #fff8ef;
  font-size: 12px;
  font-weight: 900;
  padding: 8px 10px;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .projects-preview {
    padding: 0 12px;
    margin-top: 56px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .head {
    align-items: center;
  }
}
</style>
  color: var(--preview-text-main);
