<template>
  <div v-if="route" class="fig-infobar">
    <div class="fig-info-chip">
      <span class="fig-muted">فایل</span>
      <span dir="ltr">{{ fileInfo.file || '-' }}</span>
    </div>
    <div class="fig-info-chip">
      <span class="fig-muted">نوع</span>
      <span>{{ fileInfo.file_type || '-' }}</span>
    </div>
    <div class="fig-info-chip">
      <span class="fig-muted">کامپوننت</span>
      <span>{{ fileInfo.component || '-' }}</span>
    </div>
    <div class="fig-info-chip">
      <span class="fig-muted">Override</span>
      <span>{{ activeVisualOverrideCount.toLocaleString('fa-IR') }}</span>
    </div>
    <div class="fig-info-chip fig-info-chip-wide">
      <span class="fig-muted">ادیت فایل جداگانه</span>
      <select :value="selectedTargetFile" :disabled="!editableFiles.length" @change="onChange">
        <option v-if="!editableFiles.length" value="">فایل قابل ادیتی پیدا نشد</option>
        <option v-for="item in editableFiles" :key="item.file" :value="item.file">{{ item.label }}</option>
      </select>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  route: { type: String, default: '' },
  fileInfo: { type: Object, default: () => ({ file: '', file_type: '', component: '' }) },
  activeVisualOverrideCount: { type: Number, default: 0 },
  editableFiles: { type: Array, default: () => [] },
  selectedTargetFile: { type: String, default: '' },
})

const emit = defineEmits(['update:selectedTargetFile', 'change'])

function onChange(event) {
  const value = String(event?.target?.value || '')
  emit('update:selectedTargetFile', value)
  emit('change', value)
}
</script>
