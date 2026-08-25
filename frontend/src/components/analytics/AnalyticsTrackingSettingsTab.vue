<template>
  <section class="settings-tab">

    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری تنظیمات...
    </div>

    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🔧</span>
          <h3>کلیدهای فعال‌سازی رویداد</h3>
          <span class="badge-count">{{ local.toggles.length }}</span>
        </div>
        <div class="toggle-list">
          <label
            v-for="row in local.toggles"
            :key="row.event_key"
            class="toggle-row"
            :class="{ active: row.is_active }"
          >
            <div class="toggle-switch" @click.prevent="row.is_active = row.is_active ? 0 : 1">
              <div class="switch-track" :class="{ on: row.is_active }">
                <div class="switch-thumb"></div>
              </div>
            </div>
            <div class="toggle-info">
              <span class="toggle-key">{{ row.event_key }}</span>
              <small class="toggle-desc">{{ row.description }}</small>
            </div>
            <span class="toggle-status" :class="row.is_active ? 'on' : 'off'">
              {{ row.is_active ? 'فعال' : 'غیرفعال' }}
            </span>
          </label>
          <div v-if="!local.toggles.length" class="empty-cell">رویدادی تعریف نشده.</div>
        </div>
      </article>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🎯</span>
          <h3>Goals قابل تعریف</h3>
          <span class="badge-count">{{ local.goals.length }}</span>
          <button class="mini-action" @click="addGoal">+ هدف جدید</button>
        </div>
        <div class="card-list">
          <div v-for="(row, idx) in local.goals" :key="row.name || idx" class="setting-card">
            <div class="setting-card-header">
              <span class="card-num">{{ idx + 1 }}</span>
              <span class="card-title">{{ row.title || 'بدون عنوان' }}</span>
              <div class="card-chips">
                <span class="mini-chip" :class="row.is_active ? 'green' : 'gray'">
                  {{ row.is_active ? 'فعال' : 'غیرفعال' }}
                </span>
                <span class="mini-chip blue" v-if="row.is_default">پیش‌فرض</span>
              </div>
            </div>
            <div class="setting-fields">
              <label class="field">
                <span>عنوان Goal</span>
                <input v-model="row.title" placeholder="مثلاً خرید کامل" />
              </label>
              <div class="field-row">
                <label class="field checkbox-field">
                  <input type="checkbox" v-model="row.is_active" :true-value="1" :false-value="0" />
                  <span>فعال</span>
                </label>
                <label class="field checkbox-field">
                  <input type="checkbox" v-model="row.is_default" :true-value="1" :false-value="0" @change="ensureSingleDefault(idx)" />
                  <span>پیش‌فرض</span>
                </label>
              </div>
              <label class="field full">
                <span>مراحل (JSON)</span>
                <textarea v-model="row.steps_json" rows="2" placeholder='["visit","add_to_cart","checkout","order"]'></textarea>
              </label>
            </div>
          </div>
          <div v-if="!local.goals.length" class="empty-cell">Goal تعریف نشده است.</div>
        </div>
      </article>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🧩</span>
          <h3>Saved Segments</h3>
          <span class="badge-count">{{ local.segments.length }}</span>
          <button class="mini-action" @click="addSegment">+ سگمنت جدید</button>
        </div>
        <div class="card-list">
          <div v-for="(row, idx) in local.segments" :key="row.key || idx" class="setting-card">
            <div class="setting-card-header">
              <span class="card-num">{{ idx + 1 }}</span>
              <span class="card-title">{{ row.title || row.key || 'Segment' }}</span>
              <span class="mini-chip" :class="row.is_active ? 'green' : 'gray'">
                {{ row.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
            </div>
            <div class="setting-fields segment-fields">
              <label class="field">
                <span>عنوان</span>
                <input v-model="row.title" placeholder="مثلاً موبایل تهران" />
              </label>
              <label class="field">
                <span>کلید (اختیاری)</span>
                <input v-model="row.key" placeholder="mobile-tehran" class="mono" :disabled="row.key === '__all__'" />
              </label>
              <label class="field checkbox-field">
                <input type="checkbox" v-model="row.is_active" :true-value="1" :false-value="0" />
                <span>فعال</span>
              </label>
              <label class="field full">
                <span>منبع‌ها (با کاما)</span>
                <input :value="joinList(row.source_channels)" @input="onListInput(row, 'source_channels', $event)" placeholder="google,direct,instagram" />
              </label>
              <label class="field full">
                <span>دستگاه‌ها (با کاما)</span>
                <input :value="joinList(row.device_types)" @input="onListInput(row, 'device_types', $event)" placeholder="mobile,desktop,tablet" />
              </label>
              <label class="field full">
                <span>شهرها (با کاما)</span>
                <input :value="joinList(row.cities)" @input="onListInput(row, 'cities', $event)" placeholder="tehran,shiraz" />
              </label>
              <label class="field full">
                <span>گروه صفحه (با کاما)</span>
                <input :value="joinList(row.page_groups)" @input="onListInput(row, 'page_groups', $event)" placeholder="sofas,blog,catalog" />
              </label>
              <label class="field full">
                <span>کمپین (utm_campaign) با کاما</span>
                <input :value="joinList(row.campaigns)" @input="onListInput(row, 'campaigns', $event)" placeholder="sale1405,newyear" />
              </label>
              <label class="field full">
                <span>یادداشت</span>
                <textarea v-model="row.note" rows="2" placeholder="توضیح اختیاری"></textarea>
              </label>
            </div>
          </div>
          <div v-if="!local.segments.length" class="empty-cell">Segment تعریف نشده است.</div>
        </div>
      </article>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🔔</span>
          <h3>قوانین هشدار</h3>
          <span class="badge-count">{{ local.alerts.length }}</span>
        </div>
        <div class="card-list">
          <div
            v-for="(row, idx) in local.alerts"
            :key="row.name || idx"
            class="setting-card"
          >
            <div class="setting-card-header">
              <span class="card-num">{{ idx + 1 }}</span>
              <span class="card-title">{{ row.metric_key || 'شاخص نامشخص' }}</span>
              <span class="mini-chip" :class="row.is_active ? 'green' : 'gray'">
                {{ row.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
            </div>
            <div class="setting-fields">
              <label class="field">
                <span>کلید شاخص</span>
                <input v-model="row.metric_key" placeholder="مثلاً conversion_rate" />
              </label>
              <label class="field">
                <span>عملگر</span>
                <select v-model="row.operator">
                  <option value="<">کمتر از (&lt;)</option>
                  <option value=">">بیشتر از (&gt;)</option>
                  <option value="<=">کمتر یا مساوی</option>
                  <option value=">=">بیشتر یا مساوی</option>
                </select>
              </label>
              <label class="field">
                <span>آستانه</span>
                <input type="number" v-model.number="row.threshold_value" placeholder="عدد" />
              </label>
              <label class="field">
                <span>بازه (روز)</span>
                <input type="number" v-model.number="row.window_days" placeholder="۷" />
              </label>
              <label class="field checkbox-field">
                <input type="checkbox" v-model="row.is_active" :true-value="1" :false-value="0" />
                <span>فعال</span>
              </label>
              <label class="field full">
                <span>گیرندگان (ایمیل با ویرگول)</span>
                <textarea v-model="row.recipients" rows="2" placeholder="admin@example.com, user@example.com"></textarea>
              </label>
            </div>
          </div>
          <div v-if="!local.alerts.length" class="empty-cell">قانون هشداری تعریف نشده.</div>
        </div>
      </article>

      <article class="panel glass-card">
        <div class="panel-header">
          <span class="panel-icon">🛡</span>
          <h3>استثناهای آی‌پی</h3>
          <span class="badge-count">{{ local.ip_exclusions.length }}</span>
        </div>
        <div class="card-list">
          <div
            v-for="(row, idx) in local.ip_exclusions"
            :key="row.name || idx"
            class="setting-card"
          >
            <div class="setting-card-header">
              <span class="card-num">{{ idx + 1 }}</span>
              <span class="card-title mono">{{ row.ip_or_cidr || 'آی‌پی وارد نشده' }}</span>
              <span class="mini-chip" :class="row.is_active ? 'green' : 'gray'">
                {{ row.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
            </div>
            <div class="setting-fields">
              <label class="field">
                <span>آی‌پی یا CIDR</span>
                <input v-model="row.ip_or_cidr" placeholder="192.168.1.0/24" class="mono" />
              </label>
              <label class="field checkbox-field">
                <input type="checkbox" v-model="row.is_active" :true-value="1" :false-value="0" />
                <span>فعال</span>
              </label>
              <label class="field full">
                <span>یادداشت</span>
                <textarea v-model="row.note" rows="2" placeholder="توضیح اختیاری..."></textarea>
              </label>
            </div>
          </div>
          <div v-if="!local.ip_exclusions.length" class="empty-cell">استثنایی تعریف نشده.</div>
        </div>
      </article>

      <div class="actions">
        <button class="ghost-action-btn" @click="$emit('refresh')">↻ بازخوانی</button>
        <button class="save-btn" :disabled="saving" @click="save">
          <span v-if="saving" class="spinning">↻</span>
          {{ saving ? 'در حال ذخیره...' : '💾 ذخیره تنظیمات' }}
        </button>
      </div>

    </template>
  </section>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  data:    { type: Object,  default: () => ({ toggles: [], goals: [], funnels: [], segments: [], alerts: [], ip_exclusions: [] }) },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: '' },
  saving:  { type: Boolean, default: false },
})

const emit = defineEmits(['save', 'refresh'])

const local = reactive({ toggles: [], goals: [], segments: [], alerts: [], ip_exclusions: [] })

const clone = (value) => JSON.parse(JSON.stringify(value || []))

const normalizeGoal = (row) => {
  const copy = { ...(row || {}) }
  if (!copy.steps_json) {
    const steps = Array.isArray(copy.steps) ? copy.steps : ['visit', 'add_to_cart', 'checkout', 'order']
    copy.steps_json = JSON.stringify(steps)
  }
  copy.is_active = copy.is_active ? 1 : 0
  copy.is_default = copy.is_default ? 1 : 0
  return copy
}

const normalizeSegment = (row) => ({
  ...(row || {}),
  key: row?.key || '',
  title: row?.title || '',
  is_active: row?.is_active ? 1 : 0,
  source_channels: Array.isArray(row?.source_channels) ? row.source_channels : [],
  device_types: Array.isArray(row?.device_types) ? row.device_types : [],
  cities: Array.isArray(row?.cities) ? row.cities : [],
  page_groups: Array.isArray(row?.page_groups) ? row.page_groups : [],
  campaigns: Array.isArray(row?.campaigns) ? row.campaigns : [],
  note: row?.note || '',
})

watch(
  () => props.data,
  (value) => {
    local.toggles = clone(value?.toggles)
    const rawGoals = value?.goals?.length ? value.goals : (value?.funnels || [])
    local.goals = clone(rawGoals).map((row) => normalizeGoal(row))
    local.segments = clone(value?.segments).map((row) => normalizeSegment(row))
    local.alerts = clone(value?.alerts)
    local.ip_exclusions = clone(value?.ip_exclusions)
  },
  { deep: true, immediate: true }
)

function ensureSingleDefault(targetIndex) {
  local.goals.forEach((row, idx) => {
    if (idx !== targetIndex) row.is_default = 0
  })
}

function addGoal() {
  local.goals.push(normalizeGoal({
    title: 'Goal جدید',
    is_active: 1,
    is_default: local.goals.length ? 0 : 1,
    steps_json: '["visit","add_to_cart","checkout","order"]',
  }))
}

function addSegment() {
  local.segments.push(normalizeSegment({
    key: '',
    title: 'Segment جدید',
    is_active: 1,
    source_channels: [],
    device_types: [],
    cities: [],
    page_groups: [],
    campaigns: [],
    note: '',
  }))
}

function splitList(value) {
  return String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function joinList(listValue) {
  return (Array.isArray(listValue) ? listValue : []).join(', ')
}

function onListInput(row, key, event) {
  row[key] = splitList(event?.target?.value)
}

function save() {
  const goals = local.goals.map((row) => normalizeGoal(row))
  const segments = local.segments.map((row) => normalizeSegment(row))
  emit('save', {
    toggles: local.toggles,
    goals,
    funnels: goals,
    segments,
    alerts: local.alerts,
    ip_exclusions: local.ip_exclusions,
  })
}
</script>

<style scoped>
.settings-tab { display: grid; gap: 12px; }

.state-card {
  display: flex; align-items: center; gap: 10px;
  padding: 20px; border-radius: 14px;
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  font-size: 14px; color: var(--admin-text-soft);
}
.state-card.error { color: #f87171; }
.state-icon { font-size: 18px; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.7s linear infinite; }

.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}
.panel { overflow: hidden; }

.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
  flex-wrap: wrap;
}
.panel-icon { font-size: 15px; }
.panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; flex: 1; }
.badge-count {
  font-size: 11px; font-weight: 700;
  background: var(--admin-chip-bg); border: 1px solid var(--admin-border);
  border-radius: 999px; padding: 2px 8px; color: var(--admin-text-soft);
}
.mini-action {
  border: 1px solid var(--admin-border);
  border-radius: 999px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  padding: 4px 10px;
  font-size: 11px;
  cursor: pointer;
}

.toggle-list { padding: 8px 12px; display: grid; gap: 4px; }
.toggle-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 12px;
  border: 1px solid transparent;
  cursor: pointer; transition: background 0.15s, border-color 0.15s;
}
.toggle-row:hover { background: rgba(255,255,255,0.04); }
.toggle-row.active { border-color: rgba(129,140,248,0.25); background: rgba(129,140,248,0.05); }

.switch-track {
  width: 36px; height: 20px; border-radius: 99px;
  background: var(--admin-border);
  position: relative; transition: background 0.2s; cursor: pointer; flex-shrink: 0;
}
.switch-track.on { background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end)); }
.switch-thumb {
  position: absolute; top: 3px; right: 3px;
  width: 14px; height: 14px; border-radius: 50%; background: #fff;
  transition: transform 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.switch-track.on .switch-thumb { transform: translateX(-16px); }

.toggle-info { flex: 1; display: grid; gap: 2px; }
.toggle-key  { font-size: 13px; font-weight: 500; font-family: monospace; }
.toggle-desc { font-size: 11px; color: var(--admin-text-soft); }
.toggle-status { font-size: 11px; font-weight: 600; white-space: nowrap; }
.toggle-status.on  { color: #6ee7b7; }
.toggle-status.off { color: var(--admin-text-soft); }

.card-list { padding: 10px 12px; display: grid; gap: 8px; }
.setting-card {
  border: 1px solid var(--admin-border);
  border-radius: 14px; overflow: hidden;
  background: rgba(255,255,255,0.02);
}
.setting-card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; border-bottom: 1px solid var(--admin-border);
  background: rgba(255,255,255,0.03);
}
.card-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--admin-border); color: var(--admin-text-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.card-title { font-size: 13px; font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-chips { display: flex; gap: 5px; flex-shrink: 0; }

.mini-chip {
  padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 600;
}
.mini-chip.green { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.mini-chip.gray  { background: rgba(156,163,175,0.15); color: #9ca3af; }
.mini-chip.blue  { background: rgba(147,197,253,0.15); color: #93c5fd; }

.setting-fields {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  padding: 10px 12px;
  align-items: end;
}
.segment-fields { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.field { display: grid; gap: 4px; }
.field span { font-size: 11px; color: var(--admin-text-soft); }
.field.full { grid-column: 1 / -1; }
.field-row { display: flex; align-items: end; gap: 10px; }
.checkbox-field { flex-direction: row; align-items: center; gap: 6px; padding: 8px 0; }
.checkbox-field span { font-size: 12px; color: var(--text-main); }

.field input[type="text"],
.field input[type="number"],
.field input:not([type="checkbox"]),
.field select,
.field textarea {
  border: 1px solid var(--admin-border);
  border-radius: 10px; padding: 8px 10px;
  background: var(--admin-input-bg); color: var(--text-main);
  font-family: inherit; font-size: 12px;
  transition: border-color 0.15s;
  width: 100%;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: var(--admin-tab-active-start, #818cf8);
}
.field textarea { resize: vertical; min-height: 60px; }
.mono { font-family: monospace; }

.empty-cell { padding: 14px; text-align: center; font-size: 12px; color: var(--admin-text-soft); }

.actions { display: flex; justify-content: flex-end; gap: 8px; }
.ghost-action-btn {
  border: 1px solid var(--admin-border); border-radius: 10px;
  padding: 9px 16px; font-family: inherit; font-size: 13px;
  cursor: pointer; color: var(--text-main); background: var(--admin-input-bg);
  transition: border-color 0.15s;
}
.ghost-action-btn:hover { border-color: var(--admin-tab-active-start, #818cf8); }
.save-btn {
  display: flex; align-items: center; gap: 6px;
  border: none; border-radius: 10px;
  padding: 9px 20px; font-family: inherit; font-size: 13px; font-weight: 600;
  cursor: pointer; color: #fff;
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  transition: opacity 0.15s;
}
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 980px) {
  .setting-fields { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .segment-fields { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 580px) {
  .setting-fields { grid-template-columns: 1fr; }
  .segment-fields { grid-template-columns: 1fr; }
  .toggle-row { flex-wrap: wrap; }
}
</style>
