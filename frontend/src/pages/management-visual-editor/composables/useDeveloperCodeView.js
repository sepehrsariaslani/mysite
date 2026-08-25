import { computed, ref } from 'vue'

function toKebabCase(value) {
  return String(value || '')
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}

function buildCssBlock(selector, styles = {}) {
  if (!selector) return ''
  const rows = Object.entries(styles)
    .filter(([key, value]) => String(key || '').trim() && String(value || '').trim())
    .map(([key, value]) => `  ${toKebabCase(key)}: ${String(value)};`)
  if (!rows.length) return `${selector} {}`
  return `${selector} {\n${rows.join('\n')}\n}`
}

function buildHtmlSnippet(layer) {
  if (!layer) return ''
  const tag = String(layer.tag || 'div').toLowerCase()
  const label = String(layer.original_text || '').trim()
  if (!label) return `<${tag}></${tag}>`
  return `<${tag}>${label}</${tag}>`
}

function extractTokenRefs(styles = {}) {
  const refs = new Set()
  for (const value of Object.values(styles || {})) {
    const text = String(value || '')
    const matches = text.match(/var\(\s*(--[A-Za-z0-9_-]+)\s*\)/g) || []
    for (const match of matches) {
      const token = String(match || '').match(/--[A-Za-z0-9_-]+/)
      if (token?.[0]) refs.add(token[0])
    }
  }
  return Array.from(refs).sort((a, b) => a.localeCompare(b))
}

function buildReactSnippet(layer, styles = {}) {
  if (!layer) return ''
  const tag = String(layer.tag || 'div').toLowerCase()
  const text = String(layer.original_text || '').trim()
  const safeName = `Layer${tag.replace(/[^a-z0-9]+/gi, ' ').split(/\s+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join('') || 'Node'}`
  const styleRows = Object.entries(styles || {})
    .filter(([key, value]) => String(key || '').trim() && String(value || '').trim())
    .map(([key, value]) => `  ${String(key).includes('-') ? `'${key}'` : key}: ${JSON.stringify(String(value))},`)
  const styleBlock = styleRows.length ? `const style = {\n${styleRows.join('\n')}\n}\n\n` : ''
  const body = text ? `${text}` : ''
  return `${styleBlock}export function ${safeName}() {\n  return <${tag}${styleRows.length ? ' style={style}' : ''}>${body}</${tag}>\n}`
}

function cssKeyToReactKey(key) {
  const raw = String(key || '').trim()
  if (!raw) return ''
  if (raw.startsWith('--')) return raw
  if (!raw.includes('-')) return raw
  const parts = raw.split('-').filter(Boolean)
  if (!parts.length) return ''
  return parts[0] + parts.slice(1).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join('')
}

function normalizeConstraintInfo(constraints) {
  const row = constraints || {}
  return {
    horizontal: String(row.horizontal || 'left'),
    vertical: String(row.vertical || 'top'),
    size: String(row.size || 'fixed'),
  }
}

function buildConstraintComment(constraints) {
  const c = normalizeConstraintInfo(constraints)
  return `// Constraints: H=${c.horizontal}, V=${c.vertical}, Size=${c.size}`
}

function inferPrimaryContent(layer) {
  const text = String(layer?.original_text || '').trim()
  if (text) return text
  const tag = String(layer?.tag || 'div').toLowerCase()
  if (tag === 'img') return ''
  return 'Content'
}

function parsePx(value) {
  const source = String(value || '').trim()
  const match = source.match(/^-?\d+(?:\.\d+)?/)
  if (!match) return null
  const num = Number.parseFloat(match[0])
  return Number.isFinite(num) ? num : null
}

function styleValueForSwift(value) {
  const source = String(value || '').trim()
  if (!source) return '0'
  if (/^-?\d+(\.\d+)?px$/i.test(source)) return String(parsePx(source))
  if (/^-?\d+(\.\d+)?$/.test(source)) return source
  return JSON.stringify(source)
}

function buildSwiftUISnippet(layer, styles = {}, constraints = {}, inspect = null) {
  if (!layer) return ''
  const content = inferPrimaryContent(layer)
  const tag = String(layer.tag || 'div').toLowerCase()
  const swiftView = tag === 'img' ? 'Image("asset")' : `Text(${JSON.stringify(content)})`
  const width = styleValueForSwift(styles.width || inspect?.box?.width || '')
  const height = styleValueForSwift(styles.height || inspect?.box?.height || '')
  const background = String(styles.backgroundColor || '').trim()
  const foreground = String(styles.color || '').trim()
  const constraintLine = buildConstraintComment(constraints)
  const backgroundLine = background ? `\n      .background(Color(${JSON.stringify(background)}))` : ''
  const foregroundLine = foreground ? `\n      .foregroundColor(Color(${JSON.stringify(foreground)}))` : ''
  return `${constraintLine}
import SwiftUI

struct LayerSnippetView: View {
  var body: some View {
    ${swiftView}
      .frame(width: ${width}, height: ${height}, alignment: .topLeading)${foregroundLine}${backgroundLine}
  }
}`
}

function buildComposeSnippet(layer, styles = {}, constraints = {}, inspect = null) {
  if (!layer) return ''
  const content = inferPrimaryContent(layer)
  const tag = String(layer.tag || 'div').toLowerCase()
  const width = parsePx(styles.width || inspect?.box?.width || '')
  const height = parsePx(styles.height || inspect?.box?.height || '')
  const background = String(styles.backgroundColor || '').trim()
  const textColor = String(styles.color || '').trim()
  const constraintLine = buildConstraintComment(constraints)
  const modifiers = []
  if (width !== null) modifiers.push(`width(${Math.max(0, Math.round(width))}.dp)`)
  if (height !== null) modifiers.push(`height(${Math.max(0, Math.round(height))}.dp)`)
  if (background) modifiers.push(`background(color = Color(${JSON.stringify(background)}))`)
  const modifierText = modifiers.length ? `\n        .${modifiers.join('\n        .')}` : ''
  const body =
    tag === 'img'
      ? 'Image(painter = painterResource(id = R.drawable.asset), contentDescription = null)'
      : `Text(text = ${JSON.stringify(content)}${textColor ? `, color = Color(${JSON.stringify(textColor)})` : ''})`
  return `${constraintLine}
@Composable
fun LayerSnippet() {
    Box(
      modifier = Modifier${modifierText}
    ) {
      ${body}
    }
}`
}

function buildAdvancedReactSnippet(layer, styles = {}, constraints = {}, inspect = null) {
  if (!layer) return ''
  const tag = String(layer.tag || 'div').toLowerCase()
  const componentName = `Layer${tag.replace(/[^a-z0-9]+/gi, ' ').split(/\s+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join('') || 'Node'}`
  const styleRows = Object.entries(styles || {})
    .filter(([key, value]) => String(key || '').trim() && String(value || '').trim())
    .map(([key, value]) => `  ${cssKeyToReactKey(key).includes('-') ? `'${cssKeyToReactKey(key)}'` : cssKeyToReactKey(key)}: ${JSON.stringify(String(value))},`)
  const fallbackWidth = Number(inspect?.box?.width || 0) > 0 ? `  width: ${JSON.stringify(`${Math.round(Number(inspect.box.width))}px`)},` : ''
  const fallbackHeight = Number(inspect?.box?.height || 0) > 0 ? `  height: ${JSON.stringify(`${Math.round(Number(inspect.box.height))}px`)},` : ''
  const rows = [...styleRows]
  if (fallbackWidth && !rows.some((row) => row.includes('width:'))) rows.push(fallbackWidth)
  if (fallbackHeight && !rows.some((row) => row.includes('height:'))) rows.push(fallbackHeight)
  const styleBlock = rows.length ? `const style = {\n${rows.join('\n')}\n}\n\n` : ''
  const content = inferPrimaryContent(layer)
  const constraintLine = buildConstraintComment(constraints)
  return `${constraintLine}
${styleBlock}export function ${componentName}() {
  return <${tag}${rows.length ? ' style={style}' : ''}>${tag === 'img' ? '' : content}</${tag}>
}`
}

function buildAdvancedVueSnippet(layer, styles = {}, constraints = {}) {
  if (!layer) return ''
  const tag = String(layer.tag || 'div').toLowerCase()
  const content = inferPrimaryContent(layer)
  const styleRows = Object.entries(styles || {})
    .filter(([key, value]) => String(key || '').trim() && String(value || '').trim())
    .map(([key, value]) => `  ${toKebabCase(key)}: ${String(value)};`)
  const scopedClass = `layer-${tag}`
  const cssBody = styleRows.length ? `.${scopedClass} {\n${styleRows.join('\n')}\n}` : `.${scopedClass} {}`
  return `${buildConstraintComment(constraints)}
<template>
  <${tag} class="${scopedClass}">${tag === 'img' ? '' : content}</${tag}>
</template>

<style scoped>
${cssBody}
</style>`
}

function buildRedlineSnippet(redline) {
  if (!redline) return '// Select exactly two layers for redline handoff'
  const alignment = Array.isArray(redline.alignment?.matched) ? redline.alignment.matched.join(', ') : ''
  return `// Redline between two selected nodes
deltaX: ${redline.delta?.x ?? 0}px
deltaY: ${redline.delta?.y ?? 0}px
horizontalGap: ${redline.gap?.x ?? 0}px
verticalGap: ${redline.gap?.y ?? 0}px
centerDistance: ${redline.center_distance ?? 0}px
alignment: ${alignment || 'none'}`
}

export function useDeveloperCodeView({
  visualSelectedLayer,
  visualOverridesMap,
  sourceCode,
  rawCss,
  handoffInspect,
  handoffRedline,
  selectedConstraintState,
}) {
  const snippetTab = ref('css')

  const selectedOverride = computed(() => {
    const selector = String(visualSelectedLayer.value?.selector || '').trim()
    if (!selector) return null
    return visualOverridesMap.value?.[selector] || null
  })

  const cssSnippet = computed(() => {
    const selector = String(visualSelectedLayer.value?.selector || '').trim()
    const row = selectedOverride.value
    if (!selector || !row) return ''
    const block = buildCssBlock(selector, row.styles || {})
    if (row.apply_html) {
      const htmlPreview = String(row.html_content || '').slice(0, 240)
      return `${block}\n\n/* rich-text html override */\n/* ${htmlPreview} */`
    }
    if (row.apply_text) return `${block}\n\n/* text-content override */\n/* ${row.text_content || ''} */`
    return block
  })

  const htmlSnippet = computed(() => buildHtmlSnippet(visualSelectedLayer.value))

  const vueSnippet = computed(() => {
    const layer = visualSelectedLayer.value
    const row = selectedOverride.value
    return buildAdvancedVueSnippet(layer, row?.styles || {}, selectedConstraintState?.value || {})
  })

  const reactSnippet = computed(() => {
    const layer = visualSelectedLayer.value
    const row = selectedOverride.value
    return buildAdvancedReactSnippet(layer, row?.styles || {}, selectedConstraintState?.value || {}, handoffInspect?.value || null)
  })

  const swiftuiSnippet = computed(() => {
    const layer = visualSelectedLayer.value
    const row = selectedOverride.value
    return buildSwiftUISnippet(layer, row?.styles || {}, selectedConstraintState?.value || {}, handoffInspect?.value || null)
  })

  const composeSnippet = computed(() => {
    const layer = visualSelectedLayer.value
    const row = selectedOverride.value
    return buildComposeSnippet(layer, row?.styles || {}, selectedConstraintState?.value || {}, handoffInspect?.value || null)
  })

  const tokenSnippet = computed(() => {
    const selector = String(visualSelectedLayer.value?.selector || '').trim()
    const row = selectedOverride.value
    if (!selector || !row) return ''
    const refs = extractTokenRefs(row.styles || {})
    if (!refs.length) return '// No token reference on selected layer'
    return refs.map((token) => `${token}: var(${token});`).join('\n')
  })

  const redlineSnippet = computed(() => buildRedlineSnippet(handoffRedline?.value || null))

  const fullSourcePreview = computed(() => String(sourceCode.value || '').slice(0, 4000))
  const rawCssPreview = computed(() => String(rawCss.value || ''))

  return {
    snippetTab,
    selectedOverride,
    cssSnippet,
    htmlSnippet,
    vueSnippet,
    reactSnippet,
    swiftuiSnippet,
    composeSnippet,
    tokenSnippet,
    redlineSnippet,
    fullSourcePreview,
    rawCssPreview,
  }
}
