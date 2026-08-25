import { describe, expect, it, vi, beforeEach } from 'vitest'
import { ref, nextTick } from 'vue'

import { useEditorMode } from '../src/pages/management-visual-editor/composables/useEditorMode'
import { useDeveloperCodeView } from '../src/pages/management-visual-editor/composables/useDeveloperCodeView'

describe('management visual editor ui composables', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
    window.history.replaceState({}, '', '/mysite/management-editor')
  })

  it('syncs editor mode with query and localStorage', async () => {
    window.history.replaceState({}, '', '/mysite/management-editor?mode=developer')

    const { mode, setMode } = useEditorMode()
    expect(mode.value).toBe('developer')

    setMode('design')
    await nextTick()

    const url = new URL(window.location.href)
    expect(url.searchParams.get('mode')).toBe('design')
    expect(localStorage.getItem('mysite.management_editor.mode')).toBe('design')
  })

  it('builds snippets from selected layer and overrides', () => {
    const visualSelectedLayer = ref({
      tag: 'button',
      selector: '.cta-primary',
      original_text: 'Buy Now',
    })
    const visualOverridesMap = ref({
      '.cta-primary': {
        selector: '.cta-primary',
        styles: { backgroundColor: '#0d99ff', color: '#ffffff' },
        apply_text: true,
        text_content: 'سفارش',
      },
    })
    const sourceCode = ref('<template><button class="cta-primary">Buy Now</button></template>')
    const rawCss = ref('.cta-primary{border-radius:12px;}')

    const { cssSnippet, htmlSnippet, vueSnippet } = useDeveloperCodeView({
      visualSelectedLayer,
      visualOverridesMap,
      sourceCode,
      rawCss,
    })

    expect(cssSnippet.value).toContain('.cta-primary')
    expect(cssSnippet.value).toContain('background-color')
    expect(htmlSnippet.value).toContain('<button>Buy Now</button>')
    expect(vueSnippet.value).toContain('<template>')
  })
})
