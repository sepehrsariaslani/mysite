<template>
  <Transition name="fade-overlay">
    <div v-if="isOpen" class="mobile-menu-overlay" @click.self="close">
      <!-- Blurred Backdrop with subtle texture -->
      <div class="menu-texture"></div>
      
      <div class="menu-content" :class="{ 'content-visible': isVisible }">
        <!-- Close Button -->
        <button class="close-btn" @click="close">
          <i class="pi pi-times"></i>
        </button>

        <!-- Profile / Header Section -->
        <div class="profile-section">
          <div class="user-avatar" v-if="user">
            <img :src="user.avatar || '/assets/mysite/images/default-avatar.png'" alt="Avatar" />
          </div>
          <div class="user-avatar-placeholder" v-else>
            <i class="pi pi-user"></i>
          </div>
          <div class="user-info">
            <h3>{{ user ? `Hi, ${user.first_name}` : 'Welcome Guest' }}</h3>
            <p>{{ user ? 'Manage your account' : 'Sign in for better experience' }}</p>
          </div>
        </div>

        <!-- Navigation Links -->
        <nav class="menu-nav">
          <ul class="menu-list">
            <li v-for="(item, index) in menuItems" 
                :key="item.label" 
                :style="{ animationDelay: `${index * 0.1}s` }"
                class="menu-item">
              <a :href="item.path" @click="close">
                <div class="item-icon">
                  <i :class="item.icon"></i>
                </div>
                <span class="item-label">{{ item.label }}</span>
                <i class="pi pi-chevron-right arrow-icon"></i>
              </a>
            </li>
          </ul>
        </nav>

        <!-- Bottom Actions -->
        <div class="menu-footer">
          <div class="social-links">
            <a href="#"><i class="pi pi-instagram"></i></a>
            <a href="#"><i class="pi pi-whatsapp"></i></a>
            <a href="#"><i class="pi pi-telegram"></i></a>
          </div>
          <div class="auth-action" v-if="!user">
            <a href="/login" class="login-btn" @click="close">ورود / ثبت‌نام</a>
          </div>
          <div class="auth-action" v-else>
            <button class="logout-btn" @click="logout">Logout</button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const isVisible = ref(false);
const user = ref(null); // Mock user or fetch from auth store

const menuItems = [
  { label: 'خانه', path: '/mysite', icon: 'pi pi-home' },
  { label: 'دسته‌بندی‌ها', path: '/categories', icon: 'pi pi-th-large' },
  { label: 'مبلمان', path: '/sofas', icon: 'pi pi-box' },
  { label: 'صندلی اپن', path: '/barstools', icon: 'pi pi-chart-bar' },
  { label: 'سرویس خواب', path: '/beds', icon: 'pi pi-bed' },
  { label: 'مشاوره', path: '/consultation', icon: 'pi pi-comments' },
  { label: 'بلاگ', path: '/blog', icon: 'pi pi-book' }
];

watch(() => props.isOpen, (val) => {
  if (val) {
    setTimeout(() => { isVisible.ref = true; }, 50);
  } else {
    isVisible.ref = false;
  }
});

const close = () => {
  isVisible.value = false;
  setTimeout(() => emit('close'), 300);
};

const logout = () => {
  // logout logic
  close();
};
</script>

<style scoped>
.mobile-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: var(--glass-bg);
  backdrop-filter: blur(25px) saturate(180%);
  display: flex;
  justify-content: flex-end;
}

.menu-texture {
  position: absolute;
  inset: 0;
  background-image: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
  opacity: 0.05;
  pointer-events: none;
}

.menu-content {
  width: 85%;
  max-width: 400px;
  height: 100%;
  background: var(--bg-secondary);
  border-left: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  padding: 40px 24px;
  transform: translateX(100%);
  transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  position: relative;
}

.content-visible {
  transform: translateX(0);
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 48px;
  margin-top: 20px;
}

.user-avatar, .user-avatar-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar-placeholder i {
  font-size: 24px;
  color: var(--text-muted);
}

.user-info h3 {
  color: var(--text-main);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.user-info p {
  color: var(--text-dim);
  margin: 4px 0 0;
  font-size: 0.85rem;
}

.menu-nav {
  flex: 1;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin-bottom: 12px;
  opacity: 0;
  transform: translateY(20px);
  animation: slideIn 0.5s forwards ease;
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item a {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  color: var(--text-main);
  text-decoration: none;
  transition: all 0.3s ease;
}

.menu-item a:active {
  background: var(--glass-bg-hover);
  transform: scale(0.98);
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--glass-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-orange); /* Primary brand color */
}

.item-label {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
}

.arrow-icon {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.menu-footer {
  margin-top: auto;
  border-top: 1px solid var(--glass-border);
  padding-top: 24px;
}

.social-links {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}

.social-links a {
  color: var(--text-muted);
  font-size: 1.5rem;
  transition: color 0.3s;
}

.login-btn {
  display: block;
  width: 100%;
  padding: 16px;
  background: var(--accent-brown);
  border: none;
  border-radius: 16px;
  color: var(--accent-gold);
  text-align: center;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(80, 49, 48, 0.2);
}

.logout-btn {
  width: 100%;
  padding: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  color: var(--text-muted);
  font-weight: 600;
  cursor: pointer;
}

/* Transitions */
.fade-overlay-enter-active,
.fade-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.fade-overlay-enter-from,
.fade-overlay-leave-to {
  opacity: 0;
}
</style>
