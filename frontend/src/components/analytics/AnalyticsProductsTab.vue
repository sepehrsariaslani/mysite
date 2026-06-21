<template>
  <section class="products-tab">

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <span class="state-icon spinning">↻</span>
      در حال بارگذاری گزارش محصولات...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-card error">
      <span class="state-icon">⚠️</span>
      {{ error }}
    </div>

    <template v-else-if="data">

      <!-- ── Main table ── -->
      <article class="panel glass-card">
        <div class="panel-header">
          <div class="header-right">
            <span class="panel-icon">📦</span>
            <h3>جدول محصولات</h3>
          </div>
          <span class="row-count">{{ fa(data.total) }} ردیف</span>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>مدل</th>
                <th>دسته</th>
                <th>بازدید</th>
                <th>سبد</th>
                <th>خرید</th>
                <th>نرخ تبدیل</th>
                <th>درآمد</th>
                <th>زمان تصمیم</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.items || []" :key="`${row.model_name}-${row.item_group}`">
                <td class="model-name">{{ row.model_name }}</td>
                <td>
                  <span class="category-chip">{{ row.item_group || '-' }}</span>
                </td>
                <td class="num">{{ fa(row.views) }}</td>
                <td class="num">{{ fa(row.add_to_cart) }}</td>
                <td class="num">{{ fa(row.purchases) }}</td>
                <td class="num">
                  <span class="badge" :class="convClass(row.conversion_rate)">
                    {{ fa2(row.conversion_rate) }}٪
                  </span>
                </td>
                <td class="num money">{{ money(row.revenue) }}</td>
                <td class="num">
                  <span class="time-chip" :class="timeClass(row.avg_decision_minutes)">
                    {{ fa2(row.avg_decision_minutes) }} دقیقه
                  </span>
                </td>
              </tr>
              <tr v-if="!(data.items || []).length">
                <td colspan="8" class="empty-cell">محصولی یافت نشد.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- ── Two insight panels ── -->
      <div class="insights-grid">

        <!-- Top selling -->
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">🏆</span>
            <h3>پرفروش‌ترین‌ها</h3>
          </div>
          <div class="insight-list">
            <div
              v-for="(row, idx) in data.charts?.top_selling || []"
              :key="`s-${row.model_name}`"
              class="insight-row"
            >
              <div class="insight-rank" :class="`rank-${idx + 1}`">{{ idx + 1 }}</div>
              <div class="insight-info">
                <span class="insight-name">{{ row.model_name }}</span>
                <div class="insight-bar-wrap">
                  <div class="insight-bar-track">
                    <div
                      class="insight-bar-fill green"
                      :style="`width:${topSellingPercent(row.purchases)}%`"
                    ></div>
                  </div>
                  <span class="insight-val">{{ fa(row.purchases) }} خرید</span>
                </div>
              </div>
            </div>
            <div v-if="!(data.charts?.top_selling || []).length" class="empty-cell">داده‌ای ثبت نشده.</div>
          </div>
        </article>

        <!-- High views, low purchases -->
        <article class="panel glass-card">
          <div class="panel-header">
            <span class="panel-icon">⚠️</span>
            <h3>پربازدید با خرید پایین</h3>
          </div>
          <div class="insight-list">
            <div
              v-for="(row, idx) in data.charts?.top_viewed_low_buy || []"
              :key="`v-${row.model_name}`"
              class="insight-row"
            >
              <div class="insight-rank warn">{{ idx + 1 }}</div>
              <div class="insight-info">
                <span class="insight-name">{{ row.model_name }}</span>
                <div class="insight-meta">
                  <span class="meta-pill views">{{ fa(row.views) }} بازدید</span>
                  <span class="meta-pill buys">{{ fa(row.purchases) }} خرید</span>
                  <span class="meta-pill rate" v-if="row.views">
                    {{ fa2((row.purchases / row.views) * 100) }}٪
                  </span>
                </div>
              </div>
            </div>
            <div v-if="!(data.charts?.top_viewed_low_buy || []).length" class="empty-cell">داده‌ای ثبت نشده.</div>
          </div>
        </article>

      </div>
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data:    { type: Object,  default: null  },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: ''    },
})

const fa    = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2   = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })
const money = (v) => `${Number(v || 0).toLocaleString('fa-IR')} تومان`

// Badge classes
const convClass = (v) => {
  const n = Number(v || 0)
  if (n >= 10) return 'green'
  if (n >= 4)  return 'yellow'
  return 'red'
}
const timeClass = (v) => {
  const n = Number(v || 0)
  if (n <= 10) return 'fast'
  if (n <= 30) return 'mid'
  return 'slow'
}

// Bar percent for top selling
const topSellingMax = computed(() => {
  const rows = props.data?.charts?.top_selling || []
  return Math.max(1, ...rows.map((r) => Number(r.purchases || 0)))
})
const topSellingPercent = (v) => (Number(v || 0) / topSellingMax.value) * 100
</script>

<style scoped>
.products-tab { display: grid; gap: 12px; }

/* State */
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

/* Glass */
.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}
.panel { overflow: hidden; }

/* Panel header */
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
}
.header-right { display: flex; align-items: center; gap: 8px; }
.panel-icon { font-size: 15px; }
.panel-header h3 { margin: 0; font-size: 0.9rem; font-weight: 600; }
.row-count {
  font-size: 12px; color: var(--admin-text-soft);
  border: 1px solid var(--admin-border); border-radius: 999px;
  padding: 2px 10px;
}

/* Table */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td {
  text-align: right; padding: 9px 12px;
  font-size: 12px; border-bottom: 1px solid var(--admin-border); white-space: nowrap;
}
th { color: var(--admin-text-soft); font-weight: 600; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.03); }
.num { text-align: left; font-variant-numeric: tabular-nums; }
.model-name { max-width: 200px; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.money { color: #fcd34d; }
.empty-cell { text-align: center; color: var(--admin-text-soft); font-size: 12px; padding: 16px; }

/* Category chip */
.category-chip {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  background: var(--admin-chip-bg); border: 1px solid var(--admin-border);
  font-size: 11px; color: var(--admin-text-soft);
}

/* Conversion badges */
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.badge.green  { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.badge.yellow { background: rgba(252,211,77,0.15);  color: #fcd34d; }
.badge.red    { background: rgba(248,113,113,0.15); color: #f87171; }

/* Time chip */
.time-chip { font-size: 12px; }
.time-chip.fast { color: #6ee7b7; }
.time-chip.mid  { color: #fcd34d; }
.time-chip.slow { color: #f87171; }

/* Insights grid */
.insights-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Insight list */
.insight-list { padding: 10px 14px; display: grid; gap: 10px; }
.insight-row  { display: flex; align-items: flex-start; gap: 10px; }

/* Rank circle */
.insight-rank {
  width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff;
  background: linear-gradient(135deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
}
.insight-rank.rank-1 { background: linear-gradient(135deg, #fcd34d, #f59e0b); }
.insight-rank.rank-2 { background: linear-gradient(135deg, #d1d5db, #9ca3af); }
.insight-rank.rank-3 { background: linear-gradient(135deg, #c4a06a, #a07848); }
.insight-rank.warn   { background: rgba(248,113,113,0.2); color: #f87171; }

.insight-info { flex: 1; display: grid; gap: 5px; min-width: 0; }
.insight-name {
  font-size: 12px; font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Bar */
.insight-bar-wrap { display: flex; align-items: center; gap: 8px; }
.insight-bar-track { flex: 1; height: 5px; background: var(--admin-border); border-radius: 99px; overflow: hidden; }
.insight-bar-fill  { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.insight-bar-fill.green { background: linear-gradient(90deg, #6ee7b7, #34d399); }
.insight-val { font-size: 11px; color: var(--admin-text-soft); white-space: nowrap; }

/* Meta pills */
.insight-meta { display: flex; flex-wrap: wrap; gap: 5px; }
.meta-pill {
  padding: 2px 7px; border-radius: 999px; font-size: 11px;
  border: 1px solid var(--admin-border);
}
.meta-pill.views { color: #93c5fd; border-color: rgba(147,197,253,0.3); }
.meta-pill.buys  { color: #6ee7b7; border-color: rgba(110,231,183,0.3); }
.meta-pill.rate  { color: #f87171; border-color: rgba(248,113,113,0.3); }

@media (max-width: 980px) { .insights-grid { grid-template-columns: 1fr; } }
</style>