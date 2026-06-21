<template>
  <div class="fig-color-field" ref="rootEl">
    <button class="fig-color-trigger" type="button" @click="toggleOpen">
      <span class="fig-color-swatch" :style="{ background: displayColor }"></span>
      <span class="fig-color-label">{{ modelValue || 'transparent' }}</span>
    </button>

    <div v-if="open" class="fig-color-popover">
      <input class="fig-color-native" type="color" :value="hex" @input="onHexInput" />
      <div class="fig-color-alpha-row">
        <label>Alpha</label>
        <input type="range" min="0" max="100" :value="alpha" @input="onAlphaInput" />
        <span>{{ alpha }}%</span>
      </div>
      <input class="fig-prop-input" dir="ltr" :value="hexText" @input="onHexTextInput" placeholder="#RRGGBB" />

      <div class="fig-color-presets">
        <button
          v-for="preset in dedupedPresets"
          :key="preset"
          type="button"
          class="fig-color-preset"
          :style="{ background: preset }"
          :title="preset"
          @click="setColor(preset, alpha)"
        ></button>
      </div>

      <div v-if="recentColors.length" class="fig-color-presets fig-color-presets-recent">
        <button
          v-for="recent in recentColors"
          :key="recent"
          type="button"
          class="fig-color-preset"
          :style="{ background: recent }"
          :title="recent"
          @click="setRawColor(recent)"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const RECENT_LIMIT = 8
const recentColorsStore = ref([])

const props = defineProps({
  modelValue: { type: String, default: '' },
  presets: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const rootEl = ref(null)

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function normalizeHex(value) {
  const raw = String(value || '').trim().replace('#', '')
  if (/^[0-9a-fA-F]{3}$/.test(raw)) {
    return `#${raw.split('').map((c) => `${c}${c}`).join('').toLowerCase()}`
  }
  if (/^[0-9a-fA-F]{6}$/.test(raw)) return `#${raw.toLowerCase()}`
  return '#111111'
}

function parseColor(value) {
  const raw = String(value || '').trim()
  if (!raw) return { hex: '#111111', alpha: 100 }

  if (/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(raw)) {
    return { hex: normalizeHex(raw), alpha: 100 }
  }

  const rgba = raw.match(/rgba?\(([^)]+)\)/i)
  if (rgba) {
    const parts = rgba[1].split(',').map((part) => String(part || '').trim())
    const r = clamp(Number(parts[0] || 0), 0, 255)
    const g = clamp(Number(parts[1] || 0), 0, 255)
    const b = clamp(Number(parts[2] || 0), 0, 255)
    const a = parts.length > 3 ? clamp(Math.round(Number(parts[3] || 1) * 100), 0, 100) : 100
    const hex = `#${[r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')}`
    return { hex, alpha: a }
  }

  return { hex: '#111111', alpha: 100 }
}

const parsed = computed(() => parseColor(props.modelValue))
const hex = computed(() => parsed.value.hex)
const alpha = computed(() => parsed.value.alpha)
const hexText = computed(() => parsed.value.hex)
const displayColor = computed(() => {
  if (!props.modelValue) return 'transparent'
  return props.modelValue
})

const dedupedPresets = computed(() => {
  const merged = [...props.presets, '#111111', '#ffffff', '#0d99ff', 'transparent']
  return Array.from(new Set(merged.filter(Boolean)))
})

const recentColors = computed(() => [...recentColorsStore.value])

function pushRecentColor(color) {
  const next = String(color || '').trim()
  if (!next) return
  const rows = [...recentColorsStore.value]
  const idx = rows.indexOf(next)
  if (idx >= 0) rows.splice(idx, 1)
  rows.unshift(next)
  if (rows.length > RECENT_LIMIT) rows.splice(RECENT_LIMIT)
  recentColorsStore.value = rows
}

function emitColor(hexValue, alphaValue) {
  const normalizedHex = normalizeHex(hexValue)
  const nextAlpha = clamp(Number(alphaValue || 100), 0, 100)
  let next = normalizedHex
  if (nextAlpha < 100) {
    const [r, g, b] = [1, 3, 5].map((start) => parseInt(normalizedHex.slice(start, start + 2), 16))
    next = `rgba(${r}, ${g}, ${b}, ${(nextAlpha / 100).toFixed(2)})`
  }
  emit('update:modelValue', next)
  pushRecentColor(next)
}

function setRawColor(color) {
  emit('update:modelValue', color)
  pushRecentColor(color)
}

function setColor(color, alphaValue) {
  if (String(color).toLowerCase() === 'transparent') {
    emit('update:modelValue', 'transparent')
    pushRecentColor('transparent')
    return
  }
  emitColor(color, alphaValue)
}

function onHexInput(event) {
  emitColor(event?.target?.value, alpha.value)
}

function onAlphaInput(event) {
  emitColor(hex.value, Number(event?.target?.value || 100))
}

function onHexTextInput(event) {
  emitColor(event?.target?.value, alpha.value)
}

function toggleOpen() {
  open.value = !open.value
}

function closeOnOutsideClick(event) {
  const root = rootEl.value
  if (!root || root.contains(event.target)) return
  open.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', closeOnOutsideClick, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', closeOnOutsideClick, true)
})
</script>
