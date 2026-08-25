<template>
  <div v-if="error" class="fig-status fig-status-error">{{ error }}</div>
  <div v-else-if="success" class="fig-status fig-status-success">{{ success }}</div>
</template>

<script setup>
defineProps({
  error: { type: String, default: '' },
  success: { type: String, default: '' },
})
</script>
