<template>
  <section class="support-page" dir="rtl">
<header class="head">
      <div>
        <p class="eyebrow">پشتیبانی</p>
        <h1>مدیریت پشتیبانی</h1>
      </div>
      <div class="head-actions">
        <button class="ghost" :disabled="runtime.loading || loadingDashboard" @click="refreshAll">
          {{ runtime.loading || loadingDashboard ? 'در حال بروزرسانی...' : 'بروزرسانی' }}
        </button>
      </div>
    </header>

    <article v-if="!runtime.ready" class="state error">
      <strong>زیرساخت پشتیبانی آماده نیست</strong>
      <p>{{ runtime.message || 'ساختار پشتیبانی هنوز مهاجرت (migrate) نشده است.' }}</p>
      <p v-if="runtime.missing_doctypes.length">داک‌تایپ‌های ناقص: {{ runtime.missing_doctypes.join('، ') }}</p>
      <p v-if="runtime.missing_tables.length">جدول‌های ناقص: {{ runtime.missing_tables.join('، ') }}</p>
      <small>دستور راه‌اندازی: <code>bench --site den migrate</code> سپس <code>bench --site den clear-cache</code></small>
    </article>

    <template v-else>
      <div class="tabs">
        <button v-for="tab in tabs" :key="tab.id" :class="['tab', { active: activeTab === tab.id }]" @click="activeTab = tab.id">
          {{ tab.label }}
        </button>
      </div>

      <section v-if="activeTab === 'kpis'" class="panel">
        <div v-if="dashboardError" class="state error">{{ dashboardError }}</div>
        <div class="kpis">
          <article class="kpi"><p>کل تیکت</p><strong>{{ toFa(dashboard.counts.total) }}</strong></article>
          <article class="kpi"><p>باز</p><strong>{{ toFa(dashboard.counts.open) }}</strong></article>
          <article class="kpi"><p>حل‌شده</p><strong>{{ toFa(dashboard.counts.resolved) }}</strong></article>
          <article class="kpi"><p>بسته</p><strong>{{ toFa(dashboard.counts.closed) }}</strong></article>
          <article class="kpi"><p>نقض SLA</p><strong>{{ toFa(dashboard.counts.sla_failed) }}</strong></article>
          <article class="kpi"><p>تحقق SLA</p><strong>{{ toFa(dashboard.counts.sla_fulfilled) }}</strong></article>
          <article class="kpi"><p>میانگین اولین پاسخ</p><strong>{{ formatDuration(dashboard.averages.first_response_time) }}</strong></article>
          <article class="kpi"><p>میانگین پاسخ</p><strong>{{ formatDuration(dashboard.averages.avg_response_time) }}</strong></article>
        </div>

        <div class="table-wrap" v-if="dashboard.daily.length">
          <table>
            <thead><tr><th>تاریخ</th><th>تعداد تیکت</th></tr></thead>
            <tbody>
              <tr v-for="row in dashboard.daily" :key="row.date">
                <td>{{ row.date }}</td>
                <td>{{ toFa(row.count) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="activeTab === 'tickets'" class="panel split">
        <div class="left">
          <div class="toolbar">
            <input v-model.trim="ticketFilters.search" placeholder="جستجو در تیکت" />
            <input v-model.trim="ticketFilters.customer" placeholder="مشتری" />
            <button class="ghost" :disabled="ticketsLoading" @click="loadTickets">اعمال</button>
          </div>

          <div v-if="ticketsError" class="state error">{{ ticketsError }}</div>
          <div v-else-if="ticketsLoading" class="state">در حال دریافت لیست تیکت‌ها...</div>
          <div v-else-if="!tickets.length" class="state">تیکتی پیدا نشد.</div>

          <div v-else class="ticket-list">
            <button
              v-for="ticket in tickets"
              :key="ticket.name"
              class="ticket-item"
              :class="{ active: selectedTicketName === ticket.name }"
              @click="selectTicket(ticket.name)"
            >
              <strong>{{ ticket.subject }}</strong>
              <small>{{ ticket.name }} | {{ ticket.customer || '-' }}</small>
              <small>{{ formatSupportStatus(ticket.status) }} | {{ ticket.assigned_to || 'در صف' }}</small>
            </button>
          </div>
        </div>

        <div class="right">
          <div v-if="ticketDetailLoading" class="state">در حال دریافت جزئیات...</div>
          <div v-else-if="ticketDetailError" class="state error">{{ ticketDetailError }}</div>
          <div v-else-if="!ticketDetail.ticket" class="state">یک تیکت را انتخاب کنید.</div>
          <div v-else>
            <h3>{{ ticketDetail.ticket.subject }}</h3>
            <p class="muted">{{ ticketDetail.ticket.name }} | {{ formatSupportStatus(ticketDetail.ticket.status) }} | {{ ticketDetail.ticket.customer || '-' }}</p>
            <p class="muted">عامل: {{ ticketDetail.ticket.assigned_to || 'تخصیص نشده' }} | تیم: {{ formatTeamName(ticketDetail.ticket.team) }}</p>
            <p class="desc" v-html="ticketDetail.ticket.description"></p>

            <label class="field">
              <span>تغییر وضعیت</span>
              <select v-model="ticketStatusForm.status">
                <option v-for="status in supportStatuses" :key="status.name" :value="status.name">{{ formatSupportStatus(status.label_agent || status.name) }}</option>
              </select>
            </label>
            <label class="field">
              <span>جزئیات حل مسئله</span>
              <textarea v-model="ticketStatusForm.resolution_details" rows="3"></textarea>
            </label>
            <div class="actions">
              <button class="ghost" :disabled="statusSaving" @click="saveTicketStatus">ذخیره وضعیت</button>
            </div>

            <h4>گفتگو</h4>
            <div class="conversation">
              <article v-for="comm in ticketDetail.communications" :key="comm.name" class="bubble" :class="{ sent: comm.sent_or_received === 'Sent' }">
                <small>{{ comm.sender }} | {{ formatDate(comm.creation) }}</small>
                <p>{{ comm.content }}</p>
              </article>
            </div>

            <label class="field">
              <span>پاسخ</span>
              <textarea v-model="replyForm.message" rows="4" placeholder="پاسخ به مشتری"></textarea>
            </label>
            <div class="actions">
              <label class="inline"><input type="checkbox" v-model="replyForm.notify" /> ارسال ایمیل</label>
              <button class="gold" :disabled="replySending" @click="sendReply">ارسال پاسخ</button>
            </div>
            <p v-if="replyError" class="state error">{{ replyError }}</p>
            <p v-if="replySuccess" class="state success">{{ replySuccess }}</p>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'live_chat'" class="panel split">
        <div class="left">
          <div class="toolbar">
            <select v-model="chatFilters.status">
              <option value="">همه</option>
              <option value="Open">باز</option>
              <option value="Closed">بسته</option>
            </select>
            <input v-model.trim="chatFilters.search" placeholder="جستجو" />
            <button class="ghost" :disabled="liveChat.loading" @click="loadLiveChats">اعمال</button>
          </div>

          <div v-if="liveChat.error" class="state error">{{ liveChat.error }}</div>
          <div v-else-if="liveChat.loading" class="state">در حال دریافت چت‌ها...</div>
          <div v-else-if="!liveChat.items.length" class="state">چت فعالی پیدا نشد.</div>

          <div v-else class="ticket-list">
            <button
              v-for="chat in liveChat.items"
              :key="chat.name"
              class="ticket-item"
              :class="{ active: liveChat.selected?.name === chat.name }"
              @click="liveChat.selected = chat"
            >
              <strong>{{ chat.ticket_subject || chat.ticket }}</strong>
              <small>{{ chat.customer_user }} ← {{ chat.agent_user || 'در صف' }}</small>
              <small>{{ chat.last_message || '-' }}</small>
            </button>
          </div>
        </div>

        <div class="right">
          <div v-if="!liveChat.selected" class="state">یک چت را انتخاب کنید.</div>
          <div v-else>
            <h3>{{ liveChat.selected.ticket_subject || liveChat.selected.ticket }}</h3>
            <p class="muted">{{ liveChat.selected.ticket }} | {{ formatSupportStatus(liveChat.selected.status) }} | {{ liveChat.selected.customer_user }}</p>
            <p class="desc">{{ liveChat.selected.last_message || 'پیامی ثبت نشده است.' }}</p>
            <label class="field">
              <span>پاسخ در چت</span>
              <textarea v-model="liveChat.reply" rows="4" placeholder="پاسخ شما"></textarea>
            </label>
            <div class="actions">
              <button class="gold" :disabled="liveChat.replying" @click="sendLiveChatReply">ارسال پاسخ چت</button>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'shifts'" class="panel">
        <div class="toolbar">
          <button class="ghost" :disabled="shiftState.loading" @click="loadShiftStatus">بروزرسانی شیفت</button>
          <button class="ghost" :disabled="shiftState.loading" @click="loadOnlineAgents">بروزرسانی عاملان آنلاین</button>
        </div>
        <div v-if="shiftState.error" class="state error">{{ shiftState.error }}</div>
        <div v-else-if="shiftState.loading" class="state">در حال دریافت وضعیت شیفت...</div>
        <div v-else class="kpis">
          <article class="kpi"><p>آنلاین</p><strong>{{ shiftState.status.online ? 'بله' : 'خیر' }}</strong></article>
          <article class="kpi"><p>عامل آنلاین</p><strong>{{ toFa((shiftState.status.online_agents || []).length) }}</strong></article>
          <article class="kpi"><p>شیفت فعال</p><strong>{{ toFa((shiftState.status.active_shifts || []).length) }}</strong></article>
        </div>

        <div class="table-wrap" v-if="shiftState.status.active_shifts?.length">
          <table>
            <thead><tr><th>نام شیفت</th><th>تیم</th></tr></thead>
            <tbody>
              <tr v-for="row in shiftState.status.active_shifts" :key="row.name">
                <td>{{ formatShiftName(row.shift_name) }}</td>
                <td>{{ formatTeamName(row.team) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="field">
          <span>تخصیص سریع تیکت انتخاب‌شده</span>
          <small class="muted">تیکت: {{ selectedTicketName || '-' }}</small>
          <div class="actions">
            <select v-model="shiftState.assignAgent">
              <option value="">انتخاب خودکار</option>
              <option v-for="agent in shiftState.onlineAgents" :key="agent" :value="agent">{{ agent }}</option>
            </select>
            <button class="gold" :disabled="!selectedTicketName || shiftState.assigning" @click="assignSelectedTicket">
              تخصیص
            </button>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'macros'" class="panel split">
        <div class="left">
          <div class="toolbar">
            <button class="ghost" :disabled="macros.loading" @click="loadMacros">بروزرسانی ماکروها</button>
          </div>
          <div v-if="macros.error" class="state error">{{ macros.error }}</div>
          <div v-else-if="macros.loading" class="state">در حال دریافت ماکروها...</div>
          <div v-else-if="!macros.items.length" class="state">ماکرویی ثبت نشده است.</div>
          <div v-else class="ticket-list">
            <button
              v-for="macro in macros.items"
              :key="macro.name"
              class="ticket-item"
              :class="{ active: macros.selected?.name === macro.name }"
              @click="macros.selected = macro"
            >
              <strong>{{ formatMacroName(macro.macro_name || macro.name) }}</strong>
              <small>{{ formatMacroCategory(macro.category) }}</small>
              <small>{{ macro.default_status ? formatSupportStatus(macro.default_status) : 'بدون تغییر وضعیت' }}</small>
            </button>
          </div>
        </div>
        <div class="right">
          <div v-if="!macros.selected" class="state">یک ماکرو را انتخاب کنید.</div>
          <div v-else>
            <h3>{{ formatMacroName(macros.selected.macro_name || macros.selected.name) }}</h3>
            <p class="desc" v-html="macros.selected.content"></p>
            <p class="muted">تیکت انتخاب‌شده: {{ selectedTicketName || '-' }}</p>
            <div class="actions">
              <button class="gold" :disabled="!selectedTicketName || macros.applying" @click="applyMacroToSelectedTicket">اعمال روی تیکت</button>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'qa'" class="panel">
        <div class="toolbar">
          <input v-model.trim="qaFilters.search" placeholder="جستجو در سوال/پاسخ" />
          <label class="inline"><input type="checkbox" v-model="qaFilters.only_unanswered" /> فقط بی‌پاسخ</label>
          <button class="ghost" :disabled="qaLoading" @click="loadQa">اعمال</button>
        </div>
        <div v-if="qaError" class="state error">{{ qaError }}</div>
        <div v-else-if="qaLoading" class="state">در حال دریافت پرسش‌ها...</div>
        <div v-else-if="!qaItems.length" class="state">پرسشی پیدا نشد.</div>

        <div v-else class="qa-grid">
          <article v-for="item in qaItems" :key="item.question_id" class="qa-card">
            <div class="qa-head">
              <strong>{{ item.item_code || '-' }}</strong>
              <small>{{ item.question_author }}</small>
            </div>
            <p>{{ item.question }}</p>
            <p class="answer" v-if="item.answer"><b>پاسخ فعلی:</b> {{ item.answer }}</p>
            <textarea v-model="qaDraft[item.question_id]" rows="3" placeholder="ثبت/ویرایش پاسخ"></textarea>
            <div class="actions">
              <button class="ghost" @click="toggleQuestionVisibility(item.question_id, item.question_published === 1 ? 0 : 1)">
                {{ item.question_published === 1 ? 'مخفی کردن سوال' : 'نمایش سوال' }}
              </button>
              <button class="gold" @click="submitQaAnswer(item.question_id)">ذخیره پاسخ</button>
            </div>
          </article>
        </div>
      </section>

      <section v-else-if="activeTab === 'automation'" class="panel">
        <h3>قوانین خودکار</h3>
        <p class="muted">قواعد خودکار وضعیت/اولویت/تیم/ارجاع از طریق داک‌تایپ داخلی مدیریت می‌شود.</p>
        <div class="links">
          <a href="/app/ms-support-automation-rule" target="_blank" rel="noreferrer">قانون خودکار پشتیبانی</a>
          <a href="/app/ms-support-macro" target="_blank" rel="noreferrer">ماکروهای پشتیبانی</a>
          <a href="/app/ms-support-shift" target="_blank" rel="noreferrer">شیفت‌های پشتیبانی</a>
        </div>
      </section>

      <section v-else class="panel">
        <h3>توافق سطح خدمات (SLA)</h3>
        <p class="muted">مدیریت قوانین SLA از طریق فرم‌های استاندارد این داک‌تایپ‌ها انجام می‌شود.</p>
        <div class="links">
          <a href="/app/ms-support-sla" target="_blank" rel="noreferrer">تعریف SLA</a>
          <a href="/app/ms-support-ticket-status" target="_blank" rel="noreferrer">وضعیت‌های تیکت</a>
          <a href="/app/ms-support-ticket-priority" target="_blank" rel="noreferrer">اولویت‌های تیکت</a>
          <a href="/app/ms-support-team" target="_blank" rel="noreferrer">تیم‌های پشتیبانی</a>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'

const tabs = [
  { id: 'tickets', label: 'تیکت‌ها' },
  { id: 'live_chat', label: 'چت زنده' },
  { id: 'shifts', label: 'شیفت‌ها' },
  { id: 'macros', label: 'ماکروها' },
  { id: 'automation', label: 'اتوماسیون' },
  { id: 'qa', label: 'پرسش و پاسخ' },
  { id: 'kpis', label: 'شاخص‌ها' },
  { id: 'sla', label: 'SLA' },
]

const activeTab = ref('tickets')

const runtime = reactive({
  loading: false,
  ready: false,
  message: '',
  missing_doctypes: [],
  missing_tables: [],
})

const dashboard = reactive({
  counts: { total: 0, open: 0, resolved: 0, closed: 0, sla_failed: 0, sla_fulfilled: 0 },
  averages: { first_response_time: 0, avg_response_time: 0 },
  daily: [],
})
const loadingDashboard = ref(false)
const dashboardError = ref('')

const tickets = ref([])
const ticketsLoading = ref(false)
const ticketsError = ref('')
const selectedTicketName = ref('')
const ticketDetail = reactive({ ticket: null, communications: [], comments: [], activities: [] })
const ticketDetailLoading = ref(false)
const ticketDetailError = ref('')
const supportStatuses = ref([])
const statusSaving = ref(false)

const ticketFilters = reactive({ search: '', customer: '' })
const ticketStatusForm = reactive({ status: '', resolution_details: '' })
const replyForm = reactive({ message: '', notify: true })
const replySending = ref(false)
const replyError = ref('')
const replySuccess = ref('')

const liveChat = reactive({ loading: false, error: '', items: [], selected: null, reply: '', replying: false })
const chatFilters = reactive({ status: 'Open', search: '' })

const shiftState = reactive({
  loading: false,
  error: '',
  status: { online: false, online_agents: [], active_shifts: [] },
  onlineAgents: [],
  assignAgent: '',
  assigning: false,
})

const macros = reactive({ loading: false, error: '', items: [], selected: null, applying: false })

const qaItems = ref([])
const qaLoading = ref(false)
const qaError = ref('')
const qaFilters = reactive({ search: '', only_unanswered: false })
const qaDraft = reactive({})
const supportStatusMap = {
  open: 'باز',
  closed: 'بسته',
  resolved: 'حل‌شده',
  paused: 'متوقف',
  'in progress': 'در حال پیگیری',
  'on hold': 'در انتظار',
  'first response due': 'مهلت پاسخ اولیه',
  'resolution due': 'مهلت حل',
  failed: 'ناموفق',
  fulfilled: 'موفق',
}
const macroNameMap = {
  'quick acknowledge': 'تایید سریع',
  'need more info': 'نیاز به اطلاعات بیشتر',
}
const macroCategoryMap = {
  general: 'عمومی',
}
const shiftNameMap = {
  'default support shift': 'شیفت پیش‌فرض پشتیبانی',
}
const teamNameMap = {
  'support team': 'تیم پشتیبانی',
}

function toFa(value) {
  return Number(value || 0).toLocaleString('fa-IR')
}

function formatSupportStatus(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  const translated = supportStatusMap[text.toLowerCase()]
  return translated || text
}

function formatMacroName(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  return macroNameMap[text.toLowerCase()] || text
}

function formatMacroCategory(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  return macroCategoryMap[text.toLowerCase()] || text
}

function formatShiftName(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  return shiftNameMap[text.toLowerCase()] || text
}

function formatTeamName(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  return teamNameMap[text.toLowerCase()] || text
}

function formatDate(raw) {
  if (!raw) return '-'
  const dt = new Date(raw)
  if (Number.isNaN(dt.getTime())) return raw
  return dt.toLocaleString('fa-IR')
}

function formatDuration(seconds) {
  const sec = Math.round(Number(seconds || 0))
  if (!sec) return '-'
  if (sec < 60) return `${toFa(sec)} ثانیه`
  const mins = Math.round(sec / 60)
  if (mins < 60) return `${toFa(mins)} دقیقه`
  const hours = (mins / 60).toFixed(1)
  return `${Number(hours).toLocaleString('fa-IR')} ساعت`
}

async function apiGet(method, params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value)
  })
  const response = await fetch(`/api/method/mysite.api.${method}?${query.toString()}`, { credentials: 'same-origin' })
  const payload = await response.json()
  if (!response.ok || payload?.exc || payload?.exception || payload?.exc_type) throw new Error(payload?.message || 'خطا در دریافت داده')
  return payload.message || payload
}

async function apiPost(method, body = {}) {
  const response = await fetch(`/api/method/mysite.api.${method}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
    },
    body: JSON.stringify(body),
  })
  const payload = await response.json()
  if (!response.ok || payload?.exc || payload?.exception || payload?.exc_type) throw new Error(payload?.message || 'خطا در ثبت داده')
  return payload.message || payload
}

async function ensureRuntime() {
  runtime.loading = true
  try {
    const health = await apiGet('get_support_runtime_health', { include_phase2: 1 })
    runtime.ready = !!health.ready
    runtime.message = health.message || ''
    runtime.missing_doctypes = Array.isArray(health.missing_doctypes) ? health.missing_doctypes : []
    runtime.missing_tables = Array.isArray(health.missing_tables) ? health.missing_tables : []
  } catch (error) {
    runtime.ready = false
    runtime.message = error?.message || 'خطا در بررسی وضعیت زیرساخت پشتیبانی.'
    runtime.missing_doctypes = []
    runtime.missing_tables = []
  } finally {
    runtime.loading = false
  }
}

async function refreshAll() {
  await ensureRuntime()
  if (!runtime.ready) return
  await Promise.all([loadDashboard(), loadStatuses(), loadTickets(), loadShiftStatus(), loadOnlineAgents(), loadMacros()])
}

async function loadDashboard() {
  dashboardError.value = ''
  loadingDashboard.value = true
  try {
    const data = await apiGet('get_management_support_dashboard')
    dashboard.counts = data.counts || dashboard.counts
    dashboard.averages = data.averages || dashboard.averages
    dashboard.daily = Array.isArray(data.daily) ? data.daily : []
  } catch (error) {
    dashboardError.value = error?.message || 'خطا در دریافت KPI'
  } finally {
    loadingDashboard.value = false
  }
}

async function loadStatuses() {
  try {
    const response = await fetch('/api/resource/MS Support Ticket Status?fields=["name","label_agent"]&filters=[["enabled","=",1]]&limit_page_length=200', {
      credentials: 'same-origin',
    })
    if (!response.ok) {
      supportStatuses.value = []
      return
    }
    const payload = await response.json()
    supportStatuses.value = Array.isArray(payload?.data) ? payload.data : []
  } catch (error) {
    supportStatuses.value = []
  }
}

async function loadTickets() {
  ticketsError.value = ''
  ticketsLoading.value = true
  try {
    const data = await apiGet('get_management_support_tickets', {
      page: 1,
      page_size: 100,
      search: ticketFilters.search || undefined,
      customer: ticketFilters.customer || undefined,
    })
    tickets.value = Array.isArray(data.items) ? data.items : []
    if (!selectedTicketName.value && tickets.value.length) {
      await selectTicket(tickets.value[0].name)
    }
  } catch (error) {
    ticketsError.value = error?.message || 'خطا در دریافت تیکت‌ها'
  } finally {
    ticketsLoading.value = false
  }
}

async function selectTicket(name) {
  selectedTicketName.value = name
  ticketDetailError.value = ''
  ticketDetailLoading.value = true
  replyError.value = ''
  replySuccess.value = ''
  try {
    const data = await apiGet('get_management_support_ticket_detail', { name })
    ticketDetail.ticket = data.ticket || null
    ticketDetail.communications = Array.isArray(data.communications) ? data.communications : []
    ticketDetail.comments = Array.isArray(data.comments) ? data.comments : []
    ticketDetail.activities = Array.isArray(data.activities) ? data.activities : []
    ticketStatusForm.status = ticketDetail.ticket?.status || ''
    ticketStatusForm.resolution_details = ticketDetail.ticket?.resolution_details || ''
  } catch (error) {
    ticketDetailError.value = error?.message || 'خطا در دریافت جزئیات تیکت'
    ticketDetail.ticket = null
    ticketDetail.communications = []
  } finally {
    ticketDetailLoading.value = false
  }
}

async function sendReply() {
  replyError.value = ''
  replySuccess.value = ''
  if (!selectedTicketName.value) return
  replySending.value = true
  try {
    await apiPost('reply_management_support_ticket', {
      name: selectedTicketName.value,
      message: replyForm.message,
      notify: replyForm.notify,
    })
    replyForm.message = ''
    replySuccess.value = 'پاسخ با موفقیت ثبت شد.'
    await selectTicket(selectedTicketName.value)
    await Promise.all([loadDashboard(), loadTickets()])
  } catch (error) {
    replyError.value = error?.message || 'ارسال پاسخ انجام نشد.'
  } finally {
    replySending.value = false
  }
}

async function saveTicketStatus() {
  if (!selectedTicketName.value || !ticketStatusForm.status) return
  statusSaving.value = true
  try {
    await apiPost('update_management_support_ticket_status', {
      name: selectedTicketName.value,
      status: ticketStatusForm.status,
      resolution_details: ticketStatusForm.resolution_details,
    })
    await Promise.all([selectTicket(selectedTicketName.value), loadTickets(), loadDashboard()])
  } catch (error) {
    ticketDetailError.value = error?.message || 'ذخیره وضعیت انجام نشد.'
  } finally {
    statusSaving.value = false
  }
}

async function loadLiveChats() {
  liveChat.loading = true
  liveChat.error = ''
  try {
    const data = await apiGet('management_list_support_live_chats', {
      page: 1,
      page_size: 200,
      status: chatFilters.status || undefined,
      search: chatFilters.search || undefined,
    })
    liveChat.items = Array.isArray(data.items) ? data.items : []
    if (!liveChat.selected && liveChat.items.length) {
      liveChat.selected = liveChat.items[0]
    }
  } catch (error) {
    liveChat.error = error?.message || 'خطا در دریافت چت‌ها'
  } finally {
    liveChat.loading = false
  }
}

async function sendLiveChatReply() {
  if (!liveChat.selected || !String(liveChat.reply || '').trim()) return
  liveChat.replying = true
  try {
    await apiPost('management_reply_support_chat', {
      chat_link_name: liveChat.selected.name,
      channel_id: liveChat.selected.raven_channel,
      ticket_name: liveChat.selected.ticket,
      message: liveChat.reply,
    })
    liveChat.reply = ''
    await Promise.all([loadLiveChats(), loadTickets(), loadDashboard()])
    if (liveChat.selected?.ticket) {
      await selectTicket(liveChat.selected.ticket)
    }
  } catch (error) {
    liveChat.error = error?.message || 'ارسال پاسخ چت انجام نشد.'
  } finally {
    liveChat.replying = false
  }
}

async function loadShiftStatus() {
  shiftState.loading = true
  shiftState.error = ''
  try {
    shiftState.status = await apiGet('get_support_shift_status')
  } catch (error) {
    shiftState.error = error?.message || 'خطا در دریافت وضعیت شیفت'
  } finally {
    shiftState.loading = false
  }
}

async function loadOnlineAgents() {
  try {
    const data = await apiGet('get_support_online_agents')
    shiftState.onlineAgents = Array.isArray(data.items) ? data.items : []
  } catch (error) {
    shiftState.onlineAgents = []
  }
}

async function assignSelectedTicket() {
  if (!selectedTicketName.value) return
  shiftState.assigning = true
  try {
    await apiPost('set_support_shift_assignment', {
      ticket_name: selectedTicketName.value,
      agent_user: shiftState.assignAgent || undefined,
    })
    await Promise.all([selectTicket(selectedTicketName.value), loadTickets(), loadShiftStatus()])
  } catch (error) {
    shiftState.error = error?.message || 'تخصیص انجام نشد.'
  } finally {
    shiftState.assigning = false
  }
}

async function loadMacros() {
  macros.loading = true
  macros.error = ''
  try {
    const data = await apiGet('get_management_support_macros')
    macros.items = Array.isArray(data.items) ? data.items : []
    if (!macros.selected && macros.items.length) {
      macros.selected = macros.items[0]
    }
  } catch (error) {
    macros.error = error?.message || 'خطا در دریافت ماکروها'
  } finally {
    macros.loading = false
  }
}

async function applyMacroToSelectedTicket() {
  if (!selectedTicketName.value || !macros.selected) return
  macros.applying = true
  try {
    await apiPost('apply_management_support_macro', {
      name: selectedTicketName.value,
      macro: macros.selected.name,
      notify: true,
    })
    await Promise.all([selectTicket(selectedTicketName.value), loadTickets(), loadDashboard()])
  } catch (error) {
    macros.error = error?.message || 'اعمال ماکرو انجام نشد.'
  } finally {
    macros.applying = false
  }
}

async function loadQa() {
  qaLoading.value = true
  qaError.value = ''
  try {
    const data = await apiGet('get_management_feedback_queue', {
      search: qaFilters.search || undefined,
      only_unanswered: qaFilters.only_unanswered ? 1 : 0,
      limit: 200,
    })
    qaItems.value = Array.isArray(data.items) ? data.items : []
    qaItems.value.forEach((item) => {
      qaDraft[item.question_id] = item.answer || ''
    })
  } catch (error) {
    qaError.value = error?.message || 'خطا در دریافت پرسش‌ها'
  } finally {
    qaLoading.value = false
  }
}

async function submitQaAnswer(questionId) {
  const answer = String(qaDraft[questionId] || '').trim()
  if (!answer) {
    qaError.value = 'متن پاسخ خالی است.'
    return
  }
  qaError.value = ''
  try {
    await apiPost('reply_management_product_question', {
      question_id: questionId,
      answer,
      notify: true,
    })
    await loadQa()
  } catch (error) {
    qaError.value = error?.message || 'ذخیره پاسخ انجام نشد.'
  }
}

async function toggleQuestionVisibility(commentId, published) {
  qaError.value = ''
  try {
    await apiPost('set_feedback_visibility', {
      comment_id: commentId,
      published,
    })
    await loadQa()
  } catch (error) {
    qaError.value = error?.message || 'تغییر وضعیت نمایش انجام نشد.'
  }
}

watch(activeTab, async (tab) => {
  if (!runtime.ready) return
  if (tab === 'tickets' && !tickets.value.length) await loadTickets()
  if (tab === 'qa' && !qaItems.value.length) await loadQa()
  if (tab === 'live_chat' && !liveChat.items.length) await loadLiveChats()
  if (tab === 'shifts') await Promise.all([loadShiftStatus(), loadOnlineAgents()])
  if (tab === 'macros' && !macros.items.length) await loadMacros()
  if (tab === 'kpis') await loadDashboard()
})

onMounted(async () => {
  await ensureRuntime()
  if (!runtime.ready) return
  await Promise.all([loadDashboard(), loadStatuses(), loadTickets(), loadShiftStatus(), loadOnlineAgents(), loadMacros()])
})
</script>

<style scoped>
.support-page {
  padding: var(--space-5);
  padding-bottom: 80px;
  display: grid;
  gap: var(--space-4);
  color: var(--text-main);
  overflow-x: hidden;
  max-width: 100vw;
  box-sizing: border-box;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.eyebrow {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-dim);
}
h1 {
  margin: 0;
  font-size: var(--text-2xl);
}
.tabs {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.tab {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-pill);
  padding: 8px 14px;
  cursor: pointer;
}
.tab.active {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  border-color: transparent;
}
.panel {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-panel-bg);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}
.kpi {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  background: var(--admin-input-bg);
}
.kpi p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}
.kpi strong {
  margin-top: 6px;
  display: block;
  font-size: var(--text-lg);
}
.state {
  border-radius: var(--radius-md);
  padding: var(--space-3);
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
}
.state.error {
  border-color: #c44545;
  color: #c44545;
}
.state.success {
  border-color: #2f855a;
  color: #2f855a;
}
.split {
  grid-template-columns: 340px 1fr;
  align-items: start;
}
.left,
.right {
  display: grid;
  gap: var(--space-3);
}
.toolbar {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.toolbar input,
.toolbar select,
.field textarea,
.field select,
.field input {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  color: var(--text-main);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
}
.ticket-list {
  display: grid;
  gap: var(--space-2);
}
.ticket-item {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  text-align: right;
  display: grid;
  gap: var(--space-1);
  cursor: pointer;
}
.ticket-item.active {
  border-color: var(--admin-tab-active-start);
}
.ticket-item small,
.muted {
  color: var(--admin-text-soft);
}
.desc {
  margin: 0;
  line-height: 1.75;
}
.field {
  display: grid;
  gap: var(--space-2);
}
.actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  align-items: center;
}
.inline {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}
button.ghost,
button.gold {
  border-radius: var(--radius-md);
  border: 1px solid var(--admin-border);
  padding: 8px 12px;
  font-family: inherit;
  cursor: pointer;
}
button.ghost {
  background: var(--admin-input-bg);
  color: var(--text-main);
}
button.gold {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  border-color: transparent;
  color: #fff;
}
.conversation {
  display: grid;
  gap: var(--space-2);
  max-height: 320px;
  overflow: auto;
}
.bubble {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  background: var(--admin-input-bg);
}
.bubble.sent {
  border-color: color-mix(in srgb, var(--admin-tab-active-start) 50%, var(--admin-border));
}
.bubble p {
  margin: 6px 0 0;
  line-height: 1.8;
}
.table-wrap {
  overflow: auto;
}
.table-wrap table {
  width: 100%;
  border-collapse: collapse;
}
.table-wrap th,
.table-wrap td {
  border-bottom: 1px solid var(--admin-border);
  padding: var(--space-2);
  text-align: right;
}
.qa-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--space-3);
}
.qa-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  background: var(--admin-input-bg);
}
.qa-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.qa-card textarea {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-panel-bg);
  color: var(--text-main);
  padding: var(--space-2);
  font-family: inherit;
}
.links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}
.links a {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  text-decoration: none;
  color: var(--text-main);
  background: var(--admin-input-bg);
}
code {
  direction: ltr;
  unicode-bidi: bidi-override;
}
@media (max-width: 1080px) {
  .split {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .support-page {
  }
  .head {
    flex-direction: column;
    gap: var(--space-2);
  }
  .head-actions {
    width: 100%;
  }
  .head-actions .btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
