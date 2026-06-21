<template>
  <section class="best-preview" dir="rtl" v-if="cards.length">
    <div class="best-head">
      <div>
        <p class="best-eyebrow">Best Sellers</p>
        <h2>پرفروش‌ترین محصولات</h2>
      </div>
      <a :href="allProductsRoute" class="best-view-all">مشاهده همه</a>
    </div>

    <div class="best-body">
      <aside class="kind-rail">
        <button
          v-for="option in kindOptions"
          :key="option.id"
          type="button"
          class="kind-pill"
          :class="{ active: activeKind === option.id }"
          @click="activeKind = option.id"
        >
          {{ option.label }}
        </button>
      </aside>

      <div class="cards-track-wrap">
        <div class="cards-track">
          <article
            v-for="(product, index) in visibleCards"
            :key="product.id || `${product.item_code}-${index}`"
            class="product-card"
            :style="{ '--card-bg': palette[index % palette.length] }"
          >
            <a :href="productRoute(product)" class="card-link">
              <div class="card-glass"></div>
              <div class="card-top">
                <p class="title">{{ product.title }}</p>
              </div>

              <div class="img-wrap">
                <img :src="product.image" :alt="product.title" loading="lazy" />
              </div>

              <div class="card-foot">
                <strong>{{ formatPrice(product.base_price) }}</strong>
              </div>
            </a>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  products: { type: Array, default: () => [] },
  selectedCustomer: { type: String, default: '' },
})

const palette = [
  'linear-gradient(165deg, #ffffff 0%, #f5f4f1 100%)',
  'linear-gradient(165deg, #ffffff 0%, #f3f2ef 100%)',
  'linear-gradient(165deg, #ffffff 0%, #f7f6f3 100%)',
  'linear-gradient(165deg, #ffffff 0%, #f2f1ee 100%)',
]

const kindNameMap = {
  all: 'همه',
  sofa: 'مبل',
  barstool: 'صندلی اپن',
  chair: 'صندلی ناهارخوری',
  dining_table: 'میز ناهارخوری',
  coffee_table: 'میز جلومبلی',
  bench: 'نیمکت',
  table: 'میز',
}
const preferredKindOrder = [
  'all',
  'sofa',
  'barstool',
  'chair',
  'dining_table',
  'bench',
  'coffee_table',
  'table',
]

const localCustomer = ref(
  props.selectedCustomer
    || window.SelectedCustomer
    || (() => {
      try {
        return localStorage.getItem('mysite_selected_customer') || ''
      } catch (error) {
        return ''
      }
    })()
)

const activeKind = ref('all')

const cards = computed(() =>
  (props.products || [])
    .filter((item) => item && item.route)
    .map((item) => {
      const price = Number(item.base_price || 0)
      const sold = Number(item.sold_qty || 0)
      return {
        ...item,
        base_price: Number.isFinite(price) ? price : 0,
        sold_qty: Number.isFinite(sold) ? sold : 0,
        kind: String(item.kind || '').trim().toLowerCase(),
      }
    })
)

const kindOptions = computed(() => {
  const seen = new Set(cards.value.map((item) => String(item.kind || '').trim()).filter(Boolean))
  const options = []

  for (const key of preferredKindOrder) {
    if (key !== 'all' && !seen.has(key)) continue
    options.push({ id: key, label: kindNameMap[key] || key })
    seen.delete(key)
  }

  for (const key of seen) {
    options.push({ id: key, label: kindNameMap[key] || key })
  }

  return options
})

watch(kindOptions, (options) => {
  const allowed = new Set(options.map((option) => option.id))
  if (!allowed.has(activeKind.value)) activeKind.value = 'all'
}, { immediate: true })

const visibleCards = computed(() => {
  const selected = cards.value.filter((item) => (
    activeKind.value === 'all' || item.kind === activeKind.value
  ))
  return [...selected]
    .sort((a, b) => (b.sold_qty || 0) - (a.sold_qty || 0))
    .slice(0, 12)
})

const allProductsRoute = computed(() => {
  const base = '/categories'
  if (!localCustomer.value) return base
  return `${base}?customer=${encodeURIComponent(localCustomer.value)}`
})

function formatPrice(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function productRoute(product) {
  const route = String(product?.route || '').trim()
  if (!route) return '#'
  if (!localCustomer.value || route.includes('customer=')) return route
  const joiner = route.includes('?') ? '&' : '?'
  return `${route}${joiner}customer=${encodeURIComponent(localCustomer.value)}`
}
</script>

<style scoped>
.best-preview {
  max-width: 1320px;
  margin: 72px auto 0;
  padding: 0 24px;
  position: relative;
  z-index: 1;
}

.best-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.best-eyebrow {
  margin: 0 0 8px;
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.best-head h2 {
  margin: 0;
  font-size: clamp(25px, 3vw, 36px);
  font-weight: 930;
}

.best-view-all {
  text-decoration: none;
  color: #36251b;
  background: var(--accent-gold);
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 830;
}

.best-body {
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.kind-rail {
  align-self: start;
  max-height: 348px;
  overflow-y: auto;
  border-radius: 24px;
  border: 1px solid var(--glass-border);
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  padding: 10px 8px;
}

.kind-pill {
  border: 0;
  background: transparent;
  color: var(--text-dim);
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  border-radius: 14px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 800;
  padding: 8px 0;
  min-height: 62px;
  cursor: pointer;
}

.kind-pill.active {
  color: var(--text-main);
  background: color-mix(in srgb, var(--glass-bg) 60%, #fff 40%);
  box-shadow: inset 0 0 0 1px var(--glass-border-bright);
}

.cards-track-wrap {
  border-radius: 30px;
  border: 1px solid var(--glass-border);
  background: #fff;
  backdrop-filter: blur(11px) saturate(135%);
  -webkit-backdrop-filter: blur(11px) saturate(135%);
  padding: 10px;
  overflow-x: auto;
  overflow-y: hidden;
}

.cards-track {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(208px, 232px);
  gap: 10px;
}

.product-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #ece7df;
  background: var(--card-bg);
  min-height: 352px;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.5),
    0 12px 24px rgba(43, 30, 20, 0.1);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.35),
    0 20px 38px rgba(0, 0, 0, 0.2);
}

.card-link {
  position: relative;
  z-index: 1;
  color: #2e1f16;
  text-decoration: none;
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 352px;
  height: 100%;
}

.card-glass {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 72% 24%, rgba(255, 255, 255, 0.25), transparent 42%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.13), transparent 44%);
  pointer-events: none;
}

.card-top {
  padding: 12px 12px 0;
}

.title {
  margin: 0;
  font-size: 34px;
  line-height: 1.15;
  font-weight: 880;
  color: rgba(54, 38, 26, 0.9);
}

.img-wrap {
  display: flex;
  align-items: end;
  justify-content: center;
  padding: 0 10px 6px;
}

.img-wrap img {
  width: 100%;
  max-width: 198px;
  height: 208px;
  object-fit: contain;
  filter: drop-shadow(0 12px 12px rgba(72, 46, 27, 0.18));
}

.card-foot {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 8px 11px;
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.3);
}

.card-foot strong {
  font-size: 16px;
  font-weight: 900;
  color: #2b1d14;
}

@media (max-width: 920px) {
  .best-preview {
    padding: 0 12px;
    margin-top: 56px;
  }

  .best-body {
    grid-template-columns: 1fr;
  }

  .kind-rail {
    flex-direction: row;
    overflow: auto;
    padding: 8px;
  }

  .kind-pill {
    writing-mode: horizontal-tb;
    transform: none;
    min-height: 0;
    min-width: 82px;
    padding: 8px 10px;
    font-size: 12px;
  }

  .cards-track {
    grid-auto-columns: minmax(190px, 210px);
  }

  .title {
    font-size: 26px;
  }
}
</style>
