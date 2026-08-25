<template>
  <div class="contact-page" dir="rtl">
    <CategoryBar />

    <section class="contact-section">
      <div class="contact-hero">
        <div class="hero-content">
          <span class="contact-badge">پیوستن به تیم دنروم</span>
          <h1>همکاری با ما</h1>
          <p>اگر خلاق و پرانرژی هستید، ما منتظر شما هستیم</p>
        </div>
      </div>

      <div class="contact-main">
        <div class="contact-form-wrapper">
          <h2>فرم درخواست همکاری</h2>
          <form @submit.prevent="submitForm" class="contact-form">
            <input type="text" placeholder="نام و نام خانوادگی" v-model="form.name" required>
            <input type="tel" placeholder="شماره تماس" v-model="form.phone" required>
            <select v-model="form.role">
              <option value="">سمت مورد نظر</option>
              <option value="sales">فروش و بازاریابی</option>
              <option value="design">طراحی داخلی</option>
              <option value="admin">امور اداری</option>
            </select>
            <textarea placeholder="توضیحات و سوابق" v-model="form.message" rows="5" required></textarea>
            <button type="submit" class="submit-btn">ارسال درخواست</button>
          </form>
        </div>
        <div class="contact-info-panel">
          <h2>چرا دنروم؟</h2>
          <ul class="perks-list">
            <li>محیط کاری خلاق و پویا</li>
            <li>حقوق و مزایای عالی</li>
            <li>فرصت رشد و یادگیری</li>
            <li>بیمه و خدمات رفاهی</li>
          </ul>
        </div>
      </div>
    </section>


  </div>
</template>

<script setup>
import { ref } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

const form = ref({ name: '', phone: '', role: '', message: '' })

function submitForm() {
  trackAnalyticsEvent('form_submit', {
    properties: {
      form_type: 'cooperation_form',
      role: form.value.role || '',
    },
  })
  alert('درخواست شما با موفقیت ثبت شد. تیم منابع انسانی با شما تماس خواهد گرفت.')
  form.value = { name: '', phone: '', role: '', message: '' }
}
</script>

<style scoped>
.contact-page {
  --contact-bg: #ffffff;
  --contact-surface: #ffffff;
  --contact-surface-soft: #f7f2ea;
  --contact-border: rgba(122, 86, 58, 0.2);
  --contact-border-strong: rgba(122, 86, 58, 0.3);
  --contact-shadow: 0 22px 48px rgba(64, 42, 25, 0.1);
  --contact-shadow-strong: 0 28px 58px rgba(64, 42, 25, 0.14);
  --contact-text: #2f2118;
  --contact-muted: rgba(56, 38, 25, 0.68);
  --contact-accent: #ca9556;
  --contact-accent-strong: #7b4f34;
  --contact-accent-soft: rgba(202, 149, 86, 0.16);
  background: var(--contact-bg);
  min-height: 100vh;
  font-family: 'Peyda', sans-serif;
  color: var(--contact-text);
}

[data-theme='dark'] .contact-page {
  --contact-bg: #fcfaf7;
  --contact-surface: #ffffff;
  --contact-surface-soft: #f4ece2;
  --contact-border: rgba(122, 86, 58, 0.24);
  --contact-border-strong: rgba(122, 86, 58, 0.34);
  --contact-shadow: 0 22px 48px rgba(64, 42, 25, 0.11);
  --contact-shadow-strong: 0 28px 58px rgba(64, 42, 25, 0.15);
  --contact-text: #2f2118;
  --contact-muted: rgba(56, 38, 25, 0.7);
  --contact-accent: #c8904f;
  --contact-accent-strong: #744a31;
  --contact-accent-soft: rgba(200, 144, 79, 0.18);
}

.contact-section {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px 90px;
}

.contact-hero {
  position: relative;
  background: transparent;
  padding: 108px 0 22px;
  text-align: center;
  margin-bottom: 20px;
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 820px;
  margin: 0 auto;
  background: linear-gradient(145deg, var(--contact-surface) 0%, var(--contact-surface-soft) 100%);
  backdrop-filter: blur(16px);
  padding: 52px 36px;
  border-radius: 34px;
  border: 1px solid var(--contact-border);
  box-shadow: var(--contact-shadow);
}

.contact-badge {
  background: var(--contact-accent-soft);
  color: var(--contact-accent-strong);
  padding: 8px 20px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 800;
  margin-bottom: 20px;
  display: inline-block;
  border: 1px solid var(--contact-border-strong);
}

.contact-hero h1 {
  font-size: clamp(2.3rem, 4.8vw, 3.6rem);
  font-weight: 1000;
  color: var(--contact-text);
  margin-bottom: 14px;
  letter-spacing: -0.6px;
}

.contact-hero p {
  font-size: 1.06rem;
  color: var(--contact-muted);
  max-width: 560px;
  margin: 0 auto;
}

.contact-main {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}

.contact-form-wrapper {
  background: var(--contact-surface);
  padding: 36px;
  border-radius: 28px;
  backdrop-filter: blur(12px);
  border: 1px solid var(--contact-border);
  box-shadow: var(--contact-shadow);
}

.contact-form-wrapper h2 {
  font-size: 1.7rem;
  font-weight: 900;
  margin-bottom: 8px;
  color: var(--contact-text);
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 22px;
}

.contact-form input,
.contact-form select,
.contact-form textarea {
  padding: 14px 16px;
  background: #fff;
  border: 1px solid var(--contact-border);
  border-radius: 14px;
  color: var(--contact-text);
  font-family: inherit;
  font-size: 0.98rem;
  transition: 0.3s;
}

.contact-form input:focus,
.contact-form select:focus,
.contact-form textarea:focus {
  border-color: var(--contact-accent);
  box-shadow: 0 0 0 3px rgba(202, 149, 86, 0.16);
  outline: none;
}

.contact-form input::placeholder,
.contact-form textarea::placeholder {
  color: rgba(63, 43, 29, 0.52);
}

.contact-form select option {
  color: var(--contact-text);
}

.submit-btn {
  background: linear-gradient(135deg, var(--contact-accent) 0%, #b97d40 100%);
  color: #fff;
  padding: 16px;
  border: none;
  border-radius: 14px;
  font-weight: 880;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.3s;
  margin-top: 6px;
  box-shadow: 0 14px 28px rgba(168, 108, 52, 0.24);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 30px rgba(168, 108, 52, 0.3);
}

.contact-info-panel {
  background: var(--contact-surface);
  padding: 34px 30px;
  border-radius: 28px;
  border: 1px solid var(--contact-border);
  box-shadow: var(--contact-shadow);
}

.contact-info-panel h2 {
  margin: 0;
  font-size: 1.7rem;
  color: var(--contact-text);
  font-weight: 900;
}

.perks-list {
  margin-top: 20px;
  padding-right: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.perks-list li {
  list-style: disc;
  color: var(--contact-muted);
  font-weight: 600;
}

@media (max-width: 1024px) {
  .contact-main { grid-template-columns: 1fr; }
  .contact-hero { padding: 92px 0 16px; }
}

@media (max-width: 768px) {
  .contact-section { padding: 0 14px 72px; }
  .hero-content { padding: 36px 20px; border-radius: 24px; }
  .contact-form-wrapper { padding: 24px 18px; border-radius: 22px; }
  .contact-info-panel { padding: 24px 18px; border-radius: 22px; }
  .contact-hero h1 { font-size: clamp(2rem, 9vw, 2.8rem); }
}
</style>
