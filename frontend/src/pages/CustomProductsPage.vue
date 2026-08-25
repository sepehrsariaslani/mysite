<template>
  <div class="custom-page" dir="rtl">
    <CategoryBar />

    <section class="custom-hero">
      <div class="hero-content">
        <h1>محصولات سفارشی</h1>
        <p>مبلمان خود را مطابق با سلیقه و فضای خود طراحی کنید</p>
      </div>
    </section>

    <div class="custom-body">
      <div class="form-section">
        <h2>ثبت درخواست سفارش اختصاصی</h2>
        <p>لطفاً اطلاعات و طرح مورد نظر خود را ارسال کنید تا کارشناسان ما با شما تماس بگیرند.</p>
        
        <form @submit.prevent="submitForm" class="custom-form">
          <div class="row">
            <input type="text" placeholder="نام و نام خانوادگی" v-model="form.name" required>
            <input type="tel" placeholder="شماره تماس" v-model="form.phone" required>
          </div>
          <select v-model="form.type">
            <option value="">نوع محصول (مبل، صندلی، میز و...)</option>
            <option value="sofa">مبلمان راحتی</option>
            <option value="table">میز ناهارخوری</option>
            <option value="other">سایر موارد</option>
          </select>
          <textarea placeholder="توضیحات ابعاد، رنگ و متریال مورد نظر..." v-model="form.desc" rows="6" required></textarea>
          <button type="submit">ثبت درخواست سفارشی سازی</button>
        </form>
      </div>

      <div class="info-sidebar">
        <div class="step-card">
          <span>۱</span>
          <h4>ارسال طرح</h4>
          <p>طرح یا ابعاد مورد نظر خود را از طریق فرم ارسال کنید.</p>
        </div>
        <div class="step-card">
          <span>۲</span>
          <h4>بررسی فنی</h4>
          <p>تیم طراحی دنروم امکان ساخت و متریال لازم را بررسی می‌کند.</p>
        </div>
        <div class="step-card">
          <span>۳</span>
          <h4>تایید و ساخت</h4>
          <p>پس از تایید نهایی طرح و قیمت، فرآیند ساخت آغاز می‌شود.</p>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

const form = ref({ name: '', phone: '', type: '', desc: '' })

function submitForm() {
  trackAnalyticsEvent('form_submit', {
    properties: {
      form_type: 'custom_product_form',
      product_type: form.value.type || '',
    },
  })
  alert('درخواست سفارشی شما ثبت شد. کارشناسان فنی دنروم به زودی برای جزئیات بیشتر با شما تماس می‌گیرند.')
  form.value = { name: '', phone: '', type: '', desc: '' }
}
</script>

<style scoped>
.custom-page {
  background: #0a0a0a;
  min-height: 100vh;
  font-family: 'Peyda', sans-serif;
  color: white;
}

.custom-hero {
  background: transparent;
  padding: 120px 40px;
  text-align: center;
  position: relative;
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 800px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(40px);
  padding: 60px 40px;
  border-radius: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 100px rgba(0,0,0,0.5);
}

.custom-hero h1 {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 1000;
  margin-bottom: 16px;
  color: white;
}

.custom-hero p {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.4);
  max-width: 600px;
  margin: 0 auto;
}

.custom-body {
  max-width: 1400px;
  margin: 100px auto;
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 60px;
  padding: 0 40px;
}

.form-section h2 {
  font-size: 2.25rem;
  font-weight: 900;
  margin-bottom: 12px;
  color: white;
}

.form-section p {
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  margin-bottom: 48px;
  font-weight: 500;
}

.custom-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.custom-form .row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.custom-form input, 
.custom-form select, 
.custom-form textarea {
  padding: 18px 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  color: white;
  font-family: inherit;
  font-size: 1rem;
  transition: 0.3s;
}

.custom-form input:focus, 
.custom-form select:focus, 
.custom-form textarea:focus {
  background: rgba(255, 255, 255, 0.05);
  border-color: white;
  outline: none;
}

.custom-form button {
  background: white;
  color: black;
  padding: 24px;
  border: none;
  border-radius: 24px;
  font-weight: 900;
  font-size: 1.25rem;
  cursor: pointer;
  transition: 0.4s;
  margin-top: 10px;
  box-shadow: 0 15px 40px rgba(255, 255, 255, 0.1);
}

.custom-form button:hover {
  background: #ff9800;
  color: white;
  transform: translateY(-5px);
  box-shadow: 0 20px 50px rgba(255, 152, 0, 0.3);
}

.info-sidebar {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.step-card {
  background: rgba(255, 255, 255, 0.03);
  padding: 40px;
  border-radius: 40px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: 0.4s;
}

.step-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.step-card span {
  position: absolute;
  left: 30px;
  top: 10px;
  font-size: 6rem;
  font-weight: 1000;
  color: rgba(255, 255, 255, 0.04);
  line-height: 1;
}

.step-card h4 {
  color: #ff9800;
  margin-bottom: 12px;
  font-size: 1.5rem;
  font-weight: 900;
  position: relative;
}

.step-card p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.7;
  position: relative;
  font-weight: 500;
}

@media (max-width: 1024px) {
  .custom-body { grid-template-columns: 1fr; margin: 60px auto; }
}

@media (max-width: 768px) {
  .custom-hero { padding: 80px 20px; }
  .custom-body { padding: 0 20px; }
  .custom-form .row { grid-template-columns: 1fr; }
  .form-section h2 { font-size: 1.8rem; }
}
</style>
