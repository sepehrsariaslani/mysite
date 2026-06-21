<template>
  <div class="fig-prop-section">
    <button class="fig-prop-section-head" type="button" @click="$emit('toggle')">
      <span class="fig-prop-section-title">
        <span v-if="icon" class="fig-prop-section-icon" aria-hidden="true">
          <svg v-if="icon === 'position'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v18M3 12h18"/><circle cx="12" cy="12" r="2"/></svg>
          <svg v-else-if="icon === 'layout'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          <svg v-else-if="icon === 'appearance'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/></svg>
          <svg v-else-if="icon === 'fill'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 11l-7-7-8 8a4 4 0 0 0 0 6 4 4 0 0 0 6 0l9-9z"/><path d="M2 22h20"/></svg>
          <svg v-else-if="icon === 'stroke'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/></svg>
          <svg v-else-if="icon === 'effects'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v6m0 6v6m9-9h-6M9 12H3"/><circle cx="12" cy="12" r="2.5"/></svg>
          <svg v-else-if="icon === 'typography'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M12 7v13"/></svg>
          <svg v-else-if="icon === 'variables'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7" cy="12" r="3"/><circle cx="17" cy="7" r="3"/><circle cx="17" cy="17" r="3"/><path d="M9.5 10.5L14.5 8.5M9.5 13.5l5 2"/></svg>
          <svg v-else-if="icon === 'styles'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l3 6 6 3-6 3-3 6-3-6-6-3 6-3 3-6z"/></svg>
          <svg v-else width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>
        </span>
        <span>{{ title }}</span>
      </span>
      <svg :style="{ transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }" width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M10 7l5 5-5 5z"/></svg>
    </button>
    <div v-show="open" class="fig-prop-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  open: { type: Boolean, default: true },
  icon: { type: String, default: '' },
})

defineEmits(['toggle'])
</script>
