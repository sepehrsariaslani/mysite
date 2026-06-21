<template>
  <div class="about-page" dir="rtl">
    <section class="about-shell">
      <div class="about-bg" aria-hidden="true">
        <span class="orb orb-1"></span>
        <span class="orb orb-2"></span>
        <span class="orb orb-3"></span>
      </div>

      <header class="hero-panel liquid-panel" data-reveal>
        <div class="hero-top-row">
          <span class="hero-badge">{{ content.hero.badge }}</span>
          <span class="hero-year">{{ toPersianDigits(content.hero.foundedYear) }}</span>
        </div>
        <h1>{{ content.hero.title }}</h1>
        <p class="hero-subtitle">{{ content.hero.subtitle }}</p>
        <p class="hero-intro">{{ content.hero.intro }}</p>
        <div class="hero-actions">
          <a class="hero-btn hero-btn-primary" href="/consultation">مشاوره و فروش</a>
          <a class="hero-btn hero-btn-ghost" href="/cooperation">همکاری با ما</a>
        </div>
      </header>

      <section class="mission-vision-grid">
        <article class="liquid-panel info-card" data-reveal>
          <span class="card-kicker">ماموریت</span>
          <h2>{{ content.mission.title }}</h2>
          <div class="rich-content" v-html="content.mission.body"></div>
        </article>
        <article class="liquid-panel info-card" data-reveal>
          <span class="card-kicker">چشم انداز</span>
          <h2>{{ content.vision.title }}</h2>
          <div class="rich-content" v-html="content.vision.body"></div>
        </article>
      </section>

      <section class="values-section" data-reveal>
        <div class="section-head">
          <span class="kicker">ارزش ها</span>
          <h2>ارزش های کلیدی ما</h2>
        </div>

        <div class="values-grid">
          <article
            v-for="(item, idx) in content.values"
            :key="`${item.title}-${idx}`"
            class="liquid-panel value-card"
            :style="{ '--local-delay': `${idx * 80}ms` }"
          >
            <span class="value-icon">{{ item.icon }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </section>

      <section class="history-section" data-reveal>
        <article class="liquid-panel history-overview">
          <span class="kicker">تاریخچه</span>
          <h2>{{ content.history.title }}</h2>
          <p class="history-intro">{{ content.history.intro }}</p>
          <div class="rich-content" v-html="content.history.body"></div>
        </article>

        <ol class="timeline-zigzag">
          <li
            v-for="(event, idx) in content.timeline"
            :key="`${event.year}-${event.title}-${idx}`"
            class="timeline-row"
            :class="[(idx % 2 === 0 ? 'left' : 'right'), { highlight: event.highlight }]"
            data-reveal
          >
            <span class="timeline-center-dot" aria-hidden="true">{{ toPersianDigits(event.year) }}</span>
            <span class="timeline-link" aria-hidden="true"></span>
            <span class="timeline-icon" aria-hidden="true">{{ event.highlight ? '✦' : '•' }}</span>
            <article class="liquid-panel timeline-content">
              <span class="timeline-step">{{ toPersianDigits(event.year) }}</span>
              <h3>{{ event.title }}</h3>
              <p>{{ event.description }}</p>
            </article>
          </li>
        </ol>
      </section>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const FALLBACK_CONTENT = {
  hero: {
    badge: 'ABOUT DENROOM',
    title: 'ما دن‌روم هستیم',
    subtitle: 'طراحی، ساخت و اجرای مبلمان سفارشی برای فضاهای مسکونی و تجاری',
    intro: 'تمرکز ما روی ترکیب طراحی معاصر، کیفیت ساخت دقیق و تجربه خرید شفاف است.',
    foundedYear: 1396,
  },
  mission: {
    title: 'ماموریت ما',
    body: '<p>ماموریت دن‌روم ساخت محصولاتی است که هم از نظر زیبایی و هم از نظر کاربری، زندگی روزمره را بهتر کنند.</p>',
  },
  vision: {
    title: 'چشم‌انداز ما',
    body: '<p>چشم‌انداز ما تبدیل‌شدن به مرجع مبلمان سفارشی در ایران است.</p>',
  },
  history: {
    title: 'تاریخچه دن‌روم',
    intro: 'دن‌روم از یک کارگاه تخصصی کوچک شروع شد و امروز به یک تیم کامل طراحی و تولید تبدیل شده است.',
    body: '<p>طی این مسیر، کیفیت ساخت، خدمات حرفه‌ای و شخصی‌سازی واقعی هسته اصلی رشد ما بوده است.</p>',
  },
  values: [
    { icon: '✦', title: 'کیفیت واقعی', description: 'متریال استاندارد و کنترل کیفیت دقیق در هر مرحله.' },
    { icon: '✦', title: 'شفافیت', description: 'اطلاعات روشن درباره محصول، قیمت و زمان تحویل.' },
    { icon: '✦', title: 'مشتری‌محوری', description: 'راه‌حل متناسب با نیاز واقعی هر پروژه.' },
    { icon: '✦', title: 'نوآوری کاربردی', description: 'ترکیب طراحی روز با راحتی و دوام.' },
  ],
  timeline: [
    { year: '۱۳۹۶', title: 'شروع مسیر', description: 'آغاز فعالیت با تمرکز بر مبلمان سفارشی.', highlight: 0 },
    { year: '۱۳۹۸', title: 'توسعه محصولات', description: 'گسترش سبد محصولات و افزایش تنوع مدل‌ها.', highlight: 0 },
    { year: '۱۴۰۱', title: 'پروژه‌های بزرگ', description: 'ورود به اجرای پروژه‌های مسکونی و تجاری.', highlight: 1 },
    { year: 'امروز', title: 'توسعه مستمر', description: 'بهبود تجربه دیجیتال و خدمات تخصصی.', highlight: 0 },
  ],
}

function asText(value, fallback = '') {
  const text = String(value ?? '').trim()
  return text || fallback
}

function asNumber(value, fallback = 0) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function asSort(value, fallback = 0) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function normalizePayload(source) {
  const payload = source && typeof source === 'object' ? source : {}
  const hero = payload.hero && typeof payload.hero === 'object' ? payload.hero : {}
  const mission = payload.mission && typeof payload.mission === 'object' ? payload.mission : {}
  const vision = payload.vision && typeof payload.vision === 'object' ? payload.vision : {}
  const history = payload.history && typeof payload.history === 'object' ? payload.history : {}

  const values = asArray(payload.values)
    .map((item, idx) => ({
      icon: asText(item?.icon, '✦'),
      title: asText(item?.title ?? item?.value_title),
      description: asText(item?.description ?? item?.value_description),
      sortOrder: asSort(item?.sort_order, (idx + 1) * 10),
    }))
    .filter((item) => item.title && item.description)
    .sort((a, b) => a.sortOrder - b.sortOrder || a.title.localeCompare(b.title, 'fa'))
    .map(({ icon, title, description }) => ({ icon, title, description }))

  const timeline = asArray(payload.timeline)
    .map((item, idx) => ({
      year: asText(item?.year ?? item?.year_label),
      title: asText(item?.title ?? item?.milestone_title),
      description: asText(item?.description ?? item?.milestone_description),
      highlight: Number(item?.highlight ?? item?.is_highlight) ? 1 : 0,
      sortOrder: asSort(item?.sort_order, (idx + 1) * 10),
    }))
    .filter((item) => item.year && item.title && item.description)
    .sort((a, b) => a.sortOrder - b.sortOrder)
    .map(({ year, title, description, highlight }) => ({ year, title, description, highlight }))

  return {
    hero: {
      badge: asText(hero.badge, FALLBACK_CONTENT.hero.badge),
      title: asText(hero.title, FALLBACK_CONTENT.hero.title),
      subtitle: asText(hero.subtitle, FALLBACK_CONTENT.hero.subtitle),
      intro: asText(hero.intro, FALLBACK_CONTENT.hero.intro),
      foundedYear: asNumber(hero.founded_year ?? hero.foundedYear, FALLBACK_CONTENT.hero.foundedYear),
    },
    mission: {
      title: asText(mission.title, FALLBACK_CONTENT.mission.title),
      body: asText(mission.body, FALLBACK_CONTENT.mission.body),
    },
    vision: {
      title: asText(vision.title, FALLBACK_CONTENT.vision.title),
      body: asText(vision.body, FALLBACK_CONTENT.vision.body),
    },
    history: {
      title: asText(history.title, FALLBACK_CONTENT.history.title),
      intro: asText(history.intro, FALLBACK_CONTENT.history.intro),
      body: asText(history.body, FALLBACK_CONTENT.history.body),
    },
    values: values.length ? values : FALLBACK_CONTENT.values,
    timeline: timeline.length ? timeline : FALLBACK_CONTENT.timeline,
  }
}

function toPersianDigits(value) {
  return String(value).replace(/\d/g, (digit) => '۰۱۲۳۴۵۶۷۸۹'[Number(digit)])
}

const bootData = typeof window !== 'undefined' ? (window.AboutPageData || window.aboutPageData || {}) : {}
const content = normalizePayload(bootData)

let revealObserver = null

function setupRevealAnimations() {
  const nodes = Array.from(document.querySelectorAll('.about-page [data-reveal]'))
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
    {
      threshold: 0.15,
      rootMargin: '0px 0px -8% 0px',
    }
  )

  nodes.forEach((node, index) => {
    node.style.setProperty('--reveal-delay', `${Math.min(index * 80, 260)}ms`)
    revealObserver.observe(node)
  })
}

onMounted(() => {
  setupRevealAnimations()
})

onUnmounted(() => {
  revealObserver?.disconnect()
  revealObserver = null
})
</script>
<style scoped>
.about-page {
  --about-bg: #ffffff;
  --about-surface: rgba(255, 255, 255, 0.74);
  --about-surface-soft: rgba(247, 235, 218, 0.62);
  --about-border: rgba(122, 86, 58, 0.24);
  --about-border-strong: rgba(122, 86, 58, 0.34);
  --about-shadow: 0 28px 60px rgba(77, 49, 28, 0.14);
  --about-shadow-soft: 0 14px 34px rgba(77, 49, 28, 0.09);
  --about-text: #2f2118;
  --about-muted: rgba(56, 38, 25, 0.72);
  --about-accent: #c68a4b;
  --about-accent-strong: #6f4830;
  min-height: 100vh;
  background: var(--about-bg);
  color: var(--about-text);
  font-family: 'Peyda', sans-serif;
  overflow: hidden;
}

[data-theme='dark'] .about-page {
  --about-bg: #f9f4ec;
  --about-surface: rgba(255, 255, 255, 0.78);
  --about-surface-soft: rgba(244, 228, 205, 0.66);
  --about-border: rgba(122, 86, 58, 0.28);
  --about-border-strong: rgba(122, 86, 58, 0.38);
  --about-shadow: 0 30px 64px rgba(77, 49, 28, 0.16);
  --about-shadow-soft: 0 16px 36px rgba(77, 49, 28, 0.11);
  --about-text: #2f2118;
  --about-muted: rgba(56, 38, 25, 0.74);
  --about-accent: #bb7f41;
  --about-accent-strong: #663f2b;
}

.about-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px 110px;
  position: relative;
}

.about-bg {
  position: absolute;
  inset: 40px 0 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(66px);
  opacity: 0.5;
  animation: drift 12s ease-in-out infinite alternate;
}

.orb-1 {
  width: 340px;
  height: 340px;
  top: 46px;
  right: -54px;
  background: radial-gradient(circle, rgba(206, 149, 85, 0.86) 0%, rgba(206, 149, 85, 0) 72%);
}

.orb-2 {
  width: 440px;
  height: 440px;
  left: -130px;
  top: 300px;
  background: radial-gradient(circle, rgba(166, 117, 82, 0.62) 0%, rgba(166, 117, 82, 0) 72%);
  animation-delay: 1.8s;
}

.orb-3 {
  width: 280px;
  height: 280px;
  right: 36%;
  bottom: 130px;
  background: radial-gradient(circle, rgba(241, 210, 176, 0.7) 0%, rgba(241, 210, 176, 0) 72%);
  animation-delay: 3.2s;
}

.liquid-panel {
  position: relative;
  background: linear-gradient(135deg, var(--about-surface) 0%, var(--about-surface-soft) 100%);
  border: 1px solid var(--about-border);
  box-shadow: var(--about-shadow-soft), inset 0 1px 0 rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(15px) saturate(145%);
  -webkit-backdrop-filter: blur(15px) saturate(145%);
  overflow: hidden;
}

.liquid-panel::before {
  content: "";
  position: absolute;
  inset: -52% auto auto -40%;
  width: 160%;
  height: 180px;
  background: linear-gradient(115deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.38), rgba(255, 255, 255, 0));
  transform: rotate(-9deg);
  animation: sheen 8.6s linear infinite;
  pointer-events: none;
}

[data-reveal] {
  opacity: 0;
  transform: translateY(26px) scale(0.985);
  transition: opacity 0.68s ease, transform 0.68s ease;
  transition-delay: var(--reveal-delay, 0ms);
}

[data-reveal].visible {
  opacity: 1;
  transform: none;
}

.hero-panel {
  margin-top: 104px;
  border-radius: 34px;
  padding: 44px 42px;
  z-index: 2;
}

.hero-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(198, 138, 75, 0.16);
  border: 1px solid var(--about-border-strong);
  color: var(--about-accent-strong);
  font-weight: 800;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
}

.hero-year {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--about-border);
  color: var(--about-accent-strong);
  font-size: 0.86rem;
  font-weight: 760;
}

.hero-panel h1 {
  margin: 0 0 12px;
  font-size: clamp(2.2rem, 4.8vw, 3.8rem);
  font-weight: 1000;
  color: var(--about-text);
  line-height: 1.12;
}

.hero-subtitle {
  margin: 0;
  max-width: 880px;
  font-size: clamp(1.05rem, 2vw, 1.24rem);
  font-weight: 650;
  color: var(--about-accent-strong);
  line-height: 1.9;
}

.hero-intro {
  margin: 14px 0 0;
  max-width: 930px;
  color: var(--about-muted);
  line-height: 1.95;
  font-size: 1.01rem;
}

.hero-actions {
  margin-top: 26px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-btn {
  text-decoration: none;
  border-radius: 999px;
  padding: 12px 20px;
  font-size: 0.92rem;
  font-weight: 820;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.hero-btn-primary {
  background: linear-gradient(135deg, var(--about-accent) 0%, #b6773d 100%);
  color: #fff;
  box-shadow: 0 14px 28px rgba(177, 118, 64, 0.32);
}

.hero-btn-ghost {
  color: var(--about-accent-strong);
  border: 1px solid var(--about-border-strong);
  background: rgba(255, 255, 255, 0.74);
}

.hero-btn:hover {
  transform: translateY(-2px);
}

.mission-vision-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  position: relative;
  z-index: 1;
}

.info-card {
  border-radius: 28px;
  padding: 28px 24px 24px;
}

.card-kicker,
.kicker {
  display: inline-block;
  margin-bottom: 10px;
  color: var(--about-accent);
  font-size: 0.84rem;
  font-weight: 820;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.info-card h2,
.section-head h2,
.history-overview h2 {
  margin: 0 0 10px;
  font-size: clamp(1.56rem, 2.2vw, 2.1rem);
  font-weight: 930;
  color: var(--about-text);
}

.rich-content :deep(p) {
  margin: 0 0 8px;
  color: var(--about-muted);
  font-size: 0.99rem;
  line-height: 1.95;
}

.rich-content :deep(p:last-child) {
  margin-bottom: 0;
}

.values-section {
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.section-head {
  margin-bottom: 12px;
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.value-card {
  border-radius: 24px;
  padding: 20px 16px 18px;
  animation: floatUp 1s ease both;
  animation-delay: var(--local-delay, 0ms);
}

.value-icon {
  display: inline-grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(198, 138, 75, 0.18);
  color: var(--about-accent-strong);
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.value-card h3 {
  margin: 0;
  font-size: 1.03rem;
  font-weight: 860;
  color: var(--about-text);
}

.value-card p {
  margin: 8px 0 0;
  color: var(--about-muted);
  line-height: 1.85;
  font-size: 0.92rem;
}

.history-section {
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.history-overview {
  border-radius: 28px;
  padding: 30px 24px;
  margin-bottom: 16px;
}

.history-intro {
  margin: 0 0 12px;
  color: var(--about-accent-strong);
  font-weight: 700;
  line-height: 1.85;
}

.timeline-zigzag {
  position: relative;
  list-style: none;
  margin: 0;
  padding: 4px 0 6px;
  direction: ltr;
}

.timeline-zigzag::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  background: linear-gradient(to bottom, rgba(198, 138, 75, 0.92), rgba(198, 138, 75, 0.35));
}

.timeline-row {
  position: relative;
  min-height: 212px;
  padding: 10px 0;
}

.timeline-center-dot {
  position: absolute;
  left: 50%;
  top: 64px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  border: 2px solid rgba(198, 138, 75, 0.9);
  box-shadow: 0 0 0 4px rgba(198, 138, 75, 0.18);
  z-index: 2;
}

.timeline-link {
  position: absolute;
  top: 69px;
  border-top: 2px dashed rgba(124, 89, 58, 0.5);
  z-index: 0;
}

.timeline-row.left .timeline-link {
  left: 56px;
  width: calc(50% - 56px);
}

.timeline-row.right .timeline-link {
  left: 50%;
  width: calc(50% - 56px);
}

.timeline-icon {
  position: absolute;
  top: 42px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: linear-gradient(140deg, rgba(198, 138, 75, 0.95) 0%, rgba(157, 104, 55, 0.96) 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 860;
  box-shadow: 0 14px 28px rgba(155, 102, 52, 0.34);
  z-index: 1;
}

.timeline-row.left .timeline-icon {
  left: 30px;
}

.timeline-row.right .timeline-icon {
  right: 30px;
}

.timeline-content {
  width: min(420px, calc(50% - 126px));
  border-radius: 22px;
  padding: 20px 20px 18px;
  direction: rtl;
  text-align: right;
  border-color: var(--about-border);
}

.timeline-row.left .timeline-content {
  margin-left: 96px;
  margin-right: auto;
}

.timeline-row.right .timeline-content {
  margin-right: 96px;
  margin-left: auto;
}

.timeline-row.highlight .timeline-content {
  border-color: var(--about-border-strong);
  box-shadow: var(--about-shadow);
}

.timeline-row.highlight .timeline-icon {
  box-shadow: 0 16px 30px rgba(155, 102, 52, 0.4);
}

.timeline-step {
  display: inline-block;
  margin-bottom: 8px;
  color: var(--about-accent);
  font-size: 0.74rem;
  font-weight: 830;
  letter-spacing: 0.08em;
}

.timeline-year {
  display: inline-block;
  margin-right: 10px;
  background: rgba(198, 138, 75, 0.17);
  color: var(--about-accent-strong);
  border: 1px solid var(--about-border-strong);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 820;
}

.timeline-content h3 {
  margin: 10px 0 0;
  font-size: 1.09rem;
  font-weight: 860;
  color: var(--about-text);
}

.timeline-content p {
  margin: 8px 0 0;
  color: var(--about-muted);
  line-height: 1.9;
  font-size: 0.92rem;
}

@keyframes drift {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(26px, -20px) scale(1.08); }
}

@keyframes sheen {
  0% { transform: translateX(-120%) rotate(-9deg); }
  100% { transform: translateX(146%) rotate(-9deg); }
}

@keyframes floatUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: none; }
}

@media (max-width: 1180px) {
  .values-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .timeline-row {
    min-height: 196px;
  }

  .timeline-content {
    width: min(360px, calc(50% - 116px));
  }
}

@media (max-width: 920px) {
  .about-shell {
    padding: 0 14px 84px;
  }

  .hero-panel {
    margin-top: 88px;
    border-radius: 26px;
    padding: 30px 20px;
  }

  .mission-vision-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-card,
  .history-overview {
    border-radius: 22px;
    padding: 24px 16px;
  }

  .timeline-zigzag {
    direction: rtl;
    padding: 2px 0;
  }

  .timeline-zigzag::before {
    left: auto;
    right: 22px;
    transform: none;
  }

  .timeline-row {
    min-height: auto;
    padding: 0 0 14px;
  }

  .timeline-center-dot {
    left: auto;
    right: 22px;
    top: 52px;
    transform: translate(50%, -50%);
  }

  .timeline-link {
    left: auto !important;
    right: 22px;
    top: 57px;
    width: 44px !important;
  }

  .timeline-icon {
    top: 34px;
    left: auto !important;
    right: 64px;
    width: 44px;
    height: 44px;
    font-size: 0.9rem;
  }

  .timeline-content {
    width: auto;
    margin: 0 !important;
    margin-right: 122px !important;
    border-radius: 18px;
    padding: 16px 14px;
  }

  .timeline-row:last-child {
    padding-bottom: 0;
  }
}

@media (max-width: 680px) {
  .hero-top-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    width: 100%;
    flex-direction: column;
  }

  .hero-btn {
    width: 100%;
    text-align: center;
  }

  .values-grid {
    grid-template-columns: 1fr;
  }

  .value-card {
    border-radius: 20px;
  }

  .timeline-zigzag::before,
  .timeline-center-dot {
    right: 16px;
  }

  .timeline-link {
    right: 16px;
    width: 34px !important;
  }

  .timeline-icon {
    right: 54px;
    width: 40px;
    height: 40px;
    font-size: 0.82rem;
  }

  .timeline-content {
    margin-right: 104px !important;
  }

  .timeline-step {
    font-size: 0.7rem;
  }

  .timeline-content h3 {
    font-size: 1.02rem;
  }
}




/* MYSITE-MANAGEMENT-VISUAL-STYLES:START */
main:nth-of-type(1) > div:nth-of-type(1) > section:nth-of-type(1) > section:nth-of-type(3) > ol:nth-of-type(1) > li:nth-of-type(5) > span:nth-of-type(3) {
  position: relative;
}

li.highlight {
  align-items: flex-start;
  position: relative;
  text-align: left;
  min-height: auto;
  display: flex;
}

div:nth-of-type(1) > main:nth-of-type(1) > div:nth-of-type(1) > section:nth-of-type(1) > section:nth-of-type(3) > ol:nth-of-type(1) > li:nth-of-type(2) {
  min-height: auto;
}

div:nth-of-type(1) > main:nth-of-type(1) > div:nth-of-type(1) > section:nth-of-type(1) > section:nth-of-type(3) > ol:nth-of-type(1) > li:nth-of-type(1) {
  min-height: auto;
}
/* MYSITE-MANAGEMENT-VISUAL-STYLES:END */
</style>
