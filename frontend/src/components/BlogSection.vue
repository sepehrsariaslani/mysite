<template>
  <section class="blog-section" dir="rtl">
    <!-- Ambient background -->
    <div class="blog-ambient">
      <div class="ambient-orb orb-1"></div>
      <div class="ambient-orb orb-2"></div>
    </div>

    <div class="blog-inner">
      <!-- Header -->
      <div class="blog-header">
        <div class="blog-eyebrow">
          <span class="eyebrow-pill">مجله دن‌روم</span>
        </div>
        <h2 class="blog-title">
          آخرین <em>مطالب</em> ما
        </h2>
        <p class="blog-subtitle">
          از راهنمای چیدمان تا ترندهای روز دکوراسیون — همه چیز برای خانه‌ای رویایی
        </p>
      </div>

      <!-- Cards Grid -->
      <div class="blog-grid">

        <!-- Featured large card -->
        <div v-if="featuredPost" class="blog-card blog-card--featured" @mouseenter="hoveredIdx = 0" @mouseleave="hoveredIdx = null">
          <div class="bc-img-wrap">
            <img
              :src="featuredPost.meta_image || 'https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?auto=format&fit=crop&q=80&w=1400'"
              :alt="featuredPost.title"
              class="bc-img"
            />
            <div class="bc-img-overlay"></div>
          </div>

          <!-- Glass tag top -->
          <div class="bc-tag">
            <span class="tag-dot"></span>
            {{ getMetaValue(featuredPost, 'دسته بندی') }}
          </div>

          <!-- Bottom glass content panel -->
          <div class="bc-glass-panel">
            <div class="panel-shimmer"></div>
            <div class="bc-meta">
              <span class="bc-date">{{ featuredPost.published_on }}</span>
              <span class="bc-sep">·</span>
              <span class="bc-read">{{ getMetaValue(featuredPost, 'زمان مطالعه') }}</span>
            </div>
            <h3 class="bc-title">{{ featuredPost.title }}</h3>
            <p class="bc-excerpt">
              {{ featuredPost.meta_description }}
            </p>
            <a :href="'/blog?post=' + toParam(featuredPost.name)" class="bc-link">
              بخوانید
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M19 12H5M12 5l-7 7 7 7"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Small cards column -->
        <div class="blog-side-cards">
          <div
            v-for="(post, i) in sidePosts"
            :key="i"
            class="blog-card blog-card--small"
            @mouseenter="hoveredIdx = i + 1"
            @mouseleave="hoveredIdx = null"
          >
            <div class="bc-img-wrap">
              <img :src="post.image" :alt="post.title" class="bc-img" />
              <div class="bc-img-overlay"></div>
            </div>

            <div class="bc-tag bc-tag--sm">
              <span class="tag-dot"></span>
              {{ getMetaValue(post, 'دسته بندی') }}
            </div>

            <div class="bc-glass-panel bc-glass-panel--sm">
              <div class="panel-shimmer"></div>
              <div class="bc-meta">
                <span class="bc-date">{{ post.published_on }}</span>
                <span class="bc-sep">·</span>
                <span class="bc-read">{{ getMetaValue(post, 'زمان مطالعه') }}</span>
              </div>
              <h3 class="bc-title bc-title--sm">{{ post.title }}</h3>
              <a :href="'/blog?post=' + toParam(post.name)" class="bc-link bc-link--sm">
                بخوانید
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M19 12H5M12 5l-7 7 7 7"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

      </div>

      <!-- Bottom CTA -->
      <div class="blog-footer">
        <a href="/blog" class="blog-all-btn">
          <span>مشاهده همه مطالب</span>
          <div class="btn-arrow-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M19 12H5M12 5l-7 7 7 7"/>
            </svg>
          </div>
        </a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const hoveredIdx = ref(null)
const featuredPost = ref(null)
const sidePosts = ref([])

onMounted(async () => {
  try {
    const res = await fetch('/api/method/mysite.api.get_blog_posts')
    const data = await res.json()
    const posts = data.message || []
    if (posts.length > 0) {
      featuredPost.value = posts[0]
      sidePosts.value = posts.slice(1, 3)
    }
  } catch (err) {
    console.error('Failed to fetch blog posts:', err)
  }
})

function getMetaValue(post, label) {
  // Simple helper to parse meta or use standard fields
  if (label === 'زمان مطالعه') return post.custom_read_time || '۵ دقیقه'
  if (label === 'دسته بندی') return post.blog_category || 'مجله'
  return ''
}

function toParam(value) {
  return encodeURIComponent(String(value || ''))
}
</script>

<style scoped>
/* ══════ SECTION BASE ══════ */
.blog-section {
  position: relative;
  padding: 120px 24px;
  background: transparent;
  overflow: hidden;
  font-family: 'Peyda', sans-serif;
  --blog-surface: var(--home-surface-strong, rgba(255, 255, 255, 0.78));
  --blog-surface-soft: var(--home-surface, rgba(255, 255, 255, 0.6));
  --blog-border: var(--home-border, rgba(120, 85, 57, 0.2));
  --blog-border-strong: var(--home-border-strong, rgba(120, 85, 57, 0.32));
  --blog-text-main: var(--home-text-main, var(--text-main));
  --blog-text-muted: var(--home-text-muted, var(--text-muted));
  --blog-text-soft: var(--home-text-soft, var(--text-dim));
  --blog-accent: var(--home-accent, var(--accent-gold));
  --blog-accent-strong: var(--home-accent-strong, var(--accent-brown));
  --blog-shadow: var(--home-shadow, 0 20px 52px rgba(71, 45, 27, 0.12));
}

/* Ambient blobs */
.blog-ambient { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.ambient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, color-mix(in srgb, var(--blog-accent) 45%, transparent) 0%, transparent 70%);
  top: -100px; left: -150px;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, color-mix(in srgb, var(--blog-accent-strong) 20%, transparent) 0%, transparent 70%);
  bottom: -80px; right: -100px;
}

.blog-inner {
  max-width: 1280px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* ══════ HEADER ══════ */
.blog-header {
  text-align: center;
  margin-bottom: 64px;
}

.blog-eyebrow {
  margin-bottom: 20px;
}

.eyebrow-pill {
  display: inline-block;
  background: var(--blog-surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--blog-border);
  color: var(--blog-accent-strong);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.15em;
  padding: 7px 18px;
  border-radius: 100px;
}

.blog-title {
  font-size: clamp(2.4rem, 5vw, 3.6rem);
  font-weight: 950;
  color: var(--blog-text-main);
  margin: 0 0 16px;
  line-height: 1.15;
}

.blog-title em {
  font-style: normal;
  color: var(--blog-accent-strong);
  position: relative;
}

.blog-title em::after {
  content: '';
  position: absolute;
  bottom: 2px;
  right: 0; left: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--blog-accent), color-mix(in srgb, var(--blog-accent-strong) 80%, #fff 20%));
  border-radius: 3px;
}

.blog-subtitle {
  font-size: 1rem;
  color: var(--blog-text-muted);
  font-weight: 600;
  margin: 0;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ══════ GRID ══════ */
.blog-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 20px;
  margin-bottom: 48px;
}

/* ══════ CARD BASE ══════ */
.blog-card {
  position: relative;
  border-radius: 32px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.5s;
}

.blog-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--blog-shadow);
}

.blog-card--featured { min-height: 580px; }

.bc-img-wrap {
  position: absolute;
  inset: 0;
}

.bc-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.blog-card:hover .bc-img { transform: scale(1.06); }

.bc-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    var(--bg-footer) 0%,
    transparent 100%
  );
}

/* ══════ TAG (Liquid glass pill) ══════ */
.bc-tag {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 4;
  display: flex;
  align-items: center;
  gap: 7px;
  background: color-mix(in srgb, var(--blog-surface) 85%, transparent);
  backdrop-filter: blur(16px) saturate(1.8);
  border: 1px solid var(--blog-border-strong);
  border-radius: 100px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 800;
  color: #fff8ef;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.35),
    0 4px 12px rgba(0,0,0,0.15);
}

.bc-tag--sm {
  top: 14px; right: 14px;
  font-size: 11px;
  padding: 5px 12px;
}

.tag-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--blog-accent);
  flex-shrink: 0;
  animation: dot-pulse 2.5s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.65); }
}

/* ══════ GLASS PANEL (bottom content) ══════ */
.bc-glass-panel {
  position: absolute;
  bottom: 0; right: 0; left: 0;
  z-index: 3;
  padding: 28px 28px 28px;

  /* LIQUID GLASS */
  background: var(--blog-surface-soft);
  backdrop-filter: blur(28px) saturate(1.6);
  border-top: 1px solid var(--blog-border);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.08),
    inset 0 -1px 0 rgba(0,0,0,0.2);
  transition: background 0.4s;
}

.blog-card:hover .bc-glass-panel {
  background: var(--blog-surface);
}

.bc-glass-panel--sm {
  padding: 20px 20px 20px;
}

/* Shimmer reflection */
.panel-shimmer {
  position: absolute;
  top: 0; right: 0; left: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255,255,255,0.25) 30%,
    rgba(255,255,255,0.35) 50%,
    rgba(255,255,255,0.25) 70%,
    transparent 100%
  );
}

.bc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.bc-date, .bc-read {
  font-size: 11px;
  font-weight: 700;
  color: var(--blog-text-soft);
}

.bc-sep { color: rgba(255,255,255,0.25); }

.bc-title {
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--blog-text-main);
  margin: 0 0 12px;
  line-height: 1.4;
}

.bc-title--sm {
  font-size: 1rem;
  margin-bottom: 16px;
}

.bc-excerpt {
  font-size: 0.9rem;
  color: var(--blog-text-muted);
  font-weight: 600;
  line-height: 1.6;
  margin: 0 0 20px;
}

.bc-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--blog-accent-strong);
  text-decoration: none;
  font-size: 13px;
  font-weight: 900;
  background: var(--blog-surface);
  border: 1px solid var(--blog-border);
  padding: 8px 16px;
  border-radius: 100px;
  transition: all 0.3s;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.1);
}

.bc-link svg {
  width: 14px; height: 14px;
  transition: transform 0.3s;
}

.bc-link:hover {
  background: var(--blog-surface-soft);
  transform: translateX(-3px);
}

.bc-link:hover svg { transform: translateX(-4px); }

.bc-link--sm {
  padding: 6px 14px;
  font-size: 12px;
}

/* ══════ SIDE CARDS ══════ */
.blog-side-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.blog-card--small {
  flex: 1;
  min-height: 260px;
}

/* ══════ FOOTER CTA ══════ */
.blog-footer {
  display: flex;
  justify-content: center;
}

.blog-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  background: var(--blog-surface);
  backdrop-filter: blur(20px) saturate(1.5);
  border: 1px solid var(--blog-border);
  color: var(--blog-text-main);
  text-decoration: none;
  font-size: 15px;
  font-weight: 900;
  padding: 16px 28px 16px 20px;
  border-radius: 100px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow:
    0 4px 20px rgba(0,0,0,0.06),
    inset 0 1px 0 rgba(255,255,255,0.1);
}

.blog-all-btn:hover {
  background: var(--blog-accent-strong);
  color: #fff8ef;
  border-color: var(--blog-accent-strong);
  transform: translateY(-3px);
  box-shadow: var(--blog-shadow);
}

.btn-arrow-wrap {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--blog-accent-strong) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s;
}

.btn-arrow-wrap svg {
  width: 16px; height: 16px;
  transition: transform 0.3s;
}

.blog-all-btn:hover .btn-arrow-wrap {
  background: color-mix(in srgb, var(--blog-accent) 28%, transparent);
}

.blog-all-btn:hover .btn-arrow-wrap svg {
  transform: translateX(-4px);
}

/* ══════ RESPONSIVE ══════ */
@media (max-width: 900px) {
  .blog-grid { grid-template-columns: 1fr; }
  .blog-card--featured { min-height: 420px; }
  .blog-card--small { min-height: 220px; }
}
</style>
