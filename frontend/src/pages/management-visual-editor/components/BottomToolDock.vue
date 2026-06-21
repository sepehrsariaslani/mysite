<template>
  <div class="fig-bottom-dock-wrap">
    <div class="fig-bottom-dock">
      <div class="fig-bottom-tools">
        <button
          v-for="tool in tools"
          :key="tool.key"
          type="button"
          class="fig-bottom-tool"
          :class="{ 'fig-bottom-tool-active': activeTool === tool.key }"
          :title="tool.label"
          @click="$emit('set-tool', tool.key)"
        >
          <svg v-if="tool.key === 'select'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3l7.5 18 2.7-7.2L21 11.1 3 3z"/></svg>
          <svg v-else-if="tool.key === 'frame'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>
          <svg v-else-if="tool.key === 'rectangle'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>
          <svg v-else-if="tool.key === 'pen'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19c4.42 0 8-3.58 8-8 0-1.8-.59-3.46-1.6-4.8l-5.6 2.2-2.2 5.6A8 8 0 0 0 12 19z"/><circle cx="12" cy="11" r="1"/></svg>
          <svg v-else-if="tool.key === 'text'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M12 6v12"/></svg>
          <svg v-else-if="tool.key === 'comment'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H7l-4 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v18M3 12h18"/></svg>
        </button>
      </div>

      <div class="fig-bottom-mode">
        <button
          type="button"
          class="fig-bottom-mode-btn"
          :class="{ 'fig-bottom-mode-btn-active': mode === 'design' }"
          title="Design"
          @click="$emit('set-mode', 'design')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3-6 6-9 9-9 3 0 6 3 9 9"/><path d="M12 12V3"/></svg>
        </button>
        <button
          type="button"
          class="fig-bottom-mode-btn"
          :class="{ 'fig-bottom-mode-btn-active': mode === 'developer' }"
          title="Developer"
          @click="$emit('set-mode', 'developer')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activeTool: { type: String, default: 'select' },
  mode: { type: String, default: 'design' },
})

defineEmits(['set-tool', 'set-mode'])

const tools = [
  { key: 'select', label: 'Select/Move' },
  { key: 'frame', label: 'Frame' },
  { key: 'rectangle', label: 'Rectangle' },
  { key: 'pen', label: 'Pen' },
  { key: 'text', label: 'Text' },
  { key: 'comment', label: 'Comment' },
  { key: 'component', label: 'Component' },
]
</script>
