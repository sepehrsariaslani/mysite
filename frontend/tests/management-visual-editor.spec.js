import { beforeEach, describe, expect, it, vi } from 'vitest'

import { parseJsonResponse, postEditorMethodWithFallback } from '../src/pages/management-visual-editor/composables/useEditorApi'
import { useAutoSave } from '../src/pages/management-visual-editor/composables/useAutoSave'

describe('management visual editor composables', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    window.frappe = undefined
    window.csrf_token = ''
  })

  it('parseJsonResponse throws explicit error for HTML payload', async () => {
    const response = new Response('<!doctype html><html><body>500</body></html>', {
      status: 500,
      headers: { 'Content-Type': 'text/html' },
    })
    await expect(parseJsonResponse(response)).rejects.toThrow('پاسخ سرور JSON نبود')
  })

  it('postEditorMethodWithFallback falls back to form transport', async () => {
    const fetchMock = vi.fn()
    fetchMock
      .mockResolvedValueOnce(
        new Response('<!doctype html><html><body>error</body></html>', {
          status: 500,
          headers: { 'Content-Type': 'text/html' },
        })
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ ok: true, message: { ok: true } }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      )

    vi.stubGlobal('fetch', fetchMock)

    const { response, payload } = await postEditorMethodWithFallback(
      '/api/method/mysite.api.save_management_visual_editor_changes',
      { route: '/mysite', full_source: '<template></template>' }
    )

    expect(response.ok).toBe(true)
    expect(payload.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('useAutoSave enforces single-flight save', async () => {
    let unsaved = true
    let resolveVisual

    const saveSource = vi.fn(async () => true)
    const saveVisual = vi.fn(
      () =>
        new Promise((resolve) => {
          resolveVisual = () => {
            unsaved = false
            resolve(true)
          }
        })
    )

    const auto = useAutoSave({
      hasUnsavedChanges: () => unsaved,
      canRun: () => true,
      saveVisual,
      saveSource,
      debounceMs: 50,
      retryDelayMs: 50,
      maxRetries: 1,
    })

    const p1 = auto.runNow()
    const p2 = auto.runNow()

    expect(saveSource).toHaveBeenCalledTimes(1)
    expect(saveVisual).toHaveBeenCalledTimes(1)

    resolveVisual()
    await p1
    await p2

    expect(auto.getState().running).toBe(false)
  })
})
