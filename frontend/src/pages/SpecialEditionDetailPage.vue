<template>
  <div class="special-detail-page" dir="rtl">
    <CategoryBar />

    <section class="detail-shell">
      <div class="detail-bg" aria-hidden="true">
        <span class="flare flare-a"></span>
        <span class="flare flare-b"></span>
        <span class="flare flare-c"></span>
      </div>

      <header class="detail-hero liquid" data-reveal>
        <div class="hero-top">
          <span class="hero-eyebrow">SPECIAL EDITION DETAIL</span>
          <span class="hero-code">{{ detail.itemCode }}</span>
        </div>

        <h1>{{ detail.title }}</h1>
        <p class="subtitle">{{ detail.subtitle }}</p>

        <div class="hero-chips">
          <span class="chip">تیراژ {{ toPersianDigits(String(detail.editionCount)) }} عدد</span>
          <span class="chip">نسخه محدود</span>
          <span class="chip">امضای دن‌روم</span>
        </div>

        <strong class="hero-price">{{ formatPrice(detail.priceToman) }}</strong>

        <div class="hero-actions">
          <a class="btn btn-primary" :href="detail.productRoute">مشاهده صفحه محصول</a>
          <a class="btn btn-ghost" href="/mysite/special-edition">بازگشت به Special Edition</a>
        </div>
      </header>

      <section class="detail-main">
        <article class="gallery-card liquid" data-reveal>
          <div class="main-image">
            <img :src="activeImage" :alt="detail.title" />
          </div>

          <div class="thumb-list" v-if="gallery.length > 1">
            <button
              v-for="(image, index) in gallery"
              :key="`${image}-${index}`"
              class="thumb"
              :class="{ active: image === activeImage }"
              type="button"
              @click="activeImage = image"
            >
              <img :src="image" :alt="`تصویر ${index + 1}`" />
            </button>
          </div>
        </article>

        <article class="story-card liquid" data-reveal>
          <h2>روایت کالکشن</h2>
          <p>{{ detail.story }}</p>
          <p>{{ detail.craftNote }}</p>
          <p>{{ detail.luxuryNote }}</p>

          <div class="attrs" v-if="attributes.length">
            <h3>مشخصات شاخص</h3>
            <div class="attr-grid">
              <div class="attr-item" v-for="(attr, index) in attributes" :key="`${attr.label}-${index}`">
                <span>{{ attr.label }}</span>
                <strong>{{ attr.value }}</strong>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="related" data-reveal v-if="relatedItems.length">
        <div class="related-head">
          <span>CURATED SET</span>
          <h2>سایر نسخه‌های محدود</h2>
        </div>

        <div class="related-grid">
          <article v-for="(item, index) in relatedItems" :key="`${item.itemCode}-${index}`" class="related-card liquid">
            <a :href="item.detailRoute" class="related-image">
              <img :src="item.image" :alt="item.title" loading="lazy" />
            </a>
            <div class="related-body">
              <h3>{{ item.title }}</h3>
              <p>{{ item.model }}</p>
              <div class="related-footer">
                <strong>{{ formatPrice(item.priceToman) }}</strong>
                <a :href="item.detailRoute">جزئیات</a>
              </div>
            </div>
          </article>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'

const FALLBACK_DETAIL = {
  itemCode: 'SE-SAMPLE',
  title: 'Special Edition',
  subtitle: 'نسخه محدود دن‌روم',
  image: '/assets/mysite/img/placeholder.png',
  gallery: ['/assets/mysite/img/placeholder.png'],
  priceToman: 0,
  editionCount: 1,
  productRoute: '/mysite/categories',
  detailRoute: '/mysite/special-edition',
  story: 'این محصول بخشی از سری نسخه محدود دن‌روم است.',
  craftNote: 'پس از فعال‌سازی داده واقعی، اطلاعات تکمیلی از ERPNext نمایش داده می‌شود.',
  luxuryNote: 'این سری برای پروژه‌های شاخص با استاندارد ساخت ویژه تعریف شده است.',
  attributes: [],
}

function asText(value, fallback = '') {
  const text = String(value ?? '').trim()
  return text || fallback
}

function asNumber(value, fallback = 0) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function normalizeDetail(raw) {
  const value = raw && typeof raw === 'object' ? raw : {}
  const gallery = Array.isArray(value.gallery) ? value.gallery : []
  const image = asText(value.image, '/assets/mysite/img/placeholder.png')
  const normalizedGallery = gallery.map((entry) => asText(entry)).filter(Boolean)
  if (!normalizedGallery.length) normalizedGallery.push(image)

  return {
    itemCode: asText(value.item_code || value.itemCode, FALLBACK_DETAIL.itemCode),
    title: asText(value.title, FALLBACK_DETAIL.title),
    subtitle: asText(value.subtitle || value.model, FALLBACK_DETAIL.subtitle),
    image,
    gallery: normalizedGallery,
    priceToman: asNumber(value.price_toman ?? value.priceToman, FALLBACK_DETAIL.priceToman),
    editionCount: Math.max(1, asNumber(value.edition_count ?? value.editionCount, FALLBACK_DETAIL.editionCount)),
    productRoute: asText(value.product_route || value.productRoute, FALLBACK_DETAIL.productRoute),
    detailRoute: asText(value.detail_route || value.detailRoute, FALLBACK_DETAIL.detailRoute),
    story: asText(value.story, FALLBACK_DETAIL.story),
    craftNote: asText(value.craft_note || value.craftNote, FALLBACK_DETAIL.craftNote),
    luxuryNote: asText(value.luxury_note || value.luxuryNote, FALLBACK_DETAIL.luxuryNote),
    attributes: Array.isArray(value.attributes)
      ? value.attributes
          .map((attr) => ({
            label: asText(attr?.label),
            value: asText(attr?.value),
          }))
          .filter((attr) => attr.label && attr.value)
      : [],
  }
}

function normalizeRelated(raw) {
  const rows = Array.isArray(raw) ? raw : []
  return rows
    .map((item) => ({
      itemCode: asText(item?.item_code || item?.itemCode),
      title: asText(item?.title),
      model: asText(item?.model),
      image: asText(item?.image, '/assets/mysite/img/placeholder.png'),
      priceToman: asNumber(item?.price_toman ?? item?.priceToman),
      detailRoute: asText(item?.detail_route || item?.detailRoute, '/mysite/special-edition'),
    }))
    .filter((item) => item.itemCode && item.title)
}

function toPersianDigits(value) {
  return String(value).replace(/\d/g, (digit) => '۰۱۲۳۴۵۶۷۸۹'[Number(digit)])
}

function formatPrice(value) {
  const amount = Math.max(0, asNumber(value))
  if (!amount) return 'تماس برای قیمت'
  return `${toPersianDigits(amount.toLocaleString('en-US'))} تومان`
}

const detail = normalizeDetail(window.SpecialEditionDetail)
const relatedItems = normalizeRelated(window.SpecialEditionRelated)
const gallery = detail.gallery
const attributes = detail.attributes
const activeImage = ref(gallery[0] || detail.image)

let revealObserver = null

function setupReveal() {
  const nodes = Array.from(document.querySelectorAll('.special-detail-page [data-reveal]'))
  if (!nodes.length) return
  if (!('IntersectionObserver' in window)) {
    nodes.forEach((node) => node.classList.add('visible'))
    return
  }
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        entry.target.classList.add('visible')
        revealObserver?.unobserve(entry.target)
      })
    },
    { threshold: 0.14, rootMargin: '0px 0px -8% 0px' }
  )
  nodes.forEach((node) => revealObserver.observe(node))
}

onMounted(() => {
  setupReveal()
})

onUnmounted(() => {
  revealObserver?.disconnect()
  revealObserver = null
})
</script>

<style scoped>
.special-detail-page {
  --sd-bg: #060304;
  --sd-bg-soft: #120506;
  --sd-text: #f6eeee;
  --sd-muted: rgba(225, 205, 205, 0.72);
  --sd-red: #7e151d;
  --sd-red-strong: #b31f29;
  --sd-border: rgba(126, 21, 29, 0.38);
  --sd-border-soft: rgba(126, 21, 29, 0.25);
  --sd-surface: rgba(24, 8, 10, 0.78);
  --sd-surface-soft: rgba(36, 11, 14, 0.68);
  --sd-shadow: 0 30px 62px rgba(0, 0, 0, 0.46);
  min-height: 100vh;
  background: radial-gradient(circle at 18% 12%, #2b070a 0%, #110506 52%, #030202 100%);
  color: var(--sd-text);
  font-family: 'Peyda', sans-serif;
  overflow: hidden;
}

[data-theme='light'] .special-detail-page {
  --sd-bg: #f7f3f2;
  --sd-bg-soft: #eee6e5;
  --sd-text: #2f1819;
  --sd-muted: rgba(80, 52, 53, 0.72);
  --sd-red: #7e151d;
  --sd-red-strong: #5e0f14;
  --sd-border: rgba(126, 21, 29, 0.3);
  --sd-border-soft: rgba(126, 21, 29, 0.2);
  --sd-surface: rgba(255, 255, 255, 0.82);
  --sd-surface-soft: rgba(241, 235, 234, 0.84);
  --sd-shadow: 0 28px 58px rgba(86, 25, 30, 0.2);
  background: radial-gradient(circle at 18% 12%, #ffffff 0%, #f3eceb 56%, #ebe2e1 100%);
}

.detail-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px 110px;
  position: relative;
}

.detail-bg {
  position: absolute;
  inset: 30px 0 0;
  pointer-events: none;
}

.flare {
  position: absolute;
  border-radius: 50%;
  filter: blur(72px);
  animation: drift 11s ease-in-out infinite alternate;
}

.flare-a {
  width: 330px;
  height: 330px;
  top: 30px;
  right: -52px;
  background: radial-gradient(circle, rgba(142, 23, 32, 0.35) 0%, rgba(142, 23, 32, 0) 72%);
}

.flare-b {
  width: 420px;
  height: 420px;
  left: -120px;
  top: 340px;
  background: radial-gradient(circle, rgba(96, 14, 22, 0.31) 0%, rgba(96, 14, 22, 0) 72%);
  animation-delay: 1.4s;
}

.flare-c {
  width: 240px;
  height: 240px;
  left: 42%;
  bottom: 150px;
  background: radial-gradient(circle, rgba(177, 40, 53, 0.22) 0%, rgba(177, 40, 53, 0) 72%);
  animation-delay: 2.7s;
}

.liquid {
  background: linear-gradient(145deg, var(--sd-surface) 0%, var(--sd-surface-soft) 100%);
  border: 1px solid var(--sd-border);
  box-shadow: var(--sd-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.24);
  backdrop-filter: blur(16px) saturate(145%);
  -webkit-backdrop-filter: blur(16px) saturate(145%);
  overflow: hidden;
  position: relative;
}

.liquid::before {
  content: "";
  position: absolute;
  inset: -72% auto auto -34%;
  width: 146%;
  height: 220px;
  background: linear-gradient(110deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0));
  transform: rotate(-8deg);
  animation: shine 8.4s linear infinite;
  pointer-events: none;
}

[data-reveal] {
  opacity: 0;
  transform: translateY(22px) scale(0.986);
  transition: opacity 0.62s ease, transform 0.62s ease;
}

[data-reveal].visible {
  opacity: 1;
  transform: none;
}

.detail-hero {
  margin-top: 104px;
  border-radius: 36px;
  padding: 42px 38px 32px;
  z-index: 2;
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hero-eyebrow {
  font-size: 0.82rem;
  letter-spacing: 0.14em;
  color: var(--sd-red-strong);
  font-weight: 780;
}

.hero-code {
  font-size: 0.8rem;
  color: var(--sd-muted);
  border: 1px solid var(--sd-border-soft);
  border-radius: 999px;
  padding: 5px 11px;
}

.detail-hero h1 {
  margin: 14px 0 0;
  font-size: clamp(2.2rem, 4.8vw, 4.4rem);
  line-height: 1.03;
  color: var(--sd-red-strong);
  font-weight: 960;
}

.subtitle {
  margin: 10px 0 0;
  color: var(--sd-text);
  font-size: clamp(1rem, 2vw, 1.15rem);
}

.hero-chips {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border-radius: 999px;
  border: 1px solid var(--sd-border-soft);
  padding: 5px 10px;
  font-size: 0.76rem;
  color: var(--sd-muted);
  background: rgba(255, 255, 255, 0.03);
}

.hero-price {
  display: block;
  margin-top: 16px;
  color: var(--sd-red-strong);
  font-size: 1.42rem;
  font-weight: 910;
}

.hero-actions {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn {
  text-decoration: none;
  border-radius: 999px;
  padding: 10px 18px;
  font-size: 0.86rem;
  font-weight: 780;
  transition: transform 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, var(--sd-red) 0%, #5e0f15 100%);
  color: #fff;
  box-shadow: 0 12px 24px rgba(94, 15, 21, 0.34);
}

.btn-ghost {
  border: 1px solid var(--sd-border);
  color: var(--sd-text);
}

.btn:hover {
  transform: translateY(-1px);
}

.detail-main {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 14px;
}

.gallery-card,
.story-card {
  border-radius: 24px;
  padding: 16px;
}

.main-image {
  height: 430px;
  border-radius: 18px;
  border: 1px solid var(--sd-border-soft);
  background: radial-gradient(circle at 50% 26%, rgba(255, 255, 255, 0.14), transparent 68%);
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 16px;
}

.thumb-list {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.thumb {
  border: 1px solid var(--sd-border-soft);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
  padding: 0;
  cursor: pointer;
}

.thumb.active {
  border-color: var(--sd-red);
}

.thumb img {
  width: 100%;
  height: 78px;
  object-fit: cover;
}

.story-card h2 {
  margin: 2px 0 8px;
  font-size: 1.35rem;
  color: var(--sd-red-strong);
}

.story-card p {
  margin: 0 0 8px;
  color: var(--sd-muted);
  line-height: 1.92;
  font-size: 0.95rem;
}

.attrs {
  margin-top: 12px;
}

.attrs h3 {
  margin: 0 0 8px;
  font-size: 1rem;
  color: var(--sd-text);
}

.attr-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.attr-item {
  border: 1px solid var(--sd-border-soft);
  border-radius: 12px;
  padding: 10px;
}

.attr-item span {
  display: block;
  font-size: 0.77rem;
  color: var(--sd-muted);
  margin-bottom: 4px;
}

.attr-item strong {
  color: var(--sd-text);
  font-size: 0.92rem;
}

.related {
  margin-top: 16px;
}

.related-head span {
  color: var(--sd-red);
  font-size: 0.8rem;
  letter-spacing: 0.1em;
}

.related-head h2 {
  margin: 4px 0 0;
  font-size: 1.45rem;
  color: var(--sd-text);
}

.related-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.related-card {
  border-radius: 18px;
  border-color: var(--sd-border-soft);
}

.related-image {
  display: block;
  height: 170px;
  border-bottom: 1px solid var(--sd-border-soft);
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
}

.related-body {
  padding: 10px 10px 12px;
}

.related-body h3 {
  margin: 0;
  font-size: 0.98rem;
  color: var(--sd-text);
}

.related-body p {
  margin: 5px 0 0;
  font-size: 0.79rem;
  color: var(--sd-muted);
}

.related-footer {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.related-footer strong {
  font-size: 0.88rem;
  color: var(--sd-red-strong);
}

.related-footer a {
  color: var(--sd-text);
  text-decoration: none;
  font-size: 0.76rem;
  border: 1px solid var(--sd-border-soft);
  border-radius: 999px;
  padding: 4px 8px;
}

@keyframes drift {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(20px, -20px) scale(1.06); }
}

@keyframes shine {
  0% { transform: translateX(-140%) rotate(-8deg); }
  100% { transform: translateX(140%) rotate(-8deg); }
}

@media (max-width: 1180px) {
  .detail-main {
    grid-template-columns: 1fr;
  }

  .related-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 920px) {
  .detail-shell {
    padding: 0 14px 84px;
  }

  .detail-hero {
    margin-top: 86px;
    border-radius: 24px;
    padding: 28px 16px 22px;
  }

  .main-image {
    height: 310px;
  }

  .thumb-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .hero-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    text-align: center;
  }

  .related-grid {
    grid-template-columns: 1fr;
  }

  .attr-grid {
    grid-template-columns: 1fr;
  }
}
</style>
