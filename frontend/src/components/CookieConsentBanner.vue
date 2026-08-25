<template>
  <transition name="consent-fade">
    <aside v-if="visible" class="cookie-consent" dir="rtl" role="dialog" aria-live="polite" aria-label="رضایت کوکی">
      <div class="consent-content">
        <h4>حریم خصوصی و تحلیل سایت</h4>
        <p>
          برای تحلیل رفتار بازدیدکننده و بهبود تجربه خرید، از ذخیره‌سازی مرورگر (کوکی/لوکال‌استوریج) برای آنالیتیکس استفاده می‌کنیم.
          کوکی‌های ضروری سایت همیشه فعال هستند.
        </p>
      </div>
      <div class="consent-actions">
        <button type="button" class="accept" @click="accept">پذیرش</button>
        <button type="button" class="reject" @click="reject">رد</button>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { isAnalyticsConsentResolved, setAnalyticsConsent } from '../utils/analyticsConsent'

const visible = ref(false)

function accept() {
  setAnalyticsConsent('granted')
  visible.value = false
}

function reject() {
  setAnalyticsConsent('denied')
  visible.value = false
}

onMounted(() => {
  visible.value = !isAnalyticsConsentResolved()
})
</script>

<style scoped>
.cookie-consent {
  position: fixed;
  inset-inline: 14px;
  bottom: 14px;
  z-index: 900;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--admin-panel-bg) 94%, transparent);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.22);
  padding: 12px;
  display: grid;
  gap: 10px;
}

.consent-content h4 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-main);
}

.consent-content p {
  margin: 6px 0 0;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.6;
}

.consent-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.consent-actions button {
  border-radius: 10px;
  border: 1px solid var(--admin-border);
  padding: 7px 14px;
  font-family: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}

.consent-actions .accept {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(120deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
}

.consent-actions .reject {
  color: var(--text-main);
  background: var(--admin-input-bg);
}

.consent-fade-enter-active,
.consent-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.consent-fade-enter-from,
.consent-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (min-width: 980px) {
  .cookie-consent {
    inset-inline-start: auto;
    width: min(560px, calc(100vw - 28px));
  }
}
</style>
