import { hasAnalyticsConsent } from './analyticsConsent'

const STORAGE_KEY = 'denroom_funnel_session_id'

const getLocalSessionId = () => {
  if (!hasAnalyticsConsent()) return ''
  try {
    const existing = localStorage.getItem(STORAGE_KEY)
    if (existing) return existing
    const generated = `sid_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
    localStorage.setItem(STORAGE_KEY, generated)
    return generated
  } catch (error) {
    return ''
  }
}

const getCsrfToken = () => window.csrf_token || window.frappe?.csrf_token || ''

export const trackFunnelEvent = async (step, payload = {}) => {
  if (!step || !hasAnalyticsConsent()) return

  const body = {
    step,
    session_id: getLocalSessionId(),
    model_name: payload.model_name || '',
    item_code: payload.item_code || '',
    qty: Number(payload.qty || 1),
    amount: Number(payload.amount || 0),
    customer: payload.customer || '',
  }

  const csrf = getCsrfToken()
  try {
    await fetch('/api/method/mysite.www.mysite.product.track_funnel_event', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(csrf ? { 'X-Frappe-CSRF-Token': csrf } : {}),
      },
      body: JSON.stringify(body),
      keepalive: true,
    })
  } catch (error) {
    // Analytics must not break business flow.
  }
}

export const inferModelName = (product = {}, configuration = {}) => {
  return (
    configuration?.model_name
    || configuration?.meta?.model_name
    || product?.parent_model_name
    || product?.display_name
    || product?.name
    || ''
  )
}
