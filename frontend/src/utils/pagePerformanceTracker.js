import { getAnalyticsSessionId, trackAnalyticsEvent } from './analyticsTracker'

function safeNumber(value, fallback = 0) {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

function computeScrollDepth() {
  const scrollTop = window.scrollY || window.pageYOffset || 0
  const totalScrollable = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1)
  return Math.max(0, Math.min(100, Math.round((scrollTop / totalScrollable) * 100)))
}

function pageLoadMs() {
  try {
    const nav = performance.getEntriesByType?.('navigation')?.[0]
    const value = safeNumber(nav?.loadEventEnd || nav?.domComplete || 0)
    if (value > 0) return Math.round(value)
  } catch (error) {
    // Ignore and fallback.
  }
  return Math.max(1, Math.round(safeNumber(performance.now(), 0)))
}

export function initPagePerformanceTracking({ page = '' } = {}) {
  if (typeof window === 'undefined' || typeof performance === 'undefined') {
    return () => {}
  }

  let lcpMs = 0
  let clsScore = 0
  let fidMs = 0
  let inpMs = 0
  let sent = false
  const startedAt = Date.now()
  const disconnectors = []

  const observe = (type, handler, options = {}) => {
    try {
      if (typeof PerformanceObserver === 'undefined') return
      if (Array.isArray(PerformanceObserver.supportedEntryTypes) && !PerformanceObserver.supportedEntryTypes.includes(type)) return
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) handler(entry)
      })
      observer.observe({ type, buffered: true, ...options })
      disconnectors.push(() => observer.disconnect())
    } catch (error) {
      // Unsupported in browser.
    }
  }

  observe('largest-contentful-paint', (entry) => {
    lcpMs = Math.max(lcpMs, safeNumber(entry.startTime, 0))
  })

  observe('layout-shift', (entry) => {
    if (entry.hadRecentInput) return
    clsScore += safeNumber(entry.value, 0)
  })

  observe('first-input', (entry) => {
    fidMs = Math.max(fidMs, safeNumber(entry.processingStart, 0) - safeNumber(entry.startTime, 0))
  })

  observe('event', (entry) => {
    if (!safeNumber(entry.interactionId, 0)) return
    inpMs = Math.max(inpMs, safeNumber(entry.duration, 0))
  }, { durationThreshold: 40 })

  const flush = () => {
    if (sent) return
    sent = true
    disconnectors.forEach((fn) => fn())

    const sessionId = getAnalyticsSessionId()
    const timeSpent = Math.max(1, Math.round((Date.now() - startedAt) / 1000))
    const path = `${window.location.pathname || ''}${window.location.search || ''}`
    const minuteBucket = Math.floor(startedAt / 60000)

    trackAnalyticsEvent('page_performance', {
      session_id: sessionId,
      time_spent_seconds: timeSpent,
      scroll_depth: computeScrollDepth(),
      dedupe_key: `perf::${sessionId || 'anon'}::${path}::${minuteBucket}`,
      properties: {
        page,
        page_load_ms: pageLoadMs(),
        lcp_ms: Math.round(lcpMs || 0),
        cls_score: Number((clsScore || 0).toFixed(4)),
        fid_ms: Math.round(fidMs || 0),
        inp_ms: Math.round(inpMs || 0),
      },
    })
  }

  const onVisibility = () => {
    if (document.visibilityState === 'hidden') flush()
  }

  window.addEventListener('pagehide', flush, { once: true })
  document.addEventListener('visibilitychange', onVisibility)

  return () => {
    document.removeEventListener('visibilitychange', onVisibility)
    flush()
  }
}

