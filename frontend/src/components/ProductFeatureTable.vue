<template>
  <section v-if="normalizedRows.length" class="feature-section">
    <h3 class="feature-title">{{ title }}</h3>
    <div class="feature-table">
      <div
        v-for="(row, index) in normalizedRows"
        :key="`${row.label}-${index}`"
        class="feature-row"
      >
        <span class="label">{{ row.label }}</span>
        <span class="value">{{ row.value }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
    default: 'ویژگی‌ها',
  },
})

const normalizedRows = computed(() => {
  if (!Array.isArray(props.rows)) return []
  return props.rows
    .map((row) => ({
      label: String(row?.label || row?.name || '').trim(),
      value: String(row?.value || row?.content || '').trim(),
    }))
    .filter((row) => row.label || row.value)
})
</script>

<style scoped>
.feature-section {
  margin-top: 14px;
}

.feature-title {
  margin: 0 0 10px;
  font-size: 0.98rem;
}

.feature-table {
  border: 1px dashed #d9d2c8;
  border-radius: 14px;
  overflow: hidden;
}

.feature-row {
  display: grid;
  grid-template-columns: minmax(120px, 0.5fr) minmax(0, 1fr);
  gap: 10px;
  padding: 11px 12px;
  border-bottom: 1px dashed #e5ddd0;
  background: rgba(255, 255, 255, 0.42);
}

.feature-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 700;
  color: #6f6356;
}

.value {
  color: var(--text-main);
}

@media (max-width: 640px) {
  .feature-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
