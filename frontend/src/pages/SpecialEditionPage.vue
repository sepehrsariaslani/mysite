<template>
  <div class="special-page" dir="rtl">
    <CategoryBar />

    <section class="special-shell">
      <div class="special-bg" aria-hidden="true">
        <span class="glow glow-a"></span>
        <span class="glow glow-b"></span>
        <span class="glow glow-c"></span>
      </div>

      <header class="hero liquid" data-reveal>
        <p class="hero-eyebrow">{{ hero.eyebrow }}</p>
        <h1>{{ hero.title }}</h1>
        <p class="hero-subtitle">{{ hero.subtitle }}</p>
        <p class="hero-note">{{ hero.note }}</p>

        <div class="hero-stats">
          <article class="stat-pill">
            <span>مدل خاص</span>
            <strong>{{ toPersianDigits(String(stats.itemsCount)) }}</strong>
          </article>
          <article class="stat-pill">
            <span>تیراژ محدود</span>
            <strong>{{ toPersianDigits(String(stats.totalUnits)) }}</strong>
          </article>
          <article class="stat-pill">
            <span>بازه قیمت</span>
            <strong>{{ formatPriceRange(stats.minPrice, stats.maxPrice) }}</strong>
          </article>
        </div>
      </header>

      <section class="cards-grid">
        <article
          v-for="(item, index) in items"
          :key="`${item.itemCode}-${index}`"
          class="product-card liquid"
          data-reveal
          :style="{ '--card-delay': `${Math.min(index * 70, 280)}ms` }"
        >
          <a :href="item.detailRoute" class="image-wrap" :aria-label="`مشاهده ${item.title}`">
            <img :src="item.image" :alt="item.title" loading="lazy" />
            <span class="edition-badge">LIMITED {{ toPersianDigits(String(item.editionCount)) }}</span>
          </a>

          <div class="card-body">
            <div class="meta-top">
              <span class="serial">#{{ toPersianDigits(String(index + 1)) }}</span>
              <span v-if="item.isFake" class="fake-pill">نمونه نمایشی</span>
            </div>

            <h2>{{ item.title }}</h2>
            <p class="model">{{ item.model }}</p>

            <div class="card-footer">
              <strong class="price">{{ formatPrice(item.priceToman) }}</strong>
              <a :href="item.detailRoute" class="open-link">جزئیات</a>
            </div>
          </div>
        </article>
      </section>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'

const FALLBACK_HERO = {
  eyebrow: 'DENROOM SIGNATURE SERIES',
  title: 'Special Edition',
  subtitle: 'نسخه‌های محدود و لوکس دن‌روم برای فضاهای شاخص',
  note: 'این مدل‌ها با تیراژ بسیار محدود تولید می‌شوند و بعد از تکمیل ظرفیت، امکان سفارش مجدد ندارند.',
}

const FALLBACK_ITEMS = [
  {
    itemCode: 'SE-SAMPLE-01',
    title: 'Hermes Atelier',
    model: 'Signature Sofa',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 289000000,
    editionCount: 7,
    detailRoute: '/special-edition/SE-SAMPLE-01',
    productRoute: '/sofas',
    isFake: 1,
  },
  {
    itemCode: 'SE-SAMPLE-02',
    title: 'Mahour Prestige',
    model: 'Dining Chair Edition',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 126000000,
    editionCount: 12,
    detailRoute: '/special-edition/SE-SAMPLE-02',
    productRoute: '/dining-chairs',
    isFake: 1,
  },
  {
    itemCode: 'SE-SAMPLE-03',
    title: 'Lumen Grand',
    model: 'Dining Table Edition',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 314000000,
    editionCount: 5,
    detailRoute: '/special-edition/SE-SAMPLE-03',
    productRoute: '/tables',
    isFake: 1,
  },
]

function asText(value, fallback = '') {
  const text = String(value ?? '').trim()
  return text || fallback
}

function asNumber(value, fallback = 0) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function normalizeHero(raw) {
  const value = raw && typeof raw === 'object' ? raw : {}
  return {
    eyebrow: asText(value.eyebrow, FALLBACK_HERO.eyebrow),
    title: asText(value.title, FALLBACK_HERO.title),
    subtitle: asText(value.subtitle, FALLBACK_HERO.subtitle),
    note: asText(value.note, FALLBACK_HERO.note),
  }
}

function normalizeItems(raw) {
  const rows = Array.isArray(raw) ? raw : []
  const normalized = rows
    .map((item) => ({
      itemCode: asText(item?.item_code || item?.itemCode),
      title: asText(item?.title),
      model: asText(item?.model),
      image: asText(item?.image, '/assets/mysite/img/placeholder.png'),
      priceToman: asNumber(item?.price_toman ?? item?.priceToman),
      editionCount: Math.max(1, asNumber(item?.edition_count ?? item?.editionCount, 1)),
      detailRoute: asText(item?.detail_route ?? item?.detailRoute, '/special-edition'),
      productRoute: asText(item?.product_route ?? item?.productRoute, '/categories'),
      isFake: Number(item?.is_fake ?? item?.isFake) ? 1 : 0,
    }))
    .filter((item) => item.itemCode && item.title && item.priceToman > 0)

  return normalized.length ? normalized : FALLBACK_ITEMS
}

function buildStats(rows, rawStats) {
  const totalUnits = rows.reduce((acc, row) => acc + asNumber(row.editionCount), 0)
  const prices = rows.map((row) => asNumber(row.priceToman)).filter((value) => value > 0)
  const minPrice = prices.length ? Math.min(...prices) : 0
  const maxPrice = prices.length ? Math.max(...prices) : 0

  const stats = rawStats && typeof rawStats === 'object' ? rawStats : {}
  return {
    itemsCount: asNumber(stats.items_count ?? stats.itemsCount, rows.length),
    totalUnits: asNumber(stats.total_units ?? stats.totalUnits, totalUnits),
    minPrice: asNumber(stats.price_range?.min ?? stats.minPrice, minPrice),
    maxPrice: asNumber(stats.price_range?.max ?? stats.maxPrice, maxPrice),
  }
}

function toPersianDigits(value) {
  return String(value).replace(/\d/g, (digit) => '۰۱۲۳۴۵۶۷۸۹'[Number(digit)])
}

function formatPrice(value) {
  const amount = Math.max(0, asNumber(value))
  if (!amount) return 'تماس برای قیمت'
  return `${toPersianDigits(amount.toLocaleString('en-US'))} تومان`
}

function formatPriceRange(minPrice, maxPrice) {
  const min = Math.max(0, asNumber(minPrice))
  const max = Math.max(0, asNumber(maxPrice))
  if (!min && !max) return 'تماس برای قیمت'
  if (min && max && min !== max) {
    return `${toPersianDigits(min.toLocaleString('en-US'))} - ${toPersianDigits(max.toLocaleString('en-US'))}`
  }
  return toPersianDigits((max || min).toLocaleString('en-US'))
}

const hero = normalizeHero(window.SpecialEditionHero)
const items = normalizeItems(window.SpecialEditionItems)
const stats = buildStats(items, window.SpecialEditionStats)

let revealObserver = null

function setupReveal() {
  const nodes = Array.from(document.querySelectorAll('.special-page [data-reveal]'))
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
    { threshold: 0.16, rootMargin: '0px 0px -8% 0px' }
  )

  nodes.forEach((node) => {
    const localDelay = node.style.getPropertyValue('--card-delay')
    if (localDelay) node.style.setProperty('--reveal-delay', localDelay)
    revealObserver.observe(node)
  })
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
.special-page {
  --sp-bg: #060304;
  --sp-bg-soft: #140506;
  --sp-text: #f6eeee;
  --sp-muted: rgba(224, 206, 206, 0.72);
  --sp-gold: #7c171f;
  --sp-gold-strong: #b41f2a;
  --sp-border: rgba(124, 23, 31, 0.38);
  --sp-border-soft: rgba(124, 23, 31, 0.25);
  --sp-surface: rgba(25, 8, 10, 0.78);
  --sp-surface-soft: rgba(38, 11, 14, 0.7);
  --sp-shadow: 0 24px 58px rgba(0, 0, 0, 0.35);
  min-height: 100vh;
  color: var(--sp-text);
  background: radial-gradient(circle at 18% 10%, #2b070a 0%, var(--sp-bg) 52%, #030202 100%);
  font-family: 'Peyda', sans-serif;
  overflow: hidden;
}

[data-theme='light'] .special-page {
  --sp-bg: #f7f3f2;
  --sp-bg-soft: #ede5e4;
  --sp-text: #2f1819;
  --sp-muted: rgba(80, 52, 53, 0.72);
  --sp-gold: #7c171f;
  --sp-gold-strong: #5f0f14;
  --sp-border: rgba(124, 23, 31, 0.3);
  --sp-border-soft: rgba(124, 23, 31, 0.2);
  --sp-surface: rgba(255, 255, 255, 0.82);
  --sp-surface-soft: rgba(241, 235, 234, 0.82);
  --sp-shadow: 0 24px 58px rgba(86, 25, 30, 0.2);
  background: radial-gradient(circle at 18% 10%, #ffffff 0%, #f2eceb 56%, #ebe2e1 100%);
}

.special-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px 112px;
  position: relative;
}

.special-bg {
  position: absolute;
  inset: 34px 0 0;
  pointer-events: none;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(72px);
  animation: drift 12s ease-in-out infinite alternate;
}

.glow-a {
  width: 340px;
  height: 340px;
  top: 40px;
  right: -50px;
  background: radial-gradient(circle, rgba(142, 23, 32, 0.34) 0%, rgba(142, 23, 32, 0) 72%);
}

.glow-b {
  width: 460px;
  height: 460px;
  left: -140px;
  top: 360px;
  background: radial-gradient(circle, rgba(96, 14, 22, 0.3) 0%, rgba(96, 14, 22, 0) 72%);
  animation-delay: 1.6s;
}

.glow-c {
  width: 260px;
  height: 260px;
  left: 44%;
  bottom: 80px;
  background: radial-gradient(circle, rgba(180, 43, 56, 0.22) 0%, rgba(180, 43, 56, 0) 72%);
  animation-delay: 2.8s;
}

.liquid {
  background: linear-gradient(145deg, var(--sp-surface) 0%, var(--sp-surface-soft) 100%);
  border: 1px solid var(--sp-border);
  box-shadow: var(--sp-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(16px) saturate(145%);
  -webkit-backdrop-filter: blur(16px) saturate(145%);
  position: relative;
  overflow: hidden;
}

.liquid::before {
  content: "";
  position: absolute;
  inset: -70% auto auto -30%;
  width: 140%;
  height: 200px;
  background: linear-gradient(110deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
  transform: rotate(-9deg);
  animation: shine 8.2s linear infinite;
  pointer-events: none;
}

[data-reveal] {
  opacity: 0;
  transform: translateY(24px) scale(0.985);
  transition: opacity 0.62s ease, transform 0.62s ease;
  transition-delay: var(--reveal-delay, 0ms);
}

[data-reveal].visible {
  opacity: 1;
  transform: none;
}

.hero {
  margin-top: 104px;
  border-radius: 36px;
  padding: 46px 42px 36px;
  z-index: 2;
}

.hero-eyebrow {
  margin: 0;
  font-size: 0.82rem;
  letter-spacing: 0.14em;
  color: var(--sp-gold);
  font-weight: 770;
}

.hero h1 {
  margin: 14px 0 0;
  font-size: clamp(2.4rem, 5.4vw, 4.9rem);
  line-height: 1.02;
  color: var(--sp-gold-strong);
  font-weight: 960;
  text-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
}

.hero-subtitle {
  margin: 14px 0 0;
  max-width: 820px;
  font-size: clamp(1rem, 2vw, 1.22rem);
  line-height: 1.9;
  color: var(--sp-text);
  font-weight: 620;
}

.hero-note {
  margin: 10px 0 0;
  max-width: 840px;
  color: var(--sp-muted);
  line-height: 1.9;
  font-size: 0.97rem;
}

.hero-stats {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.stat-pill {
  border: 1px solid var(--sp-border-soft);
  border-radius: 16px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-pill span {
  color: var(--sp-muted);
  font-size: 0.8rem;
}

.stat-pill strong {
  color: var(--sp-gold-strong);
  font-size: 1.02rem;
}

.cards-grid {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  position: relative;
  z-index: 1;
}

.product-card {
  border-radius: 24px;
  border-color: var(--sp-border-soft);
}

.image-wrap {
  display: block;
  position: relative;
  height: 280px;
  border-bottom: 1px solid var(--sp-border-soft);
  background: radial-gradient(circle at 50% 22%, rgba(255, 255, 255, 0.15), transparent 64%);
}

.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 18px;
  transition: transform 0.45s ease;
}

.product-card:hover .image-wrap img {
  transform: scale(1.045) translateY(-4px);
}

.edition-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  border-radius: 999px;
  padding: 5px 10px;
  background: rgba(24, 8, 12, 0.72);
  border: 1px solid var(--sp-border);
  color: var(--sp-gold-strong);
  font-size: 0.73rem;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.card-body {
  padding: 14px 14px 16px;
}

.meta-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.serial {
  font-size: 0.75rem;
  color: var(--sp-gold);
  font-weight: 760;
}

.fake-pill {
  font-size: 0.68rem;
  color: var(--sp-muted);
  border: 1px solid var(--sp-border-soft);
  border-radius: 999px;
  padding: 3px 8px;
}

.card-body h2 {
  margin: 0;
  color: var(--sp-text);
  font-size: 1.26rem;
  line-height: 1.35;
  font-weight: 880;
}

.model {
  margin: 6px 0 0;
  color: var(--sp-muted);
  font-size: 0.91rem;
}

.card-footer {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.price {
  color: var(--sp-gold-strong);
  font-size: 1.06rem;
  font-weight: 860;
}

.open-link {
  text-decoration: none;
  color: var(--sp-text);
  border: 1px solid var(--sp-border);
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 0.8rem;
  font-weight: 740;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.open-link:hover {
  transform: translateY(-1px);
  border-color: var(--sp-gold);
}

@keyframes drift {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(20px, -22px) scale(1.07); }
}

@keyframes shine {
  0% { transform: translateX(-140%) rotate(-9deg); }
  100% { transform: translateX(140%) rotate(-9deg); }
}

@media (max-width: 1180px) {
  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 920px) {
  .special-shell {
    padding: 0 14px 86px;
  }

  .hero {
    margin-top: 86px;
    border-radius: 26px;
    padding: 30px 18px 24px;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .image-wrap {
    height: 244px;
  }
}

@media (max-width: 680px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .hero h1 {
    font-size: clamp(2rem, 12vw, 2.9rem);
  }

  .image-wrap {
    height: 232px;
  }

  .card-body h2 {
    font-size: 1.16rem;
  }

  .price {
    font-size: 0.95rem;
  }
}
</style>
