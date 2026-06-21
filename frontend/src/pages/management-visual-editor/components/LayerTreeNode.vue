<template>
  <div
    class="fig-layer-row"
    :class="{
      'fig-layer-row-hidden': Boolean(layer.hidden),
      'fig-layer-row-locked': Boolean(layer.locked),
    }"
    :data-layer-id="layer.id"
    draggable="true"
    :style="{ '--depth': String(Math.min(Number(layer.depth || 0), 12)) }"
    :ref="(el) => setLayerRowRef(layer.id, el)"
    @dragstart="onDragStart"
    @dragover.prevent
    @drop.prevent="onDrop"
    @contextmenu.prevent="onContextMenu"
  >
    <button
      v-if="Number(layer.child_count || 0) > 0"
      class="fig-layer-toggle"
      type="button"
      @click="$emit('toggle', layer.id)"
    >
      <svg v-if="isExpanded(layer.id)" width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"/></svg>
      <svg v-else width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M10 7l5 5-5 5z"/></svg>
    </button>
    <span v-else class="fig-layer-leaf">
      <svg width="6" height="6" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg>
    </span>
    <button
      class="fig-layer-item"
      type="button"
      :class="{
        'fig-layer-item-active': selectedId === layer.id,
        'fig-layer-item-secondary': selectedId !== layer.id && selectedIds.includes(layer.id),
        'fig-layer-item-is-hidden': Boolean(layer.hidden),
        'fig-layer-item-is-locked': Boolean(layer.locked),
      }"
      @click="onSelect"
      @dblclick="emit('start-rename', String(layer.id || ''))"
    >
      <span class="fig-layer-type-icon" :title="layerTypeTitle" aria-hidden="true">
        <svg v-if="layerType === 'frame'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="4" width="16" height="16" rx="1.8"/></svg>
        <svg v-else-if="layerType === 'text'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h16"/><path d="M12 6v12"/></svg>
        <svg v-else-if="layerType === 'image'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="5" width="17" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="M20 16l-5-5-4 4-2-2-4 4"/></svg>
        <svg v-else-if="layerType === 'component'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3l5 5-5 5-5-5z"/><path d="M7 12l5 5 5-5"/></svg>
        <svg v-else-if="layerType === 'instance'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2l5.5 5.5L12 13 6.5 7.5z"/><path d="M12 13l5.5 5.5L12 24 6.5 18.5z"/></svg>
        <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="7"/></svg>
      </span>
      <span class="fig-layer-tag">{{ layer.tag }}</span>
      <input
        v-if="isRenaming"
        ref="renameInputRef"
        class="fig-layer-rename-input"
        type="text"
        :value="renameValue"
        @input="onRenameInput"
        @keydown.enter.prevent.stop="emitRenameSubmit"
        @keydown.esc.prevent.stop="emit('rename-cancel')"
        @blur="emit('rename-cancel')"
      />
      <span v-else class="fig-layer-label">{{ layer.label || layer.selector }}</span>
      <span class="fig-layer-badges">
        <span v-if="isFavorite" class="fig-layer-badge fig-layer-badge-favorite" title="Favorite">Fav</span>
        <span v-if="isPinned" class="fig-layer-badge fig-layer-badge-pinned" title="Pinned">Pin</span>
        <span v-if="layer.is_component_instance" class="fig-layer-badge">Instance</span>
        <span v-if="layer.is_component_variant" class="fig-layer-badge">Variant</span>
        <span v-if="layer.is_auto_layout_child" class="fig-layer-badge">Auto</span>
      </span>
    </button>
    <div class="fig-layer-actions">
      <button
        class="fig-layer-action-btn"
        type="button"
        :title="isFavorite ? 'حذف از علاقه‌مندی' : 'افزودن به علاقه‌مندی'"
        @click.stop="emit('toggle-favorite', String(layer.id || ''))"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M12 17.5l-5.2 3 1.4-5.9L3.5 10l6-.5L12 4l2.5 5.5 6 .5-4.7 4.6 1.4 5.9z"/>
        </svg>
      </button>
      <button
        class="fig-layer-action-btn"
        type="button"
        :title="isPinned ? 'برداشتن پین' : 'Pin لایه'"
        @click.stop="emit('toggle-pin', String(layer.id || ''))"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h8l-1 6 3 3-2 2-3-3-3 9-2-2 3-9-3-3 2-2 3 3z"/></svg>
      </button>
      <button
        class="fig-layer-action-btn"
        type="button"
        :title="layer.hidden ? 'نمایش' : 'مخفی‌کردن'"
        @click.stop="emit('toggle-visibility', String(layer.id || ''))"
      >
        <svg v-if="layer.hidden" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6z"/><line x1="4" y1="4" x2="20" y2="20"/></svg>
        <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6z"/><circle cx="12" cy="12" r="2.5"/></svg>
      </button>
      <button
        class="fig-layer-action-btn"
        type="button"
        :title="layer.locked ? 'آزادکردن قفل' : 'قفل‌کردن'"
        @click.stop="emit('toggle-lock', String(layer.id || ''))"
      >
        <svg v-if="layer.locked" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 1 1 8 0v3"/></svg>
        <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 7.7-1.5"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'

const props = defineProps({
  layer: { type: Object, required: true },
  selectedId: { type: String, default: '' },
  selectedIds: { type: Array, default: () => [] },
  isExpanded: { type: Function, required: true },
  setLayerRowRef: { type: Function, required: true },
  isRenaming: { type: Boolean, default: false },
  renameValue: { type: String, default: '' },
  pinnedIds: { type: Array, default: () => [] },
  favoriteIds: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'toggle',
  'select',
  'drop-layer',
  'toggle-visibility',
  'toggle-lock',
  'start-rename',
  'rename-input',
  'rename-submit',
  'rename-cancel',
  'toggle-pin',
  'toggle-favorite',
  'context-menu',
])

const renameInputRef = ref(null)

const layerType = computed(() => {
  const explicit = String(props.layer?.node_type || '').trim().toLowerCase()
  if (explicit) return explicit
  const tag = String(props.layer?.tag || '').toLowerCase()
  if (['p', 'span', 'a', 'button', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) return 'text'
  if (['img', 'svg', 'picture', 'canvas', 'video'].includes(tag)) return 'image'
  if (Number(props.layer?.child_count || 0) > 0) return 'frame'
  return 'node'
})

const layerTypeTitle = computed(() => {
  if (layerType.value === 'frame') return 'Frame'
  if (layerType.value === 'text') return 'Text'
  if (layerType.value === 'image') return 'Image'
  if (layerType.value === 'component') return 'Component'
  if (layerType.value === 'instance') return 'Instance'
  return 'Layer'
})

const isPinned = computed(() => Array.isArray(props.pinnedIds) && props.pinnedIds.includes(String(props.layer?.id || '')))
const isFavorite = computed(() => Array.isArray(props.favoriteIds) && props.favoriteIds.includes(String(props.layer?.id || '')))

function onDragStart(event) {
  const currentId = String(props.layer?.id || '')
  if (!currentId) return
  try {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', currentId)
  } catch {
    // noop
  }
}

function onDrop(event) {
  const targetId = String(event?.currentTarget?.getAttribute?.('data-layer-id') || '')
  let draggedId = ''
  try {
    draggedId = String(event?.dataTransfer?.getData('text/plain') || '')
  } catch {
    draggedId = ''
  }
  if (!draggedId || !targetId || draggedId === targetId) return
  emit('drop-layer', { draggedId, targetId })
}

function onSelect(event) {
  const range = Boolean(event?.shiftKey)
  const toggle = Boolean(event?.metaKey || event?.ctrlKey)
  emit('select', { id: String(props.layer?.id || ''), range, additive: toggle, toggle })
}

function onContextMenu(event) {
  emit('context-menu', {
    id: String(props.layer?.id || ''),
    x: Number(event?.clientX || 0),
    y: Number(event?.clientY || 0),
  })
}

function onRenameInput(event) {
  emit('rename-input', String(event?.target?.value || ''))
}

function emitRenameSubmit() {
  emit('rename-submit', { id: String(props.layer?.id || ''), value: String(props.renameValue || '') })
}

watch(
  () => props.isRenaming,
  (nextValue) => {
    if (!nextValue) return
    nextTick(() => {
      const input = renameInputRef.value
      if (!input || typeof input.focus !== 'function') return
      input.focus()
      if (typeof input.select === 'function') input.select()
    })
  }
)
</script>
