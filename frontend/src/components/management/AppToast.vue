<template>
  <Teleport to="body">
    <TransitionGroup name="toast-list" tag="div" class="toast-container" dir="rtl">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast-item"
        :class="t.type"
        role="alert"
        aria-live="polite"
      >
        <component :is="iconForType(t.type)" :size="18" class="toast-icon" />
        <span class="toast-msg">{{ t.message }}</span>
        <button class="toast-close" @click="remove(t.id)" aria-label="بستن">
          <X :size="14" />
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-vue-next'

const toasts = ref([])
let idCounter = 0

function iconForType(type) {
  return { success: CheckCircle2, error: AlertCircle, warning: AlertTriangle, info: Info }[type] || Info
}

function add(message, type = 'success', duration = 3500) {
  const id = ++idCounter
  toasts.value.push({ id, message, type })
  if (duration > 0) {
    setTimeout(() => remove(id), duration)
  }
  return id
}

function remove(id) {
  const idx = toasts.value.findIndex(t => t.id === id)
  if (idx !== -1) toasts.value.splice(idx, 1)
}

defineExpose({ add, remove })
</script>

<style>
.toast-container {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  width: min(90vw, 420px);
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  pointer-events: auto;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.toast-item.success { background: rgba(22, 163, 74, 0.92); }
.toast-item.error { background: rgba(220, 38, 38, 0.92); }
.toast-item.warning { background: rgba(217, 119, 6, 0.92); }
.toast-item.info { background: rgba(37, 99, 235, 0.92); }

.toast-icon { flex-shrink: 0; }
.toast-msg { flex: 1; min-width: 0; }
.toast-close {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--duration-fast) var(--ease-out);
}
.toast-close:hover { background: rgba(255, 255, 255, 0.35); }

/* Animations */
.toast-list-enter-active {
  animation: toastIn var(--duration-normal) var(--ease-out);
}
.toast-list-leave-active {
  animation: toastOut var(--duration-fast) ease-in forwards;
}
.toast-list-move {
  transition: transform var(--duration-normal) var(--ease-out);
}

@keyframes toastIn {
  from { opacity: 0; transform: translateY(16px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes toastOut {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(-12px) scale(0.95); }
}
</style>
