<template>
  <label
    class="fig-prop-row"
    :class="{ 'fig-prop-row-overridden': canRevert }"
    @keydown.esc.stop="onEscapeFromField"
  >
    <span
      class="fig-prop-label"
      :class="{ 'fig-prop-label-scrub': canScrubLabel }"
      @mousedown="onLabelScrubStart"
    >
      <span class="fig-prop-label-text">
        <template v-for="(part, idx) in labelHighlightParts" :key="`hl-${fieldKey}-${idx}`">
          <mark v-if="part.match" class="fig-prop-highlight">{{ part.text }}</mark>
          <span v-else>{{ part.text }}</span>
        </template>
      </span>
      <small v-if="mixed" class="fig-prop-mixed-tag">Mixed</small>
    </span>

    <div class="fig-prop-control">
      <template v-if="isColor">
        <div class="fig-inline-control-row fig-inline-control-row-color">
          <ColorPickerField
            :model-value="value"
            :presets="options"
            @update:model-value="$emit('color-change', field.key, $event)"
          />
          <div class="fig-prop-actions" :class="{ 'fig-prop-actions-open': quickMenuOpen }">
            <button
              class="fig-icon-btn"
              type="button"
              title="Reset"
              :disabled="!canRevert"
              @click.stop.prevent="onRevertField"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg>
            </button>
            <button class="fig-icon-btn" type="button" title="Quick actions" @click.stop.prevent="toggleQuickMenu">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
            </button>
            <div v-if="quickMenuOpen" class="fig-prop-quick-menu" @mousedown.stop>
              <button type="button" @click="applyQuickAction('clear')">Clear</button>
              <button type="button" @click="applyQuickAction('copy')">Copy value</button>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="isBoxField && !mixed">
        <div class="fig-box-field">
          <div class="fig-inline-control-row fig-inline-control-row-with-unit">
            <input
              class="fig-prop-input"
              dir="ltr"
              :list="spacingExpressionListId"
              :value="spacingExpressionDraft"
              placeholder="8 12 8 12"
              @input="onSpacingExpressionInput($event.target.value)"
              @blur="applySpacingExpressionDraft"
              @keydown.enter.prevent="applySpacingExpressionDraft"
            />
            <select class="fig-prop-select fig-prop-select-unit" :value="boxUnitDraft" @change="onBoxUnitChange" dir="ltr">
              <option v-for="unit in unitOptions" :key="`box-unit-${unit}`" :value="unit">{{ unit || 'number' }}</option>
            </select>
            <div class="fig-prop-actions" :class="{ 'fig-prop-actions-open': quickMenuOpen }">
              <button
                class="fig-icon-btn"
                type="button"
                title="Reset"
                :disabled="!canRevert"
                @click.stop.prevent="onRevertField"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg>
              </button>
              <button
                class="fig-icon-btn"
                type="button"
                :title="isBoxLinked ? 'Split sides' : 'Link sides'"
                @click.stop.prevent="toggleBoxLinked"
              >
                <svg v-if="isBoxLinked" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 13a5 5 0 0 0 7.1 0l2.8-2.8a5 5 0 0 0-7.1-7.1L11 4.8"/><path d="M14 11a5 5 0 0 0-7.1 0L4 13.8a5 5 0 0 0 7.1 7.1l1.8-1.8"/></svg>
                <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 14l-2 2a4 4 0 1 1-6-6l2-2"/><path d="M14 10l2-2a4 4 0 1 1 6 6l-2 2"/><path d="M8 16l8-8"/></svg>
              </button>
              <button class="fig-icon-btn" type="button" title="Quick actions" @click.stop.prevent="toggleQuickMenu">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
              </button>
              <div v-if="quickMenuOpen" class="fig-prop-quick-menu" @mousedown.stop>
                <button type="button" @click="applyQuickAction('clear')">Clear</button>
                <button v-if="boxAllowsAuto" type="button" @click="applyQuickAction('auto')">Set auto</button>
                <button type="button" @click="applyQuickAction('normalize')">Normalize</button>
                <button type="button" @click="applyQuickAction('copy')">Copy value</button>
              </div>
            </div>
            <datalist :id="spacingExpressionListId">
              <option v-for="opt in spacingExpressionSuggestions" :key="`sp-${fieldKey}-${opt}`" :value="opt"></option>
            </datalist>
          </div>

          <div v-if="boxCanUseNumeric" class="fig-box-grid" :class="{ 'fig-box-grid-linked': isBoxLinked }">
            <label v-if="isBoxLinked" class="fig-box-side fig-box-side-linked">
              <span>ALL</span>
              <input
                class="fig-prop-input"
                type="text"
                dir="ltr"
                :value="boxLinkedNumber"
                @input="onBoxLinkedInput($event.target.value)"
                @keydown="onBoxLinkedKeydown"
                @blur="onBoxDraftBlur"
              />
            </label>
            <label v-for="side in (!isBoxLinked ? BOX_SIDES : [])" :key="`box-side-${side}`" class="fig-box-side">
              <span>{{ sideLabels[side] }}</span>
              <input
                class="fig-prop-input"
                type="text"
                dir="ltr"
                :value="boxSideDraft[side]"
                @input="onBoxSideInput(side, $event.target.value)"
                @keydown="onBoxSideKeydown(side, $event)"
                @blur="onBoxDraftBlur"
              />
            </label>
          </div>

          <div v-if="spacingExpressionError" class="fig-prop-error">{{ spacingExpressionError }}</div>
        </div>
      </template>

      <template v-else>
        <div v-if="options.length" class="fig-inline-control-row">
          <select
            class="fig-prop-select"
            :value="selectValue"
            @change="$emit('preset-change', field.key, $event.target.value)"
            dir="ltr"
          >
            <option v-if="mixed" value="__mixed__" disabled>Mixed</option>
            <option value="">—</option>
            <option v-for="opt in options" :key="`${field.key}-${opt}`" :value="opt">{{ opt }}</option>
            <option value="__custom__">custom…</option>
          </select>
          <div class="fig-prop-actions" :class="{ 'fig-prop-actions-open': quickMenuOpen }">
            <button
              class="fig-icon-btn"
              type="button"
              title="Reset"
              :disabled="!canRevert"
              @click.stop.prevent="onRevertField"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg>
            </button>
            <button class="fig-icon-btn" type="button" title="Quick actions" @click.stop.prevent="toggleQuickMenu">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
            </button>
            <div v-if="quickMenuOpen" class="fig-prop-quick-menu" @mousedown.stop>
              <button type="button" @click="applyQuickAction('clear')">Clear</button>
              <button v-if="allowsAutoKeyword" type="button" @click="applyQuickAction('auto')">Set auto</button>
              <button type="button" @click="applyQuickAction('copy')">Copy value</button>
            </div>
          </div>
        </div>

        <div v-if="(!options.length || showCustomInput) && !(supportsUnitAwareInput && !mixed)" class="fig-inline-control-row">
          <input
            class="fig-prop-input"
            :value="mixed ? '' : value"
            @input="$emit('input-change', field.key, $event.target.value)"
            dir="ltr"
            :placeholder="mixed ? 'Mixed' : '—'"
          />
          <div class="fig-prop-actions" :class="{ 'fig-prop-actions-open': quickMenuOpen }">
            <button
              class="fig-icon-btn"
              type="button"
              title="Reset"
              :disabled="!canRevert"
              @click.stop.prevent="onRevertField"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg>
            </button>
            <button class="fig-icon-btn" type="button" title="Quick actions" @click.stop.prevent="toggleQuickMenu">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
            </button>
            <div v-if="quickMenuOpen" class="fig-prop-quick-menu" @mousedown.stop>
              <button type="button" @click="applyQuickAction('clear')">Clear</button>
              <button type="button" @click="applyQuickAction('copy')">Copy value</button>
            </div>
          </div>
        </div>

        <div
          v-if="(!options.length || showCustomInput) && supportsUnitAwareInput && !mixed"
          class="fig-inline-control-row fig-inline-control-row-with-unit"
        >
          <input
            class="fig-prop-input fig-prop-input-number"
            type="text"
            inputmode="decimal"
            dir="ltr"
            :value="numericDraftValue"
            :placeholder="numericHasComplex ? 'custom' : '0'"
            @input="onNumericDraftInput($event.target.value)"
            @keydown="onNumericInputKeydown"
            @blur="onNumericInputBlur"
          />
          <select class="fig-prop-select fig-prop-select-unit" :value="numericUnitDraft" @change="onNumericUnitChange" dir="ltr">
            <option v-for="unit in unitOptions" :key="`unit-${unit}`" :value="unit">{{ unit || 'number' }}</option>
          </select>
          <div class="fig-prop-actions" :class="{ 'fig-prop-actions-open': quickMenuOpen }">
            <button
              class="fig-icon-btn"
              type="button"
              title="Reset"
              :disabled="!canRevert"
              @click.stop.prevent="onRevertField"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg>
            </button>
            <button class="fig-icon-btn" type="button" title="Quick actions" @click.stop.prevent="toggleQuickMenu">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
            </button>
            <div v-if="quickMenuOpen" class="fig-prop-quick-menu" @mousedown.stop>
              <button type="button" @click="applyQuickAction('clear')">Clear</button>
              <button v-if="allowsAutoKeyword" type="button" @click="applyQuickAction('auto')">Set auto</button>
              <button type="button" @click="applyQuickAction('normalize')">Normalize</button>
              <button type="button" @click="applyQuickAction('copy')">Copy value</button>
            </div>
          </div>
        </div>

        <div v-if="numericInputError" class="fig-prop-error">{{ numericInputError }}</div>
      </template>
    </div>
  </label>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import ColorPickerField from './ColorPickerField.vue'

const BOX_SIDES = ['top', 'right', 'bottom', 'left']
const BOX_FIELD_KEYS = new Set(['margin', 'padding', 'borderRadius'])
const UNIT_AWARE_FIELD_KEYS = new Set([
  'width', 'minWidth', 'maxWidth',
  'height', 'minHeight', 'maxHeight',
  'top', 'right', 'bottom', 'left',
  'gap', 'fontSize', 'lineHeight', 'letterSpacing',
  'rotation',
  'borderWidth', 'borderRadius',
  'margin', 'padding', 'opacity', 'zIndex', 'transitionDuration',
])
const AUTO_FIELD_KEYS = new Set([
  'width', 'minWidth', 'maxWidth',
  'height', 'minHeight', 'maxHeight',
  'top', 'right', 'bottom', 'left',
  'margin',
])
const MATH_ALLOWED_RE = /^[0-9+\-*/().\s]+$/
const KNOWN_UNITS = ['vmax', 'vmin', 'rem', 'vh', 'vw', 'deg', 'px', 'em', 'pt', 'ms', 's', '%']

const props = defineProps({
  field: { type: Object, required: true },
  value: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  selectValue: { type: String, default: '' },
  showCustomInput: { type: Boolean, default: false },
  mixed: { type: Boolean, default: false },
  isColor: { type: Boolean, default: false },
  overridden: { type: Boolean, default: false },
  highlightQuery: { type: String, default: '' },
})

const emit = defineEmits(['preset-change', 'input-change', 'color-change', 'revert-field'])

const sideLabels = { top: 'T', right: 'R', bottom: 'B', left: 'L' }
const unitOptions = ['', 'px', '%', 'rem', 'em', 'vh', 'vw', 'deg', 's', 'ms']
const numericUnitDraft = ref('px')
const numericDraftValue = ref('')
const numericHasComplex = ref(false)
const numericInputError = ref('')
const boxUnitDraft = ref('px')
const boxSideDraft = ref({ top: '', right: '', bottom: '', left: '' })
const boxLinkedOverride = ref(null)
const spacingExpressionDraft = ref('')
const spacingExpressionError = ref('')
const quickMenuOpen = ref(false)

let scrubStopHandler = null
let quickMenuOutsideHandler = null

function normalizeFieldKey(value) {
  return String(value || '').trim()
}

const fieldKey = computed(() => normalizeFieldKey(props.field?.key))
const isBoxField = computed(() => BOX_FIELD_KEYS.has(fieldKey.value))
const supportsUnitAwareInput = computed(() => UNIT_AWARE_FIELD_KEYS.has(fieldKey.value))
const allowsAutoKeyword = computed(() => AUTO_FIELD_KEYS.has(fieldKey.value))
const boxAllowsAuto = computed(() => fieldKey.value === 'margin')
const canRevert = computed(() => Boolean(props.overridden || props.mixed))
const spacingExpressionListId = computed(() => {
  const key = fieldKey.value.replace(/[^a-z0-9_-]/gi, '-')
  return `fig-spacing-${key || 'field'}`
})
const labelHighlightParts = computed(() => splitHighlightParts(String(props.field?.label || ''), props.highlightQuery))

function defaultUnitForField(key) {
  const fieldName = normalizeFieldKey(key)
  if (fieldName === 'opacity') return ''
  if (fieldName === 'lineHeight') return ''
  if (fieldName === 'fontWeight') return ''
  if (fieldName === 'zIndex') return ''
  if (fieldName === 'rotation') return 'deg'
  if (fieldName === 'transitionDuration') return 's'
  return 'px'
}

function parseNumericToken(value, fallbackUnit = 'px') {
  const raw = String(value || '').trim()
  if (!raw) return { number: '', unit: fallbackUnit, raw: '', empty: true, complex: false, auto: false }
  if (raw.toLowerCase() === 'auto') return { number: '', unit: fallbackUnit, raw, empty: false, complex: false, auto: true }
  const match = raw.match(/^(-?\d+(?:\.\d+)?)\s*(px|%|rem|em|vh|vw|vmin|vmax|pt|deg|s|ms)?$/i)
  if (!match) return { number: '', unit: fallbackUnit, raw, empty: false, complex: true, auto: false }
  return {
    number: String(match[1] || ''),
    unit: String(match[2] || fallbackUnit || ''),
    raw,
    empty: false,
    complex: false,
    auto: false,
  }
}

function formatNumber(value, precision = 2) {
  const number = Number(value)
  if (!Number.isFinite(number)) return ''
  const fixed = number.toFixed(Math.max(0, precision))
  return fixed.replace(/\.?0+$/, '')
}

function formatNumericCss(numberValue, unitValue = '') {
  const parsed = Number(numberValue)
  if (!Number.isFinite(parsed)) return ''
  const precision = Math.abs(parsed % 1) > 0 ? 2 : 0
  const normalized = formatNumber(parsed, precision)
  return `${normalized}${unitValue || ''}`
}

function splitBoxTokens(value) {
  const rawTokens = String(value || '').trim().split(/\s+/).filter(Boolean)
  if (!rawTokens.length) return ['', '', '', '']
  if (rawTokens.length === 1) return [rawTokens[0], rawTokens[0], rawTokens[0], rawTokens[0]]
  if (rawTokens.length === 2) return [rawTokens[0], rawTokens[1], rawTokens[0], rawTokens[1]]
  if (rawTokens.length === 3) return [rawTokens[0], rawTokens[1], rawTokens[2], rawTokens[1]]
  return [rawTokens[0], rawTokens[1], rawTokens[2], rawTokens[3]]
}

function buildBoxShorthand(tokens) {
  const rows = Array.isArray(tokens) ? tokens.map((row) => String(row || '').trim() || '0') : ['0', '0', '0', '0']
  const [t, r, b, l] = rows
  if (t === r && t === b && t === l) return t
  if (t === b && r === l) return `${t} ${r}`
  if (r === l) return `${t} ${r} ${b}`
  return `${t} ${r} ${b} ${l}`
}

function splitHighlightParts(label, query) {
  const source = String(label || '')
  const term = String(query || '').trim()
  if (!term) return [{ text: source, match: false }]
  const lowerSource = source.toLowerCase()
  const lowerTerm = term.toLowerCase()
  if (!lowerTerm) return [{ text: source, match: false }]
  const output = []
  let cursor = 0
  while (cursor < source.length) {
    const index = lowerSource.indexOf(lowerTerm, cursor)
    if (index < 0) break
    if (index > cursor) output.push({ text: source.slice(cursor, index), match: false })
    output.push({ text: source.slice(index, index + lowerTerm.length), match: true })
    cursor = index + lowerTerm.length
  }
  if (cursor < source.length) output.push({ text: source.slice(cursor), match: false })
  return output.length ? output : [{ text: source, match: false }]
}

function extractUnitFromExpression(raw, fallbackUnit = 'px') {
  const source = String(raw || '').trim()
  const lower = source.toLowerCase()
  for (const unit of KNOWN_UNITS) {
    if (!lower.endsWith(unit)) continue
    const expression = source.slice(0, source.length - unit.length).trim()
    if (!expression) continue
    return { expression, unit }
  }
  return { expression: source, unit: String(fallbackUnit || '') }
}

function isBalancedExpression(value) {
  const text = String(value || '')
  let depth = 0
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i]
    if (ch === '(') depth += 1
    if (ch === ')') {
      depth -= 1
      if (depth < 0) return false
    }
  }
  return depth === 0
}

function evaluateMathExpression(value) {
  const source = String(value || '').trim()
  if (!source) return null
  if (!MATH_ALLOWED_RE.test(source)) return null
  if (!isBalancedExpression(source)) return null
  const compact = source.replace(/\s+/g, '')
  if (!compact || /[+\-*/.]$/.test(compact)) return null
  try {
    const result = Function(`"use strict"; return (${compact})`)()
    return Number.isFinite(result) ? result : null
  } catch {
    return null
  }
}

function parseNumericInputDraft(value, fallbackUnit = 'px', options = {}) {
  const allowAuto = options?.allowAuto !== false
  const raw = String(value || '').trim()
  if (!raw) return { valid: true, empty: true, auto: false, number: '', unit: fallbackUnit, raw }
  if (allowAuto && raw.toLowerCase() === 'auto') {
    return { valid: true, empty: false, auto: true, number: '', unit: fallbackUnit, raw }
  }

  const direct = parseNumericToken(raw, fallbackUnit)
  if (!direct.complex) {
    if (direct.auto && !allowAuto) return { valid: false, empty: false, auto: false, number: '', unit: fallbackUnit, raw }
    return {
      valid: true,
      empty: false,
      auto: direct.auto,
      number: direct.number,
      unit: direct.unit || fallbackUnit || '',
      raw,
    }
  }

  const extracted = extractUnitFromExpression(raw, fallbackUnit)
  const evaluated = evaluateMathExpression(extracted.expression)
  if (!Number.isFinite(evaluated)) {
    return { valid: false, empty: false, auto: false, number: '', unit: extracted.unit || fallbackUnit || '', raw }
  }

  return {
    valid: true,
    empty: false,
    auto: false,
    number: formatNumber(evaluated, 4),
    unit: extracted.unit || fallbackUnit || '',
    raw,
  }
}

function parseSpacingExpression(value, options = {}) {
  const fallbackUnit = String(options?.fallbackUnit ?? 'px')
  const allowAuto = Boolean(options?.allowAuto)
  const raw = String(value || '').trim().replace(/,/g, ' ')
  if (!raw) return { valid: true, empty: true, value: '', tokens: [] }
  const tokens = raw.split(/\s+/).filter(Boolean)
  if (!tokens.length || tokens.length > 4) return { valid: false, empty: false, value: raw, tokens: [] }

  const normalized = []
  for (const tokenRaw of tokens) {
    const token = String(tokenRaw || '').trim()
    if (!token) return { valid: false, empty: false, value: raw, tokens: [] }
    const parsed = parseNumericInputDraft(token, fallbackUnit, { allowAuto })
    if (!parsed.valid || parsed.empty) return { valid: false, empty: false, value: raw, tokens: [] }
    if (parsed.auto) normalized.push('auto')
    else normalized.push(formatNumericCss(parsed.number, parsed.unit || fallbackUnit || ''))
  }

  return {
    valid: true,
    empty: false,
    value: buildBoxShorthand(normalized),
    tokens: normalized,
  }
}

function looksLikeComplexSpacingExpression(value) {
  const raw = String(value || '').trim()
  if (!raw) return false
  return /(calc|clamp|min|max|var)\s*\(/i.test(raw)
}

function formatSpacingToken(numberValue, unitValue) {
  return formatNumericCss(numberValue, unitValue)
}

const boxTokens = computed(() => splitBoxTokens(props.value))
const boxParsedTokens = computed(() => boxTokens.value.map((token) => parseNumericToken(token, defaultUnitForField(fieldKey.value))))
const boxCanUseNumeric = computed(() => boxParsedTokens.value.every((row) => !row.complex && !row.auto))
const boxAllEqual = computed(() => {
  const [t, r, b, l] = boxTokens.value
  return t === r && t === b && t === l
})
const isBoxLinked = computed(() => (boxLinkedOverride.value === null ? boxAllEqual.value : Boolean(boxLinkedOverride.value)))
const boxLinkedNumber = computed(() => String(boxSideDraft.value.top || ''))
const spacingExpressionSuggestions = computed(() => {
  if (!isBoxField.value) return []
  const unit = String(boxUnitDraft.value || defaultUnitForField(fieldKey.value) || '')
  const suggestions = new Set()
  const seeds = [0, 4, 8, 12, 16, 24, 32]
  for (const item of seeds) suggestions.add(formatSpacingToken(item, unit))
  const a = formatSpacingToken(8, unit)
  const b = formatSpacingToken(12, unit)
  const c = formatSpacingToken(16, unit)
  const d = formatSpacingToken(24, unit)
  suggestions.add(`${a} ${b}`)
  suggestions.add(`${a} ${b} ${a} ${b}`)
  suggestions.add(`${a} ${b} ${c} ${d}`)
  if (boxAllowsAuto.value) {
    suggestions.add('auto')
    suggestions.add('0 auto')
    suggestions.add(`${a} auto`)
  }
  return Array.from(suggestions).filter(Boolean)
})

const canScrubLabel = computed(() => {
  if (props.mixed || props.isColor) return false
  if (isBoxField.value) return boxCanUseNumeric.value && isBoxLinked.value
  if (!supportsUnitAwareInput.value) return false
  return !numericHasComplex.value
})

function syncNumericDraftFromValue() {
  const parsed = parseNumericInputDraft(props.value, defaultUnitForField(fieldKey.value), { allowAuto: allowsAutoKeyword.value })
  numericHasComplex.value = !parsed.valid
  numericDraftValue.value = parsed.valid
    ? (parsed.auto ? 'auto' : String(parsed.number || ''))
    : String(props.value || '').trim()
  numericUnitDraft.value = parsed.unit || defaultUnitForField(fieldKey.value)
  numericInputError.value = ''
}

function syncBoxDraftFromValue() {
  const parsed = boxParsedTokens.value
  const firstUnit = parsed.find((row) => row.unit)?.unit
  boxUnitDraft.value = String(firstUnit || defaultUnitForField(fieldKey.value) || 'px')
  boxSideDraft.value = {
    top: parsed[0]?.number || '',
    right: parsed[1]?.number || '',
    bottom: parsed[2]?.number || '',
    left: parsed[3]?.number || '',
  }
}

function syncSpacingExpressionDraftFromValue() {
  spacingExpressionDraft.value = String(props.value || '').trim()
  spacingExpressionError.value = ''
}

function emitNumericDraftValue(nextNumber, unitOverride = null) {
  const numberText = String(nextNumber || '').trim()
  if (!numberText) {
    emit('input-change', fieldKey.value, '')
    return
  }
  const nextUnit = unitOverride !== null ? String(unitOverride || '') : String(numericUnitDraft.value || '')
  const cssValue = formatNumericCss(numberText, nextUnit)
  emit('input-change', fieldKey.value, cssValue)
}

function commitNumericDraft() {
  const parsed = parseNumericInputDraft(numericDraftValue.value, numericUnitDraft.value, { allowAuto: allowsAutoKeyword.value })
  if (!parsed.valid) {
    numericInputError.value = 'Invalid math expression.'
    return false
  }
  numericInputError.value = ''
  if (parsed.empty) {
    emit('input-change', fieldKey.value, '')
    return true
  }
  if (parsed.auto) {
    numericDraftValue.value = 'auto'
    emit('input-change', fieldKey.value, 'auto')
    return true
  }
  numericUnitDraft.value = parsed.unit || numericUnitDraft.value
  numericDraftValue.value = formatNumber(parsed.number, scrubPrecisionForField(fieldKey.value))
  emitNumericDraftValue(numericDraftValue.value, numericUnitDraft.value)
  return true
}

function onNumericDraftInput(value) {
  numericDraftValue.value = String(value || '')
  numericInputError.value = ''
  const parsed = parseNumericInputDraft(numericDraftValue.value, numericUnitDraft.value, { allowAuto: allowsAutoKeyword.value })
  if (!parsed.valid) return
  if (parsed.empty) {
    emit('input-change', fieldKey.value, '')
    return
  }
  if (parsed.auto) {
    emit('input-change', fieldKey.value, 'auto')
    return
  }
  numericUnitDraft.value = parsed.unit || numericUnitDraft.value
  emitNumericDraftValue(parsed.number, numericUnitDraft.value)
}

function onNumericInputBlur() {
  if (!commitNumericDraft()) return
  numericInputError.value = ''
}

function onNumericUnitChange(event) {
  numericUnitDraft.value = String(event?.target?.value || '')
  numericInputError.value = ''
  const parsed = parseNumericInputDraft(numericDraftValue.value, numericUnitDraft.value, { allowAuto: allowsAutoKeyword.value })
  if (!parsed.valid || parsed.empty || parsed.auto) return
  emitNumericDraftValue(parsed.number, numericUnitDraft.value)
}

function resolveNumericStepStart() {
  const first = parseNumericInputDraft(numericDraftValue.value, numericUnitDraft.value, { allowAuto: allowsAutoKeyword.value })
  if (first.valid && !first.empty && !first.auto) return Number.parseFloat(String(first.number || '0'))
  const fallback = parseNumericInputDraft(props.value, numericUnitDraft.value, { allowAuto: allowsAutoKeyword.value })
  if (fallback.valid && !fallback.empty && !fallback.auto) return Number.parseFloat(String(fallback.number || '0'))
  return 0
}

function onNumericInputKeydown(event) {
  const key = String(event?.key || '')
  if (key === 'Enter') {
    event.preventDefault()
    commitNumericDraft()
    return
  }
  if (key === 'Escape') {
    event.preventDefault()
    syncNumericDraftFromValue()
    return
  }
  if (key !== 'ArrowUp' && key !== 'ArrowDown') return
  event.preventDefault()
  const direction = key === 'ArrowUp' ? 1 : -1
  const baseStep = scrubStepForField(fieldKey.value)
  const multiplier = event.shiftKey ? 10 : (event.altKey ? 0.1 : 1)
  const nextNumber = resolveNumericStepStart() + (direction * baseStep * multiplier)
  const precision = scrubPrecisionForField(fieldKey.value)
  numericDraftValue.value = formatNumber(nextNumber, precision)
  numericInputError.value = ''
  emitNumericDraftValue(numericDraftValue.value, numericUnitDraft.value)
}

function resolveBoxDraftTokens(nextSides, options = {}) {
  const force = Boolean(options?.force)
  const unit = String(boxUnitDraft.value || '')
  const sides = nextSides || boxSideDraft.value
  const tokens = []
  for (const side of BOX_SIDES) {
    const raw = String(sides?.[side] || '').trim()
    if (!raw) {
      if (force) {
        tokens.push(formatNumericCss('0', unit))
        continue
      }
      return { valid: false, reason: 'incomplete', tokens: [] }
    }
    const parsed = parseNumericInputDraft(raw, unit, { allowAuto: boxAllowsAuto.value })
    if (!parsed.valid || parsed.empty) return { valid: false, reason: 'invalid', tokens: [] }
    if (parsed.auto) tokens.push('auto')
    else tokens.push(formatNumericCss(parsed.number, parsed.unit || unit))
  }
  return { valid: true, tokens }
}

function emitBoxValueFromDraft(nextSides, options = {}) {
  const parsed = resolveBoxDraftTokens(nextSides, options)
  if (!parsed.valid) return false
  const shorthand = buildBoxShorthand(parsed.tokens)
  emit('input-change', fieldKey.value, shorthand)
  spacingExpressionDraft.value = shorthand
  spacingExpressionError.value = ''
  return true
}

function onBoxUnitChange(event) {
  boxUnitDraft.value = String(event?.target?.value || 'px')
  if (!boxCanUseNumeric.value) return
  emitBoxValueFromDraft(boxSideDraft.value)
}

function onBoxLinkedInput(rawValue) {
  const raw = String(rawValue || '')
  boxSideDraft.value = { top: raw, right: raw, bottom: raw, left: raw }
  spacingExpressionError.value = ''
  emitBoxValueFromDraft(boxSideDraft.value)
}

function onBoxSideInput(side, value) {
  const key = String(side || '').trim().toLowerCase()
  if (!BOX_SIDES.includes(key)) return
  const raw = String(value || '')
  boxSideDraft.value = { ...boxSideDraft.value, [key]: raw }
  spacingExpressionError.value = ''
  emitBoxValueFromDraft(boxSideDraft.value)
}

function onBoxDraftBlur() {
  if (!emitBoxValueFromDraft(boxSideDraft.value, { force: true })) {
    spacingExpressionError.value = 'Invalid value.'
  }
}

function getBoxStepStartForSide(side) {
  const raw = String(boxSideDraft.value?.[side] || '').trim()
  const parsed = parseNumericInputDraft(raw, boxUnitDraft.value, { allowAuto: boxAllowsAuto.value })
  if (parsed.valid && !parsed.empty && !parsed.auto) return Number.parseFloat(String(parsed.number || '0'))
  return 0
}

function onBoxSideKeydown(side, event) {
  const key = String(event?.key || '')
  if (key === 'Enter') {
    event.preventDefault()
    onBoxDraftBlur()
    return
  }
  if (key === 'Escape') {
    event.preventDefault()
    syncBoxDraftFromValue()
    syncSpacingExpressionDraftFromValue()
    return
  }
  if (key !== 'ArrowUp' && key !== 'ArrowDown') return
  event.preventDefault()
  const direction = key === 'ArrowUp' ? 1 : -1
  const baseStep = scrubStepForField(fieldKey.value)
  const multiplier = event.shiftKey ? 10 : (event.altKey ? 0.1 : 1)
  const nextNumber = getBoxStepStartForSide(side) + (direction * baseStep * multiplier)
  const precision = scrubPrecisionForField(fieldKey.value)
  const draft = formatNumber(nextNumber, precision)
  boxSideDraft.value = { ...boxSideDraft.value, [side]: draft }
  emitBoxValueFromDraft(boxSideDraft.value)
}

function onBoxLinkedKeydown(event) {
  const key = String(event?.key || '')
  if (key === 'Enter') {
    event.preventDefault()
    onBoxDraftBlur()
    return
  }
  if (key === 'Escape') {
    event.preventDefault()
    syncBoxDraftFromValue()
    syncSpacingExpressionDraftFromValue()
    return
  }
  if (key !== 'ArrowUp' && key !== 'ArrowDown') return
  event.preventDefault()
  const direction = key === 'ArrowUp' ? 1 : -1
  const baseStep = scrubStepForField(fieldKey.value)
  const multiplier = event.shiftKey ? 10 : (event.altKey ? 0.1 : 1)
  const nextNumber = getBoxStepStartForSide('top') + (direction * baseStep * multiplier)
  const precision = scrubPrecisionForField(fieldKey.value)
  const draft = formatNumber(nextNumber, precision)
  boxSideDraft.value = { top: draft, right: draft, bottom: draft, left: draft }
  emitBoxValueFromDraft(boxSideDraft.value)
}

function onSpacingExpressionInput(value) {
  spacingExpressionDraft.value = String(value || '')
  spacingExpressionError.value = ''
}

function applySpacingExpressionDraft() {
  const raw = String(spacingExpressionDraft.value || '').trim()
  const parsed = parseSpacingExpression(raw, {
    fallbackUnit: boxUnitDraft.value || defaultUnitForField(fieldKey.value),
    allowAuto: boxAllowsAuto.value,
  })
  if (parsed.valid) {
    spacingExpressionError.value = ''
    emit('input-change', fieldKey.value, parsed.value)
    return
  }
  if (!raw) {
    spacingExpressionError.value = ''
    emit('input-change', fieldKey.value, '')
    return
  }
  if (looksLikeComplexSpacingExpression(raw)) {
    spacingExpressionError.value = ''
    emit('input-change', fieldKey.value, raw)
    return
  }
  spacingExpressionError.value = 'Invalid spacing expression.'
}

function toggleBoxLinked() {
  const next = !isBoxLinked.value
  boxLinkedOverride.value = next
  if (next) {
    const top = String(boxSideDraft.value.top || '0')
    boxSideDraft.value = { top, right: top, bottom: top, left: top }
    emitBoxValueFromDraft(boxSideDraft.value, { force: true })
  }
}

function scrubPrecisionForField(key) {
  const fieldName = normalizeFieldKey(key)
  if (fieldName === 'opacity') return 2
  if (fieldName === 'lineHeight') return 2
  if (fieldName === 'letterSpacing') return 2
  if (fieldName === 'rotation') return 1
  return 0
}

function scrubStepForField(key) {
  const fieldName = normalizeFieldKey(key)
  if (fieldName === 'opacity') return 0.01
  if (fieldName === 'lineHeight') return 0.05
  if (fieldName === 'letterSpacing') return 0.1
  if (fieldName === 'rotation') return 1
  return 1
}

function stopLabelScrub() {
  if (typeof scrubStopHandler === 'function') scrubStopHandler()
  scrubStopHandler = null
}

function startLabelScrub(event, startValue, onApply) {
  if (!Number.isFinite(startValue)) return
  const stepBase = scrubStepForField(fieldKey.value)
  const precision = scrubPrecisionForField(fieldKey.value)
  const originX = Number(event?.clientX || 0)
  let lastUnits = 0
  let raf = null

  const onMove = (moveEvent) => {
    if (raf !== null) return
    raf = window.requestAnimationFrame(() => {
      raf = null
      const deltaX = Number(moveEvent?.clientX || 0) - originX
      const units = Math.trunc(deltaX / 4)
      if (units === lastUnits) return
      lastUnits = units
      const multiplier = moveEvent?.shiftKey ? 10 : (moveEvent?.altKey ? 0.1 : 1)
      const nextNumber = Number(formatNumber(startValue + (units * stepBase * multiplier), precision))
      onApply(nextNumber)
    })
  }

  const onUp = () => {
    if (raf !== null) window.cancelAnimationFrame(raf)
    window.removeEventListener('mousemove', onMove, true)
    window.removeEventListener('mouseup', onUp, true)
    scrubStopHandler = null
  }

  window.addEventListener('mousemove', onMove, true)
  window.addEventListener('mouseup', onUp, true)
  scrubStopHandler = onUp
}

function onLabelScrubStart(event) {
  if (!canScrubLabel.value) return
  if (Number(event?.button || 0) !== 0) return
  event.preventDefault()
  event.stopPropagation()
  stopLabelScrub()

  if (isBoxField.value) {
    const start = Number.parseFloat(String(boxSideDraft.value.top || '0'))
    if (!Number.isFinite(start)) return
    startLabelScrub(event, start, (nextNumber) => {
      const next = formatNumber(nextNumber, scrubPrecisionForField(fieldKey.value))
      boxSideDraft.value = { top: next, right: next, bottom: next, left: next }
      emitBoxValueFromDraft(boxSideDraft.value, { force: true })
    })
    return
  }

  const start = Number.parseFloat(String(resolveNumericStepStart() || '0'))
  if (!Number.isFinite(start)) return
  startLabelScrub(event, start, (nextNumber) => {
    const next = formatNumber(nextNumber, scrubPrecisionForField(fieldKey.value))
    numericDraftValue.value = next
    emitNumericDraftValue(next)
  })
}

function closeQuickMenu() {
  quickMenuOpen.value = false
}

function bindQuickMenuOutsideClose() {
  if (quickMenuOutsideHandler) return
  quickMenuOutsideHandler = (event) => {
    const target = event?.target
    if (target && typeof target.closest === 'function' && target.closest('.fig-prop-actions')) return
    closeQuickMenu()
  }
  window.addEventListener('mousedown', quickMenuOutsideHandler, true)
}

function unbindQuickMenuOutsideClose() {
  if (!quickMenuOutsideHandler) return
  window.removeEventListener('mousedown', quickMenuOutsideHandler, true)
  quickMenuOutsideHandler = null
}

function toggleQuickMenu() {
  quickMenuOpen.value = !quickMenuOpen.value
}

async function copyCurrentValueToClipboard() {
  try {
    const text = String(props.value || '').trim()
    if (!text || !navigator?.clipboard?.writeText) return
    await navigator.clipboard.writeText(text)
  } catch {
    // noop
  }
}

function applyQuickAction(action) {
  const type = String(action || '').trim()
  if (!type) return
  if (type === 'clear') emit('input-change', fieldKey.value, '')
  if (type === 'auto') emit('input-change', fieldKey.value, 'auto')
  if (type === 'normalize') {
    if (isBoxField.value) applySpacingExpressionDraft()
    else commitNumericDraft()
  }
  if (type === 'copy') copyCurrentValueToClipboard()
  closeQuickMenu()
}

function onRevertField() {
  if (!canRevert.value) return
  spacingExpressionError.value = ''
  numericInputError.value = ''
  emit('revert-field', fieldKey.value)
  closeQuickMenu()
}

function onEscapeFromField() {
  if (isBoxField.value) {
    syncBoxDraftFromValue()
    syncSpacingExpressionDraftFromValue()
  } else {
    syncNumericDraftFromValue()
  }
  closeQuickMenu()
}

watch(
  () => [fieldKey.value, props.value],
  () => {
    if (isBoxField.value) {
      syncBoxDraftFromValue()
      syncSpacingExpressionDraftFromValue()
    } else {
      syncNumericDraftFromValue()
    }
  },
  { immediate: true }
)

watch(
  () => fieldKey.value,
  () => {
    boxLinkedOverride.value = null
  }
)

watch(
  () => quickMenuOpen.value,
  (isOpen) => {
    if (isOpen) bindQuickMenuOutsideClose()
    else unbindQuickMenuOutsideClose()
  }
)

onBeforeUnmount(() => {
  stopLabelScrub()
  unbindQuickMenuOutsideClose()
})
</script>
