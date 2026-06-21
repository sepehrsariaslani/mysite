<template>
  <div class="project-details-page" dir="rtl">
    <main v-if="project" class="details-main">
      <header class="hero">
        <div class="hero-cover">
          <img v-if="currentGalleryImage?.image" :src="currentGalleryImage.image" :alt="project.title" class="cover-image" />
          <div v-else class="cover-fallback">بدون تصویر</div>
          <div class="hero-caption" v-if="currentGalleryImage?.caption">
            {{ currentGalleryImage.caption }}
          </div>

          <div class="gallery-strip" v-if="galleryImages.length > 1">
            <button
              v-for="(image, idx) in galleryImages"
              :key="image.id || idx"
              class="gallery-thumb-btn"
              :class="{ active: idx === activeImageIndex }"
              @click="activeImageIndex = idx"
            >
              <img :src="image.image" :alt="image.caption || project.title" class="gallery-thumb" />
            </button>
          </div>
        </div>

        <div class="hero-content">
          <a class="back-link" :href="projectsRoute">بازگشت به پروژه‌ها</a>
          <h1>{{ project.title }}</h1>
          <div class="meta">
            <span class="meta-pill">{{ project.project_type_label }}</span>
            <span v-if="project.customer_name" class="meta-pill ghost">{{ project.customer_name }}</span>
            <span v-if="project.location" class="meta-pill ghost">{{ project.location }}</span>
            <span v-if="project.project_date" class="meta-pill ghost">{{ formatDate(project.project_date) }}</span>
            <span v-if="project.project_area_sqm > 0" class="meta-pill ghost">
              متراژ: {{ formatArea(project.project_area_sqm) }}
            </span>
          </div>
          <p class="desc" v-if="project.short_description">{{ project.short_description }}</p>
          <div class="request-box" v-if="project.client_request">
            <strong>درخواست مشتری</strong>
            <p>{{ project.client_request }}</p>
          </div>
          <div class="full-desc" v-if="project.extended_notes" v-html="project.extended_notes"></div>
          <div class="full-desc" v-if="project.full_description" v-html="project.full_description"></div>
        </div>
      </header>

      <section class="products-section">
        <div class="section-head">
          <h2>محصولات استفاده‌شده در این پروژه</h2>
          <span class="counter">{{ project.products?.length || 0 }} محصول</span>
        </div>

        <div
          class="products-grid"
          :class="{ single: (project.products?.length || 0) === 1 }"
          v-if="project.products?.length"
        >
          <article v-for="item in project.products" :key="item.id" class="item-card">
            <div class="item-image-wrap">
              <img v-if="item.image" :src="item.image" :alt="item.item_name" class="item-image" />
              <div v-else class="item-fallback">بدون تصویر</div>
            </div>

            <div class="item-body">
              <p class="item-name">{{ item.item_name }}</p>
              <p class="item-code">{{ item.item_code }}</p>
              <p class="item-meta" v-if="item.note">{{ item.note }}</p>
              <p class="item-meta" v-if="item.cloth_name">پارچه: {{ item.cloth_name }}</p>
              <div class="item-row">
                <span class="qty">تعداد: {{ item.qty || 1 }}</span>
                <span class="price">{{ formatPrice(item.base_price) }}</span>
              </div>
              <a :href="appendCustomerQuery(item.target_route)" class="item-cta">مشاهده محصول</a>
            </div>
          </article>
        </div>

        <div v-else class="empty">
          <p>برای این پروژه هنوز محصول فعالی ثبت نشده است.</p>
        </div>
      </section>
    </main>

    <section v-else class="not-found">
      <p>اطلاعات پروژه پیدا نشد.</p>
      <a :href="projectsRoute">بازگشت به پروژه‌ها</a>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const project = ref(window.ProjectDetails || null)
const activeImageIndex = ref(0)

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

const projectsRoute = computed(() => {
  const base = '/projects'
  if (!selectedCustomer.value) return base
  return `${base}?customer=${encodeURIComponent(selectedCustomer.value)}`
})

function appendCustomerQuery(route) {
  if (!route || !selectedCustomer.value || route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(selectedCustomer.value)}`
}

function formatPrice(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function formatDate(dateText) {
  if (!dateText) return ''
  try {
    return new Date(dateText).toLocaleDateString('fa-IR')
  } catch (e) {
    return dateText
  }
}

const galleryImages = computed(() => {
  const projectImages = (project.value?.project_images || [])
    .filter((img) => img && img.image)
  if (projectImages.length) return projectImages
  if (project.value?.cover_image) return [{ id: 'cover', image: project.value.cover_image, caption: '' }]
  return []
})

const currentGalleryImage = computed(() => {
  if (!galleryImages.value.length) return null
  const normalizedIndex = Math.max(0, Math.min(activeImageIndex.value, galleryImages.value.length - 1))
  return galleryImages.value[normalizedIndex]
})

function formatArea(value) {
  const area = Number(value || 0)
  if (!Number.isFinite(area) || area <= 0) return ''
  return `${area.toLocaleString('fa-IR')} مترمربع`
}
</script>

<style scoped>
.project-details-page {
  min-height: 100vh;
  padding: 44px 24px 100px;
  background:
    radial-gradient(circle at 10% 8%, rgba(255, 205, 140, 0.2), transparent 34%),
    radial-gradient(circle at 85% 12%, rgba(133, 83, 52, 0.22), transparent 36%),
    var(--bg-main);
}

.details-main {
  max-width: 1320px;
  margin: 0 auto;
  display: grid;
  gap: 22px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  border-radius: 30px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  overflow: hidden;
}

.hero-cover {
  position: relative;
  min-height: 420px;
  background: #e8dfd6;
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6f5f56;
  font-weight: 700;
}

.hero-caption {
  position: absolute;
  inset: auto 10px 66px auto;
  max-width: 70%;
  border-radius: 10px;
  background: rgba(10, 7, 6, 0.72);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.6;
  padding: 7px 10px;
}

.gallery-strip {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 10px 10px;
  background: rgba(8, 6, 5, 0.36);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  scrollbar-width: thin;
}

.gallery-thumb-btn {
  flex: 0 0 auto;
  width: 82px;
  height: 56px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  padding: 0;
  background: transparent;
  overflow: hidden;
  cursor: pointer;
  opacity: 0.72;
}

.gallery-thumb-btn.active {
  opacity: 1;
  border-color: var(--accent-gold);
}

.gallery-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.hero-content {
  padding: 22px;
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
}

.back-link {
  display: inline-flex;
  width: fit-content;
  text-decoration: none;
  color: var(--accent-gold);
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 14px;
}

h1 {
  margin: 0;
  font-size: clamp(30px, 4.1vw, 52px);
  font-weight: 950;
  line-height: 1.08;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.meta-pill {
  border-radius: 999px;
  background: rgba(242, 201, 126, 0.24);
  border: 1px solid rgba(242, 201, 126, 0.38);
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

.desc {
  margin: 16px 0 0;
  color: var(--text-muted);
  line-height: 1.95;
  font-size: 14px;
}

.request-box {
  margin-top: 12px;
  border: 1px dashed var(--glass-border);
  border-radius: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
}

.request-box strong {
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 900;
}

.request-box p {
  margin: 6px 0 0;
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.8;
}

.full-desc {
  margin-top: 14px;
  color: var(--text-main);
  line-height: 1.95;
  border-top: 1px dashed var(--glass-border);
  padding-top: 12px;
}

.full-desc :deep(*) {
  max-width: 100%;
}

.full-desc :deep(p) {
  margin: 0 0 10px;
}

.full-desc :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
}

.full-desc :deep(ul),
.full-desc :deep(ol) {
  margin: 0 0 10px;
  padding-inline-start: 18px;
}

.products-section {
  border-radius: 26px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 18px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.section-head h2 {
  margin: 0;
  font-size: clamp(22px, 2.7vw, 34px);
  font-weight: 900;
}

.counter {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 800;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.products-grid.single {
  max-width: 420px;
}

.item-card {
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  display: grid;
  grid-template-rows: auto 1fr;
}

.item-image-wrap {
  aspect-ratio: 5 / 4;
  background: #e9e1d8;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6f5f56;
  font-size: 12px;
  font-weight: 700;
}

.item-body {
  padding: 12px;
  display: grid;
  gap: 7px;
}

.item-name {
  margin: 0;
  font-size: 15px;
  font-weight: 900;
  line-height: 1.6;
}

.item-code {
  margin: 0;
  color: var(--text-muted);
  font-size: 11px;
}

.item-meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.7;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.qty {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 700;
}

.price {
  font-size: 12px;
  color: var(--accent-gold);
  font-weight: 900;
}

.item-cta {
  margin-top: 2px;
  display: inline-flex;
  justify-content: center;
  text-decoration: none;
  background: var(--accent-gold);
  color: #3d2b20;
  border-radius: 8px;
  padding: 9px 10px;
  font-size: 12px;
  font-weight: 900;
}

.empty,
.not-found {
  padding: 22px;
  border: 1px dashed var(--glass-border);
  border-radius: 14px;
  color: var(--text-muted);
  text-align: center;
}

.not-found {
  max-width: 760px;
  margin: 80px auto 0;
}

.not-found a {
  color: var(--accent-gold);
  text-decoration: none;
  font-weight: 800;
}

@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-content {
    border-right: 0;
    border-top: 1px solid var(--glass-border);
  }

  .hero-cover {
    min-height: 320px;
  }

  .hero-caption {
    inset: auto 10px 62px auto;
    max-width: 85%;
  }
}

@media (max-width: 768px) {
  .project-details-page {
    padding: 24px 12px 90px;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .products-grid.single {
    max-width: none;
  }
}
</style>
