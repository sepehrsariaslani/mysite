<template>
  <div 
    class="glass-card" 
    :class="[
      `glass-card--${variant}`,
      { 'glass-card--hover': hoverable }
    ]"
    :style="cardStyle"
  >
    <slot></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'light', // 'light', 'dark', 'ultra'
    validator: (v) => ['light', 'dark', 'ultra'].includes(v)
  },
  blur: {
    type: String,
    default: '20px'
  },
  hoverable: {
    type: Boolean,
    default: false
  },
  opacity: {
    type: Number,
    default: 0.7
  }
})

const cardStyle = computed(() => {
  const backdropBlur = `blur(${props.blur})`
  return {
    backdropFilter: backdropBlur,
    webKitBackdropFilter: backdropBlur,
  }
})
</script>

<style scoped>
.glass-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.glass-card--light {
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
}

.glass-card--dark {
  background: rgba(80, 49, 48, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  color: #fff;
}

.glass-card--ultra {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.glass-card--hover:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>
