<template>
  <footer class="admin-footer" dir="rtl">
    <div class="admin-footer-inner">
      <p>پنل مدیریت مای‌سایت - دسترسی فقط برای نقش‌های مجاز</p>
      <div class="links">
        <a href="/management">مدیریت سیستم</a>
        <a href="/management-products">مدیریت محصولات</a>
        <a href="/management-blog">مدیریت بلاگ</a>
        <a href="/management-support">مدیریت پشتیبانی</a>
        <a href="/management-analytics">آنالیتیکس مدیریت</a>
        <a href="/mysite">صفحه اصلی سایت</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.admin-footer {
  margin-top: 30px;
  border-top: 1px solid var(--admin-border);
  background: color-mix(in srgb, var(--admin-panel-bg) 84%, transparent);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.admin-footer-inner {
  width: min(1400px, 100%);
  margin: 0 auto;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.admin-footer p {
  margin: 0;
  color: var(--admin-text-soft);
  font-size: 0.78rem;
}

.links {
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
}

.links a {
  text-decoration: none;
  color: var(--text-main);
  font-size: 0.76rem;
  border-bottom: 1px dashed color-mix(in srgb, var(--admin-border) 75%, transparent);
}

.links a:hover {
  color: var(--admin-tab-active-start);
}

@media (max-width: 980px) {
  .admin-footer-inner {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 12px;
  }
}
</style>
