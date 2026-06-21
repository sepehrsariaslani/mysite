<template>
  <section class="fig-panel fig-panel-center">
    <div class="fig-preview-toolbar">
      <span class="fig-panel-title">پیش‌نمایش</span>
      <div class="fig-preview-controls">
        <span v-if="isManagementRoute" class="fig-badge fig-badge-warning">مدیریتی</span>
        <span v-if="isComponentFile" class="fig-badge fig-badge-accent">کامپوننت</span>
        <div v-if="isComponentFile" class="fig-preview-mode">
          <span class="fig-preview-mode-static">بوم کامپوننت</span>
        </div>
        <div class="fig-device-switch" role="tablist" aria-label="Viewport preset">
          <button
            type="button"
            class="fig-device-btn"
            :class="{ 'fig-device-btn-active': viewportPreset === 'desktop' }"
            title="Desktop"
            @click="$emit('update:viewport-preset', 'desktop')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>
          </button>
          <button
            type="button"
            class="fig-device-btn"
            :class="{ 'fig-device-btn-active': viewportPreset === 'tablet' }"
            title="Tablet"
            @click="$emit('update:viewport-preset', 'tablet')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="2" width="12" height="20" rx="2"/><circle cx="12" cy="18" r="0.8"/></svg>
          </button>
          <button
            type="button"
            class="fig-device-btn"
            :class="{ 'fig-device-btn-active': viewportPreset === 'mobile' }"
            title="Mobile"
            @click="$emit('update:viewport-preset', 'mobile')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="2" width="8" height="20" rx="2"/><circle cx="12" cy="18" r="0.8"/></svg>
          </button>
        </div>

        <div class="fig-canvas-precision-controls">
          <button
            type="button"
            class="fig-mini-toggle"
            :class="{ 'fig-mini-toggle-active': rulersEnabled }"
            title="Rulers"
            @click="$emit('toggle-rulers')"
          >R</button>
          <button
            type="button"
            class="fig-mini-toggle"
            :class="{ 'fig-mini-toggle-active': gridEnabled }"
            title="Pixel grid"
            @click="$emit('toggle-grid')"
          >G</button>
          <button
            type="button"
            class="fig-mini-toggle"
            :class="{ 'fig-mini-toggle-active': layoutGridEnabled }"
            title="Layout columns"
            @click="$emit('toggle-layout-grid')"
          >L</button>
          <button
            type="button"
            class="fig-mini-toggle"
            :class="{ 'fig-mini-toggle-active': guidesEnabled }"
            title="Guides"
            @click="$emit('toggle-guides')"
          >|</button>
          <label class="fig-mini-input-wrap" title="Grid size">
            <span>Grid</span>
            <input
              class="fig-mini-input"
              type="number"
              min="2"
              max="128"
              :value="gridSize"
              @input="$emit('update:grid-size', $event.target.value)"
            />
          </label>
          <label class="fig-mini-input-wrap" title="Columns">
            <span>Cols</span>
            <input
              class="fig-mini-input"
              type="number"
              min="1"
              max="24"
              :value="layoutGridColumns"
              @input="$emit('update:layout-grid-columns', $event.target.value)"
            />
          </label>
          <label class="fig-mini-input-wrap" title="Nudge step">
            <span>N</span>
            <input
              class="fig-mini-input"
              type="number"
              min="1"
              max="200"
              :value="nudgeStep"
              @input="$emit('update:nudge-step', $event.target.value)"
            />
          </label>
          <label class="fig-mini-input-wrap" title="Shift nudge step">
            <span>S</span>
            <input
              class="fig-mini-input"
              type="number"
              min="1"
              max="400"
              :value="nudgeStepLarge"
              @input="$emit('update:nudge-step-large', $event.target.value)"
            />
          </label>
          <div class="fig-canvas-zoom-controls" role="group" aria-label="Zoom controls">
            <button type="button" class="fig-mini-toggle" title="Zoom out" @click="$emit('zoom-out')">-</button>
            <button type="button" class="fig-canvas-zoom-btn" title="Reset 100%" @click="$emit('zoom-reset')">{{ zoomLabel }}</button>
            <button type="button" class="fig-mini-toggle" title="Zoom in" @click="$emit('zoom-in')">+</button>
            <button type="button" class="fig-mini-toggle" title="Fit to screen" @click="$emit('zoom-fit')">Fit</button>
          </div>
        </div>

        <button class="fig-btn fig-btn-ghost fig-btn-sm" :disabled="previewLoading || !hasEditorTarget" @click="$emit('request-preview-load')">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
          {{ previewLoading ? 'بارگذاری...' : previewInitialized ? 'رفرش' : 'بارگذاری پیش‌نمایش' }}
        </button>
        <div v-if="selectedVisualCount > 1" class="fig-align-toolbar">
          <button type="button" class="fig-align-btn" title="Align Left" @click="$emit('align-selection', 'align-left')">L</button>
          <button type="button" class="fig-align-btn" title="Align Center" @click="$emit('align-selection', 'align-center')">C</button>
          <button type="button" class="fig-align-btn" title="Align Right" @click="$emit('align-selection', 'align-right')">R</button>
          <button type="button" class="fig-align-btn" title="Align Top" @click="$emit('align-selection', 'align-top')">T</button>
          <button type="button" class="fig-align-btn" title="Align Middle" @click="$emit('align-selection', 'align-middle')">M</button>
          <button type="button" class="fig-align-btn" title="Align Bottom" @click="$emit('align-selection', 'align-bottom')">B</button>
          <button type="button" class="fig-align-btn" title="Distribute Horizontal" @click="$emit('align-selection', 'dist-h')">DH</button>
          <button type="button" class="fig-align-btn" title="Distribute Vertical" @click="$emit('align-selection', 'dist-v')">DV</button>
        </div>
      </div>
    </div>

    <div
      class="fig-preview-viewport"
      @dragover.prevent="onDragOver"
      @dragenter.prevent="onDragEnter"
      @dragleave="onDragLeave"
      @drop.prevent="onDrop"
    >
      <div v-if="canvasZoomHudVisible" class="fig-canvas-zoom-hud">{{ canvasZoomHudText }}</div>
      <div v-if="assetDragActive" class="fig-canvas-dropzone" :class="{ 'fig-canvas-dropzone-hot': dropHot }">
        <span>Drop asset روی canvas</span>
      </div>

      <div v-if="!previewInitialized" class="fig-preview-empty">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        <p>{{ resolvedPreviewScope === 'component' ? 'پیش‌نمایش کامپوننت بارگذاری نشده' : 'پیش‌نمایش صفحه بارگذاری نشده' }}</p>
        <small v-if="resolvedPreviewScope === 'component'">در این حالت، کامپوننت داخل یک بوم سفید و مستقل رندر می‌شود.</small>
        <small v-else>روی «بارگذاری پیش‌نمایش» کلیک کن تا صفحه واقعی لود بشه</small>
        <small v-if="isComponentFile && componentUsageRoutes.length" class="fig-preview-usage">استفاده‌شده در: {{ componentUsageRoutes.join(' ، ') }}</small>
      </div>

      <div v-else-if="previewError" class="fig-preview-empty fig-preview-empty-error">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <p>{{ previewError }}</p>
      </div>

      <template v-else>
        <div class="fig-frame-shell" :class="frameShellClass" :style="{ width: frameWidth }">
          <iframe
            :ref="setFrameRef"
            class="fig-frame"
            :src="previewMode === 'url' ? visualPreviewSrc : undefined"
            :srcdoc="previewMode === 'srcdoc' ? visualPreviewSrcdoc : undefined"
            title="Visual Editor Preview"
            :sandbox="previewIframeSandbox"
            @load="$emit('frame-load')"
          ></iframe>
        </div>
        <div v-if="previewLoading" class="fig-frame-overlay">
          <div class="fig-spinner"></div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  isManagementRoute: { type: Boolean, default: false },
  isComponentFile: { type: Boolean, default: false },
  componentUsageRoutes: { type: Array, default: () => [] },
  resolvedPreviewScope: { type: String, default: 'page' },
  previewInitialized: { type: Boolean, default: false },
  previewError: { type: String, default: '' },
  previewLoading: { type: Boolean, default: false },
  hasEditorTarget: { type: Boolean, default: false },
  previewMode: { type: String, default: 'url' },
  visualPreviewSrc: { type: String, default: '' },
  visualPreviewSrcdoc: { type: String, default: '' },
  previewIframeSandbox: { type: String, default: '' },
  setFrameRef: { type: Function, required: true },
  viewportPreset: { type: String, default: 'desktop' },
  selectedVisualCount: { type: Number, default: 0 },
  assetDragActive: { type: Boolean, default: false },
  rulersEnabled: { type: Boolean, default: true },
  gridEnabled: { type: Boolean, default: false },
  layoutGridEnabled: { type: Boolean, default: false },
  guidesEnabled: { type: Boolean, default: true },
  gridSize: { type: Number, default: 8 },
  layoutGridColumns: { type: Number, default: 12 },
  nudgeStep: { type: Number, default: 1 },
  nudgeStepLarge: { type: Number, default: 10 },
  canvasZoom: { type: Number, default: 1 },
  canvasZoomHudVisible: { type: Boolean, default: false },
  canvasZoomHudText: { type: String, default: '100%' },
})

const emit = defineEmits([
  'request-preview-load',
  'frame-load',
  'update:viewport-preset',
  'align-selection',
  'drop-asset',
  'toggle-rulers',
  'toggle-grid',
  'toggle-layout-grid',
  'toggle-guides',
  'update:grid-size',
  'update:layout-grid-columns',
  'update:nudge-step',
  'update:nudge-step-large',
  'zoom-in',
  'zoom-out',
  'zoom-fit',
  'zoom-reset',
])

const zoomLabel = computed(() => `${Math.round(Math.max(0.1, Number(props.canvasZoom || 1)) * 100)}%`)

const frameWidth = computed(() => {
  if (props.viewportPreset === 'mobile') return '390px'
  if (props.viewportPreset === 'tablet') return '834px'
  return '100%'
})

const frameShellClass = computed(() => ({
  'fig-frame-shell-desktop': props.viewportPreset === 'desktop',
  'fig-frame-shell-tablet': props.viewportPreset === 'tablet',
  'fig-frame-shell-mobile': props.viewportPreset === 'mobile',
}))

const dropHot = ref(false)

function onDragEnter() {
  if (!props.assetDragActive) return
  dropHot.value = true
}

function onDragOver() {
  if (!props.assetDragActive) return
  dropHot.value = true
}

function onDragLeave(event) {
  if (!props.assetDragActive) return
  const related = event?.relatedTarget
  if (related && event?.currentTarget?.contains?.(related)) return
  dropHot.value = false
}

function onDrop(event) {
  dropHot.value = false
  let payload = ''
  try {
    payload = String(event?.dataTransfer?.getData('application/x-mysite-asset') || event?.dataTransfer?.getData('text/plain') || '')
  } catch {
    payload = ''
  }
  if (!payload) return
  let asset = null
  try {
    asset = JSON.parse(payload)
  } catch {
    asset = null
  }
  if (!asset || typeof asset !== 'object') return
  emit('drop-asset', { asset, clientX: Number(event?.clientX || 0), clientY: Number(event?.clientY || 0) })
}
</script>
