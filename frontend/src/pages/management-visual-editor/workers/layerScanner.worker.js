const IGNORED_TAGS = new Set(['script', 'style', 'meta', 'link', 'noscript'])

function isEditableElement(element) {
  if (!element || element.nodeType !== 1) return false
  const tag = String(element.tagName || '').toLowerCase()
  if (!tag || IGNORED_TAGS.has(tag)) return false
  const id = String(element.id || '').trim()
  if (id.startsWith('mysite-ve-')) return false
  return true
}

function nodeLabel(element) {
  const customLabel = String(element?.getAttribute?.('data-mysite-layer-label') || '').trim()
  if (customLabel) return customLabel
  const tag = String(element?.tagName || '').toLowerCase()
  const id = String(element?.id || '').trim()
  const cls = String(element?.className || '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .join('.')
  if (id) return `${tag}#${id}`
  if (cls) return `${tag}.${cls}`
  return tag || 'node'
}

function previewText(element, limit = 240) {
  if (!element) return ''
  let text = ''
  for (const node of Array.from(element.childNodes || [])) {
    if (node?.nodeType !== 3) continue
    const value = String(node.textContent || '').replace(/\s+/g, ' ').trim()
    if (!value) continue
    text = value
    break
  }
  if (!text) {
    text =
      String(element.getAttribute?.('aria-label') || '').trim() ||
      String(element.getAttribute?.('alt') || '').trim() ||
      String(element.getAttribute?.('title') || '').trim()
  }
  return text.slice(0, Math.max(1, Number(limit || 240)))
}

function scanLayers({
  html,
  maxNodes = 150,
  maxDepth = 8,
  maxChildren = 80,
  maxMs = 900,
}) {
  const parser = new DOMParser()
  const parsed = parser.parseFromString(`<body>${String(html || '')}</body>`, 'text/html')
  const root = parsed?.body
  if (!root) return { rows: [], timed_out: false, truncated: false }

  const rows = []
  const queue = []
  const bodyChildren = Array.from(root.children || [])
  for (let index = 0; index < bodyChildren.length; index += 1) {
    queue.push({
      element: bodyChildren[index],
      depth: 0,
      parentTmpId: '',
      path: String(index),
    })
  }

  let counter = 0
  let cursor = 0
  const startedAt = Date.now()
  let timedOut = false

  while (cursor < queue.length && rows.length < maxNodes) {
    if (Date.now() - startedAt >= maxMs) {
      timedOut = true
      break
    }
    const current = queue[cursor]
    cursor += 1
    const element = current?.element
    const depth = Number(current?.depth || 0)
    if (!isEditableElement(element) || depth > maxDepth) continue

    const tmpId = `tmp-${counter}`
    counter += 1

    const elementChildren = Array.from(element.children || [])
    const queueChildren = []
    for (let childIndex = 0; childIndex < elementChildren.length; childIndex += 1) {
      const child = elementChildren[childIndex]
      if (!isEditableElement(child)) continue
      queueChildren.push({ child, childIndex })
      if (queueChildren.length >= maxChildren) break
    }

    rows.push({
      tmp_id: tmpId,
      parent_tmp_id: String(current.parentTmpId || ''),
      depth,
      path: String(current.path || ''),
      tag: String(element.tagName || '').toLowerCase(),
      label: nodeLabel(element),
      original_text: previewText(element),
      child_count: queueChildren.length,
    })

    if (depth >= maxDepth) continue
    for (const childRow of queueChildren) {
      queue.push({
        element: childRow.child,
        depth: depth + 1,
        parentTmpId: tmpId,
        path: current.path ? `${current.path}.${childRow.childIndex}` : String(childRow.childIndex),
      })
    }
  }

  return {
    rows,
    timed_out: timedOut,
    truncated: timedOut || rows.length >= maxNodes,
  }
}

self.onmessage = (event) => {
  const payload = event?.data || {}
  const requestId = Number(payload.requestId || 0)
  try {
    const result = scanLayers(payload || {})
    self.postMessage({
      ok: true,
      requestId,
      rows: result.rows || [],
      timed_out: Boolean(result.timed_out),
      truncated: Boolean(result.truncated),
    })
  } catch (error) {
    self.postMessage({
      ok: false,
      requestId,
      error: String(error?.message || 'layer-scan-worker-failed'),
    })
  }
}
