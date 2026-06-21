<template>
  <div id="loading-screen"></div>

  <div id="app" class="h-full" data-v-app="">
    <div class="app-layout">

      <!-- ===== HEADER ===== -->
      <header class="app-header scrolled" dir="rtl">
        <div class="header-surface"></div>
        <div class="header-inner">

          <a href="/mysite" class="logo">
            <span class="logo-den">DEN</span>
            <span class="logo-room">ROOM</span>
          </a>

          <nav class="desktop-nav" aria-label="ناوبری اصلی">
            <div class="menu-wrap">
              <button class="menu-trigger active" type="button">
                محصولات
                <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <div class="menu-wrap">
              <button class="menu-trigger" type="button">
                الهام و محتوا
                <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <div class="menu-wrap">
              <button class="menu-trigger" type="button">
                خدمات
                <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <a class="quick-pill" href="/categories">همه دسته‌بندی‌ها</a>
          </nav>

          <div class="header-actions">
            <button class="action-btn" aria-label="جستجو">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>
            <button class="action-btn" aria-label="تم تاریک">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"></path>
              </svg>
            </button>
            <button class="cart-pill" aria-label="سبد خرید">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4H6z"></path>
                <path d="M3 6h18"></path>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
              <span>سبد</span>
            </button>
            <button class="hamburger" aria-label="منو">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>

        <div class="mobile-overlay"></div>

        <aside class="mobile-sheet" dir="rtl">
          <div class="sheet-head">
            <a href="/mysite" class="sheet-logo">DENROOM</a>
            <button class="sheet-close" aria-label="بستن">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <section class="sheet-section">
            <h5>دسته‌بندی محصولات</h5>
            <div class="sheet-grid">
              <a href="/sofas" class="sheet-grid-item"><strong>مبلمان</strong><small>کاناپه و مبل ماژولار</small></a>
              <a href="/barstools" class="sheet-grid-item"><strong>صندلی اپن</strong><small>کانتر و بار</small></a>
              <a href="/dining-chairs" class="sheet-grid-item"><strong>صندلی ناهارخوری</strong><small>صندلی‌های ناهارخوری</small></a>
              <a href="/tables" class="sheet-grid-item"><strong>میز ناهارخوری</strong><small>میزهای ناهارخوری</small></a>
              <a href="/coffee-tables" class="sheet-grid-item"><strong>میز جلو مبلی</strong><small>میز جلو مبلی و عسلی</small></a>
              <a href="/benches" class="sheet-grid-item"><strong>نیمکت</strong><small>مجموعه نیمکت</small></a>
              <a href="/beds" class="sheet-grid-item"><strong>تخت خواب</strong><small>سرویس خواب</small></a>
              <a href="/cushions" class="sheet-grid-item"><strong>کوسن و تکیه‌گاه</strong><small>متعلقات جانبی</small></a>
              <a href="/products-print" class="sheet-grid-item"><strong>کاتالوگ چاپی</strong><small>لیست کامل برای چاپ</small></a>
            </div>
          </section>

          <section class="sheet-section">
            <h5>الهام و محتوا</h5>
            <nav class="sheet-links">
              <a href="/shop-by-look"><strong>Shop by Look</strong><small>خرید تماشایی</small></a>
              <a href="/projects"><strong>پروژه‌ها</strong><small>خانه رستوران‌های کافه</small></a>
              <a href="/gallery"><strong>گالری</strong><small>تصاویر الهام‌بخش</small></a>
              <a href="/blog"><strong>بلاگ</strong><small>راهنمای چیدمان و دکوراسیون</small></a>
              <a href="/special-edition"><strong>Special Edition</strong><small>نسخه‌های محدود</small></a>
              <a href="/outlet"><strong>Outlet</strong><small>قیمت‌های ویژه</small></a>
              <a href="/faq"><strong>سوالات متداول</strong><small>پاسخ سریع</small></a>
            </nav>
          </section>

          <section class="sheet-section">
            <h5>خدمات</h5>
            <nav class="sheet-links">
              <a href="/consultation"><strong>مشاوره</strong><small>مشاوره انتخاب محصول</small></a>
              <a href="/about"><strong>درباره ما</strong><small>ماموریت، ارزش‌ها و تاریخچه</small></a>
              <a href="/dashboard"><strong>مدیریت حساب</strong><small>پنل حساب</small></a>
              <a href="/saved"><strong>ذخیره‌شده‌ها</strong><small>لیست علاقه‌مندی</small></a>
              <a href="/login"><strong>ورود</strong><small>حساب کاربری</small></a>
            </nav>
          </section>
        </aside>
      </header>

      <!-- ===== MAIN ===== -->
      <main class="app-main">
        <div class="downloads-page page" dir="rtl">
          <div class="coming-soon-wrapper">
            <div class="cs-content">
              <span class="cs-badge">به زودی</span>
              <h1>کاتالوگ‌های دیجیتال</h1>
              <p>مجموعه کاتالوگ‌های جامع محصولات دن‌روم به زودی در دسترس خواهند بود.</p>

              <div class="catalogs-grid">
                <div
                  v-for="catalog in catalogs"
                  :key="catalog.name"
                  class="catalog-card"
                  :class="catalog.className"
                >
                  <div class="catalog-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                  </div>
                  <h3>{{ catalog.name }}</h3>
                  <button class="dl-btn" disabled>دانلود — به زودی</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Support FAB removed -->

      <!-- ===== MOBILE BOTTOM NAV ===== -->
      <nav class="mobile-bottom-nav" dir="rtl" aria-label="ناوبری موبایل">
        <div class="nav-glass"></div>
        <div class="nav-shimmer"></div>
        <div class="nav-container">
          <a href="/dashboard" class="nav-item">
            <div class="icon-wrap">
              <span class="icon-svg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <circle cx="12" cy="8" r="4"></circle>
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"></path>
                </svg>
              </span>
              <span class="icon-ripple"></span>
            </div>
            <span class="item-label">مدیریت</span>
          </a>
          <a href="/shop-by-look" class="nav-item">
            <div class="icon-wrap">
              <span class="icon-svg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <rect x="3" y="3" width="7" height="9" rx="1.5"></rect>
                  <rect x="14" y="3" width="7" height="5" rx="1.5"></rect>
                  <rect x="14" y="12" width="7" height="9" rx="1.5"></rect>
                  <rect x="3" y="16" width="7" height="5" rx="1.5"></rect>
                </svg>
              </span>
              <span class="icon-ripple"></span>
            </div>
            <span class="item-label">Shop by Look</span>
          </a>
          <a href="/categories" class="nav-item nav-center">
            <div class="center-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                <rect width="7" height="7" x="3" y="3" rx="1.5"></rect>
                <rect width="7" height="7" x="14" y="3" rx="1.5"></rect>
                <rect width="7" height="7" x="14" y="14" rx="1.5"></rect>
                <rect width="7" height="7" x="3" y="14" rx="1.5"></rect>
              </svg>
            </div>
            <span class="item-label center-label">محصولات</span>
          </a>
          <button class="nav-item">
            <div class="icon-wrap">
              <span class="icon-svg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <circle cx="8" cy="21" r="1"></circle>
                  <circle cx="19" cy="21" r="1"></circle>
                  <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path>
                </svg>
              </span>
              <span class="icon-ripple"></span>
            </div>
            <span class="item-label">سبد</span>
          </button>
          <a href="/mysite" class="nav-item">
            <div class="icon-wrap">
              <span class="icon-svg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
              </span>
              <span class="icon-ripple"></span>
            </div>
            <span class="item-label">خانه</span>
          </a>
        </div>
      </nav>

      <!-- ===== FOOTER ===== -->
      <footer class="app-footer">
        <div class="footer-glass-wrap">
          <div class="footer-inner">
            <div class="footer-brand">
              <a href="/categories" class="footer-logo">
                <span class="logo-den">DEN</span>
                <span class="logo-room">ROOM</span>
              </a>
              <p class="footer-desc">دن‌روم به معنای خلوتگاه است. ما در دن در تلاش هستیم تا خانه‌های برای شما طراحی کنیم که مدرن‌ترین ایده‌ها را با اصالت طراحی ایرانی در هم آمیزد.</p>
              <div class="footer-socials">
                <a href="#" class="social-glass-btn" aria-label="Instagram">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"></path>
                  </svg>
                </a>
                <a href="#" class="social-glass-btn" aria-label="Telegram">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"></path>
                  </svg>
                </a>
                <a href="#" class="social-glass-btn" aria-label="WhatsApp">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"></path>
                  </svg>
                </a>
              </div>
            </div>

            <div class="footer-cols">
              <div class="footer-col">
                <h4>محصولات</h4>
                <a href="/sofas">مبلمان مدرن</a>
                <a href="/barstools">صندلی اپن</a>
                <a href="/tables">میز ناهارخوری</a>
                <a href="/coffee-tables">میز جلو مبلی و جانبی</a>
              </div>
              <div class="footer-col">
                <h4>خدمات مشتریان</h4>
                <a href="#">پشتیبانی آنلاین</a>
                <a href="/faq">سوالات متداول</a>
                <a href="#">گارانتی و ضمانت</a>
                <a href="#">پیگیری سفارش</a>
              </div>
              <div class="footer-col">
                <h4>درباره ما</h4>
                <a href="#">داستان دن‌روم</a>
                <a href="/dealers">نمایندگی‌ها</a>
                <a href="/cooperation">همکاری با ما</a>
                <a href="/blog">بلاگ</a>
              </div>
            </div>
          </div>

          <div class="footer-bottom">
            <div class="bottom-inner">
              <div class="subscribe-glass">
                <input type="email" placeholder="ایمیل خود را وارد کنید...">
                <button>تایید</button>
              </div>
              <div class="copyright-text">© ۲۰۲۴ دن‌روم. تمامی حقوق محفوظ است. طراحی شده توسط نبوغ و هوش مصنوعی :)</div>
            </div>
          </div>
        </div>
      </footer>

    </div>
  </div>
</template>

<script setup>
const catalogs = [
  { name: 'کاتالوگ جامع ۱۴۰۳', className: 'catalog-card--primary' },
  { name: 'راهنمای چیدمان', className: 'catalog-card--secondary' },
  { name: 'کاتالوگ صندلی اپن', className: 'catalog-card--tertiary' },
]
</script>

<style scoped>
.downloads-page {
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
  font-family: 'Peyda', sans-serif;
}

.coming-soon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 120px 40px;
}

.cs-content {
  max-width: 1000px;
  width: 100%;
  text-align: center;
}

.cs-badge {
  display: inline-block;
  margin-bottom: 32px;
  padding: 10px 32px;
  border: 1px solid rgba(255, 152, 0, 0.2);
  border-radius: 50px;
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
  font-size: 0.95rem;
  font-weight: 800;
}

.cs-content h1 {
  margin-bottom: 24px;
  color: #fff;
  font-size: clamp(2rem, 5vw, 3.8rem);
  font-weight: 1000;
  letter-spacing: -1px;
}

.cs-content p {
  margin: 0 auto 80px;
  max-width: 600px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.25rem;
  font-weight: 500;
  line-height: 1.8;
}

.catalogs-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.catalog-card {
  padding: 60px 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 48px;
  background: rgba(255, 255, 255, 0.03);
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(40px);
  transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1);
}

.catalog-card:hover {
  transform: translateY(-15px);
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
}

.catalog-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 90px;
  height: 90px;
  margin: 0 auto 30px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.05);
  color: #ff9800;
  transition: 0.4s;
}

.catalog-card:hover .catalog-icon {
  transform: scale(1.1) rotate(10deg);
  background: #ff9800;
  color: #fff;
}

.catalog-icon svg {
  width: 40px;
  height: 40px;
}

.catalog-card h3 {
  margin-bottom: 24px;
  color: #fff;
  font-size: 1.4rem;
  font-weight: 900;
}

.dl-btn {
  width: 100%;
  padding: 16px 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
  font-weight: 800;
  cursor: not-allowed;
  transition: 0.3s;
}

.catalog-card--primary { background-color: rgba(17, 17, 17, 0.67); }
.catalog-card--secondary { background-color: rgba(0, 0, 0, 0.66); }
.catalog-card--tertiary { background-color: rgba(17, 17, 17, 0.47); }

@media (max-width: 900px) {
  .catalogs-grid {
    grid-template-columns: 1fr;
    max-width: 400px;
    margin: 0 auto;
  }
}
</style>
