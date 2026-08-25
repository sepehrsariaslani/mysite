const DEFAULT_MAX_PRICE = Number.MAX_SAFE_INTEGER

function normalizeText(value) {
  return String(value || '').trim()
}

function normalizeNumber(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function uniqueValues(values) {
  const seen = new Set()
  const result = []
  values.forEach((value) => {
    const normalized = normalizeText(value)
    if (!normalized || seen.has(normalized)) return
    seen.add(normalized)
    result.push(normalized)
  })
  return result
}

function extractValues(item, getter) {
  if (typeof getter !== 'function') return []
  const raw = getter(item)
  if (Array.isArray(raw)) return raw
  if (raw == null) return []
  return [raw]
}

function minPrice(item, adapter) {
  const values = extractValues(item, adapter?.getPrices)
    .map(normalizeNumber)
    .filter((value) => Number.isFinite(value) && value > 0)
  return values.length ? Math.min(...values) : 0
}

function maxPrice(item, adapter) {
  const values = extractValues(item, adapter?.getPrices)
    .map(normalizeNumber)
    .filter((value) => Number.isFinite(value) && value > 0)
  return values.length ? Math.max(...values) : 0
}

export function filterItems(items = [], filters = {}, adapter = {}) {
  const modelFilters = uniqueValues(filters.models || [])
  const colorFilters = uniqueValues(filters.colors || [])
  const hasPriceRange = filters.priceActive === true
  const minBound = normalizeNumber(filters.priceMin)
  const maxBound = normalizeNumber(filters.priceMax)

  return (items || []).filter((item) => {
    if (modelFilters.length) {
      const itemName = normalizeText(adapter?.getName?.(item))
      if (!modelFilters.includes(itemName)) return false
    }

    if (colorFilters.length) {
      const itemColors = uniqueValues(extractValues(item, adapter?.getColors))
      const hasMatch = itemColors.some((color) => colorFilters.includes(color))
      if (!hasMatch) return false
    }

    if (hasPriceRange) {
      const prices = extractValues(item, adapter?.getPrices)
        .map(normalizeNumber)
        .filter((value) => Number.isFinite(value) && value > 0)

      if (!prices.length) return false

      const lower = Number.isFinite(minBound) ? minBound : 0
      const upper = Number.isFinite(maxBound) ? maxBound : DEFAULT_MAX_PRICE
      const inRange = prices.some((value) => value >= lower && value <= upper)
      if (!inRange) return false
    }

    return true
  })
}

export function sortItems(items = [], sortKey = 'default', adapter = {}) {
  const list = [...(items || [])]

  if (sortKey === 'price-low') {
    return list.sort((left, right) => minPrice(left, adapter) - minPrice(right, adapter))
  }

  if (sortKey === 'price-high') {
    return list.sort((left, right) => maxPrice(right, adapter) - maxPrice(left, adapter))
  }

  if (sortKey === 'name-asc') {
    return list.sort((left, right) => normalizeText(adapter?.getName?.(left)).localeCompare(normalizeText(adapter?.getName?.(right)), 'fa'))
  }

  return list
}

export function buildFilterOptions(items = [], adapter = {}) {
  const models = uniqueValues((items || []).map((item) => adapter?.getName?.(item)))
    .map((value) => ({ value, name: value }))

  const colors = uniqueValues(
    (items || []).flatMap((item) => extractValues(item, adapter?.getColors))
  ).map((value) => ({ value, name: value }))

  const prices = (items || [])
    .flatMap((item) => extractValues(item, adapter?.getPrices))
    .map(normalizeNumber)
    .filter((value) => Number.isFinite(value) && value > 0)

  const minBound = prices.length ? Math.floor(Math.min(...prices) / 1000000) * 1000000 : 0
  const maxBound = prices.length ? Math.ceil(Math.max(...prices) / 1000000) * 1000000 : 100000000

  return {
    models,
    colors,
    minBound,
    maxBound,
    step: 1000000,
  }
}
