import { hasAnalyticsConsent } from './analyticsConsent'
const STORAGE_KEY = 'denroom_analytics_session_id'

function csrfToken() {
  return window.csrf_token || window.frappe?.csrf_token || ''
}

export function getAnalyticsSessionId() {
  if (!hasAnalyticsConsent()) return ''
  try {
    const existing = localStorage.getItem(STORAGE_KEY)
    if (existing) return existing
    const generated = `an_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
    localStorage.setItem(STORAGE_KEY, generated)
    return generated
  } catch (error) {
    return ''
  }
}

export function deviceType() {
  const ua = (navigator.userAgent || '').toLowerCase()
  if (ua.includes('ipad') || ua.includes('tablet')) return 'tablet'
  if (ua.includes('iphone') || ua.includes('android') || ua.includes('mobile')) return 'mobile'
  if (ua.includes('windows') || ua.includes('macintosh') || ua.includes('linux')) return 'desktop'
  return 'other'
}

function browserNameFromUserAgent() {
  const ua = (navigator.userAgent || '').toLowerCase()
  if (ua.includes('edg/') || ua.includes('edge/')) return 'edge'
  if (ua.includes('opr/') || ua.includes('opera')) return 'opera'
  if (ua.includes('samsungbrowser/')) return 'samsung'
  if (ua.includes('chrome/') && !ua.includes('edg/') && !ua.includes('opr/')) return 'chrome'
  if (ua.includes('firefox/')) return 'firefox'
  if (ua.includes('safari/') && !ua.includes('chrome/')) return 'safari'
  if (ua.includes('trident/') || ua.includes('msie')) return 'ie'
  return 'other'
}

function osNameFromUserAgent() {
  const ua = (navigator.userAgent || '').toLowerCase()
  if (ua.includes('android')) return 'android'
  if (ua.includes('iphone') || ua.includes('ipad') || ua.includes('ios')) return 'ios'
  if (ua.includes('windows')) return 'windows'
  if (ua.includes('mac os x') || ua.includes('macintosh')) return 'macos'
  if (ua.includes('linux')) return 'linux'
  if (ua.includes('cros')) return 'chromeos'
  return 'other'
}

function languageCode() {
  const raw = String(navigator.language || navigator.userLanguage || '').trim().toLowerCase()
  return raw ? raw.replace('_', '-').split(',')[0].split(';')[0] : ''
}

export async function trackAnalyticsEvent(eventType, payload = {}) {
  if (!eventType || !hasAnalyticsConsent()) return

  const baseProperties = payload.properties && typeof payload.properties === 'object' ? payload.properties : {}
  const body = {
    event_type: eventType,
    event_id: payload.event_id || `${eventType}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    occurred_at: payload.occurred_at,
    session_id: payload.session_id || getAnalyticsSessionId(),
    model_name: payload.model_name || '',
    product_id: payload.product_id || payload.item_code || '',
    item_group: payload.item_group || '',
    qty: Number(payload.qty || 1),
    amount: Number(payload.amount || 0),
    cart_value: Number(payload.cart_value || 0),
    customer: payload.customer || '',
    page_url: payload.page_url || window.location.pathname + window.location.search,
    referrer_url: payload.referrer_url || document.referrer || '',
    source_channel: payload.source_channel || '',
    device_type: payload.device_type || deviceType(),
    scroll_depth: Number(payload.scroll_depth || 0),
    time_spent_seconds: Number(payload.time_spent_seconds || 0),
    left_at: payload.left_at || '',
    properties: {
      language: baseProperties.language || languageCode(),
      browser_name: baseProperties.browser_name || browserNameFromUserAgent(),
      os_name: baseProperties.os_name || osNameFromUserAgent(),
      ...baseProperties,
    },
    dedupe_key: payload.dedupe_key || '',
  }

  const csrf = csrfToken()
  try {
    await fetch('/api/method/mysite.analytics_api.track_event', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(csrf ? { 'X-Frappe-CSRF-Token': csrf } : {}),
      },
      body: JSON.stringify(body),
      keepalive: true,
    })
  } catch (error) {
    // Analytics must not block business flow.
  }
}

export async function trackPageView(payload = {}) {
  const nowIso = new Date().toISOString()
  return trackAnalyticsEvent('page_view', {
    ...payload,
    occurred_at: payload.occurred_at || nowIso,
  })
}
