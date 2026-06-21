const TEXT_ATTRIBUTES = ['placeholder', 'title', 'alt', 'aria-label']
const MAX_VISUAL_SELECTOR_MATCHES = 120
const MAX_VISUAL_ROWS = 120
const OBSERVER_THROTTLE_MS = 140
const OBSERVER_MAX_RUNS = 28
const VISUAL_TRANSIENT_SELECTOR_RE = /\.mysite-visual-(?:selected|hover|layer-highlight)\b/g

let activeObserver = null
let observerTimer = null
let observerApplyTimer = null
let observerRunCount = 0
let observerPairs = []
let observerVisualRows = []
let observerTokenState = null

function normalizeTokenName(value) {
  let text = String(value || '').trim()
  if (!text) return ''
  if (!text.startsWith('--')) text = `--${text.replace(/^[-]+/, '')}`
  text = text.replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-{2,}/g, '-')
  text = text.replace(/^--+/, '--')
  if (!/^--[a-zA-Z0-9_-]+$/.test(text)) return ''
  return text
}

function normalizeText(value) {
  return String(value || '')
    .replace(/\u00a0/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function buildPairs(items) {
  const rows = Array.isArray(items) ? items : []
  const seen = new Set()
  const pairs = []

  for (const row of rows) {
    const source = normalizeText(row?.source_text)
    const replacement = normalizeText(row?.replacement_text)
    if (!source || !replacement || source === replacement) continue

    const key = `${source}__${replacement}`
    if (seen.has(key)) continue
    seen.add(key)
    pairs.push({ source, replacement })
  }

  return pairs.sort((a, b) => b.source.length - a.source.length)
}

function sanitizeSelector(selector) {
  let value = String(selector || '').trim()
  if (!value) return ''

  value = value.replace(VISUAL_TRANSIENT_SELECTOR_RE, '')
  value = value.replace(/\s*([>+~])\s*/g, ' $1 ')
  value = value.replace(/\s+/g, ' ').trim().replace(/,+$/, '').replace(/[.>+~\s]+$/, '').trim()
  if (!value || value.includes('mysite-visual-')) return ''
  return value
}

function isRootSelectorForContent(selector) {
  const normalized = String(selector || '').trim().toLowerCase().replace(/\s+/g, ' ')
  if (!normalized) return false
  if (normalized === 'body' || normalized === 'html' || normalized === '#app' || normalized === ':root') {
    return true
  }
  return /^(body|html|#app)\b/.test(normalized)
}

function normalizeVisualRows(items) {
  const rows = Array.isArray(items) ? items : []
  const result = []
  const seen = new Set()

  for (const row of rows) {
    const selector = sanitizeSelector(row?.selector)
    if (!selector || seen.has(selector)) continue

    const styles = {}
    const rawStyles = row?.styles
    if (rawStyles && typeof rawStyles === 'object' && !Array.isArray(rawStyles)) {
      for (const [rawKey, rawValue] of Object.entries(rawStyles)) {
        const key = String(rawKey || '').trim()
        const value = String(rawValue || '').trim()
        if (!key || !value) continue
        styles[key] = value
      }
    }

    const hasText = Object.prototype.hasOwnProperty.call(row || {}, 'text_content')
    const textContent = hasText ? String(row?.text_content ?? '') : undefined
    const hasHtml = Object.prototype.hasOwnProperty.call(row || {}, 'html_content')
    const htmlContent = hasHtml ? String(row?.html_content ?? '') : undefined
    if (!Object.keys(styles).length && textContent === undefined && htmlContent === undefined) continue
    if ((hasText || hasHtml) && isRootSelectorForContent(selector)) continue

    if (selector.length > 420) continue
    seen.add(selector)
    result.push({
      selector,
      styles,
      text_content: textContent,
      html_content: htmlContent,
    })
    if (result.length >= MAX_VISUAL_ROWS) break
  }

  return result
}

function normalizeTokenCollections(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return {}
  const out = {}
  for (const [rawCollectionId, rawCollection] of Object.entries(input)) {
    const collectionId = String(rawCollectionId || '').trim()
    if (!collectionId || !rawCollection || typeof rawCollection !== 'object') continue
    const rawModes = rawCollection.modes && typeof rawCollection.modes === 'object' ? rawCollection.modes : {}
    const modes = {}
    for (const [rawMode, rawTokens] of Object.entries(rawModes)) {
      const mode = String(rawMode || '').trim().toLowerCase()
      if (!mode || !rawTokens || typeof rawTokens !== 'object') continue
      const tokens = {}
      for (const [rawTokenName, rawTokenValue] of Object.entries(rawTokens)) {
        const tokenName = normalizeTokenName(rawTokenName)
        const tokenValue = String(rawTokenValue || '').trim()
        if (!tokenName || !tokenValue) continue
        tokens[tokenName] = tokenValue
      }
      modes[mode] = tokens
    }
    out[collectionId] = { id: collectionId, modes }
  }
  return out
}

function resolveTokenRuntimeValue(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('@')) {
    const alias = normalizeTokenName(raw.slice(1))
    return alias ? `var(${alias})` : ''
  }
  return raw
}

function applyTokenOverridesOnce(tokenState) {
  if (!tokenState || typeof tokenState !== 'object') return
  const collections = normalizeTokenCollections(tokenState.collections)
  const preferredCollection = String(tokenState.activeCollection || '').trim()
  const collectionId = preferredCollection && collections[preferredCollection]
    ? preferredCollection
    : Object.keys(collections)[0]
  if (!collectionId) return
  const preferredMode = String(tokenState.activeMode || 'light').trim().toLowerCase() || 'light'
  const modeTokens = collections[collectionId]?.modes?.[preferredMode] || collections[collectionId]?.modes?.light || {}
  if (!modeTokens || typeof modeTokens !== 'object') return
  const root = document.documentElement
  if (!root) return
  for (const [tokenName, tokenValue] of Object.entries(modeTokens)) {
    const runtimeValue = resolveTokenRuntimeValue(tokenValue)
    if (!runtimeValue) continue
    root.style.setProperty(tokenName, runtimeValue)
  }
}

function replaceValue(value, pairs) {
  let result = String(value || '')
  for (const pair of pairs) {
    if (!result.includes(pair.source)) continue
    result = result.split(pair.source).join(pair.replacement)
  }
  return result
}

function applyTextOverridesOnce(pairs) {
  const root = document.body
  if (!root || !pairs.length) return

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  let node = walker.nextNode()
  while (node) {
    const original = String(node.nodeValue || '')
    if (original.trim()) {
      const replaced = replaceValue(original, pairs)
      if (replaced !== original) node.nodeValue = replaced
    }
    node = walker.nextNode()
  }

  const selector = TEXT_ATTRIBUTES.map((attr) => `[${attr}]`).join(',')
  if (!selector) return
  const elements = root.querySelectorAll(selector)
  elements.forEach((element) => {
    TEXT_ATTRIBUTES.forEach((attr) => {
      const value = element.getAttribute(attr)
      if (!value) return
      const replaced = replaceValue(value, pairs)
      if (replaced !== value) {
        element.setAttribute(attr, replaced)
      }
    })
  })
}

function applyVisualOverridesOnce(visualRows) {
  if (!visualRows.length) return
  for (const row of visualRows) {
    let elements = []
    try {
      elements = document.querySelectorAll(row.selector)
    } catch {
      continue
    }
    if (!elements.length) continue
    Array.from(elements).slice(0, MAX_VISUAL_SELECTOR_MATCHES).forEach((element) => {
      if (row.html_content !== undefined) {
        element.innerHTML = row.html_content
      } else if (row.text_content !== undefined) {
        element.textContent = row.text_content
      }
      const styles = row.styles || {}
      for (const [key, value] of Object.entries(styles)) {
        if (!value) continue
        if (key.includes('-')) {
          element.style.setProperty(key, value)
        } else {
          element.style[key] = value
        }
      }
    })
  }
}

function applyAllOnce(pairs, visualRows, tokenState = null) {
  applyTextOverridesOnce(pairs)
  applyVisualOverridesOnce(visualRows)
  applyTokenOverridesOnce(tokenState)
}

export function stopRouteContentOverrideObserver() {
  if (activeObserver) {
    activeObserver.disconnect()
    activeObserver = null
  }
  if (observerTimer) {
    window.clearTimeout(observerTimer)
    observerTimer = null
  }
  if (observerApplyTimer) {
    window.clearTimeout(observerApplyTimer)
    observerApplyTimer = null
  }
  observerRunCount = 0
  observerPairs = []
  observerVisualRows = []
  observerTokenState = null
}

function scheduleObserverApply() {
  if (!activeObserver) return
  if (observerApplyTimer) return
  observerApplyTimer = window.setTimeout(() => {
    observerApplyTimer = null
    if (!activeObserver) return
    if (observerRunCount >= OBSERVER_MAX_RUNS) {
      stopRouteContentOverrideObserver()
      return
    }
    observerRunCount += 1
    activeObserver.disconnect()
    try {
      applyAllOnce(observerPairs, observerVisualRows, observerTokenState)
    } finally {
      if (!activeObserver || !document.body) return
      activeObserver.observe(document.body, {
        subtree: true,
        childList: true,
        characterData: true,
        attributes: true,
        attributeFilter: TEXT_ATTRIBUTES,
      })
    }
  }, OBSERVER_THROTTLE_MS)
}

export function applyRouteContentOverrides(items, options = {}) {
  stopRouteContentOverrideObserver()

  const pairs = buildPairs(items)
  const visualRows = normalizeVisualRows(options.visualItems)
  const tokenState = {
    collections: options.tokenCollections,
    activeCollection: options.tokenActiveCollection,
    activeMode: options.tokenActiveMode,
  }
  const hasTokens = Object.keys(normalizeTokenCollections(tokenState.collections)).length > 0
  if (!pairs.length && !visualRows.length && !hasTokens) return { count: 0, visualCount: 0 }

  applyAllOnce(pairs, visualRows, tokenState)

  // Visual-only overrides are applied once to avoid runtime observer storms.
  if (!pairs.length) {
    return { count: 0, visualCount: visualRows.length }
  }

  if (!document.body) {
    return { count: pairs.length, visualCount: visualRows.length }
  }

  observerPairs = pairs
  observerVisualRows = visualRows
  observerTokenState = tokenState
  observerRunCount = 0
  activeObserver = new MutationObserver(() => {
    scheduleObserverApply()
  })
  activeObserver.observe(document.body, {
    subtree: true,
    childList: true,
    characterData: true,
    attributes: true,
    attributeFilter: TEXT_ATTRIBUTES,
  })

  const observeMs = Math.max(1000, Number(options.observeMs || 5000))
  observerTimer = window.setTimeout(() => {
    stopRouteContentOverrideObserver()
  }, observeMs)

  return { count: pairs.length, visualCount: visualRows.length }
}

async function fetchMessage(url) {
  try {
    const response = await fetch(url, { credentials: 'same-origin' })
    const payload = await response.json()
    return payload?.message || payload || {}
  } catch (error) {
    return {}
  }
}

export async function fetchAndApplyRouteContentOverrides(route = window.location.pathname) {
  const safeRoute = String(route || '').trim() || '/'
  try {
    const [contentMessage, visualMessage] = await Promise.all([
      fetchMessage(`/api/method/mysite.api.get_route_content_overrides?route=${encodeURIComponent(safeRoute)}`),
      fetchMessage(`/api/method/mysite.api.get_route_visual_overrides?route=${encodeURIComponent(safeRoute)}`),
    ])
    const items = Array.isArray(contentMessage?.items) ? contentMessage.items : []
    const visualItems = Array.isArray(visualMessage?.items) ? visualMessage.items : []
    return applyRouteContentOverrides(items, {
      visualItems,
      tokenCollections: visualMessage?.token_collections || {},
      tokenActiveCollection: visualMessage?.token_active_collection || '',
      tokenActiveMode: visualMessage?.token_active_mode || 'light',
    })
  } catch (error) {
    stopRouteContentOverrideObserver()
    return { count: 0, visualCount: 0, error: String(error?.message || error || '') }
  }
}
