<template>
  <header class="fig-topbar">
    <div class="fig-topbar-left">
      <a class="fig-icon-link" href="/management" title="بازگشت">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      </a>
      <span class="fig-route-label" v-if="route" dir="ltr">{{ route }}</span>
      <span class="fig-route-label fig-muted" v-else>صفحه‌ای انتخاب نشده</span>
    </div>

    <div class="fig-topbar-center" role="toolbar" aria-label="Editor Tools">
      <div class="fig-tool-states" role="tablist" aria-label="Tool states">
        <button
          v-for="tool in TOOL_ITEMS"
          :key="tool.key"
          type="button"
          class="fig-tool-state-btn"
          :class="{ 'fig-tool-state-btn-active': activeTool === tool.key }"
          :title="tool.label"
          @click="$emit('set-tool', tool.key)"
        >
          <span>{{ tool.shortcut }}</span>
        </button>
      </div>

      <div class="fig-topbar-actions-group">
        <button class="fig-topbar-btn" type="button" :disabled="loading" title="Refresh" @click="$emit('reload')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
        </button>
        <button class="fig-topbar-btn" type="button" :disabled="!hasEditorTarget" title="Duplicate Selected" @click="$emit('duplicate')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
        <button class="fig-topbar-btn" type="button" :disabled="!hasEditorTarget" title="Add Element" @click="$emit('add-element')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
        <button class="fig-topbar-btn" type="button" :disabled="loading || !hasEditorTarget" title="Save Visual" @click="$emit('save-visual')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
        </button>
        <button class="fig-topbar-btn fig-topbar-btn-primary" type="button" :disabled="loading || !hasEditorTarget" title="Save Source" @click="$emit('save-source')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </button>
      </div>

      <div class="fig-topbar-quick-actions">
        <div class="fig-topbar-quick-frame">
          <select class="fig-topbar-select fig-topbar-select-sm" :value="selectedFramePreset" @change="onFramePresetInput($event.target.value)">
            <option v-for="preset in FRAME_PRESETS" :key="preset.key" :value="preset.key">{{ preset.label }}</option>
          </select>
          <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Insert Frame Preset" @click="$emit('create-frame-preset', selectedFramePreset)">Frame</button>
        </div>

        <div class="fig-topbar-quick-boolean" role="group" aria-label="Boolean Operations">
          <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Union" @click="$emit('boolean-op', 'union')">U</button>
          <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Subtract" @click="$emit('boolean-op', 'subtract')">S</button>
          <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Intersect" @click="$emit('boolean-op', 'intersect')">I</button>
          <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Exclude" @click="$emit('boolean-op', 'exclude')">E</button>
        </div>

        <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Flatten selection" @click="$emit('flatten-selection')">Flatten</button>
        <button class="fig-topbar-mini-btn" type="button" :disabled="!hasEditorTarget" title="Mask selection" @click="$emit('mask-selection')">Mask</button>
      </div>
    </div>

    <div class="fig-topbar-right">
      <div class="fig-topbar-branch-tools" v-if="versioningBranches.length">
        <select
          class="fig-topbar-select"
          dir="ltr"
          :value="activeBranch"
          title="Active Branch"
          @change="$emit('set-active-branch', $event.target.value)"
        >
          <option v-for="row in versioningBranches" :key="`branch-${row.name}`" :value="row.name">
            {{ row.name }}{{ row.is_active ? ' *' : '' }}
          </option>
        </select>
        <button class="fig-topbar-mini-btn" type="button" title="Create Branch" @click="$emit('create-branch')">+B</button>
        <button class="fig-topbar-mini-btn" type="button" title="Milestone" @click="$emit('create-milestone')">MS</button>
        <button class="fig-topbar-mini-btn" type="button" title="Merge Branch" @click="$emit('merge-branch')">M</button>
      </div>

      <div class="fig-topbar-branch-tools" v-if="componentLibrarySummaries.length">
        <select
          class="fig-topbar-select"
          dir="ltr"
          :value="activeLibraryName"
          title="Server Library"
          @change="$emit('set-library-name', $event.target.value)"
        >
          <option v-for="row in componentLibrarySummaries" :key="`library-${row.name}`" :value="row.name">
            {{ row.name }}
          </option>
        </select>
        <button class="fig-topbar-mini-btn" type="button" title="Pull Library" @click="$emit('consume-library')">Pull</button>
        <button class="fig-topbar-mini-btn" type="button" title="Push Library" @click="$emit('publish-library')">Push</button>
      </div>

      <div class="fig-mode-switch" role="tablist" aria-label="Editor mode">
        <button
          type="button"
          class="fig-mode-btn"
          :class="{ 'fig-mode-btn-active': mode === 'design' }"
          @click="$emit('set-mode', 'design')"
        >
          Design
        </button>
        <button
          type="button"
          class="fig-mode-btn"
          :class="{ 'fig-mode-btn-active': mode === 'developer' }"
          @click="$emit('set-mode', 'developer')"
        >
          Developer
        </button>
      </div>

      <span v-if="(visualDirty || sourceDirty) && !savingVisual && !savingSource" class="fig-unsaved-badge">ذخیره‌نشده</span>
      <span
        v-if="hasEditorTarget"
        class="fig-auto-badge"
        :class="{
          'fig-auto-badge-pending': autoSavePending && !autoSaveRunning,
          'fig-auto-badge-saving': autoSaveRunning,
        }"
      >
        {{ autoSaveRunning ? 'Auto Save...' : autoSavePending ? 'Auto Save در صف' : 'Auto Save روشن' }}
      </span>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const TOOL_ITEMS = [
  { key: 'select', shortcut: 'V', label: 'Select (V)' },
  { key: 'frame', shortcut: 'F', label: 'Frame (F)' },
  { key: 'rectangle', shortcut: 'R', label: 'Rectangle (R)' },
  { key: 'text', shortcut: 'T', label: 'Text (T)' },
  { key: 'pen', shortcut: 'P', label: 'Pen (P)' },
]

const FRAME_PRESETS = [
  { key: 'desktop', label: 'Desktop 1440' },
  { key: 'tablet', label: 'Tablet 768' },
  { key: 'mobile', label: 'Mobile 390' },
  { key: 'card', label: 'Card 420x320' },
]

const selectedFramePreset = ref('desktop')

defineProps({
  route: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  savingVisual: { type: Boolean, default: false },
  savingSource: { type: Boolean, default: false },
  hasEditorTarget: { type: Boolean, default: false },
  visualDirty: { type: Boolean, default: false },
  sourceDirty: { type: Boolean, default: false },
  autoSavePending: { type: Boolean, default: false },
  autoSaveRunning: { type: Boolean, default: false },
  mode: { type: String, default: 'design' },
  activeTool: { type: String, default: 'select' },
  activeBranch: { type: String, default: 'main' },
  versioningBranches: { type: Array, default: () => [] },
  componentLibrarySummaries: { type: Array, default: () => [] },
  activeLibraryName: { type: String, default: 'global' },
})

const emit = defineEmits([
  'reload',
  'save-visual',
  'save-source',
  'set-mode',
  'set-tool',
  'duplicate',
  'add-element',
  'create-frame-preset',
  'boolean-op',
  'flatten-selection',
  'mask-selection',
  'set-active-branch',
  'create-branch',
  'create-milestone',
  'merge-branch',
  'set-library-name',
  'consume-library',
  'publish-library',
])

function onFramePresetInput(value) {
  const next = String(value || '').trim().toLowerCase()
  if (!FRAME_PRESETS.some((row) => row.key === next)) return
  selectedFramePreset.value = next
}
</script>
