<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb" dir="rtl">
    <ol class="breadcrumb-list">
      <li class="breadcrumb-item">
        <a href="/mysite" class="breadcrumb-link home-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
        </a>
      </li>
      <li v-for="(crumb, index) in crumbs" :key="index" class="breadcrumb-item">
        <span class="separator">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </span>
        <a v-if="crumb.route" :href="crumb.route" class="breadcrumb-link">{{ crumb.label }}</a>
        <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  crumbs: {
    type: Array,
    required: true,
    // Example: [{ label: 'مبلمان', route: '/mysite/sofas' }, { label: 'اورامان' }]
  }
})
</script>

<style scoped>
.breadcrumbs {
  padding: 1rem 0;
  margin-bottom: 0.5rem;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.breadcrumb-link {
  text-decoration: none;
  color: #888;
  font-size: 0.85rem;
  font-weight: 600;
  transition: color 0.2s, transform 0.2s;
}

.breadcrumb-link:hover {
  color: #503130;
  transform: translateY(-1px);
}

.home-link {
  display: flex;
  align-items: center;
}

.breadcrumb-current {
  color: #1a1a1a;
  font-size: 0.85rem;
  font-weight: 800;
}

.separator {
  color: #ccc;
  display: flex;
  align-items: center;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .breadcrumb-link, .breadcrumb-current {
    font-size: 0.75rem;
  }
}
</style>
