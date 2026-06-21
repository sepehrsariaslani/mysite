import { ref } from 'vue'

export const managementAccessVersion = ref(0)

function safeArray(value) {
  return Array.isArray(value) ? value : []
}

export function getManagementAccessSnapshot() {
  const boot = window.management_boot || {}
  const runtime = window.__managementAccess || {}

  const roles = safeArray(runtime.roles).length ? safeArray(runtime.roles) : safeArray(boot.roles)
  const capabilities = safeArray(runtime.capabilities).length
    ? safeArray(runtime.capabilities)
    : safeArray(boot.capabilities)

  return {
    allowed: Boolean(runtime.allowed ?? boot.allowed ?? false),
    requiredAllowed: Boolean(runtime.required_allowed ?? boot.required_allowed ?? true),
    requiredCapability: String(runtime.required_capability || boot.required_capability || '').trim(),
    roles,
    capabilities,
  }
}

export function syncManagementAccessState(payload) {
  const msg = payload?.message || payload || {}
  const boot = window.management_boot || {}
  window.__managementAccess = {
    allowed: Boolean(msg.allowed ?? boot.allowed ?? false),
    required_allowed: Boolean(msg.required_allowed ?? boot.required_allowed ?? true),
    required_capability: String(msg.required_capability || boot.required_capability || '').trim(),
    roles: safeArray(msg.roles).length ? safeArray(msg.roles) : safeArray(boot.roles),
    capabilities: safeArray(msg.capabilities).length ? safeArray(msg.capabilities) : safeArray(boot.capabilities),
  }
  managementAccessVersion.value += 1
  return window.__managementAccess
}

export function hasManagementCapability(capability) {
  // Dependency for Vue computed/watch callers.
  managementAccessVersion.value
  const key = String(capability || '').trim()
  if (!key) return true
  const snapshot = getManagementAccessSnapshot()
  return snapshot.capabilities.includes(key)
}
