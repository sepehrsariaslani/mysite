<template>
  <div class="blog-page" dir="rtl">
    <div class="ambient-layer" aria-hidden="true">
      <div class="orb orb-a"></div>
      <div class="orb orb-b"></div>
      <div class="orb orb-c"></div>
    </div>

    <section v-if="view === 'list'" class="blog-list-view">
      <header class="journal-header reveal-in">
        <p class="journal-eyebrow">Denroom Journal</p>
        <h1>مجله طراحی و دکوراسیون دن‌روم</h1>
        <p>
          تحلیل روندها، راهنمای خرید و تجربه‌های واقعی چیدمان برای خانه و فضای کاری.
        </p>
      </header>

      <div class="toolbar reveal-in delay-1">
        <label class="search-field">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.3-4.3"></path>
          </svg>
          <input v-model.trim="searchQuery" type="search" placeholder="جستجو در مطالب..." />
        </label>

        <div class="category-chips">
          <button
            v-for="cat in categories"
            :key="cat.id"
            :class="{ active: activeCategory === cat.id }"
            @click="activeCategory = cat.id"
          >
            {{ cat.label }}
          </button>
        </div>
      </div>

      <div v-if="loadingList" class="loading-state reveal-in delay-2">
        <span class="loader-dot"></span>
        در حال بارگذاری مطالب...
      </div>

      <template v-else>
        <article
          v-if="featuredPost"
          class="featured-article reveal-in delay-2"
          @click="openPost(featuredPost)"
        >
          <div class="featured-media">
            <img :src="featuredPost.image" :alt="featuredPost.title" loading="lazy" />
          </div>
          <div class="featured-content">
            <span class="pill">{{ featuredPost.category }}</span>
            <h2>{{ featuredPost.title }}</h2>
            <p>{{ featuredPost.excerpt }}</p>
            <div class="meta-row">
              <span>{{ formatDate(featuredPost.published_on) }}</span>
              <span>{{ featuredPost.read_time }}</span>
            </div>
          </div>
        </article>

        <div class="article-grid reveal-in delay-3">
          <article
            v-for="post in regularPosts"
            :key="post.id"
            class="article-card"
            @click="openPost(post)"
          >
            <div class="card-media">
              <img :src="post.image" :alt="post.title" loading="lazy" />
              <span class="pill">{{ post.category }}</span>
            </div>
            <div class="card-body">
              <h3>{{ post.title }}</h3>
              <p>{{ post.excerpt }}</p>
              <div class="meta-row">
                <span>{{ formatDate(post.published_on) }}</span>
                <span>{{ post.read_time }}</span>
              </div>
            </div>
          </article>
        </div>

        <div v-if="!featuredPost && !regularPosts.length" class="empty-state reveal-in">
          <p>مطلبی با این فیلتر یا جستجو پیدا نشد.</p>
        </div>
      </template>
    </section>

    <section v-else-if="activePost" class="blog-detail-view">
      <div class="reading-progress">
        <span :style="{ width: `${readingProgress}%` }"></span>
      </div>

      <button class="back-btn" @click="closePost(true)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M15 18l-6-6 6-6"></path>
        </svg>
        بازگشت به لیست مطالب
      </button>

      <header class="detail-hero reveal-in">
        <div class="hero-media">
          <img :src="activePost.image" :alt="activePost.title" loading="lazy" />
          <span v-if="activePost.cover_credit" class="cover-credit">{{ activePost.cover_credit }}</span>
        </div>
        <div class="hero-content">
          <span class="pill">{{ activePost.category }}</span>
          <h1>{{ activePost.title }}</h1>
          <p v-if="activePost.subtitle" class="hero-subtitle">{{ activePost.subtitle }}</p>
          <p v-else class="hero-subtitle">{{ activePost.excerpt }}</p>
          <div class="meta-row">
            <span>{{ formatDate(activePost.published_on) }}</span>
            <span>{{ activePost.read_time }}</span>
          </div>
        </div>
      </header>

      <div class="detail-layout reveal-in delay-1">
        <aside class="detail-sidebar">
          <div v-if="tocItems.length" class="toc-box">
            <p>سرفصل‌های مقاله</p>
            <button
              v-for="item in tocItems"
              :key="item.id"
              :class="{ active: activeHeadingId === item.id, level3: item.level === 'h3' }"
              @click="scrollToHeading(item.id)"
            >
              {{ item.text }}
            </button>
          </div>

          <button class="share-btn" @click="copyCurrentLink">کپی لینک مقاله</button>
        </aside>

        <article class="article-shell">
          <div v-if="processedContent" ref="articleBodyRef" class="article-content" v-html="processedContent"></div>
          <div v-else class="article-empty">
            متن کامل این مقاله هنوز ثبت نشده است.
          </div>

          <div v-if="activePost.cta_link" class="article-cta">
            <p>اگر درباره این موضوع مشاوره می‌خواهید:</p>
            <a :href="activePost.cta_link">
              {{ activePost.cta_label || 'دریافت مشاوره' }}
            </a>
          </div>

          <section v-if="activePost.related_products?.length" class="mentioned-products">
            <h3>محصولات اشاره‌شده در این مقاله</h3>
            <div class="mentioned-grid">
              <a
                v-for="product in activePost.related_products"
                :key="`${activePost.id}-${product.id || product.item_code}`"
                :href="product.route"
                class="mentioned-card"
              >
                <img :src="product.image || '/assets/mysite/img/placeholder.png'" :alt="product.title" loading="lazy" />
                <div class="mentioned-body">
                  <strong>{{ product.title }}</strong>
                  <p v-if="product.note">{{ product.note }}</p>
                  <span>{{ formatPrice(product.base_price) }}</span>
                </div>
              </a>
            </div>
          </section>
        </article>
      </div>

      <section v-if="relatedPosts.length" class="related-section reveal-in delay-2">
        <h2>مطالب مرتبط</h2>
        <div class="related-grid">
          <article v-for="post in relatedPosts" :key="post.id" @click="openPost(post)">
            <img :src="post.image" :alt="post.title" loading="lazy" />
            <div>
              <span class="pill">{{ post.category }}</span>
              <h3>{{ post.title }}</h3>
            </div>
          </article>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const view = ref('list')
const loadingList = ref(true)
const loadingPost = ref(false)
const allPosts = ref([])
const activePost = ref(null)
const relatedPosts = ref([])

const searchQuery = ref('')
const activeCategory = ref('all')

const articleBodyRef = ref(null)
const processedContent = ref('')
const tocItems = ref([])
const activeHeadingId = ref('')
const readingProgress = ref(0)

const categories = computed(() => {
  const grouped = [{ id: 'all', label: 'همه' }]
  const seen = new Set()
  for (const post of allPosts.value) {
    const label = String(post.category || '').trim()
    if (!label || seen.has(label)) continue
    seen.add(label)
    grouped.push({ id: label, label })
  }
  return grouped
})

const filteredPosts = computed(() => {
  const q = normalize(searchQuery.value)
  return allPosts.value.filter((post) => {
    const categoryMatch = activeCategory.value === 'all' || post.category === activeCategory.value
    if (!categoryMatch) return false
    if (!q) return true
    const haystack = normalize(`${post.title} ${post.excerpt} ${post.category}`)
    return haystack.includes(q)
  })
})

const featuredPost = computed(() => {
  if (searchQuery.value || activeCategory.value !== 'all') return null
  return filteredPosts.value[0] || null
})

const regularPosts = computed(() => {
  if (!featuredPost.value) return filteredPosts.value
  return filteredPosts.value.filter((post) => post.id !== featuredPost.value.id)
})

function normalize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\u064a/g, 'ی')
    .replace(/\u0643/g, 'ک')
    .replace(/\s+/g, ' ')
    .trim()
}

function toPostObject(raw) {
  const name = String(raw?.name || raw?.id || '').trim()
  const image = String(raw?.image || raw?.meta_image || '/assets/mysite/img/placeholder.png').trim()
  const category = String(raw?.category || raw?.blog_category || 'مجله دن‌روم').trim() || 'مجله دن‌روم'
  const excerpt = String(raw?.excerpt || raw?.meta_description || '').trim()
  const readTime = String(raw?.read_time || raw?.custom_read_time || '۵ دقیقه').trim() || '۵ دقیقه'
  return {
    id: name,
    name,
    title: String(raw?.title || name || 'بدون عنوان').trim(),
    category,
    published_on: raw?.published_on || '',
    read_time: readTime,
    image,
    excerpt,
    subtitle: String(raw?.subtitle || '').trim(),
    cover_credit: String(raw?.cover_credit || '').trim(),
    cta_label: String(raw?.cta_label || '').trim(),
    cta_link: String(raw?.cta_link || '').trim(),
    content: String(raw?.content || '').trim(),
    related_products: Array.isArray(raw?.related_products) ? raw.related_products : [],
  }
}

function formatPrice(value) {
  const amount = Number(value || 0)
  if (!Number.isFinite(amount) || amount <= 0) return 'تماس بگیرید'
  return `${amount.toLocaleString('fa-IR')} تومان`
}

function formatDate(value) {
  if (!value) return ''
  const text = String(value)
  const parsed = new Date(text)
  if (Number.isNaN(parsed.getTime())) return text
  return parsed.toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' })
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

async function loadPosts() {
  loadingList.value = true
  try {
    const response = await fetch('/api/method/mysite.api.get_blog_posts?limit=120')
    const data = await response.json()
    const rows = Array.isArray(data?.message) ? data.message : []
    allPosts.value = rows.map(toPostObject).filter((post) => post.id)
  } catch (error) {
    allPosts.value = []
    console.error('Failed loading blog posts:', error)
  } finally {
    loadingList.value = false
  }
}

async function openPost(postOrId, pushHistory = true) {
  const identifier = typeof postOrId === 'string' ? postOrId : postOrId?.name
  if (!identifier || loadingPost.value) return

  loadingPost.value = true
  try {
    const response = await fetch(`/api/method/mysite.api.get_blog_post_detail?post=${encodeURIComponent(identifier)}`)
    const data = await response.json()
    const payload = data?.message || {}
    const post = payload?.post ? toPostObject(payload.post) : null
    if (!post) return

    activePost.value = post
    relatedPosts.value = Array.isArray(payload?.related_posts)
      ? payload.related_posts.map(toPostObject).filter((item) => item.id)
      : []
    view.value = 'detail'
    await buildArticleHtml(post.content)

    if (pushHistory) {
      const url = new URL(window.location.href)
      url.pathname = '/blog'
      url.searchParams.set('post', post.name)
      window.history.pushState({ post: post.name }, '', `${url.pathname}?${url.searchParams.toString()}`)
    }

    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Failed loading blog detail:', error)
  } finally {
    loadingPost.value = false
  }
}

function closePost(pushHistory = true) {
  view.value = 'list'
  activePost.value = null
  relatedPosts.value = []
  processedContent.value = ''
  tocItems.value = []
  activeHeadingId.value = ''
  readingProgress.value = 0

  if (pushHistory) {
    const url = new URL(window.location.href)
    url.pathname = '/blog'
    url.search = ''
    window.history.pushState({}, '', url.pathname)
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function buildArticleHtml(contentHtml) {
  let source = String(contentHtml || '').trim()
  if (source.includes('\\n') && !source.includes('\n')) {
    source = source.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n')
  }
  if (!source && activePost.value?.excerpt) {
    source = `<p>${escapeHtml(activePost.value.excerpt)}</p>`
  }

  const parser = new DOMParser()
  const doc = parser.parseFromString(`<div>${source}</div>`, 'text/html')

  doc.querySelectorAll('script, style, iframe, object, embed').forEach((el) => el.remove())

  const toc = []
  let headingIndex = 1
  doc.querySelectorAll('h2, h3').forEach((heading) => {
    const text = String(heading.textContent || '').trim()
    if (!text) return
    const id = `blog-heading-${headingIndex++}`
    heading.id = id
    toc.push({
      id,
      text,
      level: heading.tagName.toLowerCase(),
    })
  })

  tocItems.value = toc
  processedContent.value = doc.body.innerHTML

  await nextTick()
  updateScrollDrivenStates()
}

function scrollToHeading(id) {
  const element = document.getElementById(id)
  if (!element) return
  element.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function updateScrollDrivenStates() {
  if (view.value !== 'detail' || !articleBodyRef.value) return

  const articleEl = articleBodyRef.value
  const rect = articleEl.getBoundingClientRect()
  const articleTop = window.scrollY + rect.top
  const articleBottom = articleTop + articleEl.scrollHeight
  const viewportMid = window.scrollY + window.innerHeight * 0.4

  if (viewportMid <= articleTop) {
    readingProgress.value = 0
  } else if (viewportMid >= articleBottom) {
    readingProgress.value = 100
  } else {
    const ratio = ((viewportMid - articleTop) / Math.max(1, articleBottom - articleTop)) * 100
    readingProgress.value = Math.max(0, Math.min(100, Math.round(ratio)))
  }

  const headingElements = articleEl.querySelectorAll('h2[id], h3[id]')
  let activeId = tocItems.value[0]?.id || ''
  headingElements.forEach((heading) => {
    const hRect = heading.getBoundingClientRect()
    if (hRect.top <= 180) activeId = heading.id
  })
  activeHeadingId.value = activeId
}

function copyCurrentLink() {
  const link = window.location.href
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(link).catch(() => {})
    return
  }
  const input = document.createElement('input')
  input.value = link
  document.body.appendChild(input)
  input.select()
  document.execCommand('copy')
  document.body.removeChild(input)
}

function openPostFromLocation(pushHistory = false) {
  const url = new URL(window.location.href)
  const postId = url.searchParams.get('post')
  if (postId) {
    openPost(postId, pushHistory)
    return true
  }
  return false
}

function onPopState() {
  if (!openPostFromLocation(false)) {
    closePost(false)
  }
}

onMounted(async () => {
  await loadPosts()
  openPostFromLocation(false)
  window.addEventListener('scroll', updateScrollDrivenStates, { passive: true })
  window.addEventListener('popstate', onPopState)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateScrollDrivenStates)
  window.removeEventListener('popstate', onPopState)
})
</script>

<style scoped>
.blog-page {
  position: relative;
  min-height: 100vh;
  background:
    radial-gradient(80% 50% at 80% 0%, rgba(242, 201, 126, 0.13), transparent 70%),
    radial-gradient(60% 45% at 10% 20%, rgba(80, 49, 48, 0.35), transparent 72%),
    var(--bg-main);
  color: var(--text-main);
  overflow: hidden;
}

.ambient-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(80px);
  opacity: 0.35;
  animation: drift 12s ease-in-out infinite alternate;
}

.orb-a {
  width: 360px;
  height: 360px;
  top: -90px;
  right: -120px;
  background: rgba(242, 201, 126, 0.5);
}

.orb-b {
  width: 260px;
  height: 260px;
  bottom: 8%;
  left: -80px;
  background: rgba(255, 152, 0, 0.25);
  animation-delay: 1.8s;
}

.orb-c {
  width: 240px;
  height: 240px;
  top: 45%;
  right: 40%;
  background: rgba(255, 255, 255, 0.08);
  animation-delay: 0.7s;
}

.blog-list-view,
.blog-detail-view {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  padding: 48px 24px 96px;
}

.journal-header {
  max-width: 760px;
  margin: 0 auto 34px;
  text-align: center;
}

.journal-eyebrow {
  margin: 0 0 14px;
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.journal-header h1 {
  margin: 0;
  font-size: clamp(34px, 5.6vw, 64px);
  line-height: 1.08;
  font-weight: 960;
}

.journal-header p {
  margin: 14px 0 0;
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.9;
}

.toolbar {
  display: grid;
  gap: 14px;
  margin-bottom: 26px;
}

.search-field {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 18px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 14px 16px;
  backdrop-filter: blur(14px);
}

.search-field svg {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
}

.search-field input {
  flex: 1;
  border: 0;
  outline: 0;
  font-family: inherit;
  font-size: 1rem;
  color: var(--text-main);
  background: transparent;
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-chips button {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-muted);
  border-radius: 999px;
  padding: 10px 16px;
  font-size: 0.88rem;
  font-family: inherit;
  cursor: pointer;
}

.category-chips button.active {
  color: #2b1a13;
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  font-weight: 800;
}

.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-muted);
}

.loader-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent-gold);
  animation: pulse 0.9s ease-in-out infinite alternate;
}

.featured-article {
  display: grid;
  grid-template-columns: minmax(320px, 1.15fr) minmax(260px, 1fr);
  gap: 0;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: linear-gradient(120deg, rgba(80, 49, 48, 0.35), rgba(17, 17, 17, 0.8));
  backdrop-filter: blur(10px);
  cursor: pointer;
  margin-bottom: 24px;
}

.featured-media img {
  width: 100%;
  height: 100%;
  min-height: 310px;
  object-fit: cover;
}

.featured-content {
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.featured-content h2 {
  margin: 0;
  font-size: clamp(1.6rem, 2.4vw, 2.35rem);
  line-height: 1.35;
}

.featured-content p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.9;
}

.meta-row {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--text-dim);
  font-size: 0.88rem;
  font-weight: 600;
}

.pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border-radius: 999px;
  border: 1px solid rgba(242, 201, 126, 0.4);
  background: rgba(242, 201, 126, 0.12);
  color: var(--accent-gold);
  padding: 6px 12px;
  font-size: 0.78rem;
  font-weight: 800;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.article-card {
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
}

.card-media {
  position: relative;
}

.card-media img {
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.card-media .pill {
  position: absolute;
  top: 10px;
  right: 10px;
}

.card-body {
  padding: 16px;
}

.card-body h3 {
  margin: 0 0 8px;
  font-size: 1.2rem;
  line-height: 1.5;
}

.card-body p {
  margin: 0 0 12px;
  color: var(--text-muted);
  line-height: 1.75;
}

.empty-state {
  margin-top: 16px;
  border-radius: 16px;
  border: 1px dashed var(--glass-border-bright);
  color: var(--text-muted);
  text-align: center;
  padding: 22px;
}

.reading-progress {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 150;
  height: 3px;
  background: rgba(255, 255, 255, 0.08);
}

.reading-progress span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--accent-gold), #f3a742);
  transition: width 0.12s linear;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  border-radius: 999px;
  padding: 10px 14px;
  font-family: inherit;
  cursor: pointer;
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.detail-hero {
  border-radius: 26px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  margin-bottom: 18px;
}

.hero-media {
  position: relative;
}

.hero-media img {
  width: 100%;
  height: min(460px, 58vw);
  object-fit: cover;
}

.cover-credit {
  position: absolute;
  left: 14px;
  bottom: 14px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.72rem;
}

.hero-content {
  padding: 20px;
}

.hero-content h1 {
  margin: 12px 0 10px;
  font-size: clamp(1.9rem, 3.2vw, 3.1rem);
  line-height: 1.25;
}

.hero-subtitle {
  margin: 0 0 10px;
  color: var(--text-muted);
  line-height: 1.85;
}

.detail-layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.detail-sidebar {
  position: sticky;
  top: 80px;
  height: fit-content;
  display: grid;
  gap: 12px;
  min-width: 0;
}

.toc-box {
  border-radius: 18px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 14px;
  display: grid;
  gap: 8px;
}

.toc-box p {
  margin: 0 0 8px;
  color: var(--accent-gold);
  font-size: 0.88rem;
  font-weight: 800;
}

.toc-box button {
  text-align: right;
  border: 0;
  border-right: 2px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-family: inherit;
  cursor: pointer;
  padding: 0 8px 0 0;
  line-height: 1.65;
}

.toc-box button.level3 {
  padding-right: 12px;
  font-size: 0.9rem;
}

.toc-box button.active {
  color: var(--text-main);
  border-right-color: var(--accent-gold);
}

.share-btn {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 12px;
  font-family: inherit;
  cursor: pointer;
}

.article-shell {
  min-width: 0;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  padding: 24px;
}

.article-empty {
  border-radius: 14px;
  border: 1px dashed var(--glass-border);
  background: rgba(255, 255, 255, 0.42);
  padding: 16px;
  color: var(--text-muted);
  line-height: 1.9;
}

.article-content {
  color: var(--text-main);
  font-size: 1.06rem;
  line-height: 2.05;
  word-break: break-word;
}

.article-content :deep(h2),
.article-content :deep(h3) {
  margin-top: 34px;
  margin-bottom: 14px;
  line-height: 1.5;
  color: var(--accent-gold);
  scroll-margin-top: 120px;
}

.article-content :deep(h2) {
  font-size: 1.75rem;
}

.article-content :deep(h3) {
  font-size: 1.35rem;
}

.article-content :deep(p) {
  margin: 0 0 16px;
  color: var(--text-main);
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 0 0 18px;
  padding-right: 22px;
}

.article-content :deep(li) {
  margin-bottom: 8px;
}

.article-content :deep(img) {
  width: 100%;
  border-radius: 14px;
  margin: 18px 0;
  border: 1px solid var(--glass-border);
}

.article-content :deep(blockquote) {
  margin: 20px 0;
  border-right: 3px solid var(--accent-gold);
  background: rgba(242, 201, 126, 0.08);
  padding: 14px 16px;
  border-radius: 12px;
  color: var(--text-main);
}

.article-content :deep(pre) {
  margin: 18px 0;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: #f5efe6;
  color: #2b1a13;
  padding: 14px 16px;
  line-height: 1.9;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.article-content :deep(code) {
  background: rgba(79, 63, 48, 0.08);
  border-radius: 6px;
  padding: 0 4px;
}

.article-content :deep(.blog-inline-cta) {
  margin: 24px 0;
  border: 1px solid #e7d7bf;
  border-radius: 14px;
  background: linear-gradient(135deg, #fffaf2 0%, #f3e7d1 100%);
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.article-content :deep(.blog-inline-cta p) {
  margin: 0;
  color: #3f2a1f;
}

.article-content :deep(.blog-inline-cta a) {
  border-radius: 999px;
  padding: 8px 14px;
  text-decoration: none;
  background: var(--accent-gold);
  color: #2b1a13;
  font-weight: 800;
}

[data-theme='light'] .article-shell {
  background: #ffffff;
  border-color: #e9e2d8;
}

.article-cta {
  margin-top: 24px;
  border-radius: 14px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.article-cta p {
  margin: 0;
  color: var(--text-muted);
}

.article-cta a {
  border-radius: 999px;
  text-decoration: none;
  padding: 10px 14px;
  background: var(--accent-gold);
  color: #2b1a13;
  font-weight: 800;
  white-space: nowrap;
}

.mentioned-products {
  margin-top: 16px;
}

.mentioned-products h3 {
  margin: 0 0 10px;
  font-size: 1.25rem;
}

.mentioned-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}

.mentioned-card {
  text-decoration: none;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: inherit;
}

.mentioned-card img {
  width: 100%;
  height: 145px;
  object-fit: cover;
}

.mentioned-body {
  padding: 10px;
  display: grid;
  gap: 6px;
}

.mentioned-body strong {
  line-height: 1.5;
}

.mentioned-body p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.7;
}

.mentioned-body span {
  color: var(--accent-gold);
  font-size: 0.9rem;
  font-weight: 800;
}

.related-section {
  margin-top: 24px;
}

.related-section h2 {
  margin: 0 0 12px;
  font-size: 1.55rem;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.related-grid article {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
}

.related-grid img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.related-grid article > div {
  padding: 10px;
}

.related-grid h3 {
  margin: 8px 0 0;
  font-size: 1rem;
  line-height: 1.5;
}

.reveal-in {
  animation: rise 0.7s ease both;
}

.delay-1 { animation-delay: 0.08s; }
.delay-2 { animation-delay: 0.16s; }
.delay-3 { animation-delay: 0.24s; }

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes drift {
  from { transform: translateY(0) translateX(0); }
  to { transform: translateY(18px) translateX(-12px); }
}

@keyframes pulse {
  from { opacity: 0.4; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 1100px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .detail-sidebar {
    position: static;
    order: 2;
  }
}

@media (max-width: 860px) {
  .featured-article {
    grid-template-columns: 1fr;
  }

  .featured-media img {
    min-height: 240px;
  }
}

@media (max-width: 720px) {
  .blog-list-view,
  .blog-detail-view {
    padding: 32px 14px 90px;
  }

  .article-shell {
    padding: 16px;
  }

  .article-content {
    font-size: 1rem;
    line-height: 1.9;
  }

  .article-cta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
