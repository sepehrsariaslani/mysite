<template>
  <div class="product-hero-container">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-content">
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
        <div class="hero-stats">
          <div v-for="(stat, index) in stats" :key="index" class="stat">
            <span class="stat-num">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CATEGORY BAR -->
    <CategoryBar :categories="categories" />
  </div>
</template>

<script setup>
import CategoryBar from './CategoryBar.vue'

defineProps({
  title: String,
  description: String,
  stats: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.product-hero-container {
  position: relative;
  z-index: 10;
}

/* ── Hero ── */
.hero {
  padding: 120px 24px 60px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  background: var(--glass-bg);
  backdrop-filter: blur(40px);
  padding: 60px 40px;
  border-radius: 40px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 40px 100px rgba(0,0,0,0.5);
}

.hero h1 { 
  font-size: 3.5rem; 
  font-weight: 1000; 
  color: var(--text-main); 
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.hero p { 
  font-size: 1.1rem; 
  color: var(--text-muted); 
  font-weight: 500; 
  margin-bottom: 40px; 
  line-height: 1.6;
}

.hero-stats { 
  display: flex; 
  justify-content: center; 
  gap: 40px; 
}

.stat { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 4px; 
}

.stat-num { 
  font-size: 2.2rem; 
  font-weight: 900; 
  color: var(--accent-orange); 
  line-height: 1; 
}

.stat-label { 
  font-size: 11px; 
  color: var(--text-dim); 
  text-transform: uppercase; 
  font-weight: 700; 
  letter-spacing: 0.05em;
}

@media (max-width: 768px) {
  .hero { padding: 80px 20px 40px; }
  .hero-content { padding: 40px 24px; border-radius: 30px; }
  .hero h1 { font-size: 2.25rem; }
  .hero p { font-size: 1rem; margin-bottom: 30px; }
  .hero-stats { gap: 24px; flex-wrap: wrap; }
  .stat-num { font-size: 1.75rem; }
}
</style>
