<template>
  <section class="url-panel">

    <!-- ── Meta info cards ── -->
    <div class="meta-grid">
      <article class="meta-card glass-card" v-for="item in metaItems" :key="item.label">
        <div class="meta-top">
          <span class="meta-icon">{{ item.icon }}</span>
          <span class="meta-label">{{ item.label }}</span>
        </div>
        <div class="meta-val" :class="{ mono: item.mono }">{{ item.value }}</div>
        <div class="coverage-bar" v-if="item.progress !== undefined">
          <div class="cov-track">
            <div
              class="cov-fill"
              :class="coverageClass(item.progress)"
              :style="`width:${Math.min(item.progress, 100)}%`"
            ></div>
          </div>
          <span class="cov-pct" :class="coverageClass(item.progress)">{{ fa2(item.progress) }}٪</span>
        </div>
      </article>
    </div>

    <!-- ── Key paths ── -->
    <div class="paths-section glass-card" v-if="settings?.key_paths?.length">
      <div class="section-header">
        <span class="section-icon">🔗</span>
        <h4>مسیرهای کلیدی</h4>
        <span class="badge-count">{{ settings.key_paths.length }}</span>
      </div>
      <div class="paths">
        <a
          v-for="row in settings.key_paths"
          :key="`${row.label}-${row.path}`"
          class="path-pill"
          :href="row.path"
          target="_blank"
          rel="noopener"
        >
          <span class="pill-label">{{ row.label }}</span>
          <code class="pill-path">{{ row.path }}</code>
          <span class="pill-arrow">↗</span>
        </a>
      </div>
    </div>

    <!-- ── Unmapped routes warning ── -->
    <div class="warning-box" v-if="settings?.unmapped_routes?.length">
      <div class="warning-header">
        <span class="warn-icon">⚠️</span>
        <div>
          <strong>مسیرهای تعریف‌نشده</strong>
          <p>این مسیرها بازدید داشته‌اند اما در مسیرهای شناخته‌شده تعریف نشده‌اند.</p>
        </div>
        <span class="badge-count warn">{{ settings.unmapped_routes.length }}</span>
      </div>
      <div class="warning-items">
        <span
          v-for="row in settings.unmapped_routes"
          :key="row.route"
          class="warn-chip"
          :title="`${fa(row.views)} بازدید`"
        >
          <code>{{ row.route }}</code>
          <span class="warn-views">{{ fa(row.views) }} بازدید</span>
        </span>
      </div>
    </div>

  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  settings: { type: Object, default: null },
})

const fa  = (v) => Number(v || 0).toLocaleString('fa-IR')
const fa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 1 })

const metaItems = computed(() => {
  const s = props.settings
  return [
    { label: 'نشانی پایه',         icon: '🌐', value: s?.base_url     || '-', mono: true },
    { label: 'نام میزبان',          icon: '🖥',  value: s?.host_name    || '-', mono: true },
    { label: 'پایه API',            icon: '⚙️', value: s?.api_base_url || '-', mono: true },
    { label: 'پوشش مسیرها',         icon: '📊', value: `${fa2(s?.stats?.coverage_percent)}٪`, mono: false, progress: Number(s?.stats?.coverage_percent || 0) },
  ]
})

const coverageClass = (v) => {
  const n = Number(v || 0)
  if (n >= 80) return 'cov-high'
  if (n >= 50) return 'cov-mid'
  return 'cov-low'
}
</script>

<style scoped>
.url-panel { display: grid; gap: 12px; }

/* Glass base */
.glass-card {
  background: var(--admin-panel-bg); border: 1px solid var(--admin-border);
  border-radius: 18px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}

/* ── Meta grid ── */
.meta-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }

.meta-card { padding: 12px 14px; overflow: hidden; transition: transform 0.15s; }
.meta-card:hover { transform: translateY(-2px); }

.meta-top { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.meta-icon  { font-size: 14px; }
.meta-label { font-size: 11px; color: var(--admin-text-soft); }

.meta-val {
  font-size: 12px; font-weight: 500; word-break: break-all; line-height: 1.4;
}
.meta-val.mono { font-family: monospace; direction: ltr; text-align: left; }

/* Coverage bar */
.coverage-bar { display: flex; align-items: center; gap: 7px; margin-top: 8px; }
.cov-track { flex: 1; height: 5px; background: var(--admin-border); border-radius: 99px; overflow: hidden; }
.cov-fill  { height: 100%; border-radius: 99px; transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1); }
.cov-fill.cov-high  { background: #6ee7b7; }
.cov-fill.cov-mid   { background: #fcd34d; }
.cov-fill.cov-low   { background: #f87171; }
.cov-pct { font-size: 11px; font-weight: 600; white-space: nowrap; }
.cov-pct.cov-high { color: #6ee7b7; }
.cov-pct.cov-mid  { color: #fcd34d; }
.cov-pct.cov-low  { color: #f87171; }

/* ── Paths section ── */
.paths-section { overflow: hidden; }
.section-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid var(--admin-border);
}
.section-icon { font-size: 15px; }
.section-header h4 { margin: 0; font-size: 0.9rem; font-weight: 600; flex: 1; }
.badge-count {
  font-size: 11px; font-weight: 700;
  background: var(--admin-chip-bg); border: 1px solid var(--admin-border);
  border-radius: 999px; padding: 2px 8px; color: var(--admin-text-soft);
}
.badge-count.warn {
  background: rgba(251,191,36,0.1); border-color: rgba(251,191,36,0.3); color: #fbbf24;
}

.paths { display: flex; flex-wrap: wrap; gap: 7px; padding: 12px 14px; }

.path-pill {
  text-decoration: none; color: var(--text-main);
  border: 1px solid var(--admin-border); border-radius: 999px;
  padding: 6px 12px;
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--admin-chip-bg);
  transition: all 0.15s; font-size: 12px;
}
.path-pill:hover {
  border-color: #818cf8;
  background: rgba(129,140,248,0.08);
  color: #a5b4fc;
}
.pill-label { font-size: 12px; font-weight: 500; }
.pill-path  { font-family: monospace; font-size: 11px; color: var(--admin-text-soft); direction: ltr; }
.pill-arrow { font-size: 11px; color: var(--admin-text-soft); }
.path-pill:hover .pill-arrow { color: #818cf8; }

/* ── Warning box ── */
.warning-box {
  border: 1px solid rgba(251,191,36,0.35);
  border-radius: 18px;
  background: rgba(251,191,36,0.05);
  overflow: hidden;
}
.warning-header {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px 14px; border-bottom: 1px solid rgba(251,191,36,0.2);
}
.warn-icon { font-size: 18px; flex-shrink: 0; padding-top: 1px; }
.warning-header strong { display: block; font-size: 13px; margin-bottom: 2px; color: #fbbf24; }
.warning-header p { margin: 0; font-size: 11px; color: var(--admin-text-soft); }

.warning-items { display: flex; flex-wrap: wrap; gap: 6px; padding: 12px 14px; }

.warn-chip {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid rgba(251,191,36,0.25);
  border-radius: 8px; padding: 5px 10px;
  background: rgba(251,191,36,0.06);
  font-size: 11px;
}
.warn-chip code { font-family: monospace; direction: ltr; color: #fbbf24; }
.warn-views { color: var(--admin-text-soft); border-right: 1px solid rgba(251,191,36,0.25); padding-right: 6px; }

/* ── Responsive ── */
@media (max-width: 940px) { .meta-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 620px) { .meta-grid { grid-template-columns: 1fr; } }
</style>