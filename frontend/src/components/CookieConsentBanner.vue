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
  z-index: 2000;
  border: 1px solid rgba(180, 160, 130, 0.35);
  border-radius: 14px;
  background: rgba(30, 28, 25, 0.97);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), 0 2px 8px rgba(0, 0, 0, 0.2);
  padding: 14px 16px;
  display: grid;
  gap: 10px;
}

.consent-content h4 {
  margin: 0;
  font-size: 0.95rem;
  color: #f5f0e8;
  font-weight: 700;
}

.consent-content p {
  margin: 6px 0 0;
  font-size: 0.82rem;
  color: #c8c0b4;
  line-height: 1.7;
}

.consent-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.consent-actions button {
  border-radius: 10px;
  border: 1px solid rgba(180, 160, 130, 0.25);
  padding: 8px 18px;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.consent-actions .accept {
  color: #3a2a10;
  border-color: transparent;
  background: linear-gradient(120deg, #e8b84b, #d4a03a);
}

.consent-actions .reject {
  color: #c8c0b4;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(180, 160, 130, 0.2);
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

/* Mobile: push above bottom nav */
@media (max-width: 768px) {
  .cookie-consent {
    bottom: 90px;
  }
}

@media (min-width: 980px) {
  .cookie-consent {
    inset-inline-start: auto;
    width: min(560px, calc(100vw - 28px));
  }
}
</style>
