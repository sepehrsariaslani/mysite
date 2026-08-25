<template>
  <div class="contact-page" dir="rtl">
    <CategoryBar />

    <section class="contact-section">
      <div class="contact-hero">
        <div class="hero-content">
          <span class="contact-badge">پشتیبانی ۲۴ ساعته</span>
          <h1>مشاوره و فروش</h1>
          <p>ما همیشه آماده پاسخگویی به سوالات شما هستیم</p>
        </div>
      </div>

      <div class="contact-cards">
        <div class="contact-card" v-for="c in contactCards" :key="c.title">
          <h3>{{ c.title }}</h3>
          <p v-if="c.link"><a :href="c.link">{{ c.content }}</a></p>
          <p v-else>{{ c.content }}</p>
        </div>
      </div>

      <div class="contact-main">
        <div class="contact-form-wrapper">
          <h2>فرم تماس</h2>
          <form @submit.prevent="submitForm" class="contact-form">
            <input type="text" placeholder="نام و نام خانوادگی" v-model="form.name" required>
            <input type="tel" placeholder="شماره تماس" v-model="form.phone" required>
            <select v-model="form.subject">
              <option value="">موضوع را انتخاب کنید</option>
              <option value="sales">مشاوره فروش</option>
              <option value="support">پشتیبانی</option>
            </select>
            <textarea placeholder="پیام شما" v-model="form.message" rows="5" required></textarea>
            <button type="submit" class="submit-btn">ارسال پیام</button>
          </form>
        </div>
        <div class="contact-map">
          <h2>موقعیت ما</h2>
          <div class="map-placeholder">
            <p>تهران، خیابان ولیعصر، بالاتر از میدان ونک</p>
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script setup>
import { ref } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

const form = ref({ name: '', phone: '', subject: '', message: '' })

const contactCards = [
  { title: 'تماس تلفنی', content: '۰۲۱-۸۸۱۲۳۴۵۶', link: 'tel:+982188123456' },
  { title: 'ایمیل', content: 'info@denroom.ir', link: 'mailto:info@denroom.ir' },
  { title: 'ساعات کاری', content: 'شنبه تا چهارشنبه: ۹ صبح - ۸ شب' }
]

function submitForm() {
  trackAnalyticsEvent('form_submit', {
    properties: {
      form_type: 'consultation_form',
      subject: form.value.subject || '',
    },
  })
  alert('پیام شما با موفقیت ارسال شد. کارشناسان ما به زودی با شما تماس می‌گیرند.')
  form.value = { name: '', phone: '', subject: '', message: '' }
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
  max-width: 800px;
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
  font-size: 1.08rem;
  color: var(--contact-muted);
  max-width: 600px;
  margin: 0 auto;
}

.contact-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-bottom: 36px;
  position: relative;
  z-index: 10;
  padding: 0;
}

.contact-card {
  background: var(--contact-surface);
  padding: 30px 24px;
  border-radius: 24px;
  backdrop-filter: blur(12px);
  border: 1px solid var(--contact-border);
  text-align: center;
  transition: 0.4s cubic-bezier(0.19, 1, 0.22, 1);
  box-shadow: var(--contact-shadow);
}

.contact-card:hover {
  transform: translateY(-5px);
  border-color: var(--contact-border-strong);
  box-shadow: var(--contact-shadow-strong);
}

.contact-card h3 {
  font-size: 1.15rem;
  color: var(--contact-accent-strong);
  margin-bottom: 8px;
  font-weight: 800;
}

.contact-card p {
  color: var(--contact-muted);
  font-size: 1rem;
}
.contact-card p a {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px dashed var(--contact-border-strong);
}

.contact-main {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
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

.contact-map {
  background: var(--contact-surface);
  border-radius: 28px;
  padding: 34px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px solid var(--contact-border);
  box-shadow: var(--contact-shadow);
}

.contact-map h2 {
  font-size: 1.7rem;
  font-weight: 900;
  margin-bottom: 16px;
  color: var(--contact-text);
}

.map-placeholder {
  width: 100%;
  height: 260px;
  background: linear-gradient(150deg, #fff 0%, var(--contact-surface-soft) 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 1px dashed var(--contact-border-strong);
  color: var(--contact-muted);
  font-weight: 500;
}

@media (max-width: 1024px) {
  .contact-main { grid-template-columns: 1fr; }
  .contact-hero { padding: 92px 0 16px; }
  .contact-cards { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
  .contact-section { padding: 0 14px 72px; }
  .hero-content { padding: 36px 20px; border-radius: 24px; }
  .contact-cards { grid-template-columns: 1fr; padding: 0; }
  .contact-form-wrapper { padding: 24px 18px; border-radius: 22px; }
  .contact-map { padding: 24px 18px; border-radius: 22px; }
  .contact-hero h1 { font-size: clamp(2rem, 9vw, 2.8rem); }
}
</style>
