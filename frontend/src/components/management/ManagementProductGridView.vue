<template>
  <div class="cards-grid">
    <article
      v-for="item in items"
      :key="item.item_code"
      class="product-card"
      :class="{ active: selectedCode === item.item_code }"
      @click="emit('select', item.item_code)"
    >
      <div class="thumb">
        <img v-if="item.image" :src="item.image" :alt="item.item_name || item.item_code" />
        <div v-else class="thumb-placeholder">بدون تصویر</div>
      </div>

      <h3>{{ item.item_name || item.item_code }}</h3>
      <p class="code">{{ item.item_code }}</p>
      <p class="group">{{ item.item_group || 'بدون گروه' }}</p>

      <div class="meta-row">
        <span class="status" :class="item.status_key">{{ item.status_label }}</span>
        <small>{{ fa(item.images_count) }} تصویر</small>
      </div>
      <p class="price-chip" v-if="item.default_price_toman">{{ fa(item.default_price_toman) }} تومان</p>
    </article>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  selectedCode: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['select'])

const fa = (value) => Number(value || 0).toLocaleString('fa-IR')
</script>

<style scoped>
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
}

.product-card {
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-chip-bg);
  padding: 10px;
  display: grid;
  gap: 6px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.product-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.thumb {
  height: 106px;
  border-radius: 10px;
  border: 1px solid var(--admin-border);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  color: var(--admin-text-soft);
  font-size: 12px;
}

h3 {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.5;
}

.code,
.group {
  margin: 0;
  font-size: 11px;
  color: var(--admin-text-soft);
}

.code {
  direction: ltr;
  text-align: left;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-row small {
  color: var(--admin-text-soft);
  font-size: 11px;
}

.price-chip {
  margin: 0;
  font-size: 12px;
  color: var(--accent-gold);
  font-weight: 700;
}

.status {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--admin-border);
}

.status.active {
  color: #bbf7d0;
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.12);
}

.status.hidden {
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.12);
}

.status.disabled {
  color: #fecaca;
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
}
</style>
