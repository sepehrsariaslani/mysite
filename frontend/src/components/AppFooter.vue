<template>
  <footer class="app-footer">
    <div class="footer-glass-wrap">
      <div class="footer-inner">
        <!-- Brand column -->
        <div class="footer-brand">
          <a href="/categories" class="footer-logo">
            <span class="logo-den">DEN</span><span class="logo-room">ROOM</span>
          </a>
          <p class="footer-desc">
            دن، به معنای خلوتگاه است. ما در دن در تلاش هستیم تا خانه‌ای برای شما طراحی کنیم که مدرن‌ترین ایده‌ها را با اصالت طرح‌های ایرانی در هم آمیزد.
          </p>
          <div class="footer-socials">
            <a href="#" class="social-glass-btn" aria-label="Instagram">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
            </a>
            <a href="#" class="social-glass-btn" aria-label="Telegram">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
            </a>
            <a href="#" class="social-glass-btn" aria-label="WhatsApp">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            </a>
          </div>
        </div>

        <!-- Links columns -->
        <div class="footer-cols">
          <div class="footer-col" v-for="col in footerLinks" :key="col.title">
            <h4>{{ col.title }}</h4>
            <a v-for="link in col.links" :key="link.text" :href="link.url">{{ link.text }}</a>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="footer-bottom">
        <div class="bottom-inner">
          <div class="subscribe-glass">
            <input type="email" placeholder="عضویت در خبرنامه..." />
            <button>تایید</button>
          </div>
          <div class="copyright-text">© ۲۰۲۴ دن‌روم. تمامی حقوق محفوظ است. طراحی شده توسط نبوغ و هوش مصنوعی :)</div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const footerLinks = [
  {
    title: 'محصولات',
    links: [
      { text: 'مبلمان مدرن', url: '/sofas' },
      { text: 'صندلی اپن', url: '/barstools' },
      { text: 'میز ناهارخوری', url: '/tables' },
      { text: 'میز جلومبلی و عسلی', url: '/coffee-tables' }
    ]
  },
  {
    title: 'خدمات مشتریان',
    links: [
      { text: 'پشتیبانی آنلاین', url: '#' },
      { text: 'سوالات متداول', url: '/faq' },
      { text: 'گارانتی و ضمانت', url: '#' },
      { text: 'پیگیری سفارش', url: '#' }
    ]
  },
  {
    title: 'درباره ما',
    links: [
      { text: 'داستان دن‌روم', url: '#' },
      { text: 'شعب و نمایندگی‌ها', url: '/dealers' },
      { text: 'همکاری با ما', url: '/cooperation' },
      { text: 'بلاگ', url: '/blog' }
    ]
  }
]
</script>

<style scoped>
.app-footer {
  position: relative;
  background: var(--bg-main);
  z-index: 20; /* Ensure it covers fixed gallery on mobile */
}

@media (max-width: 1024px) {
  .app-footer {
    margin-top: 0;
  }
}

.footer-glass-wrap {
  background: var(--bg-footer);
  backdrop-filter: blur(20px);
  color: var(--text-muted);
  padding: 80px 0 0;
  border-top: 1px solid var(--glass-border);
}

.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px 60px;
  display: flex;
  justify-content: space-between;
  gap: 60px;
  direction: rtl;
}

.footer-brand {
  flex: 0 0 320px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.footer-logo {
  font-size: 32px;
  font-weight: 1000;
  letter-spacing: 2px;
  text-decoration: none;
}
.logo-den { color: var(--text-main); }
.logo-room { color: var(--accent-gold); }

.footer-desc {
  font-size: 14px;
  line-height: 2;
  color: var(--text-dim);
  text-align: justify;
}

.footer-socials { display: flex; gap: 16px; }
.social-glass-btn {
  width: 44px; height: 44px;
  border-radius: 14px;
  background: var(--glass-bg);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-main);
  transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid var(--glass-border);
}
.social-glass-btn:hover {
  background: var(--accent-gold);
  color: var(--accent-brown);
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(242, 201, 126, 0.2);
}
.social-glass-btn svg { width: 20px; height: 20px; }

.footer-cols {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  gap: 80px;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-col h4 {
  font-size: 16px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 8px 0;
  position: relative;
}
.footer-col h4::after {
  content: '';
  position: absolute; bottom: -8px; right: 0;
  width: 24px; height: 2px; background: var(--accent-gold);
}

.footer-col a {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s;
}
.footer-col a:hover { color: var(--accent-gold); padding-right: 5px; }

.footer-bottom {
  background: rgba(0, 0, 0, 0.05);
  padding: 30px 0;
  direction: rtl;
}

.bottom-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subscribe-glass {
  display: flex;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  padding: 6px;
  border-radius: 16px;
  width: 320px;
}
.subscribe-glass input {
  flex: 1;
  background: none; border: none;
  padding: 10px 16px; color: var(--text-main);
  font-family: inherit; font-size: 14px;
}
.subscribe-glass input::placeholder { color: rgba(255,255,255,0.3); }
.subscribe-glass button {
  background: var(--accent-gold);
  color: var(--accent-brown);
  border: none;
  padding: 10px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.3s;
}
.subscribe-glass button:hover { background: var(--text-main); color: var(--bg-main); }

.copyright-text {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

@media (max-width: 1000px) {
  .footer-inner { flex-direction: column; align-items: center; text-align: center; }
  .footer-brand { align-items: center; margin-bottom: 40px; }
  .footer-desc { text-align: center; }
  .footer-cols { width: 100%; justify-content: center; gap: 40px; }
  .footer-col h4::after { left: 50%; transform: translateX(-50%); right: auto; }
  .bottom-inner { flex-direction: column-reverse; gap: 30px; }
}

@media (max-width: 600px) {
  .footer-cols { flex-direction: column; gap: 30px; }
  .subscribe-glass { width: 100%; }
}
</style>
