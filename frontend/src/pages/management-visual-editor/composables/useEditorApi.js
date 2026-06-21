const DEFAULT_TIMEOUT_MS = 45000

export function resolveCsrfToken() {
  const fromWindow = String(window.csrf_token || '').trim()
  if (fromWindow) return fromWindow
  const fromFrappe = String(window.frappe?.csrf_token || '').trim()
  if (fromFrappe) return fromFrappe
  try {
    const metaToken = String(document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '').trim()
    if (metaToken) return metaToken
  } catch {
    // noop
  }
  try {
    const cookieMatch = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)
    const cookieToken = String(cookieMatch?.[1] || '').trim()
    if (cookieToken) return decodeURIComponent(cookieToken)
  } catch {
    // noop
  }
  return ''
}

export function buildApiJsonHeaders() {
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  }
  const csrfToken = resolveCsrfToken()
  if (csrfToken) headers['X-Frappe-CSRF-Token'] = csrfToken
  return headers
}

export async function parseJsonResponse(response) {
  const text = await response.text()
  if (!text) return {}
  try {
    return JSON.parse(text)
  } catch {
    const normalized = text.trim().toLowerCase()
    const looksHtml = normalized.startsWith('<!doctype html') || normalized.startsWith('<html')
    if (looksHtml) {
      const isAuthIssue =
        Number(response.status || 0) === 401 ||
        Number(response.status || 0) === 403 ||
        Boolean(response.redirected) ||
        normalized.includes('login') ||
        normalized.includes('sign in')
      if (normalized.includes('does not exist')) {
        throw new Error('دامنه/سایت جاری در Frappe پیدا نشد. لطفاً با دامنه صحیح سایت وارد شوید.')
      }
      if (isAuthIssue) {
        throw new Error('پاسخ سرور به‌جای JSON، HTML بود. احتمالاً نشست شما منقضی شده؛ صفحه را رفرش و دوباره وارد شوید.')
      }
      throw new Error('پاسخ سرور JSON نبود و HTML برگشت. معمولاً یعنی endpoint خطای داخلی داده است.')
    }
    const snippet = text.replace(/\s+/g, ' ').trim().slice(0, 140)
    throw new Error(`پاسخ JSON معتبر نیست: ${snippet || 'empty'}`)
  }
}

function getApiMethodName(endpoint) {
  const raw = String(endpoint || '').trim()
  if (!raw) return ''
  const marker = '/api/method/'
  const idx = raw.indexOf(marker)
  if (idx === -1) return ''
  const methodPart = raw.slice(idx + marker.length)
  const [method] = methodPart.split('?')
  return String(method || '').trim()
}

function toFrappeCallResponse(payload) {
  const hasException = Boolean(payload?.exc || payload?.exception || payload?.exc_type)
  const status = hasException ? 500 : 200
  return { response: { ok: !hasException, status, redirected: false }, payload: payload || {} }
}

function callMethodViaFrappe(endpoint, body) {
  return new Promise((resolve, reject) => {
    const method = getApiMethodName(endpoint)
    if (!method || typeof window?.frappe?.call !== 'function') {
      reject(new Error('__FRAPPE_CALL_UNAVAILABLE__'))
      return
    }
    try {
      window.frappe.call({
        method,
        args: body || {},
        callback: (response) => resolve(toFrappeCallResponse(response)),
        error: (errorResponse) => {
          const message = String(errorResponse?._server_messages || errorResponse?.message || '').trim()
          reject(new Error(message || 'frappe.call error'))
        },
      })
    } catch (error) {
      reject(error)
    }
  })
}

function shouldFallbackToFormRequest(error, response) {
  const status = Number(response?.status || 0)
  if (status >= 500 || status === 404 || status === 405) return true
  const text = String(error?.message || '').toLowerCase()
  if (!text) return false
  return (
    text.includes('unexpected token') ||
    text.includes('json') ||
    text.includes('html') ||
    text.includes('پاسخ سرور json نبود') ||
    text.includes('پاسخ json معتبر نیست')
  )
}

function buildRpcFormBody(method, body) {
  const formBody = new URLSearchParams()
  formBody.set('cmd', String(method || '').trim())
  formBody.set('payload', JSON.stringify(body || {}))
  for (const [key, value] of Object.entries(body || {})) {
    if (value === undefined) continue
    if (value === null) {
      formBody.set(key, '')
      continue
    }
    if (typeof value === 'string') {
      formBody.set(key, value)
      continue
    }
    formBody.set(key, JSON.stringify(value))
  }
  return formBody
}

export async function postEditorMethodWithFallback(endpoint, body) {
  try {
    return await callMethodViaFrappe(endpoint, body)
  } catch (frappeCallError) {
    if (String(frappeCallError?.message || '') !== '__FRAPPE_CALL_UNAVAILABLE__') {
      // Fall through to fetch transport.
    }
  }

  let firstError = null
  let firstResponse = null
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      credentials: 'same-origin',
      headers: buildApiJsonHeaders(),
      body: JSON.stringify(body || {}),
    })
    firstResponse = response
    const payload = await parseJsonResponse(response)
    if (response.ok && !payload?.exception && !payload?.exc_type) return { response, payload }
    if (!shouldFallbackToFormRequest(null, response)) return { response, payload }
  } catch (error) {
    firstError = error
    if (!shouldFallbackToFormRequest(error, firstResponse)) throw error
  }

  const fallbackHeaders = {
    Accept: 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
  }
  const csrfToken = resolveCsrfToken()
  if (csrfToken) fallbackHeaders['X-Frappe-CSRF-Token'] = csrfToken

  let endpointFormResponse = null
  let endpointFormPayload = {}
  let endpointFormError = null
  try {
    const formBody = buildRpcFormBody('', body)
    formBody.delete('cmd')
    endpointFormResponse = await fetch(endpoint, {
      method: 'POST',
      credentials: 'same-origin',
      headers: fallbackHeaders,
      body: formBody.toString(),
    })
    endpointFormPayload = await parseJsonResponse(endpointFormResponse)
    if (endpointFormResponse.ok && !endpointFormPayload?.exception && !endpointFormPayload?.exc_type) {
      return { response: endpointFormResponse, payload: endpointFormPayload }
    }
  } catch (error) {
    endpointFormError = error
  }

  const method = getApiMethodName(endpoint)
  if (method) {
    const rpcResponse = await fetch('/api/method', {
      method: 'POST',
      credentials: 'same-origin',
      headers: fallbackHeaders,
      body: buildRpcFormBody(method, body).toString(),
    })
    const rpcPayload = await parseJsonResponse(rpcResponse)
    return { response: rpcResponse, payload: rpcPayload }
  }

  if (endpointFormError) throw endpointFormError
  if (firstError && !(endpointFormResponse?.ok)) throw firstError
  return { response: endpointFormResponse, payload: endpointFormPayload }
}

export async function fetchJsonWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController()
  const timeoutHandle = window.setTimeout(() => controller.abort(), Math.max(1000, Number(timeoutMs || DEFAULT_TIMEOUT_MS)))
  try {
    const response = await fetch(url, { ...options, signal: controller.signal })
    const payload = await parseJsonResponse(response)
    return { response, payload }
  } finally {
    window.clearTimeout(timeoutHandle)
  }
}
