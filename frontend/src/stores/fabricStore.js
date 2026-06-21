import { ref } from 'vue'

const STORAGE_KEY = 'mysite_selected_fabric'

function normalizeSelectedFabric(fabric) {
  if (!fabric || typeof fabric !== 'object') return null
  const qualityName = fabric.qualityName || fabric.quality || ''
  const colorName = fabric.colorName || fabric.name || fabric.item_name || ''
  const pricePerMeter = Number(fabric.pricePerMeter ?? fabric.Price ?? 0) || 0
  const normalized = {
    qualityName,
    colorName,
    pricePerMeter,
    formattedPrice: fabric.formattedPrice || fabric.formatted_Price || '',
    image: fabric.image || '',
  }

  if (fabric.itemCode || fabric.item_code) {
    normalized.itemCode = String(fabric.itemCode || fabric.item_code || '').trim()
  }
  if (fabric.code) {
    normalized.code = String(fabric.code).trim()
  }

  return normalized
}

function loadSelectedFabric() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return normalizeSelectedFabric(parsed)
  } catch (e) {
    return null
  }
}

function saveSelectedFabric(fabric) {
  try {
    const normalized = normalizeSelectedFabric(fabric)
    if (!normalized) {
      localStorage.removeItem(STORAGE_KEY)
      return
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized))
  } catch (e) {
    // Prevent UI break on storage failures.
  }
}

const selectedFabric = ref(loadSelectedFabric())

export function useFabricStore() {
  const setSelectedFabric = (fabric) => {
    selectedFabric.value = normalizeSelectedFabric(fabric)
    saveSelectedFabric(selectedFabric.value)
  }

  const clearSelectedFabric = () => setSelectedFabric(null)

  return {
    selectedFabric,
    setSelectedFabric,
    clearSelectedFabric,
  }
}
