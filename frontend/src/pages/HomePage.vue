<template>
  <div class="home-page" dir="rtl">
    <!-- Liquid Background Blobs -->
    <div class="liquid-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="blob blob-4"></div>
    </div>

    <!-- ══════ HERO SECTION ══════ -->
    <HeroSection />

    <!-- ══════ CATEGORIES (Liquid Glass Pills) ══════ -->
    <section class="cat-section">
      <div class="section-head animate-scroll">
        <span class="sh-eyebrow">کالکشن‌ها</span>
        <h2 class="sh-title">جستجوی دسته‌بندی‌ها</h2>
        <p class="sh-sub">دنیایی از انتخاب برای هر سلیقه</p>
      </div>

      <div class="cat-track">
        <div
          v-for="(cat, i) in categories"
          :key="cat.name"
          class="cat-pill"
          :class="{ 'cat-active': activeCat === i }"
          @mouseenter="setActive(i)"
          @mouseleave="resetActive"
          @click="activeCat = i"
        >
          <div class="cat-pill-img">
            <img :src="cat.image" :alt="cat.name" />
            <div class="cat-pill-grad"></div>
          </div>
          <div class="cat-pill-glass"></div>
          <div class="cat-pill-shimmer"></div>
          <div class="cat-pill-content">
            <span class="cat-num">{{ String(i + 1).padStart(2, '0') }}</span>
            <h3 class="cat-name">{{ cat.name }}</h3>
            <p class="cat-desc">{{ cat.desc }}</p>
            <a :href="cat.link" class="cat-link">مشاهده <span>←</span></a>
          </div>
          <div class="cat-orb" :style="{ background: cat.orb }"></div>
        </div>
      </div>

      <div class="cat-dots">
        <button
          v-for="(_, i) in categories"
          :key="i"
          class="cat-dot"
          :class="{ active: activeCat === i }"
          @click="activeCat = i"
        ></button>
      </div>
    </section>

    <BestSellerShowcase :products="bestSellerProducts" :selected-customer="selectedCustomer" />
    <ShopByLookPreview :scenes="shopByLookHighlights" :selected-customer="selectedCustomer" />
    <ProjectsPreview :projects="projectHighlights" :selected-customer="selectedCustomer" />

    <!-- ══════ SHARED SECTIONS (Stats, Transform, Values) ══════ -->
    <Sections />

    <!-- ══════ QUALITY ══════ -->
    <section class="quality-section">
      <div class="section-shell">
        <div class="quality-content-box">
          <div class="quality-icon">✨</div>
          <h2 class="quality-title">کیفیت بدون مرز</h2>
          <div class="quality-grid">
            <div class="q-item"><span class="q-val">۲۴</span><span class="q-label">ماه ضمانت بی قید و شرط</span></div>
            <div class="q-item"><span class="q-val">۷</span><span class="q-label">روز مهلت تست در منزل</span></div>
            <div class="q-item"><span class="q-val">۵۰+</span><span class="q-label">مدل پارچه اختصاصی</span></div>
          </div>
          <p class="quality-text">ما از بهترین چوب‌های راش و گردو در کنار پارچه‌های نانو استفاده می‌کنیم تا محصولی برای یک عمر همراهی شما تولید کنیم.</p>
        </div>
      </div>
    </section>

    <!-- ══════ BLOG ══════ -->
    <BlogSection />

    <!-- ══════ TRUST ══════ -->
    <section class="trust-section trust-section--quick">
      <div class="section-shell">
        <div class="section-head trust-head animate-scroll">
          <span class="sh-eyebrow">اعتماد سریع</span>
          <h2 class="sh-title">چرا خرید از دن‌روم مطمئن است؟</h2>
          <p class="sh-sub">سه مزیتی که از روز اول همراه شماست</p>
        </div>
        <div class="trust-grid trust-grid--quick">
          <div v-for="(item, idx) in supportItems" :key="item.title" class="trust-card liquid-glass-inner trust-card--quick">
            <div class="trust-icon">{{item.icon}}</div>
            <h3>{{item.title}}</h3>
            <p>{{item.desc}}</p>
            <p class="trust-meta">
              {{ idx === 0 ? 'پاسخ‌گویی روزانه و شخصی‌سازی انتخاب‌ها' : idx === 1 ? 'تحویل سراسری با بسته‌بندی استاندارد' : 'پشتیبانی فعال بعد از تحویل محصول' }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════ TRUST DETAILS ══════ -->
    <section class="trust-section trust-section--care">
      <div class="section-shell">
        <div class="section-head trust-head animate-scroll">
          <span class="sh-eyebrow">همراهی دن‌روم</span>
          <h2 class="sh-title">بعد از خرید هم کنار شما می‌مانیم</h2>
          <p class="sh-sub">همه خدمات، مرحله‌به‌مرحله و شفاف</p>
        </div>
        <div class="trust-grid trust-grid--care">
          <div v-for="(item, idx) in supportItems" :key="`care-${item.title}`" class="trust-card liquid-glass-inner trust-card--detail">
            <span class="trust-step">{{ String(idx + 1).padStart(2, '0') }}</span>
            <div class="trust-icon">{{item.icon}}</div>
            <h3>{{item.title}}</h3>
            <p>{{item.desc}}</p>
          </div>
        </div>
        <div class="trust-actions">
          <a href="/consultation" class="trust-btn trust-btn--primary">شروع مشاوره</a>
          <a href="/cooperation" class="trust-btn trust-btn--ghost">ارتباط با تیم خدمات</a>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import Sections from '@/components/Sections.vue'
import BlogSection from '@/components/BlogSection.vue'
import HeroSection from '@/components/HeroSection.vue'
import ShopByLookPreview from '@/components/ShopByLookPreview.vue'
import ProjectsPreview from '@/components/ProjectsPreview.vue'
import BestSellerShowcase from '@/components/BestSellerShowcase.vue'
import { ref, reactive, onMounted, onUnmounted } from 'vue'

// ── Categories ──
const activeCat = ref(0)
let autoCycle

function setActive(idx) { clearInterval(autoCycle); activeCat.value = idx }
function resetActive() {
  clearTimeout(resetTimer)
  resetTimer = setTimeout(() => startCycle(), 200)
}
let resetTimer
function startCycle() {
  clearInterval(autoCycle)
  autoCycle = setInterval(() => { activeCat.value = (activeCat.value + 1) % categories.length }, 3500)
}

const categories = [
  {
    name: 'مبلمان راحتی',
    desc: 'کالکشن‌های مدرن و مینیمال برای نشیمن',
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=800',
    link: '/sofas',
    orb: 'radial-gradient(circle, rgba(242,201,126,0.7) 0%, transparent 70%)'
  },
  {
    name: 'صندلی اپن و بار',
    desc: 'ظرافت و راحتی در پیشخوان آشپزخانه',
    image: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?auto=format&fit=crop&q=80&w=800',
    link: '/barstools',
    orb: 'radial-gradient(circle, rgba(80,49,48,0.6) 0%, transparent 70%)'
  },
  {
    name: 'میز ناهارخوری',
    desc: 'مرکز تجمعات خانوادگی شما',
    image: 'https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&q=80&w=800',
    link: '/tables',
    orb: 'radial-gradient(circle, rgba(200,160,100,0.6) 0%, transparent 70%)'
  },
  {
    name: 'میز جلومبلی و عسلی',
    desc: 'ظرافت و هنر در جزئیات پذیرایی',
    image: 'https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&q=80&w=800',
    link: '/coffee-tables',
    orb: 'radial-gradient(circle, rgba(140,120,80,0.6) 0%, transparent 70%)'
  },
  {
    name: 'نیمکت‌های مدرن',
    desc: 'ترکیب زیبایی و کارایی کنار دیوارها',
    image: 'https://images.unsplash.com/photo-1595514535311-665d95368307?auto=format&fit=crop&q=80&w=800',
    link: '/benches',
    orb: 'radial-gradient(circle, rgba(255,152,0,0.6) 0%, transparent 70%)'
  },
  {
    name: 'اکسسوری و دکور',
    desc: 'جزئیاتی که تفاوت ایجاد می‌کنند',
    image: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=800',
    link: '/categories',
    orb: 'radial-gradient(circle, rgba(141,110,99,0.6) 0%, transparent 70%)'
  },
]

const supportItems = [
  { icon: '📞', title: 'مشاوره شخصی', desc: 'تیم فروش ما در تمامی مراحل انتخاب همراه شماست' },
  { icon: '🚚', title: 'ارسال ایمن', desc: 'بسته‌بندی تخصصی و ارسال توسط تیم حرفه‌ای دن‌روم' },
  { icon: '🛠️', title: 'خدمات پس از فروش', desc: 'تهد ما پس از فروش نیز با قدرت ادامه دارد' },
]

const shopByLookHighlights = ref(window.ShopByLookHighlights || [])
const projectHighlights = ref(window.ProjectHighlights || [])
const bestSellerProducts = ref(window.BestSellerProducts || [])
const selectedCustomer = ref(window.SelectedCustomer || '')

onMounted(() => {
  startCycle()
  
  // Animation on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view')
      }
    })
  }, { threshold: 0.1 })

  document.querySelectorAll('.animate-scroll').forEach(el => observer.observe(el))
})
onUnmounted(() => clearInterval(autoCycle))
</script>

<style scoped>
.home-page {
  --home-page-bg: #ffffff;
  --home-page-bg-strong: #ffffff;
  --home-surface: rgba(255, 255, 255, 0.6);
  --home-surface-strong: rgba(255, 255, 255, 0.78);
  --home-surface-soft: rgba(255, 255, 255, 0.48);
  --home-border: rgba(120, 85, 57, 0.2);
  --home-border-strong: rgba(120, 85, 57, 0.32);
  --home-shadow: 0 20px 52px rgba(71, 45, 27, 0.12);
  --home-shadow-strong: 0 30px 72px rgba(71, 45, 27, 0.18);
  --home-text-main: #2f2118;
  --home-text-muted: rgba(50, 33, 23, 0.68);
  --home-text-soft: rgba(50, 33, 23, 0.55);
  --home-accent: #c9914f;
  --home-accent-strong: #7b4f34;
  --home-accent-soft: rgba(201, 145, 79, 0.16);
  --home-link-text: #3a2618;
  --home-shell-max: 1320px;
  --home-inline-pad: 24px;
  --home-space-xl: 96px;
  --home-space-lg: 72px;
  --home-radius-lg: 32px;
  --home-radius-md: 22px;
  --home-pill: 999px;
  --home-blob-opacity: 0;
  min-height: 100vh;
  color: var(--home-text-main);
  overflow-x: hidden;
  font-family: 'Peyda', sans-serif;
  background: #ffffff;
}

[data-theme='dark'] .home-page {
  --home-page-bg: #ffffff;
  --home-page-bg-strong: #ffffff;
  --home-surface: rgba(255, 255, 255, 0.68);
  --home-surface-strong: rgba(255, 255, 255, 0.86);
  --home-surface-soft: rgba(255, 255, 255, 0.56);
  --home-border: rgba(120, 85, 57, 0.2);
  --home-border-strong: rgba(120, 85, 57, 0.32);
  --home-shadow: 0 20px 52px rgba(71, 45, 27, 0.12);
  --home-shadow-strong: 0 30px 72px rgba(71, 45, 27, 0.18);
  --home-text-main: #2f2118;
  --home-text-muted: rgba(50, 33, 23, 0.68);
  --home-text-soft: rgba(50, 33, 23, 0.55);
  --home-accent: #c9914f;
  --home-accent-strong: #7b4f34;
  --home-accent-soft: rgba(201, 145, 79, 0.16);
  --home-link-text: #3a2618;
  --home-blob-opacity: 0;
  background: #ffffff;
}

.home-page > :not(.liquid-bg) {
  position: relative;
  z-index: 1;
}

.section-shell {
  max-width: var(--home-shell-max);
  margin: 0 auto;
  padding: 0 var(--home-inline-pad);
}

/* BLOBS */
.liquid-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(84px);
  opacity: var(--home-blob-opacity);
  animation: blob-float 20s infinite alternate;
}

.blob-1 { width: 560px; height: 560px; background: radial-gradient(circle, rgba(210, 156, 96, 0.78), transparent 72%); top: -80px; right: -160px; }
.blob-2 { width: 640px; height: 640px; background: radial-gradient(circle, rgba(164, 118, 83, 0.42), transparent 70%); bottom: -240px; left: -170px; }
.blob-3 { width: 460px; height: 460px; background: radial-gradient(circle, rgba(209, 175, 137, 0.38), transparent 74%); top: 32%; left: 12%; }
.blob-4 { width: 420px; height: 420px; background: radial-gradient(circle, rgba(155, 109, 76, 0.24), transparent 72%); top: 22%; right: 22%; }

@keyframes blob-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(26px, 42px) scale(1.08); }
}

/* CATEGORIES */
.cat-section {
  padding: var(--home-space-xl) var(--home-inline-pad) 0;
}

.section-head {
  text-align: center;
  margin: 0 auto 64px;
  max-width: 760px;
}

.sh-eyebrow {
  display: inline-block;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.2em;
  color: var(--home-accent-strong);
  text-transform: uppercase;
  margin-bottom: 14px;
  background: var(--home-surface-strong);
  padding: 7px 17px;
  border-radius: var(--home-pill);
  border: 1px solid var(--home-border);
}

.sh-title {
  font-size: clamp(2rem, 5vw, 3.15rem);
  font-weight: 950;
  color: var(--home-text-main);
  margin: 0 0 12px;
  line-height: 1.2;
}

.sh-sub {
  font-size: 1rem;
  color: var(--home-text-muted);
  font-weight: 700;
  margin: 0;
}

.cat-track {
  max-width: var(--home-shell-max);
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 14px;
  height: 530px;
}

.cat-pill {
  position: relative;
  border-radius: 40px;
  overflow: hidden;
  cursor: pointer;
  width: 104px;
  height: 450px;
  flex-shrink: 0;
  transition: all 0.75s cubic-bezier(0.16, 1, 0.3, 1);
  filter: brightness(0.75) saturate(0.72);
  isolation: isolate;
  border: 1px solid transparent;
}

.cat-pill:hover:not(.cat-active) {
  filter: brightness(0.94) saturate(0.9);
  width: 390px;
  height: 510px;
  border-color: var(--home-border-strong);
  box-shadow: var(--home-shadow-strong), inset 0 1px 0 rgba(255, 255, 255, 0.42);
}

.cat-pill.cat-active {
  width: 390px;
  height: 510px;
  filter: brightness(1) saturate(1.18);
  border-color: var(--home-border-strong);
  box-shadow: var(--home-shadow-strong), inset 0 1px 0 rgba(255, 255, 255, 0.42);
}

.cat-pill-glass {
  position: absolute;
  inset: 0;
  z-index: 2;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06) 0%, var(--home-surface) 100%);
  backdrop-filter: blur(2px);
  border-radius: inherit;
  border: 1px solid var(--home-border);
  pointer-events: none;
}

.cat-pill-shimmer {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.28) 0%, transparent 45%, rgba(255, 255, 255, 0.08) 100%);
  border-radius: inherit;
  transition: opacity 0.5s;
  opacity: 0.52;
}

.cat-pill.cat-active .cat-pill-shimmer { opacity: 1; }

.cat-pill-img {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.cat-pill-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}

.cat-pill.cat-active .cat-pill-img img { transform: scale(1.07); }

.cat-pill-grad {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(21, 15, 11, 0.7) 0%, transparent 76%);
}

.cat-pill-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 4;
  padding: 28px 24px;
  text-align: right;
}

.cat-num {
  font-size: 2.1rem;
  font-weight: 950;
  color: var(--home-accent);
  line-height: 1;
  display: block;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s 0.1s cubic-bezier(0.16, 1, 0.3, 1);
}

.cat-pill.cat-active .cat-num,
.cat-pill:hover .cat-num {
  opacity: 1;
  transform: translateY(0);
}

.cat-name {
  font-size: 1.48rem;
  font-weight: 950;
  color: #fff9f2;
  margin: 8px 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: font-size 0.5s;
}

.cat-pill:not(.cat-active) .cat-name {
  font-size: 0.92rem;
  writing-mode: vertical-rl;
  position: absolute;
  bottom: 24px;
  right: 50%;
  margin: 0;
  transform: rotate(180deg) translateX(50%);
  white-space: nowrap;
}

.cat-desc {
  font-size: 0.88rem;
  color: rgba(255, 248, 240, 0.84);
  margin: 0 0 18px;
  font-weight: 600;
  line-height: 1.65;
  opacity: 0;
  transform: translateY(15px);
  transition: all 0.5s 0.15s cubic-bezier(0.16, 1, 0.3, 1);
}

.cat-pill.cat-active .cat-desc,
.cat-pill:hover .cat-desc {
  opacity: 1;
  transform: translateY(0);
}

.cat-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--home-accent-soft);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(242, 201, 126, 0.5);
  color: #f7ddb2;
  font-weight: 900;
  font-size: 13px;
  padding: 9px 18px;
  border-radius: var(--home-pill);
  text-decoration: none;
  opacity: 0;
  transform: translateY(15px) scale(0.9);
  transition: all 0.5s 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.32);
}

.cat-pill.cat-active .cat-link,
.cat-pill:hover .cat-link {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.cat-link:hover { background: rgba(242, 201, 126, 0.3); }

.cat-orb {
  position: absolute;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  top: -60px;
  right: -60px;
  z-index: 1;
  pointer-events: none;
  filter: blur(50px);
  opacity: 0;
  transition: opacity 0.7s;
  animation: orbFloat 5s ease-in-out infinite;
}

.cat-pill.cat-active .cat-orb { opacity: 1; }

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, 30px); }
}

.cat-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 38px;
}

.cat-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--home-pill);
  background: var(--home-border);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.cat-dot.active {
  width: 34px;
  background: var(--home-accent);
}

/* QUALITY */
.quality-section {
  padding: var(--home-space-lg) 0 0;
}

.quality-content-box {
  max-width: 1120px;
  width: 100%;
  background: var(--home-surface-strong);
  backdrop-filter: blur(30px) saturate(170%);
  border-radius: 46px;
  padding: 74px 42px;
  text-align: center;
  border: 1px solid var(--home-border);
  box-shadow: var(--home-shadow);
}

.quality-icon {
  font-size: 40px;
  margin-bottom: 22px;
}

.quality-title {
  font-size: clamp(2rem, 4.2vw, 2.9rem);
  font-weight: 950;
  color: var(--home-text-main);
  margin-bottom: 48px;
}

.quality-grid {
  display: flex;
  justify-content: center;
  gap: 56px;
  flex-wrap: wrap;
  margin-bottom: 42px;
}

.q-item {
  display: grid;
  gap: 4px;
}

.q-val {
  font-size: 3.3rem;
  font-weight: 1000;
  color: var(--home-accent-strong);
  line-height: 1;
}

.q-label {
  font-size: 14px;
  font-weight: 800;
  color: var(--home-text-muted);
}

.quality-text {
  max-width: 820px;
  margin: 0 auto;
  font-size: 1.11rem;
  line-height: 1.95;
  color: var(--home-text-soft);
  font-weight: 600;
}

/* TRUST */
.trust-section {
  padding: var(--home-space-lg) 0 0;
}

.trust-section--care {
  padding-bottom: var(--home-space-xl);
}

.trust-head {
  margin-bottom: 36px;
}

.trust-grid {
  display: grid;
  gap: 20px;
}

.trust-grid--quick {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.trust-grid--care {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.liquid-glass-inner {
  position: relative;
  background: var(--home-surface);
  backdrop-filter: blur(16px) saturate(140%);
  border: 1px solid var(--home-border);
  border-radius: var(--home-radius-lg);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.liquid-glass-inner:hover {
  transform: translateY(-4px);
  box-shadow: var(--home-shadow);
  border-color: var(--home-border-strong);
}

.trust-card {
  text-align: center;
}

.trust-card--quick {
  padding: 32px 26px 26px;
}

.trust-card--detail {
  padding: 34px 26px 30px;
  text-align: right;
}

.trust-step {
  position: absolute;
  top: 14px;
  left: 14px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--home-accent-soft);
  border: 1px solid var(--home-border);
  color: var(--home-accent-strong);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.trust-icon {
  font-size: 31px;
  margin-bottom: 14px;
}

.trust-card h3 {
  font-size: 1.18rem;
  font-weight: 900;
  color: var(--home-text-main);
  margin: 0 0 10px;
}

.trust-card p {
  margin: 0;
  font-size: 0.93rem;
  color: var(--home-text-muted);
  font-weight: 650;
  line-height: 1.75;
}

.trust-meta {
  margin-top: 11px;
  color: var(--home-accent-strong);
  font-size: 0.81rem;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.trust-actions {
  margin-top: 22px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.trust-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 170px;
  padding: 11px 20px;
  border-radius: var(--home-pill);
  text-decoration: none;
  font-size: 13px;
  font-weight: 900;
  transition: all 0.25s ease;
}

.trust-btn--primary {
  background: var(--home-accent-strong);
  color: #fff8ee;
  border: 1px solid transparent;
}

.trust-btn--ghost {
  background: var(--home-surface-strong);
  color: var(--home-link-text);
  border: 1px solid var(--home-border);
}

.trust-btn:hover {
  transform: translateY(-2px);
}

/* ANIMATIONS */
.animate-scroll {
  opacity: 0;
  transform: translateY(42px);
  transition: 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-scroll.in-view {
  opacity: 1;
  transform: translateY(0);
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .home-page {
    --home-space-xl: 78px;
    --home-space-lg: 62px;
  }

  .cat-track {
    height: 510px;
  }

  .trust-grid--quick,
  .trust-grid--care {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .home-page {
    --home-inline-pad: 12px;
    --home-space-xl: 58px;
    --home-space-lg: 50px;
  }

  .section-head {
    margin-bottom: 36px;
  }

  .cat-track {
    height: auto;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .cat-pill {
    width: 100% !important;
    max-width: 420px;
    height: 180px !important;
  }

  .cat-pill.cat-active {
    height: 360px !important;
  }

  .cat-pill:not(.cat-active) .cat-name {
    writing-mode: initial;
    transform: none;
    position: absolute;
    bottom: 20px;
    right: 20px;
    font-size: 1.08rem;
  }

  .quality-content-box {
    border-radius: 30px;
    padding: 48px 24px;
  }

  .quality-grid {
    gap: 28px;
    margin-bottom: 32px;
  }

  .q-val {
    font-size: 2.6rem;
  }

  .trust-grid--quick,
  .trust-grid--care {
    grid-template-columns: 1fr;
  }

  .trust-card--detail {
    text-align: center;
  }

  .trust-step {
    left: 50%;
    transform: translateX(-50%);
    top: 10px;
  }

  .trust-card--detail .trust-icon {
    margin-top: 12px;
  }
}
</style>
