<template>
  <header class="fig-toolbar">
    <div class="fig-toolbar-start">
      <a class="fig-btn fig-btn-ghost" href="/mysite/management">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        بازگشت
      </a>
      <div class="fig-divider-v"></div>
      <span class="fig-route-label" v-if="route" dir="ltr">{{ route }}</span>
      <span class="fig-route-label fig-muted" v-else>صفحه‌ای انتخاب نشده</span>
    </div>
    <div class="fig-toolbar-center">
      <span class="fig-title">Visual Editor</span>
    </div>
    <div class="fig-toolbar-end">
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
      <button class="fig-btn fig-btn-ghost" :disabled="loading" @click="$emit('reload')">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
        رفرش
      </button>
      <button class="fig-btn fig-btn-ghost" :disabled="savingVisual || loading || !hasEditorTarget" @click="$emit('save-visual')">
        {{ savingVisual ? 'ذخیره...' : 'ذخیره CSS' }}
      </button>
      <button class="fig-btn fig-btn-primary" :disabled="savingSource || loading || !hasEditorTarget" @click="$emit('save-source')">
        {{ savingSource ? 'ذخیره...' : 'ذخیره فایل' }}
      </button>
      <a v-if="route" class="fig-btn fig-btn-ghost" :href="route" target="_blank" rel="noreferrer">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
      </a>
    </div>
  </header>
</template>

<script setup>
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
})

defineEmits(['reload', 'save-visual', 'save-source'])
</script>
