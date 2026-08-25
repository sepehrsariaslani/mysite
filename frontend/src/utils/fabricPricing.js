const persianDigits = '۰۱۲۳۴۵۶۷۸۹'

export function toNumber(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (value === null || value === undefined || value === '') return 0
  const normalized = String(value)
    .trim()
    .replace(/[۰-۹]/g, (d) => String(persianDigits.indexOf(d)))
    .replace(/,/g, '')
  const parsed = Number(normalized)
  return Number.isFinite(parsed) ? parsed : 0
}

export function resolveClothNeeds(primary, fallback) {
  const read = (src, key) => {
    if (!src || src[key] === undefined || src[key] === null || src[key] === '') return null
    return toNumber(src[key])
  }

  const oddRaw = read(primary, 'odd_cloth')
  const evenRaw = read(primary, 'even_cloth')
  const minorRaw = read(primary, 'minor_cloth')

  return {
    odd: oddRaw !== null ? oddRaw : toNumber(fallback?.odd_cloth),
    even: evenRaw !== null ? evenRaw : toNumber(fallback?.even_cloth),
    minor: minorRaw !== null ? minorRaw : toNumber(fallback?.minor_cloth),
  }
}

export function computeMainFabricMeters(quantity, clothNeeds) {
  const qty = Math.max(0, Math.trunc(toNumber(quantity)))
  const odd = Math.max(0, toNumber(clothNeeds?.odd))
  const rawEven = Math.max(0, toNumber(clothNeeds?.even))
  const even = rawEven > 0 ? rawEven : odd * 2
  const pairs = Math.floor(qty / 2)
  const singles = qty % 2
  return (pairs * even) + (singles * odd)
}

export function computeMinorFabricMeters(quantity, clothNeeds) {
  const qty = Math.max(0, Math.trunc(toNumber(quantity)))
  const minor = Math.max(0, toNumber(clothNeeds?.minor))
  return qty * minor
}

export function computeTotalFabricMeters(quantity, clothNeeds) {
  return computeMainFabricMeters(quantity, clothNeeds) + computeMinorFabricMeters(quantity, clothNeeds)
}

export function calculateFabricPrice(meters, pricePerMeter) {
  const safeMeters = Math.max(0, toNumber(meters))
  const safePrice = Math.max(0, toNumber(pricePerMeter))
  if (!safeMeters || !safePrice) return 0
  return Math.ceil((safeMeters * safePrice) / 10) * 10
}

export function calculatePriceWithFabric(basePrice, fabricPrice) {
  return Math.max(0, toNumber(basePrice)) + Math.max(0, toNumber(fabricPrice))
}
