<template>
  <div class="fig-code-snippets">
    <div class="fig-code-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="fig-code-tab"
        :class="{ 'fig-code-tab-active': activeTab === tab.key }"
        type="button"
        @click="$emit('update:active-tab', tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="fig-code-preview-wrap" dir="ltr">
      <pre ref="gutterRef" class="fig-code-preview-gutter" aria-hidden="true">{{ lineNumbers }}</pre>
      <pre ref="previewRef" class="fig-code-preview" @scroll="syncGutterScroll">{{ decodedSnippet }}</pre>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  activeTab: { type: String, default: 'css' },
  cssSnippet: { type: String, default: '' },
  htmlSnippet: { type: String, default: '' },
  vueSnippet: { type: String, default: '' },
  reactSnippet: { type: String, default: '' },
  swiftuiSnippet: { type: String, default: '' },
  composeSnippet: { type: String, default: '' },
  tokenSnippet: { type: String, default: '' },
  redlineSnippet: { type: String, default: '' },
  fullSourcePreview: { type: String, default: '' },
  rawCssPreview: { type: String, default: '' },
})

defineEmits(['update:active-tab'])

const tabs = [
  { key: 'css', label: 'CSS' },
  { key: 'html', label: 'HTML' },
  { key: 'vue', label: 'VUE' },
  { key: 'react', label: 'REACT' },
  { key: 'swiftui', label: 'SWIFTUI' },
  { key: 'compose', label: 'COMPOSE' },
  { key: 'tokens', label: 'TOKENS' },
  { key: 'redline', label: 'REDLINE' },
  { key: 'source', label: 'SOURCE' },
  { key: 'rawcss', label: 'RAW CSS' },
]

const activeSnippet = computed(() => {
  if (props.activeTab === 'html') return props.htmlSnippet || '// Empty HTML snippet'
  if (props.activeTab === 'vue') return props.vueSnippet || '// Empty Vue snippet'
  if (props.activeTab === 'react') return props.reactSnippet || '// Empty React snippet'
  if (props.activeTab === 'swiftui') return props.swiftuiSnippet || '// Empty SwiftUI snippet'
  if (props.activeTab === 'compose') return props.composeSnippet || '// Empty Compose snippet'
  if (props.activeTab === 'tokens') return props.tokenSnippet || '// No token reference'
  if (props.activeTab === 'redline') return props.redlineSnippet || '// Select two layers for redline'
  if (props.activeTab === 'source') return props.fullSourcePreview || '// Source is empty'
  if (props.activeTab === 'rawcss') return props.rawCssPreview || '/* Raw CSS empty */'
  return props.cssSnippet || '/* No CSS for selected layer */'
})

const previewRef = ref(null)
const gutterRef = ref(null)

function decodeUnicodeEscapes(value) {
  const source = String(value || '')
  if (!/\\u[0-9a-fA-F]{4}/.test(source)) return source
  return source.replace(/\\u([0-9a-fA-F]{4})/g, (_m, hex) => {
    const code = Number.parseInt(String(hex || ''), 16)
    if (!Number.isFinite(code)) return _m
    return String.fromCharCode(code)
  })
}

const decodedSnippet = computed(() => decodeUnicodeEscapes(activeSnippet.value))

function lineCountOf(value) {
  return Math.max(1, String(value || '').split(/\r\n|\r|\n/).length)
}

const lineNumbers = computed(() => {
  const total = lineCountOf(decodedSnippet.value)
  let out = ''
  for (let idx = 1; idx <= total; idx += 1) out += `${idx}\n`
  return out.trimEnd()
})

function syncGutterScroll() {
  if (!previewRef.value || !gutterRef.value) return
  gutterRef.value.scrollTop = previewRef.value.scrollTop
}
</script>
