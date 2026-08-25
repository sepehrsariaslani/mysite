<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>نام محصول</th>
          <th>کد</th>
          <th>گروه</th>
          <th>وضعیت</th>
          <th>تصاویر</th>
          <th>قیمت</th>
          <th>اقدام</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in items"
          :key="item.item_code"
          :class="{ active: selectedCode === item.item_code }"
          @click="emit('select', item.item_code)"
        >
          <td class="name-cell">
            <span class="name">{{ item.item_name || item.item_code }}</span>
          </td>
          <td class="mono">{{ item.item_code }}</td>
          <td>{{ item.item_group || 'بدون گروه' }}</td>
          <td>
            <span class="status" :class="item.status_key">{{ item.status_label }}</span>
          </td>
          <td>{{ fa(item.images_count) }}</td>
          <td>
            <strong v-if="item.default_price_toman" class="price">{{ fa(item.default_price_toman) }} تومان</strong>
            <span v-else class="muted">بدون قیمت</span>
          </td>
          <td>
            <button class="open-btn" type="button" @click.stop="emit('select', item.item_code)">انتخاب</button>
          </td>
        </tr>
      </tbody>
    </table>
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
.table-wrap {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-chip-bg);
  overflow: auto;
}

table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--admin-border);
  padding: 9px 10px;
  text-align: right;
  font-size: 12px;
  white-space: nowrap;
}

thead th {
  position: sticky;
  top: 0;
  background: var(--admin-panel-bg);
  color: var(--admin-text-soft);
  z-index: 1;
}

tbody tr {
  cursor: pointer;
}

tbody tr:hover td {
  background: rgba(255, 255, 255, 0.03);
}

tbody tr.active td {
  background: color-mix(in srgb, var(--accent-gold) 14%, transparent);
}

tbody tr:last-child td {
  border-bottom: none;
}

.name-cell {
  max-width: 220px;
}

.name {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mono {
  direction: ltr;
  text-align: left;
  font-family: ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
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

.price {
  color: var(--accent-gold);
}

.muted {
  color: var(--admin-text-soft);
}

.open-btn {
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  min-height: 30px;
  padding: 0 8px;
  font-family: inherit;
  font-size: 11px;
  cursor: pointer;
}

.open-btn:hover {
  border-color: var(--admin-tab-active-start);
}
</style>
