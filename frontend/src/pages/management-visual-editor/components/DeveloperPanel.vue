<template>
  <aside class="fig-panel fig-panel-right fig-dev-panel">
    <div class="fig-dev-head">
      <span class="fig-panel-title">Developer Mode</span>
      <small class="fig-muted">Inspect generated snippets and source</small>
    </div>

    <div class="fig-dev-handoff">
      <div class="fig-dev-handoff-head">
        <span class="fig-panel-title">Dev Handoff</span>
        <div class="fig-dev-handoff-actions">
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="copyActiveSnippet">Copy Snippet</button>
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="copyInspectJson">Copy Inspect</button>
        </div>
      </div>
      <div v-if="!handoffInspect" class="fig-inspector-no-style">المنتی انتخاب نشده است.</div>
      <template v-else>
        <div class="fig-dev-handoff-grid">
          <div class="fig-dev-kv"><span>Selector</span><code dir="ltr">{{ handoffInspect.selector || '—' }}</code></div>
          <div class="fig-dev-kv"><span>Tag</span><code dir="ltr">{{ handoffInspect.tag || 'div' }}</code></div>
          <div class="fig-dev-kv"><span>Position</span><code dir="ltr">x:{{ handoffInspect.box.x }} y:{{ handoffInspect.box.y }}</code></div>
          <div class="fig-dev-kv"><span>Size</span><code dir="ltr">{{ handoffInspect.box.width }} × {{ handoffInspect.box.height }}</code></div>
          <div class="fig-dev-kv"><span>Margin</span><code dir="ltr">{{ handoffInspect.margin }}</code></div>
          <div class="fig-dev-kv"><span>Padding</span><code dir="ltr">{{ handoffInspect.padding }}</code></div>
          <div class="fig-dev-kv"><span>Typography</span><code dir="ltr">{{ handoffInspect.typography }}</code></div>
          <div class="fig-dev-kv"><span>Component</span><code dir="ltr">{{ handoffInspect.component }}</code></div>
        </div>
        <div class="fig-dev-kv fig-dev-kv-block">
          <span>Tokens In Use</span>
          <code dir="ltr">{{ handoffInspect.tokens && handoffInspect.tokens.length ? handoffInspect.tokens.join(', ') : 'none' }}</code>
        </div>
      </template>
      <div class="fig-dev-kv fig-dev-kv-block">
        <span>Redline (2 nodes)</span>
        <code dir="ltr">{{ redlineLabel }}</code>
      </div>
      <div class="fig-dev-kv fig-dev-kv-block">
        <span>Measure (Alt + Hover)</span>
        <code dir="ltr">{{ measureLabel }}</code>
      </div>
    </div>

    <CodeSnippetTabs
      :active-tab="snippetTab"
      :css-snippet="cssSnippet"
      :html-snippet="htmlSnippet"
      :vue-snippet="vueSnippet"
      :react-snippet="reactSnippet"
      :swiftui-snippet="swiftuiSnippet"
      :compose-snippet="composeSnippet"
      :token-snippet="tokenSnippet"
      :redline-snippet="redlineSnippet"
      :full-source-preview="fullSourcePreview"
      :raw-css-preview="rawCssPreview"
      @update:active-tab="$emit('update:snippet-tab', $event)"
    />

    <div class="fig-source-wrap">
      <div class="fig-source-toolbar">
        <span class="fig-panel-title">کد منبع</span>
        <small class="fig-muted">هر ذخیره یک نسخه جدید می‌سازد</small>
      </div>

      <details class="fig-element-builder">
        <summary class="fig-element-builder-head">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          افزودن المنت جدید
        </summary>

        <div class="fig-element-grid">
          <label class="fig-field">
            <span>Tag</span>
            <select class="fig-select" :value="newElementForm.tag" @change="updateField('tag', $event.target.value)">
              <option v-for="tag in availableElementTags" :key="tag" :value="tag">{{ tag }}</option>
              <option value="custom">custom...</option>
            </select>
          </label>

          <label class="fig-field" v-if="newElementForm.tag === 'custom'">
            <span>Custom Tag</span>
            <input class="fig-input" :value="newElementForm.customTag" dir="ltr" placeholder="my-card" @input="updateField('customTag', $event.target.value)" />
          </label>

          <label class="fig-field">
            <span>ID</span>
            <input class="fig-input" :value="newElementForm.id" dir="ltr" placeholder="hero-main" @input="updateField('id', $event.target.value)" />
          </label>

          <label class="fig-field">
            <span>Class</span>
            <input class="fig-input" :value="newElementForm.className" dir="ltr" placeholder="card glass" @input="updateField('className', $event.target.value)" />
          </label>

          <label class="fig-field">
            <span>Text</span>
            <input class="fig-input" :value="newElementForm.text" placeholder="متن المنت" @input="updateField('text', $event.target.value)" />
          </label>

          <label class="fig-field" v-if="newElementForm.tag === 'a'">
            <span>Href</span>
            <input class="fig-input" :value="newElementForm.href" dir="ltr" @input="updateField('href', $event.target.value)" />
          </label>

          <label class="fig-field" v-if="newElementForm.tag === 'img'">
            <span>Src</span>
            <input class="fig-input" :value="newElementForm.src" dir="ltr" @input="updateField('src', $event.target.value)" />
          </label>
        </div>

        <div class="fig-element-actions">
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('insert-snippet')">افزودن به کد</button>
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('add-element')">افزودن به پیش‌نمایش</button>
        </div>
      </details>

      <div class="fig-code-editor" :style="{ '--fig-code-font-size': `${codeFontSize}px` }">
        <div class="fig-code-editor-head">
          <span class="fig-code-editor-lang">SOURCE</span>
          <div class="fig-code-editor-actions">
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="toggleDecodeUnicode">
              {{ decodeUnicode ? 'Unicode: On' : 'Unicode: Off' }}
            </button>
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="decreaseFontSize">A-</button>
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="increaseFontSize">A+</button>
          </div>
        </div>
        <div class="fig-code-editor-body">
          <pre ref="sourceGutterRef" class="fig-code-gutter" aria-hidden="true">{{ sourceLineNumbers }}</pre>
          <textarea
            class="fig-code-area fig-code-area-ide"
            :ref="setSourceEditorRef"
            :value="sourceEditorValue"
            spellcheck="false"
            @input="onSourceInput"
            @scroll="syncSourceGutter"
            @click="syncSourceCaret"
            @keyup="syncSourceCaret"
          ></textarea>
        </div>
        <div class="fig-code-editor-foot">Ln {{ sourceCaret.line }}, Col {{ sourceCaret.col }}</div>
      </div>

      <div class="fig-code-editor fig-code-editor-sm" :style="{ '--fig-code-font-size': `${codeFontSize}px` }">
        <div class="fig-code-editor-head">
          <span class="fig-code-editor-lang">RAW CSS</span>
        </div>
        <div class="fig-code-editor-body">
          <pre ref="rawCssGutterRef" class="fig-code-gutter" aria-hidden="true">{{ rawCssLineNumbers }}</pre>
          <textarea
            ref="rawCssEditorRef"
            class="fig-code-area fig-code-area-ide"
            :value="rawCssEditorValue"
            rows="10"
            spellcheck="false"
            dir="ltr"
            @input="onRawCssInput"
            @scroll="syncRawCssGutter"
            @click="syncRawCssCaret"
            @keyup="syncRawCssCaret"
          ></textarea>
        </div>
        <div class="fig-code-editor-foot">Ln {{ rawCssCaret.line }}, Col {{ rawCssCaret.col }}</div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import CodeSnippetTabs from './CodeSnippetTabs.vue'

const props = defineProps({
  snippetTab: { type: String, default: 'css' },
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
  sourceCode: { type: String, default: '' },
  rawCss: { type: String, default: '' },
  handoffInspect: { type: Object, default: null },
  handoffRedline: { type: Object, default: null },
  handoffMeasure: { type: Object, default: () => ({ visible: false, dx: null, dy: null, target: '' }) },
  newElementForm: { type: Object, required: true },
  availableElementTags: { type: Array, default: () => [] },
  setSourceTextareaRef: { type: Function, required: true },
})

const emit = defineEmits([
  'update:snippet-tab',
  'update:source-code',
  'update:raw-css',
  'update:new-element-form',
  'insert-snippet',
  'add-element',
])

const decodeUnicode = ref(true)
const codeFontSize = ref(12)
const sourceEditorRef = ref(null)
const sourceGutterRef = ref(null)
const rawCssEditorRef = ref(null)
const rawCssGutterRef = ref(null)
const sourceCaret = ref({ line: 1, col: 1 })
const rawCssCaret = ref({ line: 1, col: 1 })

function updateField(key, value) {
  emit('update:new-element-form', { ...props.newElementForm, [key]: value })
}

function decodeUnicodeEscapes(value) {
  const source = String(value || '')
  if (!decodeUnicode.value || !/\\u[0-9a-fA-F]{4}/.test(source)) return source
  return source.replace(/\\u([0-9a-fA-F]{4})/g, (_m, hex) => {
    const code = Number.parseInt(String(hex || ''), 16)
    if (!Number.isFinite(code)) return _m
    return String.fromCharCode(code)
  })
}

function setSourceEditorRef(el) {
  sourceEditorRef.value = el || null
  if (typeof props.setSourceTextareaRef === 'function') props.setSourceTextareaRef(el || null)
  syncSourceCaret()
}

function lineCountOf(value) {
  return Math.max(1, String(value || '').split(/\r\n|\r|\n/).length)
}

function buildLineNumberText(lineCount) {
  const count = Math.max(1, Number(lineCount || 1))
  let out = ''
  for (let idx = 1; idx <= count; idx += 1) out += `${idx}\n`
  return out.trimEnd()
}

function resolveCaretFromValue(value, position) {
  const text = String(value || '')
  const cursor = Math.max(0, Math.min(text.length, Number(position || 0)))
  const before = text.slice(0, cursor)
  const lines = before.split(/\r\n|\r|\n/)
  return {
    line: Math.max(1, lines.length),
    col: Math.max(1, String(lines[lines.length - 1] || '').length + 1),
  }
}

function syncSourceCaret() {
  const el = sourceEditorRef.value
  if (!el) return
  sourceCaret.value = resolveCaretFromValue(el.value, el.selectionStart)
}

function syncRawCssCaret() {
  const el = rawCssEditorRef.value
  if (!el) return
  rawCssCaret.value = resolveCaretFromValue(el.value, el.selectionStart)
}

function syncSourceGutter() {
  if (!sourceEditorRef.value || !sourceGutterRef.value) return
  sourceGutterRef.value.scrollTop = sourceEditorRef.value.scrollTop
}

function syncRawCssGutter() {
  if (!rawCssEditorRef.value || !rawCssGutterRef.value) return
  rawCssGutterRef.value.scrollTop = rawCssEditorRef.value.scrollTop
}

const sourceEditorValue = computed(() => decodeUnicodeEscapes(props.sourceCode))
const rawCssEditorValue = computed(() => decodeUnicodeEscapes(props.rawCss))
const sourceLineNumbers = computed(() => buildLineNumberText(lineCountOf(sourceEditorValue.value)))
const rawCssLineNumbers = computed(() => buildLineNumberText(lineCountOf(rawCssEditorValue.value)))

function onSourceInput(event) {
  emit('update:source-code', event?.target?.value || '')
  syncSourceCaret()
}

function onRawCssInput(event) {
  emit('update:raw-css', event?.target?.value || '')
  syncRawCssCaret()
}

function toggleDecodeUnicode() {
  decodeUnicode.value = !decodeUnicode.value
}

function decreaseFontSize() {
  codeFontSize.value = Math.max(11, Number(codeFontSize.value || 12) - 1)
}

function increaseFontSize() {
  codeFontSize.value = Math.min(18, Number(codeFontSize.value || 12) + 1)
}

const activeSnippet = computed(() => {
  if (props.snippetTab === 'html') return props.htmlSnippet || ''
  if (props.snippetTab === 'vue') return props.vueSnippet || ''
  if (props.snippetTab === 'react') return props.reactSnippet || ''
  if (props.snippetTab === 'swiftui') return props.swiftuiSnippet || ''
  if (props.snippetTab === 'compose') return props.composeSnippet || ''
  if (props.snippetTab === 'tokens') return props.tokenSnippet || ''
  if (props.snippetTab === 'redline') return props.redlineSnippet || ''
  if (props.snippetTab === 'source') return props.fullSourcePreview || ''
  if (props.snippetTab === 'rawcss') return props.rawCssPreview || ''
  return props.cssSnippet || ''
})

const measureLabel = computed(() => {
  const row = props.handoffMeasure || {}
  if (!row.visible) return 'no active measure'
  const parts = []
  if (Number.isFinite(Number(row.dx))) parts.push(`dx:${Math.round(Number(row.dx))}`)
  if (Number.isFinite(Number(row.dy))) parts.push(`dy:${Math.round(Number(row.dy))}`)
  if (row.target) parts.push(`target:${row.target}`)
  return parts.join(' | ') || 'measuring...'
})

const redlineLabel = computed(() => {
  const row = props.handoffRedline || null
  if (!row) return 'select exactly 2 layers'
  const parts = [
    `dx:${Math.round(Number(row?.delta?.x || 0))}`,
    `dy:${Math.round(Number(row?.delta?.y || 0))}`,
    `gapX:${Math.round(Number(row?.gap?.x || 0))}`,
    `gapY:${Math.round(Number(row?.gap?.y || 0))}`,
    `dist:${Math.round(Number(row?.center_distance || 0))}`,
  ]
  const aligns = Array.isArray(row?.alignment?.matched) ? row.alignment.matched : []
  if (aligns.length) parts.push(`align:${aligns.join('/')}`)
  return parts.join(' | ')
})

async function copyText(text) {
  const value = String(text || '')
  if (!value) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
      return
    }
  } catch {
    // noop
  }
  const input = document.createElement('textarea')
  input.value = value
  input.style.position = 'fixed'
  input.style.opacity = '0'
  document.body.appendChild(input)
  input.select()
  try { document.execCommand('copy') } catch { /* noop */ }
  input.remove()
}

function copyActiveSnippet() {
  void copyText(activeSnippet.value)
}

function copyInspectJson() {
  const payload = { inspect: props.handoffInspect || null, redline: props.handoffRedline || null }
  void copyText(JSON.stringify(payload, null, 2))
}
</script>
