<template>
  <section class="fig-shell fig-shell-component" :class="shellClass">
    <slot name="top" />
    <slot name="status" />
    <slot name="info" />
    <div class="fig-panels" :class="panelClass">
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'design',
  },
})

const panelClass = computed(() => ({
  'fig-panels-design': props.mode === 'design',
  'fig-panels-developer': props.mode === 'developer',
}))

const shellClass = computed(() => ({
  'fig-shell-design': props.mode === 'design',
  'fig-shell-developer': props.mode === 'developer',
}))
</script>
