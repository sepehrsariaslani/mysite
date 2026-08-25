<template>
  <button 
    class="glass-button" 
    :class="[`glass-button--${variant}`, { 'glass-button--icon': iconOnly }]"
    @click="$emit('click', $event)"
  >
    <div class="glass-bg"></div>
    <div class="glass-content">
      <slot name="icon"></slot>
      <slot></slot>
    </div>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary' // 'primary', 'secondary', 'ghost'
  },
  iconOnly: {
    type: Boolean,
    default: false
  }
})
defineEmits(['click'])
</script>

<style scoped>
.glass-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 100px;
  border: none;
  background: transparent;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  font-family: inherit;
  font-weight: 700;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.glass-button--icon {
  width: 44px;
  height: 44px;
  padding: 0;
}

.glass-bg {
  position: absolute;
  inset: 0;
  transition: all 0.4s;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.glass-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Primary: Dark glass with white text */
.glass-button--primary .glass-bg {
  background: var(--accent-brown);
  border: 1px solid var(--glass-border);
}
.glass-button--primary {
  color: #fff;
}
.glass-button--primary:hover .glass-bg {
  background: var(--accent-gold);
}
.glass-button--primary:hover { color: var(--accent-brown); }

/* Secondary: Light glass with theme text */
.glass-button--secondary .glass-bg {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}
.glass-button--secondary {
  color: var(--text-main);
}
.glass-button--secondary:hover .glass-bg {
  background: var(--glass-bg-hover);
}

/* Ghost: Ultra subtle glass */
.glass-button--ghost .glass-bg {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}
.glass-button--ghost {
  color: var(--text-main);
}
.glass-button--ghost:hover .glass-bg {
  background: var(--glass-bg-hover);
}

.glass-button:active {
  transform: scale(0.92);
}
</style>
