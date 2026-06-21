<template>
  <transition name="cart-slide">
    <div v-if="isCartOpen" class="cart-sidebar-wrapper">
      <div class="cart-backdrop" @click="isCartOpen = false"></div>

      <div class="cart-sidebar liquid-glass">
        <div class="cart-header">
          <div class="title-wrap">
            <h2>پیش‌فاکتور</h2>
            <span class="item-count">{{ cart.length }} مورد</span>
          </div>
          <div class="header-actions">
            <button class="open-page-btn" @click="goToCartPage">صفحه سبد</button>
            <button class="close-btn" @click="isCartOpen = false">×</button>
          </div>
        </div>

        <div class="cart-content custom-scrollbar">
          <div class="cart-items" v-if="!submitted && cart.length">
            <div v-for="item in cart" :key="item.id" class="cart-item glass-tile">
              <div class="item-visual">
                <img :src="item.image" :alt="item.name" />
              </div>
              <div class="item-details">
                <div class="item-name-row">
                  <span class="name">{{ item.name }}</span>
                  <button class="remove-mini" @click="removeFromCart(item.id)">حذف</button>
                </div>
                <div class="item-meta">
                  <span v-if="item.config?.wood">چوب: {{ item.config.wood }}</span>
                  <span v-if="item.config?.body || item.config?.body_color">بدنه: {{ item.config.body || item.config.body_color }}</span>
                  <span v-if="item.config?.['رنگ چوب']">چوب: {{ item.config['رنگ چوب'] }}</span>
                  <span v-if="item.config?.['رنگ بدنه']">بدنه: {{ item.config['رنگ بدنه'] }}</span>
                  <span v-if="item.config?.['ارتفاع']">ارتفاع: {{ item.config['ارتفاع'] }}</span>
                  <span v-if="item.config?.['ماژول']">ماژول: {{ item.config['ماژول'] }}</span>
                  <span v-if="item.config?.attributes?.['رنگ چوب']">چوب: {{ item.config.attributes['رنگ چوب'] }}</span>
                  <span v-if="item.config?.attributes?.['رنگ بدنه']">بدنه: {{ item.config.attributes['رنگ بدنه'] }}</span>
                  <span v-if="item.config?.attributes?.['ارتفاع']">ارتفاع: {{ item.config.attributes['ارتفاع'] }}</span>
                  <span v-if="item.config?.attributes?.['ماژول']">ماژول: {{ item.config.attributes['ماژول'] }}</span>
                  <span v-if="item.config?.quality">پارچه: {{ item.config.quality }} ({{ item.config.color }})</span>
                  <span v-if="item.config?.meters" class="meters">{{ item.config.meters }} متر</span>
                  <span v-if="item.parent_line_id" class="meters">برای: {{ getParentLabel(item.parent_line_id) }}</span>
                  <span v-if="item.note || item.config?.customer_note" class="note-chip">یادداشت: {{ item.note || item.config?.customer_note }}</span>
                </div>
                <div class="item-price-row">
                  <div class="item-qty-control">
                    <button class="qty-btn minus" @click="updateItemQuantity(item.id, -1)">−</button>
                    <span class="qty-value">{{ item.qty || 1 }}</span>
                    <button class="qty-btn plus" @click="updateItemQuantity(item.id, 1)">+</button>
                  </div>
                  <div class="item-price">{{ formatPrice(item.price) }} ت</div>
                </div>
              </div>
            </div>
          </div>

          <div class="cart-empty" v-else-if="!submitted">
            <div class="empty-animation">🛒</div>
            <p>سبد خرید شما در حال حاضر خالی است.</p>
            <button class="shop-now" @click="isCartOpen = false">ادامه بررسی محصولات</button>
          </div>

          <div class="cart-success" v-else>
            <div class="success-ring">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <h3>سفارش شما با موفقیت ثبت شد</h3>
            <div class="tracking-pill">کد پیگیری: {{ trackingCode }}</div>
            <p v-if="trackingCustomerName">ثبت‌شده برای مشتری: {{ trackingCustomerName }}</p>
            <p>کارشناسان دن‌روم به زودی جهت هماهنگی نهایی با شما تماس خواهند گرفت.</p>
            <button class="done-btn" @click="closeSuccess">متوجه شدم</button>
          </div>
        </div>

        <div class="cart-footer-area" v-if="cart.length && !submitted">
          <div v-if="isPortalAuthenticated" class="portal-customer-card glass-tile">
            <div class="portal-session-row">
              <span>ثبت برای مشتری:</span>
              <strong>{{ selectedPortalCustomerLabel || 'انتخاب نشده' }}</strong>
            </div>
            <label class="input-field" v-if="portalCustomers.length > 1">
              <span>مشتری</span>
              <select v-model="selectedPortalCustomer">
                <option value="" disabled>انتخاب مشتری</option>
                <option v-for="c in portalCustomers" :key="`cart-${c.name}`" :value="c.name">
                  {{ c.customer_name || c.name }}
                </option>
              </select>
            </label>
            <p class="portal-note">در حالت لاگین، درخواست مستقیماً به مشتری انتخابی لینک می‌شود.</p>
            <p class="portal-error" v-if="portalError">{{ portalError }}</p>
          </div>

          <div class="checkout-form glass-tile" v-else-if="showForm">
            <div class="input-field">
              <label>نام و نام خانوادگی</label>
              <input type="text" v-model="customer.name" placeholder="نام خود را وارد کنید" />
            </div>
            <div class="input-field">
              <label>شماره همراه</label>
              <input type="tel" v-model="customer.phone" dir="ltr" placeholder="09123456789" />
            </div>
          </div>

          <div class="payment-method-card glass-tile">
            <div class="input-field">
              <label>روش تکمیل سفارش</label>
              <select v-model="paymentMethod">
                <option value="quotation">فقط ثبت درخواست (بدون پرداخت آنلاین)</option>
                <option value="zarinpal" :disabled="!canUseZarinpal">پرداخت آنلاین با زرین‌پال</option>
              </select>
            </div>
            <p class="portal-note" v-if="paymentMethod === 'zarinpal'">
              بعد از ثبت درخواست، به درگاه امن زرین‌پال منتقل می‌شوید.
            </p>
            <p class="portal-error" v-if="paymentMethod === 'zarinpal' && !canUseZarinpal">
              برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد.
            </p>
          </div>

          <div class="summary-container">
            <div class="summary-row">
              <span class="label">جمع کل اقلام:</span>
              <span class="val">{{ formatPrice(totalPrice) }} تومان</span>
            </div>
            <div class="summary-row total">
              <span class="label">مبلغ نهایی:</span>
              <span class="val">{{ formatPrice(totalPrice) }} تومان</span>
            </div>
          </div>

          <button class="checkout-btn-liquid" :disabled="loading" @click="handleCheckout">
            <span v-if="loading">در حال ثبت...</span>
            <span v-else>{{ checkoutButtonLabel }}</span>
            <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useCart } from '../stores/cartStore'
import { usePortalStore } from '../stores/portalStore'
import { getAnalyticsSessionId, trackAnalyticsEvent } from '../utils/analyticsTracker'

const { cart, removeFromCart, updateItemQuantity, totalPrice, clearCart, isCartOpen } = useCart()
const { selectedCustomer, setSelectedCustomer } = usePortalStore()

const showForm = ref(false)
const loading = ref(false)
const submitted = ref(false)
const trackingCode = ref('')
const trackingCustomerName = ref('')
const portalSession = ref(null)
const portalError = ref('')
const selectedPortalCustomer = ref(selectedCustomer.value || '')
const paymentMethod = ref('quotation')

const customer = reactive({
  name: localStorage.getItem('customer_name') || '',
  phone: localStorage.getItem('customer_phone') || '',
  email: localStorage.getItem('customer_email') || ''
})

const isPortalAuthenticated = computed(() => !!portalSession.value?.authenticated)
const portalCustomers = computed(() => portalSession.value?.customers || [])
const canUseZarinpal = computed(() => Number(totalPrice.value || 0) > 0)

const selectedPortalCustomerLabel = computed(() => {
  const selected = portalCustomers.value.find((c) => c.name === selectedPortalCustomer.value)
  return selected?.customer_name || selected?.name || ''
})

const lineItemMap = computed(() => {
  const map = {}
  cart.value.forEach((item) => {
    if (item.line_id) map[item.line_id] = item
  })
  return map
})

const checkoutButtonLabel = computed(() => {
  if (paymentMethod.value === 'zarinpal') {
    return 'انتقال به زرین‌پال'
  }
  if (isPortalAuthenticated.value) {
    return 'ثبت درخواست برای مشتری'
  }
  return showForm.value ? 'تایید نهایی و ثبت درخواست' : 'تکمیل اطلاعات و ثبت'
})

watch(() => customer.name, (val) => localStorage.setItem('customer_name', val || ''))
watch(() => customer.phone, (val) => localStorage.setItem('customer_phone', val || ''))
watch(() => customer.email, (val) => localStorage.setItem('customer_email', val || ''))
watch(selectedPortalCustomer, (value) => {
  setSelectedCustomer(value || '')
})
watch(
  () => isCartOpen.value,
  async (open) => {
    if (open) {
      trackAnalyticsEvent('cart_open', {
        session_id: getAnalyticsSessionId(),
        cart_value: totalPrice.value || 0,
        qty: cart.value.length || 0,
        properties: { source: 'sidebar' }
      })
      await fetchPortalSession()
    }
  }
)

const formatPrice = (p) => {
  if (!p) return '۰'
  return Number(p).toLocaleString('fa-IR')
}

const getParentLabel = (parentLineId) => {
  const parent = lineItemMap.value[parentLineId]
  return parent?.name || '-'
}

const extractApiMessage = (payload, fallbackMessage) => {
  if (typeof payload?.message === 'string' && payload.message.trim()) {
    return payload.message.trim()
  }
  if (typeof payload?._server_messages === 'string') {
    try {
      const parsed = JSON.parse(payload._server_messages)
      if (Array.isArray(parsed) && parsed.length) {
        const first = parsed[0]
        if (typeof first === 'string' && first.trim()) return first.trim()
      }
    } catch (error) {
      // Keep fallback message.
    }
  }
  return fallbackMessage
}

const readCookie = (name) => {
  try {
    const key = `${name}=`
    const parts = document.cookie ? document.cookie.split('; ') : []
    const raw = parts.find((part) => part.startsWith(key))
    if (!raw) return ''
    return decodeURIComponent(raw.slice(key.length))
  } catch (error) {
    return ''
  }
}

const resolveCsrfToken = () => (
  window.csrf_token
  || readCookie('csrf_token')
  || ''
)

const ensureCsrfToken = async () => {
  const current = resolveCsrfToken()
  if (current) return current

  try {
    const customer = selectedPortalCustomer.value || selectedCustomer.value || ''
    const query = customer ? `?customer=${encodeURIComponent(customer)}` : ''
    const response = await fetch(`/api/method/mysite.portal_api.portal_session${query}`, {
      credentials: 'same-origin'
    })
    const payload = await response.json()
    const message = payload?.message || payload
    const token = (message?.csrf_token || '').toString().trim()
    if (token) {
      window.csrf_token = token
      return token
    }
  } catch (error) {
    // Ignore and let caller handle missing token.
  }

  return ''
}

const goToCartPage = () => {
  const customer = selectedPortalCustomer.value || selectedCustomer.value || ''
  const query = customer ? `?customer=${encodeURIComponent(customer)}` : ''
  isCartOpen.value = false
  window.location.href = `/cart${query}`
}

async function fetchPortalSession() {
  portalError.value = ''
  try {
    const query = selectedCustomer.value ? `?customer=${encodeURIComponent(selectedCustomer.value)}` : ''
    const response = await fetch(`/api/method/mysite.portal_api.portal_session${query}`, {
      credentials: 'same-origin'
    })
    const payload = await response.json()
    const message = payload?.message || payload
    portalSession.value = message
    if (message?.csrf_token) {
      window.csrf_token = message.csrf_token
    }

    if (message?.authenticated) {
      const valid = (message.customers || []).some((c) => c.name === selectedPortalCustomer.value)
      if (!valid) {
        selectedPortalCustomer.value = message.selected_customer || message.default_customer || message.customers?.[0]?.name || ''
      }
    }
  } catch (error) {
    portalSession.value = null
  }
}

const startPortalZarinpal = async () => {
  if (portalCustomers.value.length > 1 && !selectedPortalCustomer.value) {
    portalError.value = 'لطفاً مشتری را انتخاب کنید.'
    return
  }
  if (!canUseZarinpal.value) {
    portalError.value = 'برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد.'
    return
  }

  loading.value = true
  portalError.value = ''
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      portalError.value = 'توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید.'
      return
    }

    const response = await fetch('/api/method/mysite.zarinpal_api.start_portal_checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        csrf_token: csrfToken,
        customer: selectedPortalCustomer.value || undefined,
        items: cart.value
      })
    })

    const result = await response.json()
    const message = result?.message || result
    if (message?.status === 'success' && message?.payment_url) {
      trackingCode.value = message.quotation_request || ''
      trackAnalyticsEvent('order_submit', {
        session_id: getAnalyticsSessionId(),
        model_name: cart.value.find((item) => (item.type || '').toLowerCase() !== 'fabric')?.name || '',
        qty: cart.value.reduce((sum, item) => sum + Number(item.qty || 1), 0),
        amount: totalPrice.value || 0,
        cart_value: totalPrice.value || 0,
        properties: {
          source: 'sidebar_portal_zarinpal_init',
          tracking_code: message.quotation_request || ''
        }
      })
      window.location.href = message.payment_url
      return
    }
    portalError.value = extractApiMessage(result, 'اتصال به زرین‌پال انجام نشد. دوباره تلاش کنید.')
  } catch (error) {
    portalError.value = 'خطا در ارتباط با سرور.'
  } finally {
    loading.value = false
  }
}

const startGuestZarinpal = async () => {
  if (!customer.name || !customer.phone) {
    alert('برای پرداخت آنلاین، نام و شماره همراه الزامی است')
    return
  }
  if (!canUseZarinpal.value) {
    alert('برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد')
    return
  }

  loading.value = true
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      alert('توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید')
      return
    }

    const response = await fetch('/api/method/mysite.zarinpal_api.start_guest_checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        csrf_token: csrfToken,
        customer_info: customer,
        items: cart.value
      })
    })

    const result = await response.json()
    const message = result?.message || result
    if (message?.status === 'success' && message?.payment_url) {
      trackingCode.value = message.quotation_request || ''
      trackAnalyticsEvent('order_submit', {
        session_id: getAnalyticsSessionId(),
        model_name: cart.value.find((item) => (item.type || '').toLowerCase() !== 'fabric')?.name || '',
        qty: cart.value.reduce((sum, item) => sum + Number(item.qty || 1), 0),
        amount: totalPrice.value || 0,
        cart_value: totalPrice.value || 0,
        properties: {
          source: 'sidebar_guest_zarinpal_init',
          tracking_code: message.quotation_request || ''
        }
      })
      window.location.href = message.payment_url
      return
    }
    alert(extractApiMessage(result, 'اتصال به زرین‌پال انجام نشد. دوباره تلاش کنید.'))
  } catch (error) {
    console.error(error)
    alert('خطا در ارتباط با سرور')
  } finally {
    loading.value = false
  }
}

const handleCheckout = async () => {
  const nonFabricItems = cart.value.filter((item) => (item.type || '').toLowerCase() !== 'fabric')
  const modelName = nonFabricItems[0]?.name || ''
  trackAnalyticsEvent('checkout_start', {
    session_id: getAnalyticsSessionId(),
    model_name: modelName,
    qty: nonFabricItems.reduce((sum, item) => sum + Number(item.qty || 1), 0),
    cart_value: totalPrice.value || 0,
    amount: totalPrice.value || 0,
    properties: {
      source: 'sidebar',
      items_count: nonFabricItems.length
    }
  })

  if (isPortalAuthenticated.value) {
    if (portalCustomers.value.length > 1 && !selectedPortalCustomer.value) {
      portalError.value = 'لطفاً مشتری را انتخاب کنید.'
      return
    }
    if (paymentMethod.value === 'zarinpal') {
      await startPortalZarinpal()
      return
    }
    await submitPortalQuotation()
    return
  }

  if (paymentMethod.value === 'zarinpal') {
    if (!showForm.value) {
      showForm.value = true
      return
    }
    await startGuestZarinpal()
    return
  }

  if (!showForm.value) {
    showForm.value = true
    return
  }

  if (!customer.name || !customer.phone) {
    alert('لطفاً مشخصات خود را کامل وارد کنید')
    return
  }

  await submitGuestQuotation()
}

const submitPortalQuotation = async () => {
  loading.value = true
  portalError.value = ''
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      portalError.value = 'توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید.'
      return
    }

    const response = await fetch('/api/method/mysite.portal_api.portal_submit_quotation_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        csrf_token: csrfToken,
        customer: selectedPortalCustomer.value || undefined,
        items: cart.value
      })
    })

    const result = await response.json()
    if (result.message?.status === 'success') {
      trackingCode.value = result.message.name
      trackingCustomerName.value = result.message.customer_name || ''
      trackAnalyticsEvent('order_submit', {
        session_id: getAnalyticsSessionId(),
        model_name: cart.value.find((item) => (item.type || '').toLowerCase() !== 'fabric')?.name || '',
        qty: cart.value.reduce((sum, item) => sum + Number(item.qty || 1), 0),
        amount: totalPrice.value || 0,
        cart_value: totalPrice.value || 0,
        properties: {
          source: 'sidebar_portal',
          tracking_code: result.message.name || ''
        }
      })
      submitted.value = true
      clearCart()
    } else {
      portalError.value = extractApiMessage(result, 'خطا در ثبت درخواست. لطفاً دوباره تلاش کنید.')
    }
  } catch (error) {
    portalError.value = 'خطا در ارتباط با سرور.'
  } finally {
    loading.value = false
  }
}

const submitGuestQuotation = async () => {
  loading.value = true
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      alert('توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید')
      return
    }

    const response = await fetch('/api/method/mysite.www.mysite.product.submit_quotation_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken
      },
      body: JSON.stringify({
        csrf_token: csrfToken,
        customer_info: customer,
        items: cart.value
      })
    })

    const result = await response.json()
    if (result.message?.status === 'success') {
      trackingCode.value = result.message.name
      trackingCustomerName.value = result.message.customer || customer.name || ''
      trackAnalyticsEvent('order_submit', {
        session_id: getAnalyticsSessionId(),
        model_name: cart.value.find((item) => (item.type || '').toLowerCase() !== 'fabric')?.name || '',
        qty: cart.value.reduce((sum, item) => sum + Number(item.qty || 1), 0),
        amount: totalPrice.value || 0,
        cart_value: totalPrice.value || 0,
        properties: {
          source: 'sidebar_guest',
          tracking_code: result.message.name || ''
        }
      })
      submitted.value = true
      clearCart()
    } else {
      alert('خطا در ثبت درخواست. لطفاً دوباره تلاش کنید.')
    }
  } catch (error) {
    console.error(error)
    alert('خطا در ارتباط با سرور')
  } finally {
    loading.value = false
  }
}

const closeSuccess = () => {
  submitted.value = false
  showForm.value = false
  trackingCode.value = ''
  trackingCustomerName.value = ''
  isCartOpen.value = false
}

onMounted(fetchPortalSession)
</script>

<style scoped>
.cart-sidebar-wrapper {
  position: fixed; inset: 0; z-index: 2000;
  display: flex; justify-content: flex-end;
}

.cart-backdrop {
  position: absolute; inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
}

.cart-sidebar {
  width: 100%; max-width: 440px; height: 100%;
  position: relative; z-index: 10;
  background: var(--bg-secondary) !important;
  backdrop-filter: blur(40px) saturate(180%) !important;
  border-left: 1px solid var(--glass-border);
  display: flex; flex-direction: column;
  padding: 0;
  box-shadow: -20px 0 100px rgba(0,0,0,0.4);
}

.cart-header {
  padding: 40px 24px 30px;
  display: flex; justify-content: space-between; align-items: center;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.title-wrap h2 { font-size: 26px; font-weight: 800; color: var(--text-main); margin: 0; }
.item-count { font-size: 13px; font-weight: 600; color: var(--text-dim); margin-top: 4px; display: block; }
.open-page-btn {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-main);
  border-radius: 12px;
  height: 40px;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}
.open-page-btn:hover {
  transform: translateY(-1px);
  background: var(--glass-bg-hover);
}
.close-btn {
  width: 44px; height: 44px; border-radius: 12px; border: 1px solid var(--glass-border);
  background: var(--glass-bg); color: var(--text-main); font-size: 24px; cursor: pointer; transition: 0.3s;
}
.close-btn:hover { background: var(--glass-bg-hover); transform: rotate(90deg); }

.cart-content { flex: 1; overflow-y: auto; padding: 0 24px; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }

.cart-items { display: flex; flex-direction: column; gap: 16px; padding-bottom: 40px; }
.glass-tile {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.cart-item { display: flex; gap: 20px; position: relative; }
.item-visual { position: relative; width: 80px; height: 80px; flex-shrink: 0; }
.item-visual img { width: 100%; height: 100%; object-fit: contain; background: var(--glass-bg); border-radius: 16px; padding: 5px; }
.item-price-row { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.item-qty-control { display: flex; align-items: center; gap: 0; background: var(--glass-bg); border-radius: 12px; overflow: hidden; }
.qty-btn { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: none; border: none; font-size: 18px; font-weight: 700; color: var(--text-main); cursor: pointer; transition: background 0.15s; }
.qty-btn:hover { background: rgba(0,0,0,0.06); }
.qty-btn:active { background: rgba(0,0,0,0.1); }
.qty-btn.minus { padding-right: 2px; }
.qty-btn.plus { padding-left: 2px; }
.qty-value { min-width: 28px; text-align: center; font-size: 14px; font-weight: 800; color: var(--text-main); }

.item-details { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.item-name-row { display: flex; justify-content: space-between; align-items: flex-start; }
.item-name-row .name { font-size: 16px; font-weight: 700; color: var(--text-main); }
.remove-mini { background: none; border: none; color: var(--text-dim); font-size: 11px; font-weight: 600; cursor: pointer; text-decoration: underline; }

.item-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; font-weight: 500; color: var(--text-muted); }
.item-meta .meters { color: var(--text-main); border-right: 1px solid var(--glass-border); padding-right: 8px; }
.item-meta .note-chip {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  padding: 2px 8px;
}
.item-price { font-size: 15px; font-weight: 800; color: var(--accent-orange); margin-top: 4px; }

.cart-empty { text-align: center; padding-top: 100px; }
.empty-animation { font-size: 64px; margin-bottom: 24px; opacity: 0.1; }
.shop-now {
  margin-top: 24px; background: var(--text-main); color: var(--bg-main); border: none;
  padding: 14px 28px; border-radius: 16px; font-weight: 800; cursor: pointer;
}

.cart-success { text-align: center; padding: 60px 20px; color: var(--text-main); }
.success-ring {
  width: 70px; height: 70px; border-radius: 50%; background: #4caf50;
  color: white; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 30px; box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
}
.tracking-pill {
  display: inline-block; background: var(--glass-bg);
  padding: 8px 16px; border-radius: 100px; font-weight: 800; margin: 20px 0; color: var(--accent-orange);
}
.done-btn { width: 100%; margin-top: 30px; background: var(--text-main); color: var(--bg-main); border: none; padding: 18px; border-radius: 20px; font-weight: 800; cursor: pointer; }

.cart-footer-area { padding: 24px; border-top: 1px solid var(--glass-border); }
.checkout-form { margin-bottom: 24px; display: flex; flex-direction: column; gap: 16px; }
.input-field label,
.input-field span {
  font-size: 12px; font-weight: 700; color: var(--text-dim); margin-bottom: 6px; display: block;
}
.input-field input,
.input-field select {
  width: 100%; padding: 14px; border-radius: 16px; border: 1px solid var(--glass-border);
  background: var(--glass-bg); color: var(--text-main); font-weight: 600; outline: none; transition: 0.3s; font-family: inherit;
}
.input-field input:focus,
.input-field select:focus { border-color: var(--accent-gold); background: var(--glass-bg-hover); }

.portal-customer-card { margin-bottom: 16px; }
.payment-method-card { margin-bottom: 16px; }
.portal-session-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
  margin-bottom: 12px;
  color: var(--text-muted);
}
.portal-session-row strong { color: var(--text-main); }
.portal-note { margin: 10px 0 0; font-size: 12px; color: var(--text-muted); }
.portal-error { margin: 10px 0 0; font-size: 12px; color: #ffc3c3; }

.summary-container { margin-bottom: 24px; }
.summary-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; font-weight: 600; color: var(--text-muted); }
.summary-row.total { border-top: 1px solid var(--glass-border); padding-top: 16px; color: var(--text-main); }
.summary-row.total .val { font-size: 20px; font-weight: 900; color: var(--accent-orange); }

.checkout-btn-liquid {
  width: 100%; background: linear-gradient(135deg, #ff9800, #f44336); color: white; border: none;
  padding: 18px; border-radius: 20px; font-size: 1.1rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center; gap: 12px;
  cursor: pointer; box-shadow: 0 10px 30px rgba(244, 67, 54, 0.3); transition: 0.3s;
}
.checkout-btn-liquid:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 15px 40px rgba(244, 67, 54, 0.4); }
.checkout-btn-liquid:disabled { opacity: 0.5; filter: grayscale(1); }

.cart-slide-enter-active, .cart-slide-leave-active { transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
.cart-slide-enter-from, .cart-slide-leave-to { transform: translateX(100%); opacity: 0; }
</style>
