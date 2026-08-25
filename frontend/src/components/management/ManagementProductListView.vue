<template>
  <div class="list-stack">
    <article
      v-for="item in items"
      :key="item.item_code"
      class="list-row"
      :class="{ active: selectedCode === item.item_code }"
      @click="emit('select', item.item_code)"
    >
      <div class="thumb">
        <img v-if="item.image" :src="item.image" :alt="item.item_name || item.item_code" />
        <div v-else class="thumb-placeholder">بدون تصویر</div>
      </div>

      <div class="main">
        <h3>{{ item.item_name || item.item_code }}</h3>
        <p class="code">{{ item.item_code }}</p>
        <p class="group">{{ item.item_group || 'بدون گروه' }}</p>
      </div>

      <div class="meta">
        <span class="status" :class="item.status_key">{{ item.status_label }}</span>
        <small>{{ fa(item.images_count) }} تصویر</small>
        <strong v-if="item.default_price_toman">{{ fa(item.default_price_toman) }} تومان</strong>
        <strong v-else>بدون قیمت</strong>
      </div>
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
.list-stack {
  display: grid;
  gap: 8px;
}

.list-row {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-chip-bg);
  padding: 8px;
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  cursor: pointer;
}

.list-row.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.thumb {
  height: 70px;
  border-radius: 8px;
  border: 1px solid var(--admin-border);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  color: var(--admin-text-soft);
  font-size: 10px;
}

.main {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.main h3 {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.code,
.group {
  margin: 0;
  font-size: 11px;
  color: var(--admin-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.code {
  direction: ltr;
  text-align: left;
}

.meta {
  display: grid;
  justify-items: end;
  gap: 4px;
}

.meta small {
  color: var(--admin-text-soft);
  font-size: 11px;
}

.meta strong {
  font-size: 12px;
  color: var(--accent-gold);
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

@media (max-width: 760px) {
  .list-row {
    grid-template-columns: 70px minmax(0, 1fr);
  }

  .meta {
    grid-column: 1 / -1;
    justify-items: start;
    grid-auto-flow: column;
    align-items: center;
    gap: 8px;
    padding-top: 4px;
    border-top: 1px dashed var(--admin-border);
  }
}
</style>
