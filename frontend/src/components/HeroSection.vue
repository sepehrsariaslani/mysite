<template>
  <section class="hero-section" dir="rtl">

    <!-- ── Fullscreen Product Image ── -->
    <div class="hero-bg">
      <img
        src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=2400"
        alt="DenRoom Sofa"
        class="hero-bg-img"
      />
      <div class="hero-overlay-dark"></div>
      <div class="hero-overlay-gradient"></div>
    </div>

    <!-- ── Particles ── -->
    <div class="particles">
      <div class="particle" v-for="n in 5" :key="n" :style="getParticleStyle(n)"></div>
    </div>

    <!-- ── Bottom content row ── -->
    <div class="hero-bottom" :class="{ 'bottom-visible': panelVisible }">

      <!-- LEFT: Text -->
      <div class="hero-text-block">
        <div class="hero-badge" :class="{ 'badge-in': badgeVisible }">
          <span class="badge-dot"></span>
          کالکشن ۱۴۰۴
        </div>

        <h1 class="hero-title" :class="{ 'title-in': titleVisible }">
          <span>فضایی که</span>
          <span class="typed-line">
            <em class="typed-word">{{ displayedText }}</em>
            <span class="cursor">|</span>
          </span>
          <span>می‌آفریند</span>
        </h1>

        <p class="hero-desc" :class="{ 'desc-in': descVisible }">
          ترکیبی از هنر اصیل ایرانی و طراحی مدرن میان‌قرنی — خانه‌ای
          فراتر از چهاردیواری برای شما خلق می‌کنیم.
        </p>

        <div class="hero-actions" :class="{ 'actions-in': actionsVisible }">
          <a href="/categories" class="btn-primary">بررسی کالکشن‌ها</a>
          <a href="/consultation" class="btn-ghost">مشاوره رایگان</a>
        </div>
      </div>

      <!-- RIGHT: Product glass card -->
      <a href="/sofas" class="product-card" :class="{ 'card-in': cardVisible }">
        <div class="card-shimmer"></div>

        <div class="card-thumb">
          <img
            src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=400"
            alt="مبل راحتی"
            class="card-thumb-img"
          />
          <div class="card-thumb-overlay">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          </div>
        </div>

        <div class="card-info">
          <p class="card-text">مبل‌های دن‌روم با متریال درجه یک، آرامش واقعی را به خانه شما می‌آورند.</p>
          <span class="card-link">
            مشاهده محصول
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M19 12H5M12 5l-7 7 7 7"/>
            </svg>
          </span>
        </div>
      </a>
    </div>

    <!-- ── Scroll indicator ── -->
    <div class="scroll-hint" :class="{ 'hint-visible': actionsVisible }">
      <div class="scroll-track"><div class="scroll-thumb"></div></div>
    </div>

  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const panelVisible   = ref(false)
const badgeVisible   = ref(false)
const titleVisible   = ref(false)
const descVisible    = ref(false)
const actionsVisible = ref(false)
const cardVisible    = ref(false)

// Typing
const words = ['آرامش', 'زیبایی', 'سبک زندگی', 'الهام']
const displayedText = ref('')
let wordIdx = 0, charIdx = 0, isDeleting = false, timer = null

function typeEffect() {
  const cur = words[wordIdx]
  if (!isDeleting) {
    displayedText.value = cur.slice(0, ++charIdx)
    if (charIdx === cur.length) {
      timer = setTimeout(() => { isDeleting = true; typeEffect() }, 2000)
      return
    }
  } else {
    displayedText.value = cur.slice(0, --charIdx)
    if (charIdx === 0) { isDeleting = false; wordIdx = (wordIdx + 1) % words.length }
  }
  timer = setTimeout(typeEffect, isDeleting ? 55 : 95)
}

function getParticleStyle(n) {
  const p = [
    { top:'20%', right:'8%',  w:'5px', delay:'0s',   dur:'8s'  },
    { top:'50%', left:'6%',   w:'3px', delay:'1.2s', dur:'10s' },
    { top:'30%', right:'20%', w:'7px', delay:'0.5s', dur:'7s'  },
    { top:'70%', left:'15%',  w:'4px', delay:'2s',   dur:'9s'  },
    { top:'15%', left:'30%',  w:'3px', delay:'3s',   dur:'11s' },
  ][n-1]
  return { top:p.top, right:p.right, left:p.left, width:p.w, height:p.w, animationDelay:p.delay, animationDuration:p.dur }
}

onMounted(() => {
  setTimeout(() => panelVisible.value   = true, 200)
  setTimeout(() => badgeVisible.value   = true, 400)
  setTimeout(() => titleVisible.value   = true, 550)
  setTimeout(() => descVisible.value    = true, 750)
  setTimeout(() => actionsVisible.value = true, 950)
  setTimeout(() => cardVisible.value    = true, 700)
  setTimeout(() => typeEffect(),                600)
})
onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.hero-section {
  position: relative;
  width: 100%;
  min-height: 680px;
  height: 96vh;
  overflow: hidden;
  font-family: 'Peyda', sans-serif;
  display: flex;
  align-items: flex-end;
}

/* BG */
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 40%;
  animation: slow-zoom 18s ease-in-out infinite alternate;
}

@keyframes slow-zoom {
  from { transform: scale(1); }
  to { transform: scale(1.06); }
}

.hero-overlay-dark {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(248, 240, 230, 0.18) 0%, rgba(248, 240, 230, 0.26) 100%);
}

.hero-overlay-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(247, 238, 227, 0.92) 0%,
    rgba(247, 238, 227, 0.72) 28%,
    rgba(247, 238, 227, 0.3) 58%,
    rgba(247, 238, 227, 0.08) 100%
  );
}

/* PARTICLES */
.particles {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(123, 79, 52, 0.34);
  filter: blur(1px);
  animation: p-drift linear infinite;
}

@keyframes p-drift {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.4; }
  50% { transform: translateY(-28px) scale(1.3); opacity: 0.9; }
}

/* BOTTOM ROW */
.hero-bottom {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: var(--home-shell-max, 1320px);
  margin: 0 auto;
  padding: 0 var(--home-inline-pad, 24px) 58px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 36px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-bottom.bottom-visible {
  opacity: 1;
  transform: translateY(0);
}

/* TEXT BLOCK */
.hero-text-block {
  flex: 1;
  max-width: 620px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--home-surface-strong, rgba(255, 255, 255, 0.76));
  backdrop-filter: blur(12px);
  border: 1px solid var(--home-border, rgba(120, 85, 57, 0.2));
  color: var(--home-accent-strong, #7b4f34);
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
  margin-bottom: 22px;
  opacity: 0;
  transform: translateY(12px);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-badge.badge-in {
  opacity: 1;
  transform: translateY(0);
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--home-accent, #c9914f);
  animation: bdot 2s ease-in-out infinite;
}

@keyframes bdot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.7); }
}

.hero-title {
  font-size: clamp(3rem, 6.5vw, 5.3rem);
  font-weight: 950;
  color: var(--home-text-main, #2f2118);
  line-height: 1.15;
  margin: 0 0 22px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.1s;
  text-shadow: 0 10px 30px rgba(248, 240, 229, 0.4);
}

.hero-title.title-in {
  opacity: 1;
  transform: translateY(0);
}

.typed-line {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--home-accent-strong, #7b4f34);
  text-shadow: 0 0 30px rgba(123, 79, 52, 0.2);
  min-height: 1.2em;
}

.typed-word {
  font-style: normal;
}

.cursor {
  font-weight: 200;
  color: var(--home-accent-strong, #7b4f34);
  animation: cur 0.85s steps(1) infinite;
}

@keyframes cur {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.9;
  color: var(--home-text-muted, rgba(50, 33, 23, 0.68));
  font-weight: 650;
  margin: 0 0 32px;
  max-width: 520px;
  opacity: 0;
  transform: translateY(14px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s;
}

.hero-desc.desc-in {
  opacity: 1;
  transform: translateY(0);
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(14px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
}

.hero-actions.actions-in {
  opacity: 1;
  transform: translateY(0);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--home-accent-strong, #7b4f34);
  color: #fff8ee;
  text-decoration: none;
  font-weight: 900;
  font-size: 15px;
  padding: 15px 30px;
  border-radius: 14px;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 10px 30px rgba(80, 49, 30, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.24);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 45px rgba(80, 49, 30, 0.32);
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  background: var(--home-surface-strong, rgba(255, 255, 255, 0.76));
  backdrop-filter: blur(12px);
  border: 1px solid var(--home-border, rgba(120, 85, 57, 0.2));
  color: var(--home-link-text, #3a2618);
  text-decoration: none;
  font-weight: 800;
  font-size: 15px;
  padding: 15px 30px;
  border-radius: 14px;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22);
}

.btn-ghost:hover {
  background: var(--home-surface, rgba(255, 255, 255, 0.62));
  transform: translateY(-3px);
  border-color: var(--home-border-strong, rgba(120, 85, 57, 0.32));
}

/* PRODUCT CARD */
.product-card {
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  flex-shrink: 0;
  width: 400px;
  position: relative;
  cursor: pointer;
  background: var(--home-surface-strong, rgba(255, 255, 255, 0.78));
  backdrop-filter: blur(24px) saturate(1.6);
  -webkit-backdrop-filter: blur(24px) saturate(1.6);
  border: 1px solid var(--home-border, rgba(120, 85, 57, 0.2));
  border-radius: 24px;
  padding: 18px;
  box-shadow: var(--home-shadow, 0 20px 52px rgba(71, 45, 27, 0.12)), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  opacity: 0;
  transform: translateY(24px) scale(0.96);
  transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.3s;
}

.product-card.card-in {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.product-card:hover {
  background: var(--home-surface, rgba(255, 255, 255, 0.6));
  transform: translateY(-5px) scale(1.01);
  box-shadow: var(--home-shadow-strong, 0 30px 72px rgba(71, 45, 27, 0.18));
  border-color: var(--home-border-strong, rgba(120, 85, 57, 0.32));
}

.card-shimmer {
  position: absolute;
  top: 0;
  right: 20px;
  left: 20px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.46), rgba(201, 145, 79, 0.5), rgba(255, 255, 255, 0.46), transparent);
  border-radius: 1px;
  pointer-events: none;
}

.card-thumb {
  position: relative;
  width: 110px;
  height: 88px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(58, 37, 24, 0.25);
}

.card-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.product-card:hover .card-thumb-img {
  transform: scale(1.08);
}

.card-thumb-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(36, 24, 16, 0.28);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .card-thumb-overlay {
  opacity: 1;
}

.card-thumb-overlay svg {
  width: 28px;
  height: 28px;
  color: #fff9f1;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-text {
  font-size: 13px;
  font-weight: 620;
  color: var(--home-text-muted, rgba(50, 33, 23, 0.68));
  line-height: 1.65;
  margin: 0;
}

.card-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 900;
  color: var(--home-accent-strong, #7b4f34);
  transition: gap 0.3s;
}

.card-link svg {
  width: 14px;
  height: 14px;
  transition: transform 0.3s;
}

.product-card:hover .card-link {
  gap: 10px;
}

.product-card:hover .card-link svg {
  transform: translateX(-4px);
}

/* SCROLL */
.scroll-hint {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  opacity: 0;
  transition: opacity 1s 0.5s;
}

.scroll-hint.hint-visible {
  opacity: 1;
}

.scroll-track {
  width: 2px;
  height: 44px;
  background: rgba(86, 57, 38, 0.2);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.scroll-thumb {
  position: absolute;
  top: -40%;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to bottom, var(--home-accent, #c9914f), transparent);
  border-radius: 2px;
  animation: scroll-anim 2s ease-in-out infinite;
}

@keyframes scroll-anim {
  0% { top: -40%; opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

/* DARK TUNE */
[data-theme='dark'] .hero-overlay-dark {
  background: rgba(4, 3, 2, 0.42);
}

[data-theme='dark'] .hero-overlay-gradient {
  background: linear-gradient(
    to top,
    rgba(10, 7, 5, 0.94) 0%,
    rgba(10, 7, 5, 0.68) 30%,
    rgba(10, 7, 5, 0.28) 58%,
    transparent 100%
  );
}

[data-theme='dark'] .particle {
  background: rgba(242, 201, 126, 0.5);
}

[data-theme='dark'] .hero-title {
  text-shadow: 0 12px 34px rgba(0, 0, 0, 0.34);
}

[data-theme='dark'] .btn-primary {
  color: #2a1608;
  background: #f2c97e;
  box-shadow: 0 10px 30px rgba(242, 201, 126, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

[data-theme='dark'] .btn-ghost {
  color: #fff8ee;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .hero-section {
    height: 88vh;
  }

  .hero-bottom {
    flex-direction: column;
    align-items: flex-start;
    padding: 0 var(--home-inline-pad, 24px) 44px;
    gap: 24px;
  }

  .product-card {
    width: 100%;
  }

  .hero-title {
    font-size: 2.8rem;
  }
}

@media (max-width: 600px) {
  .hero-section {
    min-height: 620px;
  }

  .hero-title {
    font-size: 2.15rem;
  }

  .btn-primary,
  .btn-ghost {
    padding: 13px 22px;
    font-size: 14px;
  }

  .scroll-hint {
    bottom: 18px;
  }
}
</style>
