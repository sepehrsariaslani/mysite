const CONSENT_KEY = 'denroom_analytics_consent'
const GRANTED = 'granted'
const DENIED = 'denied'

function safeGetStorage() {
  try {
    return window.localStorage
  } catch (error) {
    return null
  }
}

export function getAnalyticsConsentStatus() {
  const storage = safeGetStorage()
  if (!storage) return ''
  const raw = String(storage.getItem(CONSENT_KEY) || '').trim().toLowerCase()
  if (raw === GRANTED || raw === DENIED) return raw
  return ''
}

export function hasAnalyticsConsent() {
  return getAnalyticsConsentStatus() === GRANTED
}

export function isAnalyticsConsentResolved() {
  const status = getAnalyticsConsentStatus()
  return status === GRANTED || status === DENIED
}

export function setAnalyticsConsent(status) {
  const normalized = String(status || '').trim().toLowerCase()
  const storage = safeGetStorage()
  if (!storage) return

  if (normalized === GRANTED || normalized === DENIED) {
    storage.setItem(CONSENT_KEY, normalized)
  } else {
    storage.removeItem(CONSENT_KEY)
  }

  if (normalized === DENIED) {
    storage.removeItem('denroom_analytics_session_id')
    storage.removeItem('denroom_funnel_session_id')
  }

  try {
    window.dispatchEvent(new CustomEvent('denroom:analytics-consent-changed', { detail: normalized }))
  } catch (error) {
    // Ignore browser compatibility issues.
  }
}
