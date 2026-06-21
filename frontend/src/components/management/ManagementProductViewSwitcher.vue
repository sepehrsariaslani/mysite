<template>
  <div class="switch-wrap" role="tablist" aria-label="حالت نمایش محصولات">
    <button
      v-for="mode in modes"
      :key="mode.key"
      type="button"
      class="mode-btn"
      :class="{ active: modelValue === mode.key }"
      :aria-selected="modelValue === mode.key ? 'true' : 'false'"
      @click="emit('update:modelValue', mode.key)"
    >
      <component :is="mode.icon" :size="14" class="icon" aria-hidden="true" />
      <span class="label">{{ mode.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { Grid3X3, List, Table } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'grid',
  },
})

const emit = defineEmits(['update:modelValue'])

const modes = [
  { key: 'grid', label: 'کارتی', icon: Grid3X3 },
  { key: 'list', label: 'لیستی', icon: List },
  { key: 'table', label: 'جدولی', icon: Table },
]
</script>

<style scoped>
.switch-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--admin-border);
  border-radius: 11px;
  background: var(--admin-input-bg);
  padding: 4px;
}

.mode-btn {
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--admin-text-soft);
  min-height: 32px;
  padding: 0 10px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn:hover {
  color: var(--text-main);
}

.mode-btn.active {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
}

.icon {
  font-size: 11px;
}

@media (max-width: 1020px) {
  .switch-wrap {
    width: 100%;
    justify-content: space-between;
  }

  .mode-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
