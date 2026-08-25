import { computed, ref, watch } from 'vue'

const MODE_STORAGE_KEY = 'mysite.management_editor.mode'

function normalizeMode(value) {
  const mode = String(value || '').trim().toLowerCase()
  return mode === 'developer' ? 'developer' : 'design'
}

function readModeFromQuery() {
  try {
    const params = new URLSearchParams(window.location.search)
    const raw = params.get('mode')
    if (!raw) return ''
    return normalizeMode(raw)
  } catch {
    return ''
  }
}

function readModeFromStorage() {
  try {
    return normalizeMode(window.localStorage.getItem(MODE_STORAGE_KEY))
  } catch {
    return 'design'
  }
}

function writeModeToStorage(mode) {
  try {
    window.localStorage.setItem(MODE_STORAGE_KEY, normalizeMode(mode))
  } catch {
    // noop
  }
}

function writeModeToQuery(mode) {
  try {
    const params = new URLSearchParams(window.location.search)
    params.set('mode', normalizeMode(mode))
    const nextUrl = `${window.location.pathname}?${params.toString()}`
    window.history.replaceState({}, '', nextUrl)
  } catch {
    // noop
  }
}

export function useEditorMode() {
  const mode = ref(readModeFromQuery() || readModeFromStorage() || 'design')

  function setMode(nextMode) {
    mode.value = normalizeMode(nextMode)
  }

  function toggleMode() {
    mode.value = mode.value === 'design' ? 'developer' : 'design'
  }

  watch(mode, (nextMode) => {
    writeModeToStorage(nextMode)
    writeModeToQuery(nextMode)
  }, { immediate: true })

  return {
    mode,
    isDesignMode: computed(() => mode.value === 'design'),
    isDeveloperMode: computed(() => mode.value === 'developer'),
    setMode,
    toggleMode,
    normalizeMode,
  }
}
