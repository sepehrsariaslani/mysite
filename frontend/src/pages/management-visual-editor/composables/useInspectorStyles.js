import { computed, ref } from 'vue'

export function toKebabStyleKey(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('--')) return raw
  return raw
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}

export function toStyleObjectKey(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('--')) return raw
  if (!raw.includes('-')) return raw
  return raw
    .toLowerCase()
    .replace(/-([a-z0-9])/g, (_, char) => char.toUpperCase())
}

export function createDefaultVisualProps() {
  return {
    text_content: '',
    display: '',
    flexDirection: '',
    justifyContent: '',
    alignItems: '',
    flexWrap: '',
    flexGrow: '',
    flexShrink: '',
    gap: '',
    color: '',
    fontSize: '',
    fontWeight: '',
    lineHeight: '',
    letterSpacing: '',
    textAlign: '',
    backgroundColor: '',
    borderColor: '',
    borderWidth: '',
    borderRadius: '',
    boxShadow: '',
    opacity: '',
    zIndex: '',
    width: '',
    minWidth: '',
    maxWidth: '',
    height: '',
    minHeight: '',
    maxHeight: '',
    overflowX: '',
    overflowY: '',
    margin: '',
    padding: '',
    transitionDuration: '',
    position: '',
    top: '',
    right: '',
    bottom: '',
    left: '',
  }
}

const COLOR_FIELDS = new Set(['color', 'backgroundColor', 'borderColor'])

const STYLE_FIELD_OPTIONS = {
  display: ['block', 'inline', 'inline-block', 'flex', 'inline-flex', 'grid', 'inline-grid', 'none'],
  flexDirection: ['row', 'row-reverse', 'column', 'column-reverse'],
  justifyContent: ['flex-start', 'center', 'flex-end', 'space-between', 'space-around', 'space-evenly'],
  alignItems: ['stretch', 'flex-start', 'center', 'flex-end', 'baseline'],
  flexWrap: ['nowrap', 'wrap', 'wrap-reverse'],
  flexGrow: ['0', '1'],
  flexShrink: ['0', '1'],
  gap: ['0', '4px', '8px', '12px', '16px', '20px', '24px', '32px'],
  color: ['inherit', '#111111', '#ffffff', '#6b7280', 'var(--text-main)', 'var(--admin-text-soft)'],
  fontSize: ['12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px', '1rem', '1.25rem', '1.5rem', '2rem'],
  fontWeight: ['300', '400', '500', '600', '700', '800', '900', 'normal', 'bold'],
  lineHeight: ['normal', '1', '1.2', '1.4', '1.6', '1.8', '2'],
  letterSpacing: ['0', '0.5px', '1px', '2px'],
  textAlign: ['right', 'left', 'center', 'justify', 'start', 'end'],
  backgroundColor: ['transparent', '#ffffff', '#000000', 'var(--admin-panel-bg)', 'var(--admin-chip-bg)'],
  borderColor: ['transparent', '#e5e7eb', '#000000', 'var(--admin-border)', 'var(--accent-gold)'],
  borderWidth: ['0', '1px', '2px', '3px', '4px'],
  borderRadius: ['0', '4px', '8px', '10px', '12px', '16px', '24px', '32px', '50%', '999px'],
  boxShadow: ['none', '0 1px 2px rgba(0,0,0,.08)', '0 8px 24px rgba(0,0,0,.12)', '0 18px 44px rgba(0,0,0,.16)', 'inset 0 1px 0 rgba(255,255,255,.45)'],
  opacity: ['1', '0.95', '0.9', '0.8', '0.7', '0.6', '0.5', '0.3', '0'],
  zIndex: ['0', '1', '2', '5', '10', '20', '50', '100'],
  width: ['auto', '100%', 'fit-content', 'min-content', 'max-content', '25%', '50%', '75%', '100vw'],
  minWidth: ['0', '120px', '160px', '200px', '240px', '320px', '50%', '100%'],
  maxWidth: ['none', '320px', '480px', '640px', '768px', '1024px', '100%'],
  height: ['auto', '100%', '50vh', '60vh', '70vh', '80vh', '100vh'],
  minHeight: ['0', '120px', '180px', '240px', '320px', '50vh', '100vh'],
  maxHeight: ['none', '240px', '320px', '480px', '640px', '100vh'],
  overflowX: ['visible', 'hidden', 'auto', 'scroll', 'clip'],
  overflowY: ['visible', 'hidden', 'auto', 'scroll', 'clip'],
  margin: ['0', '4px', '8px', '12px', '16px', '24px', '32px', '0 auto'],
  padding: ['0', '4px', '8px', '12px', '16px', '20px', '24px', '32px'],
  transitionDuration: ['0s', '0.1s', '0.15s', '0.2s', '0.3s', '0.5s', '1s'],
  position: ['static', 'relative', 'absolute', 'fixed', 'sticky'],
  top: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  right: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  bottom: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  left: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
}

const STYLE_SECTIONS = [
  {
    title: 'Position',
    icon: 'crosshair',
    fields: [
      { key: 'position', label: 'Position' },
      { key: 'top', label: 'Top' },
      { key: 'right', label: 'Right' },
      { key: 'bottom', label: 'Bottom' },
      { key: 'left', label: 'Left' },
      { key: 'zIndex', label: 'Z-Index' },
    ],
  },
  {
    title: 'Layout',
    icon: 'layout',
    fields: [
      { key: 'display', label: 'Display' },
      { key: 'flexDirection', label: 'Direction' },
      { key: 'justifyContent', label: 'Justify' },
      { key: 'alignItems', label: 'Align' },
      { key: 'flexWrap', label: 'Wrap' },
      { key: 'gap', label: 'Gap' },
      { key: 'width', label: 'W' },
      { key: 'height', label: 'H' },
      { key: 'minWidth', label: 'Min W' },
      { key: 'maxWidth', label: 'Max W' },
      { key: 'minHeight', label: 'Min H' },
      { key: 'maxHeight', label: 'Max H' },
    ],
  },
  {
    title: 'Appearance',
    icon: 'sparkles',
    fields: [
      { key: 'opacity', label: 'Opacity' },
      { key: 'overflowX', label: 'Overflow X' },
      { key: 'overflowY', label: 'Overflow Y' },
      { key: 'margin', label: 'Margin' },
      { key: 'padding', label: 'Padding' },
    ],
  },
  {
    title: 'Fill',
    icon: 'droplet',
    fields: [{ key: 'backgroundColor', label: 'Fill', isColor: true }],
  },
  {
    title: 'Stroke',
    icon: 'square',
    fields: [
      { key: 'borderColor', label: 'Stroke', isColor: true },
      { key: 'borderWidth', label: 'Width' },
      { key: 'borderRadius', label: 'Radius' },
    ],
  },
  {
    title: 'Effects',
    icon: 'sun',
    fields: [
      { key: 'boxShadow', label: 'Shadow' },
      { key: 'transitionDuration', label: 'Transition' },
    ],
  },
  {
    title: 'Typography',
    icon: 'type',
    fields: [
      { key: 'color', label: 'Color', isColor: true },
      { key: 'fontSize', label: 'Size' },
      { key: 'fontWeight', label: 'Weight' },
      { key: 'lineHeight', label: 'Line H' },
      { key: 'letterSpacing', label: 'Spacing' },
      { key: 'textAlign', label: 'Align' },
    ],
  },
]

export function useInspectorStyles({ visualProps, applyVisualField, inspectorStyleQuery }) {
  const customFieldMode = ref({})

  const styleSections = STYLE_SECTIONS
  const styleFieldOptions = STYLE_FIELD_OPTIONS

  const filteredStyleSections = computed(() => {
    const query = String(inspectorStyleQuery?.value || '').trim().toLowerCase()
    if (!query) return styleSections
    const result = []
    for (const section of styleSections) {
      const fields = (section.fields || []).filter((field) => {
        const key = String(field?.key || '').toLowerCase()
        const label = String(field?.label || '').toLowerCase()
        const kebab = toKebabStyleKey(key)
        return key.includes(query) || label.includes(query) || kebab.includes(query)
      })
      if (!fields.length) continue
      result.push({ ...section, fields })
    }
    return result
  })

  function getFieldOptions(fieldKey) {
    return Array.isArray(styleFieldOptions[fieldKey]) ? styleFieldOptions[fieldKey] : []
  }

  function getFieldSelectValue(fieldKey) {
    const value = String(visualProps.value?.[fieldKey] ?? '').trim()
    if (!value) return ''
    const options = getFieldOptions(fieldKey)
    if (!options.length) return ''
    if (options.includes(value)) return value
    return '__custom__'
  }

  function shouldShowCustomInput(fieldKey) {
    const options = getFieldOptions(fieldKey)
    if (!options.length) return true
    return Boolean(customFieldMode.value?.[fieldKey]) || getFieldSelectValue(fieldKey) === '__custom__'
  }

  function onFieldPresetChange(fieldKey, value) {
    const nextValue = String(value ?? '')
    if (nextValue === '__custom__') {
      customFieldMode.value = { ...customFieldMode.value, [fieldKey]: true }
      return
    }
    customFieldMode.value = { ...customFieldMode.value, [fieldKey]: false }
    applyVisualField(fieldKey, nextValue)
  }

  function onFieldInputChange(fieldKey, value) {
    customFieldMode.value = { ...customFieldMode.value, [fieldKey]: true }
    applyVisualField(fieldKey, value)
  }

  function isColorField(fieldKey) {
    return COLOR_FIELDS.has(String(fieldKey || '').trim())
  }

  function resetCustomFieldMode() {
    customFieldMode.value = {}
  }

  return {
    styleSections,
    styleFieldOptions,
    filteredStyleSections,
    customFieldMode,
    getFieldOptions,
    getFieldSelectValue,
    shouldShowCustomInput,
    onFieldPresetChange,
    onFieldInputChange,
    isColorField,
    resetCustomFieldMode,
  }
}
