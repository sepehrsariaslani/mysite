import { computed, nextTick, ref } from 'vue'

function normalizeLayerSearchText(layer) {
  return `${layer?.label || ''} ${layer?.tag || ''} ${layer?.selector || ''}`.toLowerCase()
}

export function useVisualLayers({
  visualLayerQuery,
  visualLayers,
  visualLayerIndex,
  visualChildrenMap,
  visualExpandedMap,
}) {
  const visualLayerRowRefs = ref({})

  function isLayerExpanded(nodeId) {
    const key = String(nodeId || '').trim()
    if (!key) return true
    return visualExpandedMap.value?.[key] !== false
  }

  function setLayerRowRef(nodeId, el) {
    const key = String(nodeId || '').trim()
    if (!key) return
    if (el) visualLayerRowRefs.value[key] = el
    else delete visualLayerRowRefs.value[key]
  }

  function toggleLayerNode(nodeId) {
    const key = String(nodeId || '').trim()
    if (!key) return
    if (Number(visualLayerIndex.value?.[key]?.child_count || 0) <= 0) return
    visualExpandedMap.value[key] = !isLayerExpanded(key)
  }

  function focusLayerRow(nodeId) {
    const key = String(nodeId || '').trim()
    if (!key) return
    nextTick(() => {
      const row = visualLayerRowRefs.value?.[key]
      if (!row || typeof row.scrollIntoView !== 'function') return
      row.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    })
  }

  function expandLayerAncestors(nodeId) {
    const key = String(nodeId || '').trim()
    if (!key) return
    const index = visualLayerIndex.value || {}
    let current = index?.[key]
    while (current) {
      const parentId = String(current.parent_id || '').trim()
      if (!parentId) break
      visualExpandedMap.value[parentId] = true
      current = index?.[parentId]
    }
  }

  const filteredVisualLayers = computed(() => {
    const term = String(visualLayerQuery.value || '').trim().toLowerCase()
    const rows = Array.isArray(visualLayers.value) ? visualLayers.value : []
    if (!rows.length) return []

    const index = visualLayerIndex.value || {}
    const childrenMap = visualChildrenMap.value || {}

    const roots = Array.isArray(childrenMap.__root__)
      ? childrenMap.__root__
      : rows.filter((row) => !row.parent_id).map((row) => row.id)

    const result = []

    if (!term) {
      const walk = (nodeId) => {
        const layer = index?.[nodeId]
        if (!layer) return
        result.push(layer)
        if (!isLayerExpanded(nodeId)) return
        const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
        for (const childId of children) walk(childId)
      }
      for (const rootId of roots) walk(rootId)
      return result
    }

    const includeSet = new Set()

    const includeDescendants = (nodeId) => {
      const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
      for (const childId of children) {
        if (includeSet.has(childId)) continue
        includeSet.add(childId)
        includeDescendants(childId)
      }
    }

    const includeAncestors = (nodeId) => {
      let current = index?.[nodeId]
      while (current) {
        includeSet.add(current.id)
        const parentId = String(current.parent_id || '').trim()
        current = parentId ? index?.[parentId] : null
      }
    }

    for (const row of rows) {
      if (!normalizeLayerSearchText(row).includes(term)) continue
      includeAncestors(row.id)
      includeDescendants(row.id)
    }

    const walkAll = (nodeId) => {
      const layer = index?.[nodeId]
      if (!layer) return
      if (includeSet.has(nodeId)) result.push(layer)
      const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
      for (const childId of children) walkAll(childId)
    }

    for (const rootId of roots) walkAll(rootId)
    return result
  })

  return {
    visualLayerRowRefs,
    filteredVisualLayers,
    isLayerExpanded,
    setLayerRowRef,
    toggleLayerNode,
    focusLayerRow,
    expandLayerAncestors,
  }
}
