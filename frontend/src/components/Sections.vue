<template>
  <div class="den-sections" dir="rtl">

    <!-- ══════════════════════════════════════════
         1. STATS COUNTER SECTION
    ══════════════════════════════════════════ -->
    <section class="stats-section" ref="statsRef">
      <!-- Background texture -->
      <div class="stats-bg">
        <div class="stats-grain"></div>
        <div class="stats-glow"></div>
      </div>

      <div class="stats-inner">
        <div class="stats-label-top">
          <span class="dot-line"></span>
          <span>دن‌روم در یک نگاه</span>
          <span class="dot-line"></span>
        </div>

        <div class="stats-grid">
          <div
            v-for="(stat, i) in stats"
            :key="i"
            class="stat-item"
            :style="{ animationDelay: i * 0.1 + 's' }"
          >
            <div class="stat-number-wrap">
              <span class="stat-value">{{ stat.current }}</span>
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </div>
            <div class="stat-divider"></div>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         2. TRANSFORMING SPACES SECTION (Zenvira-style)
    ══════════════════════════════════════════ -->
    <section class="transform-section">
      <div class="transform-inner">
        <!-- Left: Text -->
        <div class="transform-text-col">
          <div class="t-eyebrow">
            <span class="eyebrow-line"></span>
            <span>فلسفه ما</span>
          </div>
          <h2 class="transform-title">
            <em>تبدیل فضا،</em><br />
            ارتقاء تجربه
          </h2>
          <p class="transform-body">
            از مفهوم تا اجرا، فضاهایی می‌آفرینیم که آمیخته از کارکرد، احساس و هنرند — سفارشی‌شده برای بازتاب سبک زندگی و روایت شما.
          </p>
          <div class="transform-features">
            <div class="tf-item" v-for="f in features" :key="f">
              <span class="tf-check">✓</span>
              <span>{{ f }}</span>
            </div>
          </div>
          <a href="/mysite/consultation" class="transform-cta">
            مشاوره رایگان
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 5l-7 7 7 7"/>
            </svg>
          </a>
        </div>

        <!-- Right: Image collage -->
        <div class="transform-visual-col">
          <div class="visual-main-card">
            <img
              src="https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?auto=format&fit=crop&q=80&w=1200"
              alt="Interior Design"
              class="visual-img"
            />
            <div class="visual-glass-tag">
              <span class="tag-icon">🏆</span>
              <div>
                <div class="tag-title">بهترین طراح</div>
                <div class="tag-sub">جایزه ملی دکوراسیون ۱۴۰۳</div>
              </div>
            </div>
          </div>
          <div class="visual-side-cards">
            <div class="side-card sc-1">
              <img
                src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=600"
                alt=""
              />
            </div>
            <div class="side-card sc-2">
              <img
                src="https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&q=80&w=600"
                alt=""
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         3. VALUES / BELIEFS SECTION
    ══════════════════════════════════════════ -->
    <section class="values-section">
      <div class="values-bg-shape"></div>

      <div class="values-header">
        <p class="values-eyebrow">ارزش‌های دن‌روم</p>
        <h2 class="values-title">ما به چه <span class="values-accent">باور داریم</span></h2>
        <p class="values-subtitle">
          فضاهایی می‌سازیم که راحتی، زیبایی و هدف را در هم می‌آمیزند — مکان‌هایی که بی‌دردسر و ماندگار احساس می‌شوند.
        </p>
      </div>

      <div class="values-grid">
        <div
          v-for="(val, i) in values"
          :key="i"
          class="value-card"
          :class="i === 0 ? 'value-card--featured' : ''"
        >
          <div class="vc-icon-wrap" :style="{ background: val.iconBg }">
            <span class="vc-icon">{{ val.icon }}</span>
          </div>
          <div class="vc-num">{{ String(i + 1).padStart(2, '0') }}</div>
          <h3 class="vc-title">{{ val.title }}</h3>
          <p class="vc-desc">{{ val.desc }}</p>
          <div class="vc-line"></div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'

const statsRef = ref(null)

const stats = reactive([
  { target: 500, current: 0, suffix: '+', label: 'مشتری راضی' },
  { target: 320, current: 0, suffix: '+', label: 'پروژه تکمیل‌شده' },
  { target: 8,   current: 0, suffix: '',  label: 'سال تجربه' },
  { target: 4.9, current: 0, suffix: '★', label: 'امتیاز مشتریان' },
])

const features = [
  'طراحی سفارشی برای هر سبک زندگی',
  'مشاوره تخصصی چیدمان رایگان',
  'ضمانت ۲۴ ماهه بی‌قید و شرط',
  'ارسال و نصب توسط تیم حرفه‌ای',
]

const values = [
  {
    icon: '🔨',
    iconBg: 'rgba(242,201,126,0.15)',
    title: 'کیفیت اصیل',
    desc: 'هر جزئیات بازتابی از کیفیت، دقت و خلاقیت است. محصولاتی که برای یک عمر همراه شمایند.'
  },
  {
    icon: '🤝',
    iconBg: 'rgba(80,49,48,0.1)',
    title: 'همکاری صادقانه',
    desc: 'از طریق گفتگو طراحی می‌کنیم، ایده‌ها را به تجربه‌های فضایی معنادار تبدیل می‌کنیم.'
  },
  {
    icon: '♻️',
    iconBg: 'rgba(100,140,100,0.12)',
    title: 'پایداری و مسئولیت',
    desc: 'با مراقبت طراحی می‌کنیم، از مواد و روش‌هایی که ماندگاری و احترام به محیط را الهام می‌بخشند.'
  },
  {
    icon: '✨',
    iconBg: 'rgba(242,201,126,0.12)',
    title: 'نوآوری مداوم',
    desc: 'همیشه در حال یادگیری و به‌روزرسانی هستیم تا بهترین راه‌حل‌های خلاقانه را ارائه دهیم.'
  },
]

// Counter animation
function animateCounter(stat, isDecimal = false) {
  const duration = 2000
  const start = performance.now()
  const from = 0
  const to = stat.target

  function step(now) {
    const progress = Math.min((now - start) / duration, 1)
    const ease = 1 - Math.pow(1 - progress, 4)
    const val = from + (to - from) * ease
    stat.current = isDecimal ? Math.round(val * 10) / 10 : Math.floor(val)
    if (progress < 1) requestAnimationFrame(step)
    else stat.current = to
  }
  requestAnimationFrame(step)
}

onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        stats.forEach((s, i) => {
          setTimeout(() => {
            animateCounter(s, i === 3)
          }, i * 150)
        })
        observer.disconnect()
      }
    })
  }, { threshold: 0.3 })

  if (statsRef.value) observer.observe(statsRef.value)
})
</script>

<style scoped>
.den-sections {
  font-family: 'Peyda', sans-serif;
  --section-surface: var(--home-surface-strong, rgba(255, 255, 255, 0.78));
  --section-surface-soft: var(--home-surface, rgba(255, 255, 255, 0.6));
  --section-border: var(--home-border, rgba(120, 85, 57, 0.2));
  --section-border-strong: var(--home-border-strong, rgba(120, 85, 57, 0.32));
  --section-text-main: var(--home-text-main, var(--text-main));
  --section-text-muted: var(--home-text-muted, var(--text-muted));
  --section-accent: var(--home-accent, var(--accent-gold));
  --section-accent-strong: var(--home-accent-strong, var(--accent-brown));
  --section-shadow: var(--home-shadow, 0 20px 52px rgba(71, 45, 27, 0.12));
}

/* ══════ STATS SECTION ══════ */
.stats-section {
  position: relative;
  background: var(--section-surface);
  padding: 80px 24px;
  overflow: hidden;
}

.stats-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.stats-grain {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.4;
}

.stats-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 300px;
  background: radial-gradient(ellipse, color-mix(in srgb, var(--section-accent) 24%, transparent) 0%, transparent 70%);
}

.stats-inner {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.stats-label-top {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 56px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text-muted);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.dot-line {
  display: block;
  width: 50px;
  height: 1px;
  background: var(--section-accent);
  opacity: 0.3;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}

.stat-item {
  text-align: center;
  padding: 20px 24px;
  position: relative;
  animation: statFadeIn 0.6s both;
}

.stat-item + .stat-item::before {
  content: '';
  position: absolute;
  right: 0;
  top: 20%;
  height: 60%;
  width: 1px;
  background: var(--glass-border);
}

@keyframes statFadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-number-wrap {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: clamp(3rem, 5vw, 4.5rem);
  font-weight: 950;
  color: var(--section-accent-strong);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.stat-suffix {
  font-size: 2rem;
  font-weight: 950;
  color: var(--section-accent-strong);
  opacity: 0.7;
}

.stat-divider {
  width: 32px;
  height: 2px;
  background: var(--section-accent);
  opacity: 0.3;
  margin: 0 auto 12px;
  border-radius: 2px;
}

.stat-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}


/* ══════ TRANSFORM SECTION ══════ */
.transform-section {
  padding: 120px 24px;
  background: transparent;
  position: relative;
  z-index: 1;
}

.transform-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

.t-eyebrow {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 12px;
  font-weight: 800;
  color: var(--section-accent-strong);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 28px;
}

.eyebrow-line {
  display: block;
  width: 40px;
  height: 2px;
  background: var(--section-accent);
  border-radius: 2px;
}

.transform-title {
  font-size: clamp(2.4rem, 4vw, 3.5rem);
  font-weight: 950;
  color: var(--section-text-main);
  line-height: 1.15;
  margin: 0 0 28px;
}

.transform-title em {
  font-style: normal;
  color: var(--section-accent-strong);
  position: relative;
  display: inline-block;
}

.transform-title em::after {
  content: '';
  position: absolute;
  bottom: 4px;
  right: 0;
  left: 0;
  height: 3px;
  background: var(--section-accent);
  border-radius: 2px;
}

.transform-body {
  font-size: 1.05rem;
  line-height: 1.9;
  color: var(--section-text-muted);
  font-weight: 600;
  margin: 0 0 36px;
  max-width: 480px;
}

.transform-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 44px;
}

.tf-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--section-text-main);
}

.tf-check {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--home-accent-soft, rgba(201, 145, 79, 0.16));
  border: 1.5px solid var(--section-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--section-accent-strong);
  flex-shrink: 0;
}

.transform-cta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: var(--section-accent-strong);
  color: #fff8ee;
  text-decoration: none;
  font-weight: 900;
  font-size: 15px;
  padding: 16px 32px;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--section-shadow);
}

.transform-cta svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s;
}

.transform-cta:hover {
  background: color-mix(in srgb, var(--section-accent-strong) 86%, #fff 14%);
  transform: translateY(-3px);
  box-shadow: var(--section-shadow);
}

.transform-cta:hover svg {
  transform: translateX(-5px);
}

/* Visual column */
.transform-visual-col {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  align-items: start;
}

.visual-main-card {
  position: relative;
  border-radius: 32px;
  overflow: hidden;
  aspect-ratio: 3/4;
}

.visual-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.visual-main-card:hover .visual-img {
  transform: scale(1.05);
}

.visual-glass-tag {
  position: absolute;
  bottom: 20px;
  right: 16px;
  left: 16px;
  background: var(--section-surface-soft);
  backdrop-filter: blur(20px) saturate(1.8);
  border: 1px solid var(--section-border);
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.tag-icon { font-size: 22px; }

.tag-title {
  font-size: 13px;
  font-weight: 900;
  color: var(--section-text-main);
}

.tag-sub {
  font-size: 11px;
  font-weight: 700;
  color: var(--section-text-muted);
}

.visual-side-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 120px;
}

.side-card {
  border-radius: 20px;
  overflow: hidden;
  aspect-ratio: 1;
}

.side-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s;
}

.side-card:hover img { transform: scale(1.08); }

.sc-1 { transform: translateY(20px); }
.sc-2 { transform: translateY(-10px); }


/* ══════ VALUES SECTION ══════ */
.values-section {
  padding: 120px 24px;
  background: var(--section-surface);
  position: relative;
  overflow: hidden;
}

.values-bg-shape {
  position: absolute;
  top: -200px;
  left: -200px;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--section-accent) 26%, transparent) 0%, transparent 70%);
  pointer-events: none;
}

.values-header {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 80px;
}

.values-eyebrow {
  font-size: 12px;
  font-weight: 800;
  color: var(--section-accent-strong);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin: 0 0 20px;
}

.values-title {
  font-size: clamp(2.5rem, 5vw, 3.8rem);
  font-weight: 950;
  color: var(--section-text-main);
  margin: 0 0 20px;
  line-height: 1.15;
}

.values-accent {
  color: var(--section-accent-strong);
  position: relative;
  display: inline-block;
}

.values-accent::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  left: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--section-accent), color-mix(in srgb, var(--section-accent-strong) 80%, #fff 20%));
  border-radius: 4px;
}

.values-subtitle {
  font-size: 1.05rem;
  color: var(--section-text-muted);
  font-weight: 600;
  line-height: 1.8;
  margin: 0;
}

.values-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.value-card {
  background: var(--section-surface-strong);
  border-radius: 28px;
  padding: 36px 28px;
  border: 1px solid var(--section-border);
  position: relative;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--section-shadow);
}

.value-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--section-shadow);
  border-color: var(--section-border-strong);
}

.value-card--featured {
  background: linear-gradient(145deg, color-mix(in srgb, var(--section-accent-strong) 88%, #fff 12%) 0%, color-mix(in srgb, var(--section-accent-strong) 74%, #000 26%) 100%);
  border-color: transparent;
}

.value-card--featured .vc-num,
.value-card--featured .vc-title,
.value-card--featured .vc-desc {
  color: rgba(255,255,255,0.9);
}

.value-card--featured .vc-num {
  color: var(--accent-gold);
  opacity: 0.5;
}

.value-card--featured .vc-line {
  background: var(--glass-border-bright);
}

.vc-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.vc-icon {
  font-size: 22px;
}

.vc-num {
  font-size: 11px;
  font-weight: 900;
  color: var(--section-accent-strong);
  opacity: 0.2;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}

.vc-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--section-text-main);
  margin-bottom: 14px;
}

.vc-desc {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--section-text-muted);
  line-height: 1.7;
  margin: 0;
}

.vc-line {
  width: 32px;
  height: 2px;
  background: var(--home-accent-soft, rgba(201, 145, 79, 0.2));
  border-radius: 2px;
  margin-top: 24px;
  transition: width 0.4s;
}

.value-card:hover .vc-line {
  width: 60px;
}

/* ══════ RESPONSIVE ══════ */
@media (max-width: 1024px) {
  .values-grid { grid-template-columns: repeat(2, 1fr); }
  .transform-inner { grid-template-columns: 1fr; gap: 60px; }
  .transform-visual-col { max-width: 480px; }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 32px; }
  .stat-item + .stat-item::before { display: none; }
  .stat-item:nth-child(2n)::before { display: none; }
  .values-grid { grid-template-columns: 1fr; }
  .transform-title { font-size: 2.2rem; }
}
</style>
