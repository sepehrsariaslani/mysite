<template>
  <article class="stat-card" :class="toneClass" :style="`--tone-color:${toneHex}`">
    <!-- Decorative orb -->
    <div class="card-orb" aria-hidden="true"></div>

    <!-- Trend icon top-right -->
    <div class="card-top">
      <span class="card-icon" v-if="icon">{{ icon }}</span>
      <span class="trend-badge" v-if="trend !== null" :class="trend >= 0 ? 'up' : 'down'">
        {{ trend >= 0 ? '▲' : '▼' }} {{ Math.abs(trend).toLocaleString('fa-IR', { maximumFractionDigits: 1 }) }}٪
      </span>
    </div>

    <p class="label">{{ title }}</p>
    <div class="value">{{ value }}</div>
    <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>

    <!-- Optional mini progress bar -->
    <div class="progress-wrap" v-if="progress !== null">
      <div class="progress-track">
        <div class="progress-fill" :style="`width:${Math.min(Math.max(progress, 0), 100)}%`"></div>
      </div>
      <span class="progress-label">{{ progress.toLocaleString('fa-IR', { maximumFractionDigits: 0 }) }}٪</span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title:    { type: String,  required: true },
  value:    { type: String,  required: true },
  subtitle: { type: String,  default: '' },
  tone:     { type: String,  default: 'amber' },
  icon:     { type: String,  default: '' },
  trend:    { type: Number,  default: null },   // percentage change, null = hidden
  progress: { type: Number,  default: null },   // 0-100, null = hidden
})

const tones = {
  amber: '#f6b24a',
  blue:  '#818cf8',
  mint:  '#6ee7b7',
  rose:  '#f87171',
  purple:'#c4b5fd',
}

const toneHex = computed(() => tones[props.tone] || tones.amber)
const toneClass = computed(() => {
  const allowed = new Set(Object.keys(tones))
  return allowed.has(props.tone) ? `tone-${props.tone}` : 'tone-amber'
})
</script>

<style scoped>
.stat-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid var(--admin-border);
  background: var(--admin-chip-bg);
  padding: 14px 16px 14px;
  display: grid;
  gap: 4px;
  transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.12);
}

/* Accent left border */
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 3px; height: 100%;
  background: var(--tone-color);
  border-radius: 0 18px 18px 0;
  opacity: 0.9;
}

/* Background orb glow */
.card-orb {
  position: absolute;
  inset-inline-end: -32px;
  top: -32px;
  width: 100px; height: 100px;
  border-radius: 50%;
  background: var(--tone-color);
  opacity: 0.12;
  filter: blur(20px);
  pointer-events: none;
}

/* Top row: icon + trend */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  min-height: 22px;
}
.card-icon { font-size: 16px; }

.trend-badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 7px; border-radius: 999px;
}
.trend-badge.up   { background: rgba(110,231,183,0.15); color: #6ee7b7; }
.trend-badge.down { background: rgba(248,113,113,0.15); color: #f87171; }

/* Text */
.label {
  margin: 0;
  font-size: 11px;
  color: var(--admin-text-soft);
  letter-spacing: 0.02em;
}
.value {
  font-size: clamp(1.15rem, 2.5vw, 1.65rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-main);
}
.subtitle {
  margin: 0;
  font-size: 11px;
  color: var(--text-muted, #999);
}

/* Progress bar */
.progress-wrap {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 6px;
}
.progress-track {
  flex: 1; height: 4px;
  background: var(--admin-border);
  border-radius: 99px; overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: 99px;
  background: var(--tone-color);
  transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  opacity: 0.85;
}
.progress-label {
  font-size: 10px;
  color: var(--admin-text-soft);
  white-space: nowrap;
}

/* Tone color vars (fallback for orb without inline style support) */
.tone-amber { --tone-color: #f6b24a; }
.tone-blue  { --tone-color: #818cf8; }
.tone-mint  { --tone-color: #6ee7b7; }
.tone-rose  { --tone-color: #f87171; }
.tone-purple{ --tone-color: #c4b5fd; }
</style>