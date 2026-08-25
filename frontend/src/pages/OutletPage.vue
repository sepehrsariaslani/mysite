<template>
  <div class="outlet-page" dir="rtl">
    <CategoryBar />

    <section class="outlet-shell">
      <div class="outlet-bg" aria-hidden="true">
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
            <span>مدل Outlet</span>
            <strong>{{ toPersianDigits(String(stats.itemsCount)) }}</strong>
          </article>
          <article class="stat-pill">
            <span>موجودی کل</span>
            <strong>{{ toPersianDigits(String(stats.totalStock)) }}</strong>
          </article>
          <article class="stat-pill">
            <span>بیشترین تخفیف</span>
            <strong>{{ toPersianDigits(String(stats.bestDiscount)) }}٪</strong>
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
            <span class="discount-badge">OFF {{ toPersianDigits(String(item.discountPercent)) }}%</span>
          </a>

          <div class="card-body">
            <div class="meta-top">
              <span class="serial">#{{ toPersianDigits(String(index + 1)) }}</span>
              <span v-if="item.isFake" class="fake-pill">نمونه نمایشی</span>
            </div>

            <h2>{{ item.title }}</h2>
            <p class="model">{{ item.model }}</p>
            <p class="stock">موجودی: {{ toPersianDigits(String(item.stockCount)) }} عدد</p>

            <div class="card-footer">
              <div class="price-stack">
                <span class="old-price">{{ formatPrice(item.priceToman) }}</span>
                <strong class="price">{{ formatPrice(item.outletPriceToman) }}</strong>
              </div>
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
  eyebrow: 'DENROOM OUTLET SELECTION',
  title: 'Outlet',
  subtitle: 'محصولات منتخب دن‌روم با قیمت ویژه',
  note: 'محصولات Outlet تا زمان تکمیل موجودی قابل سفارش هستند و با قیمت نهایی ویژه عرضه می‌شوند.',
}

const FALLBACK_ITEMS = [
  {
    itemCode: 'OUT-SAMPLE-01',
    title: 'روژان کلاسیک',
    model: 'مبلمان Outlet',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 142000000,
    outletPriceToman: 108000000,
    discountPercent: 24,
    stockCount: 3,
    detailRoute: '/mysite/outlet/OUT-SAMPLE-01',
    productRoute: '/mysite/sofas',
    isFake: 1,
  },
  {
    itemCode: 'OUT-SAMPLE-02',
    title: 'ماهور مینیمال',
    model: 'صندلی ناهارخوری Outlet',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 36000000,
    outletPriceToman: 26200000,
    discountPercent: 27,
    stockCount: 6,
    detailRoute: '/mysite/outlet/OUT-SAMPLE-02',
    productRoute: '/mysite/dining-chairs',
    isFake: 1,
  },
  {
    itemCode: 'OUT-SAMPLE-03',
    title: 'آوا ۶ نفره',
    model: 'میز ناهارخوری Outlet',
    image: '/assets/mysite/img/placeholder.png',
    priceToman: 88000000,
    outletPriceToman: 64200000,
    discountPercent: 27,
    stockCount: 2,
    detailRoute: '/mysite/outlet/OUT-SAMPLE-03',
    productRoute: '/mysite/tables',
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
      outletPriceToman: asNumber(item?.outlet_price_toman ?? item?.outletPriceToman),
      discountPercent: Math.max(1, asNumber(item?.discount_percent ?? item?.discountPercent, 1)),
      stockCount: Math.max(1, asNumber(item?.stock_count ?? item?.stockCount, 1)),
      detailRoute: asText(item?.detail_route ?? item?.detailRoute, '/mysite/outlet'),
      productRoute: asText(item?.product_route ?? item?.productRoute, '/mysite/categories'),
      isFake: Number(item?.is_fake ?? item?.isFake) ? 1 : 0,
    }))
    .filter((item) => item.itemCode && item.title && item.outletPriceToman > 0)

  return normalized.length ? normalized : FALLBACK_ITEMS
}

function buildStats(rows, rawStats) {
  const totalStock = rows.reduce((acc, row) => acc + asNumber(row.stockCount), 0)
  const bestDiscount = rows.reduce((acc, row) => Math.max(acc, asNumber(row.discountPercent)), 0)

  const stats = rawStats && typeof rawStats === 'object' ? rawStats : {}
  return {
    itemsCount: asNumber(stats.items_count ?? stats.itemsCount, rows.length),
    totalStock: asNumber(stats.total_stock ?? stats.totalStock, totalStock),
    bestDiscount: asNumber(stats.best_discount ?? stats.bestDiscount, bestDiscount),
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

const hero = normalizeHero(window.OutletHero)
const items = normalizeItems(window.OutletItems)
const stats = buildStats(items, window.OutletStats)

let revealObserver = null

function setupReveal() {
  const nodes = Array.from(document.querySelectorAll('.outlet-page [data-reveal]'))
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
.outlet-page {
  --ot-bg: #120f0c;
  --ot-bg-soft: #1e1812;
  --ot-text: #f5eee3;
  --ot-muted: rgba(226, 212, 195, 0.76);
  --ot-accent: #c8a16e;
  --ot-accent-strong: #edd0a5;
  --ot-border: rgba(200, 161, 110, 0.34);
  --ot-border-soft: rgba(200, 161, 110, 0.24);
  --ot-surface: rgba(39, 30, 20, 0.78);
  --ot-surface-soft: rgba(55, 42, 28, 0.68);
  --ot-shadow: 0 24px 58px rgba(0, 0, 0, 0.35);
  min-height: 100vh;
  color: var(--ot-text);
  background: radial-gradient(circle at 18% 10%, #3f3122 0%, var(--ot-bg) 52%, #0f0c09 100%);
  font-family: 'Peyda', sans-serif;
  overflow: hidden;
}

[data-theme='light'] .outlet-page {
  --ot-bg: #f8f1e4;
  --ot-bg-soft: #f2e6d2;
  --ot-text: #3b2f1f;
  --ot-muted: rgba(96, 78, 56, 0.72);
  --ot-accent: #b48953;
  --ot-accent-strong: #8e6635;
  --ot-border: rgba(180, 137, 83, 0.3);
  --ot-border-soft: rgba(180, 137, 83, 0.2);
  --ot-surface: rgba(255, 255, 255, 0.84);
  --ot-surface-soft: rgba(245, 235, 220, 0.85);
  --ot-shadow: 0 24px 58px rgba(107, 80, 44, 0.2);
  background: radial-gradient(circle at 18% 10%, #fffdf7 0%, #f7efe2 56%, #f1e4d1 100%);
}

.outlet-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px 112px;
  position: relative;
}

.outlet-bg {
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
  background: radial-gradient(circle, rgba(214, 178, 128, 0.33) 0%, rgba(214, 178, 128, 0) 72%);
}

.glow-b {
  width: 460px;
  height: 460px;
  left: -140px;
  top: 360px;
  background: radial-gradient(circle, rgba(177, 133, 79, 0.28) 0%, rgba(177, 133, 79, 0) 72%);
  animation-delay: 1.6s;
}

.glow-c {
  width: 260px;
  height: 260px;
  left: 44%;
  bottom: 80px;
  background: radial-gradient(circle, rgba(241, 222, 190, 0.22) 0%, rgba(241, 222, 190, 0) 72%);
  animation-delay: 2.8s;
}

.liquid {
  background: linear-gradient(145deg, var(--ot-surface) 0%, var(--ot-surface-soft) 100%);
  border: 1px solid var(--ot-border);
  box-shadow: var(--ot-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(16px) saturate(145%);
  -webkit-backdrop-filter: blur(16px) saturate(145%);
  position: relative;
  overflow: hidden;
}

.liquid::before {
  content: '';
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
  color: var(--ot-accent);
  font-weight: 770;
}

.hero h1 {
  margin: 14px 0 0;
  font-size: clamp(2.4rem, 5.4vw, 4.9rem);
  line-height: 1.02;
  color: var(--ot-accent-strong);
  font-weight: 960;
  text-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
}

.hero-subtitle {
  margin: 14px 0 0;
  max-width: 820px;
  font-size: clamp(1rem, 2vw, 1.22rem);
  line-height: 1.9;
  color: var(--ot-text);
  font-weight: 620;
}

.hero-note {
  margin: 10px 0 0;
  max-width: 840px;
  color: var(--ot-muted);
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
  border: 1px solid var(--ot-border-soft);
  border-radius: 16px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-pill span {
  color: var(--ot-muted);
  font-size: 0.8rem;
}

.stat-pill strong {
  color: var(--ot-accent-strong);
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
  border-color: var(--ot-border-soft);
}

.image-wrap {
  display: block;
  position: relative;
  height: 280px;
  border-bottom: 1px solid var(--ot-border-soft);
  background: radial-gradient(circle at 50% 22%, rgba(255, 255, 255, 0.14), transparent 64%);
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

.discount-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  border-radius: 999px;
  padding: 5px 10px;
  background: rgba(28, 19, 11, 0.78);
  border: 1px solid var(--ot-border);
  color: var(--ot-accent-strong);
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
  color: var(--ot-accent);
  font-weight: 760;
}

.fake-pill {
  font-size: 0.68rem;
  color: var(--ot-muted);
  border: 1px solid var(--ot-border-soft);
  border-radius: 999px;
  padding: 3px 8px;
}

.card-body h2 {
  margin: 0;
  color: var(--ot-text);
  font-size: 1.26rem;
  line-height: 1.35;
  font-weight: 880;
}

.model {
  margin: 6px 0 0;
  color: var(--ot-muted);
  font-size: 0.91rem;
}

.stock {
  margin: 6px 0 0;
  color: var(--ot-accent);
  font-size: 0.8rem;
  font-weight: 700;
}

.card-footer {
  margin-top: 12px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
}

.price-stack {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.old-price {
  color: var(--ot-muted);
  font-size: 0.78rem;
  text-decoration: line-through;
}

.price {
  color: var(--ot-accent-strong);
  font-size: 1.06rem;
  font-weight: 860;
}

.open-link {
  text-decoration: none;
  color: var(--ot-text);
  border: 1px solid var(--ot-border);
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 0.8rem;
  font-weight: 740;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.open-link:hover {
  transform: translateY(-1px);
  border-color: var(--ot-accent);
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
  .outlet-shell {
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
