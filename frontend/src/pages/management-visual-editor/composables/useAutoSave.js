export function useAutoSave({
  hasUnsavedChanges,
  canRun,
  saveVisual,
  saveSource,
  debounceMs = 1400,
  retryDelayMs = 2600,
  maxRetries = 3,
}) {
  let timer = null
  let retryCount = 0
  let running = false
  let pending = false

  function clear() {
    if (timer !== null) {
      window.clearTimeout(timer)
      timer = null
    }
  }

  function cancel() {
    clear()
    pending = false
  }

  function schedule(delayMs = debounceMs) {
    if (!hasUnsavedChanges()) {
      cancel()
      return
    }
    pending = true
    clear()
    timer = window.setTimeout(() => {
      timer = null
      void runNow()
    }, Math.max(500, Number(delayMs || debounceMs)))
  }

  async function runNow() {
    if (!hasUnsavedChanges()) {
      pending = false
      retryCount = 0
      return true
    }
    if (!canRun() || running) {
      schedule(Math.max(900, debounceMs))
      return false
    }

    running = true
    pending = false
    let ok = true
    try {
      const sourceOk = await saveSource()
      const visualOk = await saveVisual()
      ok = Boolean(sourceOk) && Boolean(visualOk)
    } finally {
      running = false
    }

    if (ok && !hasUnsavedChanges()) {
      retryCount = 0
      return true
    }

    if (!ok) {
      retryCount += 1
      if (retryCount <= maxRetries && hasUnsavedChanges()) {
        schedule(retryDelayMs)
      }
      return false
    }

    retryCount = 0
    if (hasUnsavedChanges()) schedule(debounceMs)
    return true
  }

  return {
    schedule,
    runNow,
    cancel,
    clear,
    getState: () => ({ pending, running, retryCount }),
  }
}
