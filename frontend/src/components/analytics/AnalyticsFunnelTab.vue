<template>
  <section class="funnel-tab">

    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری فانل تبدیل...
    </div>

    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">

      <div class="steps-row">
        <article
          v-for="(step, idx) in data.steps || []"
          :key="step.step"
          class="step-card glass-card"
        >
          <div class="step-num">{{ idx + 1 }}</div>
          <p class="step-name">{{ labels[step.step] || step.step }}</p>
          <div class="step-count">{{ fa(step.count) }}</div>

          <div class="drop-row" v-if="step.drop_percent > 0">
            <div class="drop-bar-track">
              <div
                class="drop-bar-fill"
                :style="`width:${Math.min(step.drop_percent, 100)}%`"
                :class="dropClass(step.drop_percent)"
              ></div>
            </div>
            <span class="drop-label" :class="dropClass(step.drop_percent)">
              {{ fa2(step.drop_percent) }}٪ ریزش
            </span>
          </div>
          <div class="drop-row no-drop" v-else>
            <span>نقطه شروع</span>
          </div>

          <button class="diagnose-btn" @click="$emit('diagnose', step.step)">
            🔍 چرا ریزش؟
          </button>
        </article>
      </div>

      <div class="kpi-row">
        <article class="kpi-card glass-card">
          <div class="kpi-top"><span class="kpi-icon">👁</span><span class="kpi-label">بازدید → سبد</span></div>
          <div class="kpi-val">{{ fa2(data.conversion_rate?.view_to_cart_percent) }}٪</div>
        </article>
        <article class="kpi-card glass-card">
          <div class="kpi-top"><span class="kpi-icon">🛒</span><span class="kpi-label">سبد → سفارش</span></div>
          <div class="kpi-val">{{ fa2(data.conversion_rate?.cart_to_order_percent) }}٪</div>
        </article>
        <article class="kpi-card glass-card highlight">
          <div class="kpi-top"><span class="kpi-icon">⚡</span><span class="kpi-label">بازدید → سفارش</span></div>
          <div class="kpi-val">{{ fa2(data.conversion_rate?.view_to_order_percent) }}٪</div>
        </article>
      </div>

      <div class="panel-row">
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📉</span>
            <h3>بیشترین ریزش محصول</h3>
          </div>
          <div class="state-inline" v-if="!(data.top_drop_products || []).length">داده‌ای ثبت نشده.</div>
          <div class="table-wrap" v-else>
            <table>
              <thead><tr><th>مدل</th><th>سبد</th><th>سفارش</th><th>ریزش٪</th></tr></thead>
              <tbody>
                <tr v-for="row in data.top_drop_products" :key="row.model_name">
                  <td class="model-name">{{ row.model_name }}</td>
                  <td class="num">{{ fa(row.add_to_cart) }}</td>
                  <td class="num">{{ fa(row.order_submit) }}</td>
                  <td class="num">
                    <span class="badge" :class="dropClass(row.drop_percent)">{{ fa2(row.drop_percent) }}٪</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">📱</span>
            <h3>تفکیک دستگاه</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>دستگاه</th><th>بازدید</th><th>سبد</th><th>پرداخت</th><th>سفارش</th></tr></thead>
              <tbody>
                <tr v-for="row in data.by_device || []" :key="row.device_type">
                  <td><span class="device-icon">{{ deviceIcon(row.device_type) }}</span>{{ deviceLabel(row.device_type) }}</td>
                  <td class="num">{{ fa(row.product_view) }}</td>
                  <td class="num">{{ fa(row.add_to_cart) }}</td>
                  <td class="num">{{ fa(row.checkout_start) }}</td>
                  <td class="num">{{ fa(row.order_submit) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article class="diagnosis glass-card" v-if="diagnosisLoading">
        <span class="state-icon spinning">↻</span>
        در حال تحلیل علت ریزش...
      </article>

      <article class="diagnosis glass-card" v-else-if="diagnosis?.reasons?.length">
        <div class="panel-header">
          <span class="panel-icon">🧠</span>
          <h3>دلایل احتمالی ریزش</h3>
        </div>
        <ul class="reason-list">
          <li v-for="(r, idx) in diagnosis.reasons" :key="idx">
            <span class="reason-dot"></span>
            {{ r.message }}
          </li>
        </ul>
      </article>

    </template>
  </section>
</template>

<script setup>
defineProps({
  data:             { type: Object,  default: null  },
  loading:          { type: Boolean, default: false  },
  error:            { type: String,  default: ''     },
  diagnosis:        { type: Object,  default: null   },
  diagnosisLoading: { type: Boolean, default: false  },
})
defineEmits(['diagnose'])

const labels = {
  product_view:   'بازدید محصول',
  add_to_cart:    'افزودن به سبد',
  checkout_start: 'شروع پرداخت',
  order_submit:   'ثبت نهایی سفارش',
}
const fa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })
const deviceMap   = { mobile: 'موبایل', desktop: 'دسکتاپ', tablet: 'تبلت', other: 'سایر' }
const deviceIcons = { mobile: '📱', desktop: '🖥', tablet: '📲', other: '💻' }
const deviceLabel = (v) => deviceMap[v]   || v || '-'
const deviceIcon  = (v) => deviceIcons[v] || '💻'
const dropClass   = (v) => v <= 20 ? 'green' : v <= 50 ? 'yellow' : 'red'
</script>

<style scoped>
.funnel-tab { display: grid; gap: 12px; }

.state-card {
  display: flex; align-items: center; gap: 10px;
  padding: 20px; border-radius: 14px;
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  font-size: 14px; color: var(--admin-text-soft);
}
.state-card.error { color: #f87171; }
.state-inline { padding: 16px; font-size: 13px; color: var(--admin-text-soft); }
.state-icon { font-size: 18px; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.7s linear infinite; }

.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}

/* Steps */
.steps-row {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px;
}
.step-card { padding: 16px; display: flex; flex-direction: column; gap: 6px; transition: transform 0.15s; }
.step-card:hover { transform: translateY(-2px); }
.step-num {
  width: 22px; height: 22px; border-radius: 50%;
  background: linear-gradient(135deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; margin-bottom: 2px;
}
.step-name  { margin: 0; font-size: 12px; color: var(--admin-text-soft); }
.step-count { font-size: 1.4rem; font-weight: 700; line-height: 1.1; }

.drop-row { display: flex; flex-direction: column; gap: 4px; margin-top: 4px; }
.drop-row.no-drop span { font-size: 11px; color: var(--admin-text-soft); }
.drop-bar-track { height: 5px; background: var(--admin-border); border-radius: 99px; overflow: hidden; }
.drop-bar-fill  { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.drop-bar-fill.green  { background: #6ee7b7; }
.drop-bar-fill.yellow { background: #fcd34d; }
.drop-bar-fill.red    { background: #f87171; }
.drop-label { font-size: 11px; font-weight: 600; }
.drop-label.green  { color: #6ee7b7; }
.drop-label.yellow { color: #fcd34d; }
.drop-label.red    { color: #f87171; }

.diagnose-btn {
  margin-top: 6px; border: 1px solid var(--admin-border);
  border-radius: 9px; padding: 6px 10px; background: transparent;
  color: var(--text-main); font-family: inherit; font-size: 12px;
  cursor: pointer; transition: all 0.15s; text-align: center;
}
.diagnose-btn:hover {
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff; border-color: transparent;
}

/* KPI row */
.kpi-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.kpi-card { padding: 14px; transition: transform 0.15s; }
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card.highlight {
  border-color: var(--admin-tab-active-start, #6366f1);
  box-shadow: 0 0 0 1px var(--admin-tab-active-start, #6366f1);
}
.kpi-top   { display: flex; align-items: center; gap: 7px; margin-bottom: 8px; }
.kpi-icon  { font-size: 16px; }
.kpi-label { font-size: 12px; color: var(--admin-text-soft); }
.kpi-val   { font-size: 1.5rem; font-weight: 700; }

/* Panel row */
.panel-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.panel { overflow: hidden; }
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
}
.panel-icon { font-size: 15px; }
.panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right; padding: 8px 12px;
  font-size: 12px; border-bottom: 1px solid var(--admin-border); white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
.num { text-align: left; font-variant-numeric: tabular-nums; }
.model-name { max-width: 180px; overflow: hidden; text-overflow: ellipsis; }
.device-icon { margin-left: 5px; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.badge.green  { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.badge.yellow { background: rgba(252,211,77,0.15);  color: #fcd34d; }
.badge.red    { background: rgba(248,113,113,0.15); color: #f87171; }

/* Diagnosis */
.diagnosis { overflow: hidden; padding: 0; }
.diagnosis > .panel-header { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid var(--admin-border); }
.diagnosis > .panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; }
.diagnosis.state-card { padding: 16px; display: flex; align-items: center; gap: 10px; }

.reason-list { list-style: none; margin: 0; padding: 10px 14px; display: grid; gap: 8px; }
.reason-list li { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; line-height: 1.6; }
.reason-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--admin-tab-active-start, #6366f1);
  flex-shrink: 0; margin-top: 6px;
}

@media (max-width: 1100px) {
  .steps-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .panel-row { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .steps-row { grid-template-columns: 1fr; }
  .kpi-row   { grid-template-columns: 1fr; }
}
</style>