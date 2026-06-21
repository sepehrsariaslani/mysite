import { describe, expect, it } from 'vitest'
import { buildFilterOptions, filterItems, sortItems } from './productFiltering'

const records = [
  { name: 'مدل آ', colors: ['مشکی', 'سفید'], prices: [5000000, 3000000] },
  { name: 'مدل ب', colors: ['بژ'], prices: [7000000] },
  { name: 'مدل پ', colors: ['مشکی'], prices: [2000000] },
]

const adapter = {
  getName: (item) => item.name,
  getColors: (item) => item.colors,
  getPrices: (item) => item.prices,
}

describe('productFiltering', () => {
  it('builds deduplicated filter options', () => {
    const options = buildFilterOptions(records, adapter)

    expect(options.models.map((entry) => entry.value)).toEqual(['مدل آ', 'مدل ب', 'مدل پ'])
    expect(options.colors.map((entry) => entry.value)).toEqual(['مشکی', 'سفید', 'بژ'])
    expect(options.minBound).toBe(2000000)
    expect(options.maxBound).toBe(7000000)
    expect(options.step).toBe(1000000)
  })

  it('filters by model, color, and price range', () => {
    const byModel = filterItems(records, { models: ['مدل ب'] }, adapter)
    expect(byModel.map((item) => item.name)).toEqual(['مدل ب'])

    const byColor = filterItems(records, { colors: ['مشکی'] }, adapter)
    expect(byColor.map((item) => item.name)).toEqual(['مدل آ', 'مدل پ'])

    const byPrice = filterItems(
      records,
      { priceMin: 2500000, priceMax: 6000000, priceActive: true },
      adapter
    )
    expect(byPrice.map((item) => item.name)).toEqual(['مدل آ'])
  })

  it('supports combining all filters', () => {
    const filtered = filterItems(
      records,
      {
        models: ['مدل آ', 'مدل پ'],
        colors: ['مشکی'],
        priceMin: 1000000,
        priceMax: 2500000,
        priceActive: true,
      },
      adapter
    )

    expect(filtered.map((item) => item.name)).toEqual(['مدل پ'])
  })

  it('sorts by price and name', () => {
    const lowToHigh = sortItems(records, 'price-low', adapter)
    expect(lowToHigh.map((item) => item.name)).toEqual(['مدل پ', 'مدل آ', 'مدل ب'])

    const highToLow = sortItems(records, 'price-high', adapter)
    expect(highToLow.map((item) => item.name)).toEqual(['مدل ب', 'مدل آ', 'مدل پ'])

    const nameAsc = sortItems(records, 'name-asc', adapter)
    expect(nameAsc.map((item) => item.name)).toEqual(['مدل آ', 'مدل ب', 'مدل پ'])
  })
})
