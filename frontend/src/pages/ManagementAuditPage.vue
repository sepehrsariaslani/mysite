<template>
  <section class="audit-page" dir="rtl">
<header class="head">
      <div>
        <p class="eyebrow">Workflow & Audit</p>
        <h1>صف مدیریت تغییرات و ممیزی</h1>
      </div>
      <div class="actions">
        <button class="ghost" :disabled="loading" @click="refreshAll">{{ loading ? 'در حال بروزرسانی...' : 'بروزرسانی' }}</button>
      </div>
    </header>

    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'requests' }" @click="activeTab = 'requests'">درخواست‌های تغییر</button>
      <button v-if="canViewAudit" class="tab" :class="{ active: activeTab === 'audit' }" @click="activeTab = 'audit'">لاگ ممیزی</button>
    </div>

    <section v-if="activeTab === 'requests'" class="panel">
      <div class="filters">
        <select v-model="requestFilters.module_key">
          <option value="">همه ماژول‌ها</option>
          <option value="content">content</option>
          <option value="product">product</option>
        </select>
        <select v-model="requestFilters.state">
          <option value="">همه وضعیت‌ها</option>
          <option value="Draft">Draft</option>
          <option value="In Review">In Review</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Published">Published</option>
          <option value="Cancelled">Cancelled</option>
        </select>
        <button class="ghost" :disabled="requestsLoading" @click="loadRequests">اعمال</button>
      </div>

      <div v-if="requestsError" class="state error">{{ requestsError }}</div>
      <div v-else-if="requestsLoading" class="state">در حال دریافت درخواست‌ها...</div>
      <div v-else-if="!requests.length" class="state">درخواستی ثبت نشده است.</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>شناسه</th>
              <th>ماژول</th>
              <th>نوع هدف</th>
              <th>کلید هدف</th>
              <th>وضعیت</th>
              <th>درخواست‌دهنده</th>
              <th>اقدامات</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in requests" :key="row.name" :class="{ active: selectedRequest?.name === row.name }" @click="selectRequest(row)">
              <td>{{ row.name }}</td>
              <td>{{ row.module_key }}</td>
              <td>{{ row.target_type }}</td>
              <td>{{ row.target_key }}</td>
              <td><span class="status">{{ row.state }}</span></td>
              <td>{{ row.requested_by || '-' }}</td>
              <td class="row-actions">
                <button
                  v-for="action in availableActions(row)"
                  :key="`${row.name}-${action.key}`"
                  class="mini"
                  :class="{ danger: action.danger }"
                  :disabled="actionLoading"
                  @click.stop="runAction(row.name, action.key)"
                >
                  {{ action.label }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <article v-if="selectedRequestDetail" class="detail">
        <h3>جزئیات درخواست: {{ selectedRequestDetail.name }}</h3>
        <p class="muted">وضعیت: {{ selectedRequestDetail.state }} | ماژول: {{ selectedRequestDetail.module_key }}</p>
        <div class="json-grid">
          <label>
            <span>Request Payload</span>
            <textarea :value="prettyJson(selectedRequestDetail.request_payload_json)" rows="8" readonly></textarea>
          </label>
          <label>
            <span>Current Snapshot</span>
            <textarea :value="prettyJson(selectedRequestDetail.current_snapshot_json)" rows="8" readonly></textarea>
          </label>
        </div>
      </article>

      <p v-if="actionError" class="state error">{{ actionError }}</p>
      <p v-if="actionSuccess" class="state success">{{ actionSuccess }}</p>
    </section>

    <section v-else class="panel">
      <div class="filters">
        <select v-model="auditFilters.module_key">
          <option value="">همه ماژول‌ها</option>
          <option value="content">content</option>
          <option value="product">product</option>
          <option value="support">support</option>
          <option value="analytics">analytics</option>
          <option value="system">system</option>
        </select>
        <select v-model="auditFilters.result">
          <option value="">همه نتایج</option>
          <option value="success">success</option>
          <option value="failed">failed</option>
          <option value="denied">denied</option>
        </select>
        <button class="ghost" :disabled="auditLoading" @click="loadAudit">اعمال</button>
      </div>

      <div v-if="auditError" class="state error">{{ auditError }}</div>
      <div v-else-if="auditLoading" class="state">در حال دریافت لاگ‌ها...</div>
      <div v-else-if="!auditRows.length" class="state">لاگی برای نمایش وجود ندارد.</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>زمان</th>
              <th>ماژول</th>
              <th>اکشن</th>
              <th>هدف</th>
              <th>نتیجه</th>
              <th>کاربر</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in auditRows" :key="row.name">
              <td>{{ formatDate(row.occurred_at) }}</td>
              <td>{{ row.module_key }}</td>
              <td>{{ row.action_key }}</td>
              <td>{{ row.target_type }} / {{ row.target_key || '-' }}</td>
              <td><span class="status">{{ row.result }}</span></td>
              <td>{{ row.actor || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { getManagementAccessSnapshot, hasManagementCapability } from '../utils/managementAccess'

const activeTab = ref('requests')
const loading = ref(false)

const requestsLoading = ref(false)
const requestsError = ref('')
const requests = ref([])
const selectedRequest = ref(null)
const selectedRequestDetail = ref(null)

const actionLoading = ref(false)
const actionError = ref('')
const actionSuccess = ref('')

const auditLoading = ref(false)
const auditError = ref('')
const auditRows = ref([])

const requestFilters = reactive({
  module_key: '',
  state: '',
  limit: 80,
  offset: 0,
})

const auditFilters = reactive({
  module_key: '',
  result: '',
  limit: 150,
  offset: 0,
})
const canViewAudit = computed(() =>
  hasManagementCapability('audit.view')
  || hasManagementCapability('content.edit')
  || hasManagementCapability('product.edit')
  || hasManagementCapability('support.manage')
  || hasManagementCapability('analytics.view')
)

const WORKFLOW_ACTIONS = {
  submit_review: { key: 'submit_review', label: 'ارسال برای بازبینی', danger: false },
  return_to_draft: { key: 'return_to_draft', label: 'بازگشت به پیش‌نویس', danger: false },
  approve: { key: 'approve', label: 'تایید', danger: false },
  reject: { key: 'reject', label: 'رد', danger: true },
  publish: { key: 'publish', label: 'انتشار', danger: false },
  cancel: { key: 'cancel', label: 'لغو', danger: true },
}

function capabilityForAction(moduleKey, action) {
  const module = String(moduleKey || '').trim().toLowerCase()
  if (module === 'content') {
    if (action === 'submit_review') return 'content.edit'
    if (action === 'return_to_draft' || action === 'approve' || action === 'reject') return 'content.review'
    if (action === 'publish' || action === 'cancel') return 'content.publish'
  }
  if (module === 'product') {
    if (action === 'submit_review') return 'product.edit'
    if (action === 'return_to_draft' || action === 'approve' || action === 'reject') return 'product.review'
    if (action === 'publish' || action === 'cancel') return 'product.publish'
  }
  return 'management.access'
}

function stateActions(state) {
  const current = String(state || '').trim()
  if (current === 'Draft') return ['submit_review', 'cancel']
  if (current === 'In Review') return ['return_to_draft', 'approve', 'reject', 'cancel']
  if (current === 'Approved') return ['publish', 'cancel']
  return []
}

function availableActions(row) {
  const snapshot = getManagementAccessSnapshot()
  return stateActions(row?.state)
    .filter((action) => hasManagementCapability(capabilityForAction(row?.module_key, action)))
    .map((action) => WORKFLOW_ACTIONS[action])
    .filter(Boolean)
    .filter(() => snapshot.allowed)
}

function csrfToken() {
  return window?.csrf_token || window?.frappe?.csrf_token || ''
}

async function getJson(url) {
  const response = await fetch(url, {
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload?.message || payload?.exc || 'Request failed')
  }
  return payload?.message || payload
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'X-Frappe-CSRF-Token': csrfToken(),
    },
    body: JSON.stringify(body || {}),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload?.message || payload?.exc || 'Request failed')
  }
  return payload?.message || payload
}

function toQuery(paramsObj) {
  const params = new URLSearchParams()
  Object.entries(paramsObj).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') return
    params.set(key, String(value))
  })
  return params.toString()
}

async function loadRequests() {
  requestsLoading.value = true
  requestsError.value = ''
  try {
    const qs = toQuery(requestFilters)
    const result = await getJson(`/api/method/mysite.api.list_management_change_requests?${qs}`)
    requests.value = result?.items || []
  } catch (error) {
    requestsError.value = error?.message || 'خطا در دریافت درخواست‌ها'
  } finally {
    requestsLoading.value = false
  }
}

async function selectRequest(row) {
  selectedRequest.value = row
  selectedRequestDetail.value = null
  if (!row?.name) return
  try {
    const result = await getJson(`/api/method/mysite.api.get_management_change_request_detail?name=${encodeURIComponent(row.name)}`)
    selectedRequestDetail.value = result?.change_request || null
  } catch (error) {
    actionError.value = error?.message || 'خطا در دریافت جزئیات درخواست'
  }
}

async function runAction(name, action) {
  if (!name || !action) return
  actionLoading.value = true
  actionError.value = ''
  actionSuccess.value = ''
  try {
    await postJson('/api/method/mysite.api.transition_management_change_request', {
      name,
      action,
    })
    actionSuccess.value = `اکشن ${action} با موفقیت ثبت شد.`
    await loadRequests()
    if (selectedRequest.value?.name === name) {
      await selectRequest({ name })
    }
  } catch (error) {
    actionError.value = error?.message || 'خطا در ثبت اکشن'
  } finally {
    actionLoading.value = false
  }
}

async function loadAudit() {
  if (!canViewAudit.value) {
    auditRows.value = []
    auditError.value = 'دسترسی مشاهده لاگ ممیزی را ندارید.'
    return
  }
  auditLoading.value = true
  auditError.value = ''
  try {
    const qs = toQuery(auditFilters)
    const result = await getJson(`/api/method/mysite.api.get_management_audit_logs?${qs}`)
    auditRows.value = result?.items || []
  } catch (error) {
    auditError.value = error?.message || 'خطا در دریافت لاگ‌ها'
  } finally {
    auditLoading.value = false
  }
}

async function refreshAll() {
  loading.value = true
  const tasks = [loadRequests()]
  if (canViewAudit.value) {
    tasks.push(loadAudit())
  }
  await Promise.all(tasks)
  loading.value = false
}

function prettyJson(raw) {
  try {
    return JSON.stringify(JSON.parse(raw || '{}'), null, 2)
  } catch (error) {
    return String(raw || '')
  }
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('fa-IR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}

onMounted(() => {
  if (!canViewAudit.value && activeTab.value === 'audit') {
    activeTab.value = 'requests'
  }
  refreshAll()
})
</script>

<style scoped>
.audit-page {
  padding: var(--space-6);
  padding-bottom: 80px;
  color: var(--text-main);
  overflow-x: hidden;
  max-width: 100vw;
  box-sizing: border-box;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0;
  color: var(--admin-text-soft);
  font-size: var(--text-base);
}

h1 {
  margin: 4px 0 0;
  font-size: 1.5rem;
}

.tabs {
  display: flex;
  gap: var(--space-3);
  margin-bottom: 14px;
}

.tab {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  cursor: pointer;
}

.tab.active {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  border-color: transparent;
  color: #fff;
}

.panel {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-panel-bg);
  padding: var(--space-4);
}

.filters {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.filters select {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  padding: var(--space-2) var(--space-3);
}

.ghost,
.mini {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
}

.mini {
  font-size: 0.76rem;
  padding: 5px 8px;
}

.mini.danger {
  border-color: color-mix(in srgb, #ef4444 60%, var(--admin-border) 40%);
}

.table-wrap {
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

th,
td {
  border-bottom: 1px solid var(--admin-border);
  text-align: right;
  padding: 9px 8px;
  vertical-align: top;
}

tbody tr.active {
  background: color-mix(in srgb, var(--admin-chip-bg) 70%, transparent);
}

.status {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-pill);
  padding: 3px 8px;
  font-size: 0.72rem;
}

.row-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.state {
  margin: 8px 0;
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: color-mix(in srgb, var(--admin-chip-bg) 70%, transparent);
}

.state.error {
  color: #ef4444;
}

.state.success {
  color: #22c55e;
}

.detail {
  margin-top: 16px;
  border-top: 1px solid var(--admin-border);
  padding-top: 14px;
}

.muted {
  color: var(--admin-text-soft);
}

.json-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.json-grid textarea {
  width: 100%;
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: var(--space-3);
}

@media (max-width: 1100px) {
  .json-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .audit-page {
  }
  .head {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>
