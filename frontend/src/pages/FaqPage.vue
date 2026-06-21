<template>
  <div class="faq-page" dir="rtl">
    <section class="faq-hero">
      <div>
        <p class="eyebrow">FAQ</p>
        <h1>سوالات متداول</h1>
        <p class="sub">
          پاسخ سریع برای سوال‌های پرتکرار درباره محصولات، پارچه، سفارش و ارسال.
        </p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span>{{ filteredFaqs.length.toLocaleString('fa-IR') }}</span>
          <p>پاسخ قابل نمایش</p>
        </div>
        <div class="stat-box">
          <span>{{ categoryCount.toLocaleString('fa-IR') }}</span>
          <p>دسته‌بندی</p>
        </div>
      </div>
    </section>

    <section class="faq-toolbar">
      <label class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.3-4.3"></path>
        </svg>
        <input v-model.trim="searchQuery" type="search" placeholder="جستجو در سوالات..." />
      </label>

      <div class="chips">
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="chip"
          :class="{ active: activeCategory === cat.id }"
          @click="activeCategory = cat.id"
        >
          {{ cat.label }}
        </button>
      </div>
    </section>

    <section v-if="filteredFaqs.length" class="faq-list">
      <article
        v-for="item in filteredFaqs"
        :key="item.id"
        class="faq-item"
        :class="{ open: isOpen(item.id) }"
      >
        <button class="faq-question" @click="toggleItem(item.id)">
          <div>
            <p class="faq-category">{{ item.category }}</p>
            <h2>{{ item.question }}</h2>
          </div>
          <span class="icon" :class="{ open: isOpen(item.id) }">+</span>
        </button>

        <div class="faq-answer-wrap" :class="{ open: isOpen(item.id) }">
          <div class="faq-answer" v-html="item.answer"></div>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <p>سوالی با این فیلتر یا عبارت جستجو پیدا نشد.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const faqItems = ref(window.FAQItems || [])
const bootCategories = ref(window.FAQCategories || [])
const searchQuery = ref('')
const activeCategory = ref('all')
const openItemIds = ref({})

const categories = computed(() => {
  if (Array.isArray(bootCategories.value) && bootCategories.value.length) {
    return bootCategories.value
  }
  const found = new Set()
  const output = [{ id: 'all', label: 'همه' }]
  for (const item of faqItems.value) {
    const label = normalizeText(item?.category || 'عمومی')
    if (!label || found.has(label)) continue
    found.add(label)
    output.push({ id: categoryId(item), label })
  }
  return output
})

const categoryCount = computed(() => categories.value.filter((cat) => cat.id !== 'all').length)

const filteredFaqs = computed(() => {
  const query = normalizeText(searchQuery.value)
  return faqItems.value.filter((item) => {
    const categoryOk = activeCategory.value === 'all' || categoryId(item) === activeCategory.value
    if (!categoryOk) return false
    if (!query) return true
    const plainAnswer = stripHtml(item?.answer || '')
    const searchable = normalizeText(`${item?.question || ''} ${plainAnswer} ${item?.category || ''}`)
    return searchable.includes(query)
  })
})

watch(
  filteredFaqs,
  (items) => {
    if (!items.length) {
      openItemIds.value = {}
      return
    }
    if (items.some((item) => isOpen(item.id))) return
    openItemIds.value = { [items[0].id]: true }
  },
  { immediate: true },
)

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\u064a/g, 'ی')
    .replace(/\u0643/g, 'ک')
    .replace(/\s+/g, ' ')
    .trim()
}

function stripHtml(value) {
  return String(value || '').replace(/<[^>]*>/g, ' ')
}

function categoryId(item) {
  const direct = normalizeText(item?.category_id || '')
  if (direct) return direct
  return normalizeText(item?.category || 'عمومی')
    .replace(/[^a-z0-9_\u0600-\u06ff]+/g, '_')
    .replace(/^_+|_+$/g, '') || 'general'
}

function isOpen(itemId) {
  return !!openItemIds.value[itemId]
}

function toggleItem(itemId) {
  if (isOpen(itemId)) {
    openItemIds.value = {
      ...openItemIds.value,
      [itemId]: false,
    }
    return
  }
  openItemIds.value = {
    ...openItemIds.value,
    [itemId]: true,
  }
}
</script>

<style scoped>
.faq-page {
  min-height: 100vh;
  padding: 44px 24px 100px;
  background:
    radial-gradient(circle at 12% 8%, rgba(255, 201, 132, 0.2), transparent 32%),
    radial-gradient(circle at 90% 18%, rgba(149, 92, 51, 0.26), transparent 35%),
    var(--bg-main);
}

.faq-hero {
  max-width: 1320px;
  margin: 0 auto 18px;
  padding: 24px;
  border-radius: 28px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 18px;
  flex-wrap: wrap;
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
  max-width: 680px;
  font-size: 15px;
  line-height: 1.9;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(130px, 1fr));
  gap: 10px;
}

.stat-box {
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 12px 14px;
  text-align: center;
}

.stat-box span {
  display: block;
  font-size: 22px;
  font-weight: 900;
}

.stat-box p {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.faq-toolbar {
  max-width: 1320px;
  margin: 0 auto 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  width: min(430px, 100%);
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: var(--glass-bg);
  padding: 10px 14px;
}

.search-box svg {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-main);
  font-size: 14px;
  font-family: inherit;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  color: #3b281e;
}

.faq-list {
  max-width: 1320px;
  margin: 0 auto;
  display: grid;
  gap: 10px;
}

.faq-item {
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  background: var(--glass-bg);
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.faq-item.open {
  border-color: var(--accent-gold);
}

.faq-question {
  width: 100%;
  border: none;
  background: transparent;
  color: inherit;
  text-align: right;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
}

.faq-category {
  margin: 0 0 3px;
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 800;
}

.faq-question h2 {
  margin: 0;
  font-size: 17px;
  line-height: 1.7;
  font-weight: 900;
}

.icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  display: grid;
  place-items: center;
  font-size: 24px;
  line-height: 1;
  color: var(--accent-gold);
  transition: transform 0.2s ease;
}

.icon.open {
  transform: rotate(45deg);
}

.faq-answer-wrap {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.2s ease;
}

.faq-answer-wrap.open {
  grid-template-rows: 1fr;
}

.faq-answer {
  min-height: 0;
  overflow: hidden;
  color: var(--text-muted);
  padding: 0 16px 16px;
  line-height: 2;
  font-size: 14px;
}

.faq-answer :deep(p) {
  margin: 0 0 10px;
}

.faq-answer :deep(ul),
.faq-answer :deep(ol) {
  margin: 0;
  padding-right: 18px;
}

.empty-state {
  max-width: 1320px;
  margin: 0 auto;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 22px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .faq-page {
    padding: 26px 14px 90px;
  }

  .faq-hero {
    padding: 16px;
    border-radius: 20px;
  }

  .hero-stats {
    width: 100%;
  }

  .faq-question h2 {
    font-size: 15px;
  }
}
</style>
