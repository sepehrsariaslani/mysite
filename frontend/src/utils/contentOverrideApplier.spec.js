import { beforeEach, describe, expect, it, vi } from 'vitest'

import { applyRouteContentOverrides, stopRouteContentOverrideObserver } from './contentOverrideApplier'

describe('contentOverrideApplier', () => {
  let observerCreateCount = 0

  beforeEach(() => {
    observerCreateCount = 0
    vi.restoreAllMocks()
    vi.unstubAllGlobals()

    class FakeMutationObserver {
      constructor() {
        observerCreateCount += 1
      }
      observe() {}
      disconnect() {}
    }

    vi.stubGlobal('MutationObserver', FakeMutationObserver)
    document.body.innerHTML = '<div id="root">A</div>'
  })

  it('does not start observer for visual-only overrides', () => {
    const result = applyRouteContentOverrides([], {
      visualItems: [{ selector: '#root', styles: { color: 'rgb(255, 0, 0)' } }],
    })

    expect(result.visualCount).toBe(1)
    expect(observerCreateCount).toBe(0)
  })

  it('starts observer for text overrides', () => {
    const result = applyRouteContentOverrides([
      { source_text: 'A', replacement_text: 'B' },
    ])

    expect(result.count).toBe(1)
    expect(observerCreateCount).toBe(1)

    stopRouteContentOverrideObserver()
  })
})
