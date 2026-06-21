<template>
  <aside class="fig-panel fig-panel-left">
    <div class="fig-left-tabs">
      <button type="button" class="fig-left-tab-btn" :class="{ 'fig-left-tab-btn-active': activeTab === 'pages' }" @click="activeTab = 'pages'">Pages</button>
      <button type="button" class="fig-left-tab-btn" :class="{ 'fig-left-tab-btn-active': activeTab === 'layers' }" @click="activeTab = 'layers'">Layers</button>
      <button type="button" class="fig-left-tab-btn" :class="{ 'fig-left-tab-btn-active': activeTab === 'assets' }" @click="activeTab = 'assets'">Assets</button>
    </div>

    <div v-if="activeTab === 'pages'" class="fig-section">
      <div class="fig-section-header">
        <span>Pages</span>
      </div>

      <div class="fig-search-wrap">
        <svg class="fig-search-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          class="fig-search"
          v-model="pageQuery"
          placeholder="جستجو در صفحات"
        />
      </div>

      <div class="fig-pages-list">
        <button
          v-for="page in visibleEditorPages"
          :key="page.id"
          type="button"
          class="fig-page-item"
          :class="{ 'fig-page-item-active': activePageId === page.id }"
          @click="emit('select-page', page.id)"
        >
          <span class="fig-page-item-title" dir="ltr">{{ page.label }}</span>
          <span v-if="page.description" class="fig-page-item-desc" dir="ltr">{{ page.description }}</span>
        </button>
        <div v-if="!visibleEditorPages.length" class="fig-layer-empty">صفحه‌ای پیدا نشد</div>
      </div>

      <div class="fig-pages-history">
        <div class="fig-section-header">
          <span>تاریخچه نسخه</span>
        </div>
        <input
          class="fig-input"
          :value="saveNote"
          placeholder="یادداشت نسخه (اختیاری)"
          @input="$emit('update:save-note', $event.target.value)"
        />
        <div v-if="!historyVersions.length" class="fig-layer-empty">نسخه‌ای ثبت نشده</div>
        <div v-else class="fig-history-list">
          <div v-for="version in historyVersions" :key="version.id" class="fig-history-item">
            <div class="fig-history-meta">
              <span class="fig-history-date">{{ formatDate(version.saved_at) }}</span>
              <span class="fig-muted">{{ version.saved_by || '-' }}</span>
              <span class="fig-muted">{{ version.note || 'بدون یادداشت' }}</span>
            </div>
            <button class="fig-btn fig-btn-xs" :disabled="restoringVersionId === version.id" @click="$emit('restore-version', version.id)">
              {{ restoringVersionId === version.id ? '...' : 'بازگردانی' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="activeTab === 'layers'" class="fig-section">
      <div class="fig-section-header">
        <span>لایه‌ها</span>
        <div class="fig-section-actions">
          <button
            class="fig-icon-btn"
            title="اسکن لایه‌ها"
            :disabled="!previewInitialized || previewLoading || layerScanInProgress"
            @click="$emit('scan-preview-layers')"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </button>
        </div>
      </div>

      <div class="fig-search-wrap">
        <svg class="fig-search-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          class="fig-search"
          :value="visualLayerQuery"
          placeholder="جستجو در لایه‌ها"
          @input="$emit('update:visual-layer-query', $event.target.value)"
        />
      </div>

      <div
        ref="layerListRef"
        class="fig-layer-list"
        tabindex="0"
        @scroll="onLayerListScroll"
        @keydown="onLayerListKeydown"
      >
        <div v-if="layerScanInProgress" class="fig-layer-scanning">
          <div class="fig-spinner fig-spinner-sm"></div>
          <span>اسکن لایه‌ها...</span>
        </div>

        <div v-else-if="!filteredVisualLayers.length" class="fig-layer-empty">
          <span v-if="!previewInitialized">پیش‌نمایش را بارگذاری کن</span>
          <span v-else>لایه‌ای یافت نشد</span>
        </div>

        <template v-else>
          <div v-if="shouldVirtualize" class="fig-layer-spacer" :style="{ height: `${topSpacerHeight}px` }"></div>
          <LayerTreeNode
            v-for="layer in visibleVirtualLayers"
            :key="layer.id"
            :layer="layer"
            :selected-id="visualSelectedId"
            :selected-ids="visualSelectedIds"
            :is-expanded="isLayerExpanded"
            :set-layer-row-ref="setLayerRowRef"
            :is-renaming="renamingLayerId === layer.id"
            :rename-value="renamingLayerId === layer.id ? renameDraftValue : ''"
            :pinned-ids="pinnedLayerIds"
            :favorite-ids="favoriteLayerIds"
            @toggle="$emit('toggle-layer-node', $event)"
            @select="onLayerNodeSelect"
            @drop-layer="$emit('layer-drop', $event)"
            @toggle-visibility="$emit('toggle-layer-visibility', $event)"
            @toggle-lock="$emit('toggle-layer-lock', $event)"
            @toggle-pin="togglePinnedLayer"
            @toggle-favorite="toggleFavoriteLayer"
            @context-menu="openLayerContextMenu"
            @start-rename="startRenameLayer"
            @rename-input="onRenameInput"
            @rename-submit="commitRenameLayer"
            @rename-cancel="cancelRenameLayer"
          />
          <div v-if="shouldVirtualize" class="fig-layer-spacer" :style="{ height: `${bottomSpacerHeight}px` }"></div>
          <div v-if="shouldVirtualize" class="fig-layer-virtual-badge">Virtualized {{ filteredVisualLayers.length }}</div>
        </template>
      </div>

      <div
        v-if="layerContextMenu.visible"
        class="fig-layer-context-menu"
        :style="{ left: `${layerContextMenu.x}px`, top: `${layerContextMenu.y}px` }"
        @click.stop
      >
        <button
          v-for="action in layerContextActions"
          :key="action.key"
          type="button"
          class="fig-layer-context-item"
          :class="{ 'fig-layer-context-item-danger': action.danger }"
          @click="onLayerContextAction(action.key)"
        >
          {{ action.label }}
        </button>
      </div>
    </div>

    <div v-else class="fig-section">
      <div class="fig-section-header">
        <span>Assets</span>
      </div>
      <div class="fig-search-wrap">
        <svg class="fig-search-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          class="fig-search"
          :value="assetQuery"
          placeholder="Search assets"
          @input="$emit('update:asset-query', $event.target.value)"
        />
      </div>
      <div class="fig-assets-filters" role="tablist" aria-label="Asset category">
        <button type="button" class="fig-assets-filter-btn" :class="{ 'fig-assets-filter-btn-active': activeAssetCategory === 'all' }" @click="activeAssetCategory = 'all'">All</button>
        <button type="button" class="fig-assets-filter-btn" :class="{ 'fig-assets-filter-btn-active': activeAssetCategory === 'component' }" @click="activeAssetCategory = 'component'">Components</button>
        <button type="button" class="fig-assets-filter-btn" :class="{ 'fig-assets-filter-btn-active': activeAssetCategory === 'style' }" @click="activeAssetCategory = 'style'">Styles</button>
        <button type="button" class="fig-assets-filter-btn" :class="{ 'fig-assets-filter-btn-active': activeAssetCategory === 'token' }" @click="activeAssetCategory = 'token'">Tokens</button>
        <button type="button" class="fig-assets-filter-btn" :class="{ 'fig-assets-filter-btn-active': activeAssetCategory === 'image' }" @click="activeAssetCategory = 'image'">Images</button>
      </div>
      <div class="fig-assets-upload-row">
        <button
          class="fig-btn fig-btn-xs fig-btn-ghost"
          type="button"
          :disabled="imageUploading"
          @click="triggerImageUpload"
        >
          {{ imageUploading ? 'Uploading...' : 'Upload image' }}
        </button>
        <button
          class="fig-btn fig-btn-xs fig-btn-ghost"
          type="button"
          :disabled="imageLibraryLoading"
          @click="$emit('refresh-image-assets')"
        >
          {{ imageLibraryLoading ? 'Loading...' : 'Refresh' }}
        </button>
        <input
          ref="assetImageUploadInput"
          type="file"
          accept="image/*"
          class="fig-upload-hidden-input"
          @change="onAssetImageUploadChange"
        />
      </div>
      <div class="fig-assets-list">
        <div v-if="!visibleAssetItems.length" class="fig-layer-empty">Assetی پیدا نشد</div>
        <div
          v-for="asset in visibleAssetItems"
          :key="asset.id"
          class="fig-asset-item"
          draggable="true"
          @dragstart="onAssetDragStart($event, asset)"
          @dragend="onAssetDragEnd"
        >
          <span v-if="asset.type === 'image'" class="fig-asset-thumb-wrap">
            <img :src="asset.previewUrl || asset.url" :alt="asset.name || 'image'" class="fig-asset-thumb" loading="lazy" />
          </span>
          <div class="fig-asset-meta">
            <strong>{{ asset.name }}</strong>
            <small class="fig-muted">{{ resolveAssetType(asset) }}</small>
            <small v-if="asset.description" class="fig-asset-desc" dir="ltr">{{ asset.description }}</small>
          </div>
          <button class="fig-btn fig-btn-xs fig-btn-ghost" type="button" @click="$emit('insert-asset', asset)">Insert</button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import LayerTreeNode from './LayerTreeNode.vue'

const LAYER_PANEL_STORAGE_KEY = 'mysite.management_editor.layer_panel_meta'

const activeTab = ref('layers')
const activeAssetCategory = ref('all')
const pageQuery = ref('')
const assetImageUploadInput = ref(null)
const layerListRef = ref(null)
const layerScrollTop = ref(0)
const layerViewportHeight = ref(380)
const renamingLayerId = ref('')
const renameDraftValue = ref('')
const pinnedLayerIds = ref([])
const favoriteLayerIds = ref([])
const layerContextMenu = ref({ visible: false, x: 0, y: 0, layerId: '' })
const VIRTUAL_ROW_HEIGHT = 24
const VIRTUAL_OVERSCAN = 14
let layerListResizeObserver = null

const props = defineProps({
  visualLayerQuery: { type: String, default: '' },
  filteredVisualLayers: { type: Array, default: () => [] },
  previewInitialized: { type: Boolean, default: false },
  previewLoading: { type: Boolean, default: false },
  layerScanInProgress: { type: Boolean, default: false },
  visualSelectedId: { type: String, default: '' },
  visualSelectedIds: { type: Array, default: () => [] },
  visualLayerIndex: { type: Object, default: () => ({}) },
  visualChildrenMap: { type: Object, default: () => ({}) },
  assetQuery: { type: String, default: '' },
  filteredAssetItems: { type: Array, default: () => [] },
  imageUploading: { type: Boolean, default: false },
  imageLibraryLoading: { type: Boolean, default: false },
  saveNote: { type: String, default: '' },
  historyVersions: { type: Array, default: () => [] },
  restoringVersionId: { type: String, default: '' },
  editorPages: { type: Array, default: () => [] },
  activePageId: { type: String, default: '' },
  isLayerExpanded: { type: Function, required: true },
  setLayerRowRef: { type: Function, required: true },
  formatDate: { type: Function, required: true },
})

const emit = defineEmits([
  'update:visual-layer-query',
  'scan-preview-layers',
  'toggle-layer-node',
  'select-layer',
  'layer-drop',
  'toggle-layer-visibility',
  'toggle-layer-lock',
  'rename-layer',
  'layer-context-action',
  'select-page',
  'update:asset-query',
  'insert-asset',
  'asset-drag-start',
  'asset-drag-end',
  'upload-image-file',
  'refresh-image-assets',
  'update:save-note',
  'restore-version',
])

const visibleAssetItems = computed(() => {
  const rows = Array.isArray(props.filteredAssetItems) ? props.filteredAssetItems : []
  if (activeAssetCategory.value === 'all') return rows
  return rows.filter((row) => String(row?.type || '').toLowerCase() === activeAssetCategory.value)
})

const visibleEditorPages = computed(() => {
  const rows = Array.isArray(props.editorPages) ? props.editorPages : []
  const term = String(pageQuery.value || '').trim().toLowerCase()
  if (!term) return rows
  return rows.filter((row) => {
    const label = String(row?.label || '').toLowerCase()
    const description = String(row?.description || '').toLowerCase()
    return label.includes(term) || description.includes(term)
  })
})

const layerContextActions = computed(() => {
  const layerId = String(layerContextMenu.value.layerId || '').trim()
  const layer = layerId ? props.visualLayerIndex?.[layerId] : null
  if (!layerId || !layer) return []
  const hidden = Boolean(layer.hidden)
  const locked = Boolean(layer.locked)
  const pinned = pinnedLayerIds.value.includes(layerId)
  const favorite = favoriteLayerIds.value.includes(layerId)
  return [
    { key: 'rename', label: 'Rename' },
    { key: 'duplicate', label: 'Duplicate' },
    { key: 'copy-selector', label: 'Copy Selector' },
    { key: hidden ? 'show' : 'hide', label: hidden ? 'Show Layer' : 'Hide Layer' },
    { key: locked ? 'unlock' : 'lock', label: locked ? 'Unlock Layer' : 'Lock Layer' },
    { key: pinned ? 'unpin' : 'pin', label: pinned ? 'Unpin Layer' : 'Pin Layer' },
    { key: favorite ? 'unfavorite' : 'favorite', label: favorite ? 'Remove Favorite' : 'Add Favorite' },
    { key: 'delete', label: 'Delete', danger: true },
  ]
})

const shouldVirtualize = computed(() => {
  if (activeTab.value !== 'layers') return false
  return Number(props.filteredVisualLayers?.length || 0) > 220
})

const virtualStartIndex = computed(() => {
  if (!shouldVirtualize.value) return 0
  return Math.max(0, Math.floor(Number(layerScrollTop.value || 0) / VIRTUAL_ROW_HEIGHT) - VIRTUAL_OVERSCAN)
})

const virtualEndIndex = computed(() => {
  const total = Number(props.filteredVisualLayers?.length || 0)
  if (!shouldVirtualize.value) return total
  const viewportRows = Math.ceil((Number(layerViewportHeight.value || 380) + VIRTUAL_ROW_HEIGHT) / VIRTUAL_ROW_HEIGHT)
  return Math.min(total, virtualStartIndex.value + viewportRows + (VIRTUAL_OVERSCAN * 2))
})

const visibleVirtualLayers = computed(() => {
  const rows = Array.isArray(props.filteredVisualLayers) ? props.filteredVisualLayers : []
  if (!shouldVirtualize.value) return rows
  return rows.slice(virtualStartIndex.value, virtualEndIndex.value)
})

const topSpacerHeight = computed(() => {
  if (!shouldVirtualize.value) return 0
  return virtualStartIndex.value * VIRTUAL_ROW_HEIGHT
})

const bottomSpacerHeight = computed(() => {
  if (!shouldVirtualize.value) return 0
  const total = Number(props.filteredVisualLayers?.length || 0)
  return Math.max(0, (total - virtualEndIndex.value) * VIRTUAL_ROW_HEIGHT)
})

function normalizeNodeIdList(value) {
  if (!Array.isArray(value)) return []
  const out = []
  for (const row of value) {
    const id = String(row || '').trim()
    if (!id || out.includes(id)) continue
    out.push(id)
  }
  return out
}

function readLayerPanelStorage() {
  try {
    const raw = window.localStorage.getItem(LAYER_PANEL_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    pinnedLayerIds.value = normalizeNodeIdList(parsed?.pinned)
    favoriteLayerIds.value = normalizeNodeIdList(parsed?.favorite)
  } catch {
    pinnedLayerIds.value = []
    favoriteLayerIds.value = []
  }
}

function persistLayerPanelStorage() {
  try {
    window.localStorage.setItem(LAYER_PANEL_STORAGE_KEY, JSON.stringify({
      pinned: normalizeNodeIdList(pinnedLayerIds.value),
      favorite: normalizeNodeIdList(favoriteLayerIds.value),
    }))
  } catch {
    // noop
  }
}

function pruneLayerMetaIds() {
  const knownIds = new Set(Object.keys(props.visualLayerIndex || {}))
  pinnedLayerIds.value = normalizeNodeIdList(pinnedLayerIds.value).filter((id) => knownIds.has(id))
  favoriteLayerIds.value = normalizeNodeIdList(favoriteLayerIds.value).filter((id) => knownIds.has(id))
}

function togglePinnedLayer(nodeId) {
  const id = String(nodeId || '').trim()
  if (!id) return
  if (pinnedLayerIds.value.includes(id)) {
    pinnedLayerIds.value = pinnedLayerIds.value.filter((row) => row !== id)
  } else {
    pinnedLayerIds.value = [...pinnedLayerIds.value, id]
  }
}

function toggleFavoriteLayer(nodeId) {
  const id = String(nodeId || '').trim()
  if (!id) return
  if (favoriteLayerIds.value.includes(id)) {
    favoriteLayerIds.value = favoriteLayerIds.value.filter((row) => row !== id)
  } else {
    favoriteLayerIds.value = [...favoriteLayerIds.value, id]
  }
}

function closeLayerContextMenu() {
  if (!layerContextMenu.value.visible) return
  layerContextMenu.value = { visible: false, x: 0, y: 0, layerId: '' }
}

function openLayerContextMenu(payload) {
  const layerId = String(payload?.id || '').trim()
  if (!layerId) return
  const x = Number(payload?.x || 0)
  const y = Number(payload?.y || 0)
  const maxX = Math.max(8, Number(window?.innerWidth || 1280) - 232)
  const maxY = Math.max(8, Number(window?.innerHeight || 800) - 300)
  layerContextMenu.value = {
    visible: true,
    layerId,
    x: Math.min(Math.max(8, x), maxX),
    y: Math.min(Math.max(8, y), maxY),
  }
  onLayerNodeSelect({ id: layerId })
}

function onLayerContextAction(actionKey) {
  const action = String(actionKey || '').trim()
  const layerId = String(layerContextMenu.value.layerId || '').trim()
  if (!action || !layerId) {
    closeLayerContextMenu()
    return
  }
  if (action === 'rename') {
    startRenameLayer(layerId)
    closeLayerContextMenu()
    return
  }
  if (action === 'pin' || action === 'unpin') {
    togglePinnedLayer(layerId)
    closeLayerContextMenu()
    return
  }
  if (action === 'favorite' || action === 'unfavorite') {
    toggleFavoriteLayer(layerId)
    closeLayerContextMenu()
    return
  }
  if (action === 'show' || action === 'hide') {
    emit('toggle-layer-visibility', layerId)
    closeLayerContextMenu()
    return
  }
  if (action === 'lock' || action === 'unlock') {
    emit('toggle-layer-lock', layerId)
    closeLayerContextMenu()
    return
  }
  emit('layer-context-action', { id: layerId, action })
  closeLayerContextMenu()
}

function onGlobalPointerDown(event) {
  if (!layerContextMenu.value.visible) return
  const target = event?.target
  if (target?.closest?.('.fig-layer-context-menu')) return
  closeLayerContextMenu()
}

function measureLayerViewportHeight() {
  const nextHeight = Number(layerListRef.value?.clientHeight || 380)
  if (nextHeight > 0) layerViewportHeight.value = nextHeight
}

function onLayerListScroll(event) {
  layerScrollTop.value = Number(event?.target?.scrollTop || 0)
}

function resolveLayerRows() {
  return Array.isArray(props.filteredVisualLayers) ? props.filteredVisualLayers : []
}

function resolveLayerRangeIds(anchorId, targetId) {
  const rows = resolveLayerRows()
  if (!rows.length) return []
  const ids = rows.map((row) => String(row?.id || '')).filter(Boolean)
  const anchorIndex = ids.indexOf(String(anchorId || ''))
  const targetIndex = ids.indexOf(String(targetId || ''))
  if (anchorIndex < 0 || targetIndex < 0) return [String(targetId || '')].filter(Boolean)
  const start = Math.min(anchorIndex, targetIndex)
  const end = Math.max(anchorIndex, targetIndex)
  return ids.slice(start, end + 1)
}

function onLayerNodeSelect(payload) {
  const targetId = String(payload?.id || '').trim()
  if (!targetId) return
  const range = Boolean(payload?.range)
  if (range) {
    const anchorId = String(props.visualSelectedId || props.visualSelectedIds?.[0] || '').trim()
    const rangeIds = resolveLayerRangeIds(anchorId || targetId, targetId)
    emit('select-layer', { id: targetId, range: true, rangeIds, additive: Boolean(payload?.additive) })
    return
  }
  emit('select-layer', { id: targetId, additive: Boolean(payload?.additive), toggle: Boolean(payload?.toggle) })
}

function startRenameLayer(layerId) {
  const id = String(layerId || '').trim()
  if (!id) return
  const layer = props.visualLayerIndex?.[id]
  renamingLayerId.value = id
  renameDraftValue.value = String(layer?.label || layer?.selector || layer?.tag || id)
}

function onRenameInput(value) {
  renameDraftValue.value = String(value || '')
}

function cancelRenameLayer() {
  renamingLayerId.value = ''
  renameDraftValue.value = ''
}

function commitRenameLayer(payload) {
  const id = String(payload?.id || renamingLayerId.value || '').trim()
  if (!id) return
  const value = String(payload?.value ?? renameDraftValue.value ?? '').trim()
  emit('rename-layer', { id, value })
  cancelRenameLayer()
}

function onLayerListKeydown(event) {
  if (activeTab.value !== 'layers') return
  const key = String(event?.key || '').toLowerCase()
  if (!key) return

  if (renamingLayerId.value) {
    if (key === 'escape') {
      event.preventDefault()
      event.stopPropagation()
      cancelRenameLayer()
    }
    return
  }

  const selectedId = String(props.visualSelectedId || '').trim()
  if (!selectedId) return
  const selectedLayer = props.visualLayerIndex?.[selectedId] || null
  const children = Array.isArray(props.visualChildrenMap?.[selectedId]) ? props.visualChildrenMap[selectedId] : []
  const parentId = String(selectedLayer?.parent_id || '').trim()
  const rows = resolveLayerRows()
  const selectedIndex = rows.findIndex((row) => String(row?.id || '') === selectedId)

  if (key === 'arrowup' || key === 'arrowdown') {
    event.preventDefault()
    event.stopPropagation()
    if (selectedIndex < 0) return
    const delta = key === 'arrowup' ? -1 : 1
    const nextIndex = Math.min(rows.length - 1, Math.max(0, selectedIndex + delta))
    const nextId = String(rows[nextIndex]?.id || '').trim()
    if (nextId) emit('select-layer', { id: nextId })
    return
  }

  if (key === 'enter') {
    event.preventDefault()
    event.stopPropagation()
    startRenameLayer(selectedId)
    return
  }

  if (key === 'arrowleft') {
    event.preventDefault()
    event.stopPropagation()
    if (Number(selectedLayer?.child_count || 0) > 0 && props.isLayerExpanded(selectedId)) {
      emit('toggle-layer-node', selectedId)
      return
    }
    if (parentId) emit('select-layer', { id: parentId })
    return
  }

  if (key === 'arrowright') {
    event.preventDefault()
    event.stopPropagation()
    if (Number(selectedLayer?.child_count || 0) > 0 && !props.isLayerExpanded(selectedId)) {
      emit('toggle-layer-node', selectedId)
      return
    }
    if (children.length) emit('select-layer', { id: String(children[0] || '') })
  }
}

function ensureSelectedLayerVisible() {
  if (!shouldVirtualize.value) return
  const selectedId = String(props.visualSelectedId || '').trim()
  if (!selectedId) return
  const rows = Array.isArray(props.filteredVisualLayers) ? props.filteredVisualLayers : []
  const selectedIndex = rows.findIndex((row) => String(row?.id || '') === selectedId)
  if (selectedIndex < 0) return
  const listEl = layerListRef.value
  if (!listEl) return
  const rowTop = selectedIndex * VIRTUAL_ROW_HEIGHT
  const rowBottom = rowTop + VIRTUAL_ROW_HEIGHT
  const viewTop = Number(listEl.scrollTop || 0)
  const viewBottom = viewTop + Number(listEl.clientHeight || 0)
  if (rowTop >= viewTop && rowBottom <= viewBottom) return
  const targetTop = Math.max(0, rowTop - Math.max(0, Math.round((listEl.clientHeight - VIRTUAL_ROW_HEIGHT) / 2)))
  listEl.scrollTop = targetTop
  layerScrollTop.value = targetTop
}

function resolveAssetType(asset) {
  const type = String(asset?.type || '').toLowerCase()
  if (type === 'component') return 'Component'
  if (type === 'style') return 'Style'
  if (type === 'token') return 'Token'
  if (type === 'image') return 'Image'
  return 'Preset'
}

function triggerImageUpload() {
  assetImageUploadInput.value?.click?.()
}

function onAssetImageUploadChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  emit('upload-image-file', file, { applyToSelection: false })
  if (event?.target) event.target.value = ''
}

function onAssetDragStart(event, asset) {
  const payload = JSON.stringify(asset || {})
  try {
    event.dataTransfer.effectAllowed = 'copy'
    event.dataTransfer.setData('application/x-mysite-asset', payload)
    event.dataTransfer.setData('text/plain', payload)
  } catch {
    // noop
  }
  emit('asset-drag-start', asset)
}

function onAssetDragEnd() {
  emit('asset-drag-end')
}

watch(
  () => props.visualSelectedId,
  () => {
    if (renamingLayerId.value && renamingLayerId.value !== String(props.visualSelectedId || '').trim()) {
      cancelRenameLayer()
    }
    nextTick(() => ensureSelectedLayerVisible())
  }
)

watch(
  () => props.filteredVisualLayers?.length,
  () => {
    const maxScroll = Math.max(0, (Number(props.filteredVisualLayers?.length || 0) * VIRTUAL_ROW_HEIGHT) - Number(layerViewportHeight.value || 0))
    if (layerScrollTop.value > maxScroll) {
      layerScrollTop.value = maxScroll
      if (layerListRef.value) layerListRef.value.scrollTop = maxScroll
    }
    nextTick(() => ensureSelectedLayerVisible())
  }
)

watch(
  () => props.visualLayerIndex,
  () => {
    pruneLayerMetaIds()
  },
  { deep: true }
)

watch([pinnedLayerIds, favoriteLayerIds], () => {
  persistLayerPanelStorage()
}, { deep: true })

onMounted(() => {
  measureLayerViewportHeight()
  readLayerPanelStorage()
  if (typeof ResizeObserver !== 'undefined' && layerListRef.value) {
    layerListResizeObserver = new ResizeObserver(() => measureLayerViewportHeight())
    layerListResizeObserver.observe(layerListRef.value)
  }
  window.addEventListener('pointerdown', onGlobalPointerDown, true)
  window.addEventListener('scroll', closeLayerContextMenu, true)
  window.addEventListener('blur', closeLayerContextMenu)
})

onBeforeUnmount(() => {
  if (layerListResizeObserver) {
    try { layerListResizeObserver.disconnect() } catch { /* noop */ }
  }
  layerListResizeObserver = null
  window.removeEventListener('pointerdown', onGlobalPointerDown, true)
  window.removeEventListener('scroll', closeLayerContextMenu, true)
  window.removeEventListener('blur', closeLayerContextMenu)
})
</script>
