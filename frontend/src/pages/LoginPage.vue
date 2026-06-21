<template>
  <div class="login-page" dir="rtl">
    <div class="bg-grid" aria-hidden="true"></div>
    <div class="bg-glow bg-glow-a" aria-hidden="true"></div>
    <div class="bg-glow bg-glow-b" aria-hidden="true"></div>

    <section class="login-shell">
      <span class="liquid-layer liquid-layer-a" aria-hidden="true"></span>
      <span class="liquid-layer liquid-layer-b" aria-hidden="true"></span>
      <span class="liquid-sheen" aria-hidden="true"></span>

      <aside class="showcase-panel">
        <a href="/mysite" class="showcase-brand">DENROOM</a>

        <div class="orb-stage" aria-hidden="true">
          <span class="orb orb-main"></span>
          <span class="orb orb-mid"></span>
          <span class="orb orb-small"></span>
          <span class="pod pod-1"></span>
          <span class="pod pod-2"></span>
          <span class="pod pod-3"></span>
        </div>

        <div class="showcase-copy">
          <h2>پنل مشتری دن‌روم</h2>
          <p>
            سفارش‌ها، پارچه‌های انتخابی، پروژه‌ها و محصولات ذخیره‌شده‌ات را یکجا مدیریت کن.
          </p>
        </div>

        <div class="showcase-meta">
          <span>Secure Session</span>
          <span>Fast Support</span>
          <span>Realtime Updates</span>
        </div>
      </aside>

      <section class="form-panel">
        <div class="panel-top">
          <a href="/mysite" class="mini-logo">
            <span class="logo-den">DEN</span><span class="logo-room">ROOM</span>
          </a>
          <a href="/mysite" class="go-home">صفحه اول</a>
        </div>

        <header class="form-head">
          <h1>ورود به حساب کاربری</h1>
          <p>با حساب خود وارد شوید تا قیمت‌ها و انتخاب‌های شخصی‌سازی‌شده را ببینید.</p>
        </header>

        <form @submit.prevent="handleLogin" class="login-form">
          <label class="field-wrap">
            <span>نام کاربری یا ایمیل</span>
            <input
              type="text"
              v-model="email"
              autocomplete="username"
              placeholder="info@denroom.ir"
              required
            />
          </label>

          <label class="field-wrap">
            <span>رمز عبور</span>
            <div class="password-wrap">
              <input
                :type="showPass ? 'text' : 'password'"
                v-model="password"
                autocomplete="current-password"
                placeholder="••••••••"
                required
              />
              <button type="button" class="toggle-pass" @click="showPass = !showPass" :aria-label="showPass ? 'پنهان کردن رمز' : 'نمایش رمز'">
                <svg v-if="showPass" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.89 1 12c.8-2.2 2.24-4.16 4.11-5.64M9.9 4.24A10.93 10.93 0 0 1 12 4c5 0 9.27 3.11 11 8a11.8 11.8 0 0 1-1.67 2.87" />
                  <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>
          </label>

          <div class="form-footer">
            <label class="remember">
              <input type="checkbox" v-model="remember" />
              <span>مرا به خاطر بسپار</span>
            </label>
            <a href="/login#forgot">فراموشی رمز عبور؟</a>
          </div>

          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">ورود به پنل</span>
            <span v-else class="loader-tiny"></span>
            <i class="submit-orb" aria-hidden="true"></i>
          </button>
        </form>

        <footer class="panel-foot">
          <span>حساب هنوز فعال نیست؟</span>
          <a href="/consultation">درخواست فعال‌سازی</a>
        </footer>
      </section>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const email = ref('')
const password = ref('')
const remember = ref(false)
const showPass = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const nextUrl = new URLSearchParams(window.location.search).get('next') || '/dashboard'

async function checkSession() {
  try {
    const response = await fetch('/api/method/mysite.portal_api.portal_session')
    const payload = await response.json()
    if (payload?.message?.authenticated) {
      window.location.href = nextUrl
    }
  } catch (error) {
    // Ignore session check errors.
  }
}

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch('/api/method/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        usr: email.value,
        pwd: password.value,
        remember_me: remember.value ? 1 : 0,
      }),
    })

    const text = await response.text()
    let payload = {}
    try {
      payload = JSON.parse(text)
    } catch (error) {
      payload = {}
    }

    if (!response.ok || payload?.exception || payload?.exc_type) {
      throw new Error('ورود ناموفق بود. لطفا نام کاربری یا رمز عبور را بررسی کنید.')
    }

    window.location.href = nextUrl
  } catch (error) {
    errorMessage.value = error?.message || 'خطا در ارتباط با سرور.'
  } finally {
    loading.value = false
  }
}

onMounted(checkSession)
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #130d0c;
  position: relative;
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 34px 16px;
}

.login-page,
.login-page *,
.login-page *::before,
.login-page *::after {
  box-sizing: border-box;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: radial-gradient(circle at center, #000 0%, transparent 82%);
  opacity: 0.28;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(62px);
  pointer-events: none;
}

.bg-glow-a {
  width: 460px;
  height: 460px;
  background: rgba(242, 201, 126, 0.28);
  top: -160px;
  right: -100px;
  animation: floatGlow 12s ease-in-out infinite alternate;
}

.bg-glow-b {
  width: 420px;
  height: 420px;
  background: rgba(143, 90, 76, 0.28);
  bottom: -170px;
  left: -90px;
  animation: floatGlow 15s ease-in-out infinite alternate-reverse;
}

.login-shell {
  position: relative;
  z-index: 2;
  width: min(1160px, 100%);
  min-height: 680px;
  border-radius: 34px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  box-shadow:
    0 34px 90px rgba(0, 0, 0, 0.45),
    inset 0 0 0 1px rgba(255, 255, 255, 0.07);
  animation: shellReveal 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  isolation: isolate;
}

.liquid-layer {
  position: absolute;
  z-index: 1;
  border-radius: 44% 56% 63% 37% / 36% 40% 60% 64%;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: radial-gradient(circle at 32% 24%, rgba(255, 255, 255, 0.52) 0%, rgba(255, 255, 255, 0.08) 44%, rgba(255, 255, 255, 0.02) 100%);
  box-shadow:
    inset 0 2px 6px rgba(255, 255, 255, 0.28),
    0 16px 40px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(18px) saturate(165%);
  -webkit-backdrop-filter: blur(18px) saturate(165%);
  opacity: 0.72;
  pointer-events: none;
  animation: liquidDrift 14s ease-in-out infinite;
}

.liquid-layer-a {
  width: 240px;
  height: 240px;
  left: 42%;
  top: -78px;
}

.liquid-layer-b {
  width: 180px;
  height: 180px;
  left: 50%;
  bottom: -78px;
  animation-delay: -4.2s;
  opacity: 0.58;
}

.liquid-sheen {
  position: absolute;
  inset: -42% -12% auto;
  z-index: 1;
  height: 58%;
  background: linear-gradient(115deg, rgba(255, 255, 255, 0) 18%, rgba(255, 255, 255, 0.26) 46%, rgba(255, 255, 255, 0) 76%);
  transform: translateX(-60%) rotate(-8deg);
  animation: sheenSweep 8.5s ease-in-out infinite;
  pointer-events: none;
}

.showcase-panel {
  position: relative;
  z-index: 3;
  padding: 26px 28px;
  background:
    radial-gradient(circle at 84% 8%, rgba(255, 255, 255, 0.22), transparent 28%),
    linear-gradient(165deg, #6f4037 0%, #8a5847 34%, #3f2a28 100%);
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  gap: 16px;
}

.showcase-brand {
  width: fit-content;
  text-decoration: none;
  color: #fff;
  font-weight: 900;
  letter-spacing: 0.06em;
  font-size: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 999px;
  padding: 7px 12px;
}

.orb-stage {
  position: relative;
  min-height: 400px;
}

.orb {
  position: absolute;
  border-radius: 50%;
  box-shadow: 0 20px 36px rgba(0, 0, 0, 0.2);
}

.orb-main {
  z-index: 1000;
  width: 168px;
  height: 168px;
  background: radial-gradient(circle at 33% 28%, #fff8e8 0%, #f6d8ad 58%, #e2aa75 100%);
  right: 30%;
  top: 20%;
  animation: orbFloat 5.5s ease-in-out infinite;
}

.orb-mid {
  z-index: 1000;
  width: 122px;
  height: 122px;
  background: radial-gradient(circle at 35% 30%, #ffe8ca 0%, #f6c48f 62%, #d88a56 100%);
  right: 7%;
  top: 44%;
  animation: orbFloat 6.1s ease-in-out infinite reverse;
}

.orb-small {
  z-index: 1000;
  width: 88px;
  height: 88px;
  background: radial-gradient(circle at 35% 28%, #fff4e3 0%, #f0c695 62%, #c98f5d 100%);
  right: 55%;
  top: 58%;
  animation: orbFloat 4.6s ease-in-out infinite;
}

.pod {
  position: absolute;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.28);
}

.pod-1 {
  width: 92px;
  height: 30px;
  right: 28%;
  top: 57%;
}

.pod-2 {
  width: 75px;
  height: 26px;
  right: 4%;
  top: 72%;
}

.pod-3 {
  width: 65px;
  height: 24px;
  right: 54%;
  top: 78%;
}

.showcase-copy h2 {
  margin: 0;
  color: #fff;
  font-size: clamp(1.8rem, 2.4vw, 2.5rem);
  line-height: 1.2;
  font-weight: 900;
}

.showcase-copy p {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 0.96rem;
  line-height: 1.9;
  max-width: 520px;
}

.showcase-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.showcase-meta span {
  border: 1px solid rgba(255, 255, 255, 0.27);
  color: #fff;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.73rem;
  font-weight: 800;
}

.form-panel {
  position: relative;
  z-index: 3;
  background:
    linear-gradient(160deg, rgba(252, 248, 239, 0.88) 0%, rgba(244, 235, 222, 0.72) 100%);
  backdrop-filter: blur(10px) saturate(125%);
  -webkit-backdrop-filter: blur(10px) saturate(125%);
  padding: 28px 30px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-right: 1px solid rgba(255, 255, 255, 0.36);
}

.form-panel::before {
  content: '';
  position: absolute;
  inset: 10px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.48);
  pointer-events: none;
}

.form-panel::after {
  content: '';
  position: absolute;
  top: 8%;
  right: -34%;
  width: 66%;
  height: 48%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0) 68%);
  filter: blur(14px);
  pointer-events: none;
}

.panel-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 28px;
}

.mini-logo {
  text-decoration: none;
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  font-weight: 900;
  font-size: 1.12rem;
}

.logo-den {
  color: #1d1614;
}

.logo-room {
  color: #b17b2f;
}

.go-home {
  text-decoration: none;
  border: 1px solid rgba(81, 62, 49, 0.22);
  color: #3a2a23;
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 0.79rem;
  font-weight: 760;
}

.go-home:hover {
  border-color: #b17b2f;
  color: #1f1511;
}

.form-head h1 {
  margin: 0;
  color: #1a1311;
  font-size: clamp(1.6rem, 2.4vw, 2.15rem);
  line-height: 1.3;
  font-weight: 900;
}

.form-head p {
  margin: 10px 0 0;
  color: #5f5248;
  line-height: 1.9;
  font-size: 0.9rem;
}

.login-form {
  margin-top: 24px;
  display: grid;
  gap: 14px;
  width: 100%;
  min-width: 0;
}

.field-wrap {
  display: grid;
  gap: 8px;
  width: 100%;
  min-width: 0;
}

.field-wrap > span {
  color: #6d5a4c;
  font-size: 0.82rem;
  font-weight: 800;
}

.field-wrap input {
  display: block;
  width: 100%;
  max-width: 100%;
  height: 48px;
  border-radius: 14px;
  border: 1px solid rgba(198, 184, 162, 0.72);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.72) 0%, rgba(255, 255, 255, 0.54) 100%);
  backdrop-filter: blur(8px) saturate(130%);
  -webkit-backdrop-filter: blur(8px) saturate(130%);
  padding: 0 14px;
  font-family: inherit;
  font-size: 0.92rem;
  color: #1f1916;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field-wrap input:focus {
  outline: none;
  border-color: #b17b2f;
  box-shadow: 0 0 0 4px rgba(177, 123, 47, 0.12);
}

.password-wrap {
  position: relative;
  width: 100%;
  min-width: 0;
}

.password-wrap input {
  padding-left: 46px;
}

.toggle-pass {
  position: absolute;
  left: 8px;
  top: 7px;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(198, 184, 162, 0.72);
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(10px) saturate(140%);
  -webkit-backdrop-filter: blur(10px) saturate(140%);
  color: #6a5b50;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.toggle-pass svg {
  width: 16px;
  height: 16px;
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 2px;
}

.remember {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #5f5248;
  font-size: 0.82rem;
  font-weight: 700;
}

.remember input {
  accent-color: #a77432;
}

.form-footer a {
  text-decoration: none;
  color: #9f6a26;
  font-size: 0.82rem;
  font-weight: 800;
}

.error-message {
  margin: 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: #ffe9e9;
  color: #a63939;
  border: 1px solid #f4bbbb;
  font-size: 0.83rem;
  font-weight: 700;
}

.submit-btn {
  margin-top: 6px;
  border: 0;
  height: 54px;
  border-radius: 999px;
  background: linear-gradient(140deg, #181412 0%, #3c2b23 100%);
  color: #fff;
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 24px rgba(30, 20, 18, 0.35);
}

.submit-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.submit-orb {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.42) 0%, rgba(255, 255, 255, 0) 70%);
  left: -25px;
  top: -44px;
  animation: pulseOrb 2.4s ease-in-out infinite;
}

.loader-tiny {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.panel-foot {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  color: #6a5d51;
  font-size: 0.82rem;
  font-weight: 700;
}

.panel-foot a {
  text-decoration: none;
  color: #9f6a26;
  font-weight: 900;
}

@keyframes shellReveal {
  from {
    opacity: 0;
    transform: translateY(26px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes orbFloat {
  0% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-12px) scale(1.04);
  }
  100% {
    transform: translateY(0) scale(1);
  }
}

@keyframes liquidDrift {
  0% {
    transform: translate(0, 0) rotate(0deg) scale(1);
    border-radius: 44% 56% 63% 37% / 36% 40% 60% 64%;
  }
  35% {
    transform: translate(18px, 12px) rotate(9deg) scale(1.05);
    border-radius: 58% 42% 51% 49% / 41% 59% 45% 55%;
  }
  68% {
    transform: translate(-12px, 24px) rotate(-6deg) scale(0.96);
    border-radius: 38% 62% 47% 53% / 56% 44% 58% 42%;
  }
  100% {
    transform: translate(0, 0) rotate(0deg) scale(1);
    border-radius: 44% 56% 63% 37% / 36% 40% 60% 64%;
  }
}

@keyframes sheenSweep {
  0% {
    transform: translateX(-64%) rotate(-8deg);
    opacity: 0;
  }
  20% {
    opacity: 0.7;
  }
  55% {
    opacity: 0.5;
  }
  100% {
    transform: translateX(68%) rotate(-8deg);
    opacity: 0;
  }
}

@keyframes floatGlow {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(24px, -20px) scale(1.08);
  }
}

@keyframes pulseOrb {
  0%, 100% {
    transform: scale(0.88);
    opacity: 0.45;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.2;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1060px) {
  .login-shell {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .showcase-panel {
    min-height: 410px;
  }

  .liquid-layer-a {
    left: 22%;
    top: -92px;
  }

  .liquid-layer-b {
    left: auto;
    right: 8%;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 12px;
  }

  .login-shell {
    border-radius: 22px;
  }

  .showcase-panel,
  .form-panel {
    padding: 18px 14px;
  }

  .liquid-layer {
    opacity: 0.5;
  }

  .orb-stage {
    min-height: 290px;
  }

  .showcase-copy h2 {
    font-size: 1.55rem;
  }

  .form-head h1 {
    font-size: 1.42rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .liquid-layer,
  .liquid-sheen,
  .bg-glow-a,
  .bg-glow-b,
  .orb-main,
  .orb-mid,
  .orb-small,
  .submit-orb {
    animation: none !important;
  }
}
</style>
