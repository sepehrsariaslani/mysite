<template>
  <div class="cart-page" dir="rtl">
    <div class="ambient-layer">
      <div class="orb orb-a"></div>
      <div class="orb orb-b"></div>
      <div class="orb orb-c"></div>
      <div class="grid-mask"></div>
    </div>

    <section class="cart-hero liquid-glass-panel">
      <div class="hero-copy">
        <p class="eyebrow">DENROOM CART EXPERIENCE</p>
        <h1>سبد خرید هوشمند دن‌روم</h1>
        <p class="hero-desc">
          هر آیتم را با توضیح اختصاصی ثبت کن، مشخصات را یک‌جا مرور کن و پیش‌فاکتور را دقیق برای تیم فروش ارسال کن.
        </p>
      </div>
      <div class="hero-actions">
        <button type="button" class="ghost-pill" @click="openQuickSidebar">
          سایدبار سریع
        </button>
        <button type="button" class="ghost-pill" @click="continueShopping">
          ادامه خرید
        </button>
      </div>
    </section>

    <section class="empty-state liquid-glass-panel" v-if="!submitted && !cart.length">
      <div class="empty-icon">🛍️</div>
      <h2>سبد خریدت خالیه</h2>
      <p>از محصولات دلخواهت انتخاب کن و دوباره برگرد. این صفحه برای ثبت دقیق جزئیات آماده‌ست.</p>
      <button type="button" class="primary-btn" @click="continueShopping">رفتن به محصولات</button>
    </section>

    <div class="cart-grid" v-if="!submitted && cart.length">
      <section class="cart-lines liquid-glass-panel">
        <header class="section-head">
          <h2>اقلام انتخاب‌شده</h2>
          <span>{{ totalItems }} مورد</span>
        </header>

        <transition-group name="line-stagger" tag="div" class="line-list">
          <article class="line-card" v-for="item in cart" :key="item.id">
            <div class="line-top">
              <div class="line-image-wrap">
                <img :src="item.image || '/assets/mysite/img/placeholder.png'" :alt="item.name || 'item'" />
                <span class="line-qty">{{ item.qty || 1 }}x</span>
              </div>
              <div class="line-info">
                <h3>{{ item.name }}</h3>
                <p class="line-code">{{ item.item_code }}</p>
                <div class="meta-chips">
                  <span v-for="meta in getItemMeta(item)" :key="`${item.id}-${meta}`">{{ meta }}</span>
                  <span v-if="item.parent_line_id">برای: {{ getParentLabel(item.parent_line_id) }}</span>
                </div>
              </div>
              <div class="line-price-wrap">
                <strong>{{ formatPrice(item.price) }}</strong>
                <small>تومان</small>
                <button type="button" class="remove-btn" @click="removeFromCart(item.id)">حذف</button>
              </div>
            </div>

            <label class="note-area">
              <span>توضیحات مشتری برای این محصول</span>
              <textarea
                :value="item.note || item.config?.customer_note || ''"
                @input="onItemNoteInput(item.id, $event.target.value)"
                placeholder="مثلا: تحویل برای پروژه پاسداران، پارچه خاص مشتری، اولویت ارسال یا هر نکته دیگری..."
              ></textarea>
            </label>
          </article>
        </transition-group>
      </section>

      <aside class="cart-summary liquid-glass-panel">
        <div class="summary-head">
          <h2>نهایی‌سازی درخواست</h2>
          <p>بعد از ثبت، کد پیگیری نمایش داده می‌شود.</p>
        </div>

        <div class="portal-card" v-if="isPortalAuthenticated">
          <div class="portal-title">مشتری لاگین‌شده</div>
          <p class="portal-name">{{ selectedPortalCustomerLabel || 'انتخاب نشده' }}</p>
          <label v-if="portalCustomers.length > 1" class="field">
            <span>انتخاب مشتری</span>
            <select v-model="selectedPortalCustomer">
              <option value="" disabled>یک مشتری انتخاب کنید</option>
              <option v-for="c in portalCustomers" :key="`cp-${c.name}`" :value="c.name">
                {{ c.customer_name || c.name }}
              </option>
            </select>
          </label>
          <p class="field-error" v-if="portalError">{{ portalError }}</p>
        </div>

        <div class="guest-card" v-else>
          <label class="field">
            <span>نام و نام خانوادگی</span>
            <input type="text" v-model="customer.name" placeholder="نام شما" />
          </label>
          <label class="field">
            <span>شماره همراه</span>
            <input type="tel" dir="ltr" v-model="customer.phone" placeholder="09123456789" />
          </label>
          <label class="field">
            <span>ایمیل (اختیاری)</span>
            <input type="email" dir="ltr" v-model="customer.email" placeholder="name@example.com" />
          </label>
        </div>

        <div class="payment-card">
          <label class="field">
            <span>روش تکمیل سفارش</span>
            <select v-model="paymentMethod">
              <option value="quotation">فقط ثبت درخواست (بدون پرداخت آنلاین)</option>
              <option value="zarinpal" :disabled="!canUseZarinpal">پرداخت آنلاین با زرین‌پال</option>
            </select>
          </label>
          <p class="payment-note" v-if="paymentMethod === 'zarinpal'">
            پس از ثبت درخواست، برای پرداخت به درگاه امن زرین‌پال منتقل می‌شوید.
          </p>
          <p class="field-error" v-if="paymentMethod === 'zarinpal' && !canUseZarinpal">
            برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد.
          </p>
        </div>

        <div class="totals-card">
          <div class="total-row">
            <span>تعداد ردیف</span>
            <strong>{{ totalItems }}</strong>
          </div>
          <div class="total-row">
            <span>جمع کل</span>
            <strong>{{ formatPrice(totalPrice) }} تومان</strong>
          </div>
          <div class="total-row grand">
            <span>قابل ارسال برای فروش</span>
            <strong>{{ formatPrice(totalPrice) }} تومان</strong>
          </div>
        </div>

        <div class="summary-actions">
          <button type="button" class="primary-btn" :disabled="loading" @click="handleCheckout">
            <span v-if="loading">در حال ثبت...</span>
            <span v-else>{{ checkoutButtonLabel }}</span>
          </button>
          <button type="button" class="danger-btn" :disabled="loading" @click="clearCart">پاک‌کردن سبد</button>
        </div>
      </aside>
    </div>

    <section class="success-wrap liquid-glass-panel" v-if="submitted">
      <div class="pulse-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      </div>
      <h2>درخواست شما ثبت شد</h2>
      <p class="tracking">کد پیگیری: {{ trackingCode }}</p>
      <p v-if="trackingCustomerName">ثبت‌شده برای مشتری: {{ trackingCustomerName }}</p>
      <div class="success-actions">
        <button type="button" class="primary-btn" @click="closeSuccess">بستن صفحه</button>
        <button type="button" class="ghost-pill" @click="continueShopping">ادامه خرید</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useCart } from '../stores/cartStore'
import { usePortalStore } from '../stores/portalStore'
import { getAnalyticsSessionId, trackAnalyticsEvent } from '../utils/analyticsTracker'

const { cart, totalItems, totalPrice, removeFromCart, clearCart, updateItemNote, isCartOpen } = useCart()
const { selectedCustomer, setSelectedCustomer } = usePortalStore()

const selectedPortalCustomer = ref(window.SelectedCustomer || selectedCustomer.value || '')
const portalSession = ref(null)
const portalError = ref('')
const loading = ref(false)
const submitted = ref(false)
const trackingCode = ref('')
const trackingCustomerName = ref('')
const paymentMethod = ref('quotation')

const customer = reactive({
  name: localStorage.getItem('customer_name') || '',
  phone: localStorage.getItem('customer_phone') || '',
  email: localStorage.getItem('customer_email') || ''
})

const lineItemMap = computed(() => {
  const map = {}
  cart.value.forEach((item) => {
    if (item.line_id) map[item.line_id] = item
  })
  return map
})

const isPortalAuthenticated = computed(() => !!portalSession.value?.authenticated)
const portalCustomers = computed(() => portalSession.value?.customers || [])
const canUseZarinpal = computed(() => Number(totalPrice.value || 0) > 0)
const checkoutButtonLabel = computed(() => (
  paymentMethod.value === 'zarinpal' ? 'انتقال به زرین‌پال' : 'ثبت نهایی درخواست'
))
const selectedPortalCustomerLabel = computed(() => {
  const selected = portalCustomers.value.find((c) => c.name === selectedPortalCustomer.value)
  return selected?.customer_name || selected?.name || ''
})

watch(() => customer.name, (val) => localStorage.setItem('customer_name', val || ''))
watch(() => customer.phone, (val) => localStorage.setItem('customer_phone', val || ''))
watch(() => customer.email, (val) => localStorage.setItem('customer_email', val || ''))
watch(selectedPortalCustomer, (value) => setSelectedCustomer(value || ''))

const formatPrice = (value) => {
  if (!value) return '۰'
  return Number(value).toLocaleString('fa-IR')
}

const getParentLabel = (parentLineId) => {
  const parent = lineItemMap.value[parentLineId]
  return parent?.name || '-'
}

const getItemMeta = (item) => {
  const labels = []
  const pushMeta = (label, value) => {
    if (!value) return
    labels.push(`${label}: ${value}`)
  }
  pushMeta('چوب', item?.config?.wood || item?.config?.['رنگ چوب'] || item?.config?.attributes?.['رنگ چوب'])
  pushMeta('بدنه', item?.config?.body || item?.config?.body_color || item?.config?.['رنگ بدنه'] || item?.config?.attributes?.['رنگ بدنه'])
  pushMeta('ارتفاع', item?.config?.['ارتفاع'] || item?.config?.attributes?.['ارتفاع'])
  pushMeta('ماژول', item?.config?.['ماژول'] || item?.config?.attributes?.['ماژول'])
  pushMeta('پارچه', item?.config?.quality ? `${item.config.quality} (${item.config.color || '-'})` : '')
  if (item?.config?.meters) labels.push(`${item.config.meters} متر`)
  return Array.from(new Set(labels))
}

const onItemNoteInput = (itemId, note) => {
  updateItemNote(itemId, note)
}

const openQuickSidebar = () => {
  isCartOpen.value = true
}

const continueShopping = () => {
  const referrer = document.referrer || ''
  if (referrer.includes('/')) {
    window.history.back()
    return
  }
  window.location.href = '/mysite'
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
      const exists = (message.customers || []).some((c) => c.name === selectedPortalCustomer.value)
      if (!exists) {
        selectedPortalCustomer.value = message.selected_customer || message.default_customer || message.customers?.[0]?.name || ''
      }
    }
  } catch (error) {
    portalSession.value = null
  }
}

const startPortalZarinpal = async () => {
  if (portalCustomers.value.length > 1 && !selectedPortalCustomer.value) {
    portalError.value = 'لطفا مشتری را انتخاب کنید.'
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
          source: 'cart_page_portal_zarinpal_init',
          tracking_code: message.quotation_request || ''
        }
      })
      window.location.href = message.payment_url
      return
    }
    portalError.value = extractApiMessage(result, 'اتصال به زرین‌پال انجام نشد. دوباره تلاش کنید.')
  } catch (error) {
    portalError.value = 'ارتباط با سرور برقرار نشد.'
  } finally {
    loading.value = false
  }
}

const startGuestZarinpal = async () => {
  if (!customer.name || !customer.phone) {
    window.alert('برای پرداخت آنلاین، نام و شماره همراه الزامی است.')
    return
  }
  if (!canUseZarinpal.value) {
    window.alert('برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد.')
    return
  }

  loading.value = true
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      window.alert('توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید.')
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
          source: 'cart_page_guest_zarinpal_init',
          tracking_code: message.quotation_request || ''
        }
      })
      window.location.href = message.payment_url
      return
    }
    window.alert(extractApiMessage(result, 'اتصال به زرین‌پال انجام نشد. دوباره تلاش کنید.'))
  } catch (error) {
    window.alert('خطا در ارتباط با سرور')
  } finally {
    loading.value = false
  }
}

const submitPortalQuotation = async () => {
  if (portalCustomers.value.length > 1 && !selectedPortalCustomer.value) {
    portalError.value = 'لطفا مشتری را انتخاب کنید.'
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
      trackingCustomerName.value = result.message.customer_name || selectedPortalCustomerLabel.value
      trackAnalyticsEvent('order_submit', {
        session_id: getAnalyticsSessionId(),
        model_name: cart.value.find((item) => (item.type || '').toLowerCase() !== 'fabric')?.name || '',
        qty: cart.value.reduce((sum, item) => sum + Number(item.qty || 1), 0),
        amount: totalPrice.value || 0,
        cart_value: totalPrice.value || 0,
        properties: {
          source: 'cart_page_portal',
          tracking_code: result.message.name || ''
        }
      })
      submitted.value = true
      clearCart()
    } else {
      portalError.value = extractApiMessage(result, 'ثبت درخواست انجام نشد. دوباره تلاش کنید.')
    }
  } catch (error) {
    portalError.value = 'ارتباط با سرور برقرار نشد.'
  } finally {
    loading.value = false
  }
}

const submitGuestQuotation = async () => {
  if (!customer.name || !customer.phone) {
    window.alert('لطفا نام و شماره همراه را وارد کنید.')
    return
  }

  loading.value = true
  try {
    const csrfToken = await ensureCsrfToken()
    if (!csrfToken) {
      window.alert('توکن امنیتی منقضی شده است. لطفاً صفحه را رفرش کنید.')
      return
    }

    const response = await fetch('/api/method/mysite.www.mysite.product.submit_quotation_request', {
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
          source: 'cart_page_guest',
          tracking_code: result.message.name || ''
        }
      })
      submitted.value = true
      clearCart()
    } else {
      window.alert('ثبت درخواست انجام نشد. دوباره تلاش کنید.')
    }
  } catch (error) {
    window.alert('خطا در ارتباط با سرور')
  } finally {
    loading.value = false
  }
}

const handleCheckout = async () => {
  if (!cart.value.length) return
  const nonFabricItems = cart.value.filter((item) => (item.type || '').toLowerCase() !== 'fabric')
  trackAnalyticsEvent('checkout_start', {
    session_id: getAnalyticsSessionId(),
    model_name: nonFabricItems[0]?.name || '',
    qty: nonFabricItems.reduce((sum, item) => sum + Number(item.qty || 1), 0),
    amount: totalPrice.value || 0,
    cart_value: totalPrice.value || 0,
    properties: {
      source: 'cart_page',
      items_count: nonFabricItems.length
    }
  })
  if (isPortalAuthenticated.value) {
    if (paymentMethod.value === 'zarinpal') {
      await startPortalZarinpal()
      return
    }
    await submitPortalQuotation()
    return
  }
  if (paymentMethod.value === 'zarinpal') {
    await startGuestZarinpal()
    return
  }
  await submitGuestQuotation()
}

const closeSuccess = () => {
  submitted.value = false
  trackingCode.value = ''
  trackingCustomerName.value = ''
}

onMounted(async () => {
  trackAnalyticsEvent('cart_open', {
    session_id: getAnalyticsSessionId(),
    cart_value: totalPrice.value || 0,
    qty: cart.value.length || 0,
    properties: { source: 'cart_page' }
  })
  await fetchPortalSession()
})
</script>

<style scoped>
.cart-page,
.cart-page *,
.cart-page *::before,
.cart-page *::after {
  box-sizing: border-box;
}

.cart-page {
  --cart-bg: #f6f0e8;
  --cart-surface: rgba(255, 255, 255, 0.58);
  --cart-border: rgba(120, 80, 52, 0.18);
  --cart-shadow: 0 24px 60px rgba(103, 62, 26, 0.14);
  --cart-text: #2b1b12;
  --cart-dim: #745946;
  --cart-accent: #a6472f;
  --cart-accent-2: #cf8f57;
  min-height: calc(100vh - 140px);
  padding: 36px clamp(16px, 4vw, 48px) 120px;
  background:
    radial-gradient(1400px 800px at 88% -10%, rgba(213, 114, 64, 0.14) 0%, rgba(246, 240, 232, 0) 72%),
    radial-gradient(1200px 700px at 2% 100%, rgba(160, 88, 59, 0.1) 0%, rgba(246, 240, 232, 0) 68%),
    var(--cart-bg);
  color: var(--cart-text);
  position: relative;
  overflow: hidden;
}

.ambient-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(14px);
  opacity: 0.45;
  animation: drift 13s ease-in-out infinite alternate;
}

.orb-a {
  width: 280px;
  height: 280px;
  top: 8%;
  left: 8%;
  background: rgba(205, 120, 69, 0.25);
}

.orb-b {
  width: 360px;
  height: 360px;
  right: -40px;
  top: 30%;
  animation-delay: -4s;
  background: rgba(166, 71, 47, 0.2);
}

.orb-c {
  width: 260px;
  height: 260px;
  bottom: -70px;
  left: 36%;
  animation-delay: -8s;
  background: rgba(181, 129, 65, 0.24);
}

.grid-mask {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(to right, rgba(117, 82, 59, 0.06) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(117, 82, 59, 0.06) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: radial-gradient(circle at center, black 45%, transparent 100%);
}

@keyframes drift {
  from {
    transform: translate3d(0, 0, 0) scale(1);
  }
  to {
    transform: translate3d(20px, -28px, 0) scale(1.08);
  }
}

.liquid-glass-panel {
  position: relative;
  background: var(--cart-surface);
  border: 1px solid var(--cart-border);
  border-radius: 28px;
  box-shadow: var(--cart-shadow);
  backdrop-filter: blur(20px) saturate(140%);
  z-index: 1;
}

.cart-hero {
  padding: clamp(22px, 3.4vw, 38px);
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-end;
  margin-bottom: 26px;
  animation: heroRise 0.7s ease-out both;
}

.eyebrow {
  letter-spacing: 0.24em;
  font-size: 11px;
  margin: 0 0 12px;
  color: var(--cart-dim);
}

.cart-hero h1 {
  font-size: clamp(1.7rem, 4vw, 2.45rem);
  margin: 0;
  line-height: 1.1;
}

.hero-desc {
  margin: 14px 0 0;
  color: var(--cart-dim);
  max-width: 720px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.ghost-pill,
.primary-btn,
.danger-btn {
  border: none;
  border-radius: 14px;
  padding: 12px 18px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.24s ease;
  font-family: inherit;
}

.ghost-pill {
  background: rgba(255, 255, 255, 0.56);
  border: 1px solid var(--cart-border);
  color: var(--cart-text);
}

.ghost-pill:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.76);
}

.primary-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--cart-accent), var(--cart-accent-2));
  color: #fff;
  box-shadow: 0 18px 36px rgba(166, 71, 47, 0.25);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.primary-btn:disabled,
.danger-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.danger-btn {
  width: 100%;
  background: rgba(167, 64, 47, 0.12);
  color: #7d3627;
  border: 1px solid rgba(167, 64, 47, 0.28);
}

.empty-state {
  padding: 42px;
  text-align: center;
  animation: heroRise 0.7s ease-out both;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.empty-state h2 {
  margin: 0;
}

.empty-state p {
  color: var(--cart-dim);
  line-height: 1.9;
  margin: 10px auto 22px;
  max-width: 600px;
}

.cart-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
  gap: 20px;
  align-items: start;
  min-width: 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-head h2 {
  margin: 0;
  font-size: 1.2rem;
}

.section-head span {
  color: var(--cart-dim);
  font-size: 13px;
}

.cart-lines {
  padding: 22px;
  min-width: 0;
  overflow: hidden;
}

.line-list {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.line-card {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(114, 76, 49, 0.16);
  border-radius: 22px;
  padding: 16px;
  box-shadow: 0 10px 26px rgba(107, 68, 30, 0.08);
  min-width: 0;
  overflow: hidden;
}

.line-top {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: start;
  min-width: 0;
}

.line-image-wrap {
  position: relative;
  width: 92px;
  height: 92px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(103, 61, 31, 0.12);
  background: rgba(255, 255, 255, 0.72);
}

.line-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transform: scale(0.94);
}

.line-qty {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(43, 27, 18, 0.72);
  color: #fff;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
}

.line-info h3 {
  margin: 2px 0 4px;
  font-size: 1.05rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.line-info {
  min-width: 0;
}

.line-code {
  margin: 0 0 8px;
  direction: ltr;
  text-align: right;
  font-size: 11px;
  color: var(--cart-dim);
  word-break: break-word;
}

.meta-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-chips span {
  background: rgba(246, 236, 223, 0.9);
  border: 1px solid rgba(126, 85, 56, 0.2);
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 11px;
  color: #5f4330;
}

.line-price-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 96px;
  max-width: 100%;
}

.line-price-wrap strong {
  color: var(--cart-accent);
  font-size: 1.05rem;
}

.line-price-wrap small {
  color: var(--cart-dim);
}

.remove-btn {
  margin-top: 8px;
  border: none;
  background: transparent;
  color: #8a3f2b;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  text-decoration: underline;
  font-family: inherit;
}

.note-area {
  display: block;
  margin-top: 14px;
}

.note-area span {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--cart-dim);
  margin-bottom: 6px;
}

.note-area textarea {
  width: 100%;
  max-width: 100%;
  min-height: 74px;
  border-radius: 14px;
  border: 1px solid rgba(117, 82, 54, 0.25);
  background: rgba(255, 255, 255, 0.78);
  padding: 10px 12px;
  color: var(--cart-text);
  resize: vertical;
  font-family: inherit;
  font-size: 13px;
}

.note-area textarea:focus {
  outline: none;
  border-color: rgba(166, 71, 47, 0.52);
  box-shadow: 0 0 0 4px rgba(166, 71, 47, 0.08);
}

.cart-summary {
  padding: 20px;
  position: sticky;
  top: 96px;
  min-width: 0;
  overflow: hidden;
}

.summary-head h2 {
  margin: 0;
  font-size: 1.16rem;
}

.summary-head p {
  margin: 8px 0 16px;
  color: var(--cart-dim);
  font-size: 13px;
}

.portal-card,
.guest-card,
.payment-card,
.totals-card {
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(124, 84, 56, 0.19);
  border-radius: 16px;
  padding: 14px;
  margin-bottom: 12px;
}

.portal-title {
  font-size: 12px;
  color: var(--cart-dim);
}

.portal-name {
  margin: 4px 0 10px;
  font-size: 15px;
  font-weight: 800;
}

.field {
  display: block;
  margin-bottom: 10px;
}

.field span {
  display: block;
  font-size: 12px;
  color: var(--cart-dim);
  margin-bottom: 6px;
}

.field input,
.field select {
  width: 100%;
  max-width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(121, 82, 56, 0.22);
  background: rgba(255, 255, 255, 0.82);
  height: 42px;
  padding: 0 12px;
  color: var(--cart-text);
  font-family: inherit;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: rgba(166, 71, 47, 0.5);
}

.field-error {
  margin: 6px 0 0;
  font-size: 12px;
  color: #a53f38;
}

.payment-note {
  margin: 0;
  font-size: 12px;
  color: var(--cart-dim);
  line-height: 1.8;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: #654734;
  font-size: 14px;
}

.total-row.grand {
  border-top: 1px solid rgba(117, 82, 54, 0.2);
  margin-top: 8px;
  padding-top: 12px;
  color: var(--cart-accent);
}

.summary-actions {
  display: grid;
  gap: 8px;
}

.success-wrap {
  padding: 44px 18px;
  text-align: center;
  max-width: 760px;
  margin: 0 auto;
}

.pulse-check {
  width: 76px;
  height: 76px;
  margin: 0 auto 18px;
  border-radius: 50%;
  background: linear-gradient(145deg, #69b166, #2f8e59);
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 18px 34px rgba(31, 116, 64, 0.26);
  animation: pulseCheck 1.5s ease-in-out infinite;
}

.pulse-check svg {
  width: 34px;
  height: 34px;
}

.success-wrap h2 {
  margin: 0;
}

.tracking {
  margin: 12px 0 10px;
  font-weight: 800;
  color: var(--cart-accent);
}

.success-actions {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

@keyframes pulseCheck {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes heroRise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.line-stagger-enter-active {
  transition: all 0.45s ease;
}

.line-stagger-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 1100px) {
  .cart-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .cart-summary {
    position: static;
    top: auto;
  }
}

@media (max-width: 760px) {
  .cart-page {
    padding: 18px 12px 110px;
  }

  .cart-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .line-top {
    grid-template-columns: 80px minmax(0, 1fr);
  }

  .line-price-wrap {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed rgba(113, 75, 48, 0.26);
  }

  .line-price-wrap strong {
    font-size: 1rem;
  }
}
</style>
