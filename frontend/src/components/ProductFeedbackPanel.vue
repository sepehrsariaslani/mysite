<template>
  <div class="feedback-panel liquid-glass-inner">
    <div class="feedback-summary" v-if="feedbackType === 'review'">
      <div class="avg-rating">{{ averageLabel }}</div>
      <div class="summary-text">بر اساس {{ toPersianNumber(totalCount) }} دیدگاه</div>
    </div>

    <form class="feedback-form" @submit.prevent="submitFeedback">
      <h3 class="form-title">
        {{ feedbackType === 'review' ? 'دیدگاه خود را ثبت کنید' : 'پرسش خود را ثبت کنید' }}
      </h3>

      <div class="form-grid">
        <input
          v-model.trim="form.name"
          class="text-input"
          type="text"
          placeholder="نام شما"
          maxlength="120"
        />
        <input
          v-model.trim="form.email"
          class="text-input"
          type="email"
          placeholder="ایمیل (اختیاری)"
          maxlength="140"
        />
      </div>

      <div class="rating-row" v-if="feedbackType === 'review'">
        <span class="rating-label">امتیاز شما</span>
        <div class="rating-options">
          <button
            v-for="value in [5, 4, 3, 2, 1]"
            :key="value"
            type="button"
            class="rating-chip"
            :class="{ active: Number(form.rating) === value }"
            @click="form.rating = value"
          >
            <span>{{ toPersianNumber(value) }}</span>
            <span>★</span>
          </button>
        </div>
      </div>

      <textarea
        v-model.trim="form.content"
        class="text-area"
        :placeholder="feedbackType === 'review' ? 'تجربه خرید و استفاده خود را بنویسید...' : 'سوال خود را واضح و کوتاه بنویسید...'"
        maxlength="1200"
        rows="4"
      ></textarea>

      <p v-if="submitError" class="feedback-message error">{{ submitError }}</p>
      <p v-if="submitSuccess" class="feedback-message success">{{ submitSuccess }}</p>

      <button type="submit" class="submit-btn" :disabled="submitting">
        {{ submitting ? 'در حال ثبت...' : (feedbackType === 'review' ? 'ثبت دیدگاه' : 'ثبت پرسش') }}
      </button>
    </form>

    <div class="feedback-list">
      <p v-if="loading" class="state-message">در حال دریافت اطلاعات...</p>
      <p v-else-if="items.length === 0" class="state-message">
        {{ feedbackType === 'review' ? 'هنوز دیدگاهی ثبت نشده است.' : 'هنوز پرسشی ثبت نشده است.' }}
      </p>

      <div v-else class="items-wrap">
        <article
          v-for="entry in items"
          :key="entry.id"
          class="feedback-item"
        >
          <div class="item-head">
            <strong class="author">{{ entry.author || 'کاربر' }}</strong>
            <span class="date">{{ formatDate(entry.date) }}</span>
          </div>

          <div v-if="feedbackType === 'review'" class="rating-stars">
            {{ renderStars(entry.rating) }}
          </div>

          <p class="content">{{ entry.content }}</p>

          <div v-if="feedbackType === 'question'" class="answer-box" :class="{ waiting: !entry.answer }">
            <strong>پاسخ:</strong>
            <span>{{ entry.answer || 'پرسش شما ثبت شده و در انتظار پاسخ تیم پشتیبانی دن‌روم است.' }}</span>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  feedbackType: {
    type: String,
    required: true,
    validator: (v) => ['review', 'question'].includes(v),
  },
  modelName: {
    type: String,
    default: '',
  },
  itemCode: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['count-change'])

const loading = ref(false)
const submitting = ref(false)
const submitError = ref('')
const submitSuccess = ref('')
const items = ref([])
const stats = ref({ count: 0, avg_rating: 0 })

const form = reactive({
  name: '',
  email: '',
  rating: 5,
  content: '',
})

const totalCount = computed(() => Number(stats.value.count || items.value.length || 0))
const averageLabel = computed(() => {
  const avg = Number(stats.value.avg_rating || 0)
  return avg.toLocaleString('fa-IR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
})

const toPersianNumber = (value) => {
  const numeric = Number(value || 0)
  return numeric.toLocaleString('fa-IR')
}

const formatDate = (rawDate) => {
  if (!rawDate) return ''
  const dt = new Date(rawDate)
  if (Number.isNaN(dt.getTime())) return String(rawDate)
  return dt.toLocaleDateString('fa-IR')
}

const renderStars = (rating) => {
  const safe = Math.max(1, Math.min(5, Number(rating || 0)))
  return `${'★'.repeat(safe)}${'☆'.repeat(5 - safe)}`
}

const buildQuery = () => {
  const query = new URLSearchParams()
  query.set('feedback_type', props.feedbackType)
  if (props.modelName) query.set('model_name', props.modelName)
  if (props.itemCode) query.set('item_code', props.itemCode)
  return query.toString()
}

const fetchFeedback = async () => {
  submitError.value = ''
  if (!props.modelName && !props.itemCode) {
    items.value = []
    stats.value = { count: 0, avg_rating: 0 }
    emit('count-change', 0)
    return
  }

  loading.value = true
  try {
    const res = await fetch(`/api/method/mysite.www.mysite.product.get_product_feedback?${buildQuery()}`)
    const data = await res.json()

    if (!res.ok || data?.exc) {
      throw new Error(data?.message || 'خطا در دریافت اطلاعات')
    }

    const payload = data?.message || {}
    items.value = Array.isArray(payload.items) ? payload.items : []
    stats.value = payload.stats || { count: items.value.length, avg_rating: 0 }
    emit('count-change', Number(stats.value.count || items.value.length || 0))
  } catch (err) {
    submitError.value = err?.message || 'دریافت اطلاعات با خطا مواجه شد.'
    items.value = []
    stats.value = { count: 0, avg_rating: 0 }
    emit('count-change', 0)
  } finally {
    loading.value = false
  }
}

const submitFeedback = async () => {
  submitError.value = ''
  submitSuccess.value = ''

  if (!form.content || form.content.length < 3) {
    submitError.value = props.feedbackType === 'review'
      ? 'متن دیدگاه باید حداقل ۳ کاراکتر باشد.'
      : 'متن پرسش باید حداقل ۳ کاراکتر باشد.'
    return
  }

  if (props.feedbackType === 'review' && (Number(form.rating) < 1 || Number(form.rating) > 5)) {
    submitError.value = 'امتیاز باید بین ۱ تا ۵ باشد.'
    return
  }

  submitting.value = true
  try {
    const csrfToken = window.csrf_token || window.frappe?.csrf_token || ''
    const response = await fetch('/api/method/mysite.www.mysite.product.submit_product_feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken ? { 'X-Frappe-CSRF-Token': csrfToken } : {}),
      },
      body: JSON.stringify({
        feedback_type: props.feedbackType,
        model_name: props.modelName,
        item_code: props.itemCode,
        content: form.content,
        rating: props.feedbackType === 'review' ? Number(form.rating) : null,
        author_name: form.name,
        author_email: form.email,
      }),
    })

    const result = await response.json()
    if (!response.ok || result?.exc) {
      throw new Error(result?.message || 'ثبت اطلاعات با خطا مواجه شد.')
    }

    form.content = ''
    if (props.feedbackType === 'review') form.rating = 5

    submitSuccess.value = props.feedbackType === 'review'
      ? 'دیدگاه شما با موفقیت ثبت شد.'
      : 'پرسش شما با موفقیت ثبت شد.'

    await fetchFeedback()
  } catch (err) {
    submitError.value = err?.message || 'ثبت اطلاعات با خطا مواجه شد.'
  } finally {
    submitting.value = false
  }
}

watch(
  () => [props.feedbackType, props.modelName, props.itemCode],
  () => {
    fetchFeedback()
  },
  { immediate: true }
)
</script>

<style scoped>
.feedback-panel {
  direction: rtl;
  font-family: 'Peyda', sans-serif;
  padding: 22px;
  border-radius: 24px;
  background: color-mix(in srgb, var(--glass-bg) 88%, transparent);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(14px) saturate(165%);
  -webkit-backdrop-filter: blur(14px) saturate(165%);
  display: grid;
  gap: 18px;
}

.feedback-summary {
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent-brown) 14%, transparent), color-mix(in srgb, var(--accent-gold) 18%, transparent));
  text-align: center;
  border: 1px solid var(--glass-border);
}

.avg-rating {
  font-size: 30px;
  font-weight: 900;
  color: var(--text-main);
  line-height: 1;
}

.summary-text {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-dim);
}

.feedback-form {
  display: grid;
  gap: 12px;
}

.form-title {
  margin: 0;
  font-size: 17px;
  font-weight: 900;
  color: var(--text-main);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.text-input,
.text-area {
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--bg-secondary) 90%, transparent);
  padding: 11px 12px;
  font-family: inherit;
  font-size: 14px;
  color: var(--text-main);
  box-sizing: border-box;
}

.text-input::placeholder,
.text-area::placeholder {
  color: var(--text-dim);
}

.text-area {
  resize: vertical;
  min-height: 108px;
}

.rating-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.rating-label {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-muted);
}

.rating-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.rating-chip {
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--glass-bg) 85%, transparent);
  color: var(--text-main);
  padding: 6px 11px;
  font-size: 12px;
  font-weight: 800;
  display: inline-flex;
  gap: 4px;
  align-items: center;
  cursor: pointer;
}

.rating-chip.active {
  background: var(--accent-gold);
  border-color: color-mix(in srgb, var(--accent-gold) 70%, var(--glass-border));
  color: var(--accent-brown);
}

.feedback-message {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
}

.feedback-message.error {
  color: #8d1c1c;
}

.feedback-message.success {
  color: #1f6b37;
}

.submit-btn {
  border: 1px solid color-mix(in srgb, var(--accent-gold) 45%, var(--glass-border));
  border-radius: 12px;
  background: linear-gradient(120deg, var(--accent-gold), color-mix(in srgb, var(--accent-gold) 70%, #fff 30%));
  color: var(--accent-brown);
  padding: 12px;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: wait;
}

.feedback-list {
  display: grid;
  gap: 10px;
}

.state-message {
  margin: 0;
  border-radius: 12px;
  background: color-mix(in srgb, var(--glass-bg-hover) 90%, transparent);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 700;
  padding: 12px;
  text-align: center;
}

.items-wrap {
  display: grid;
  gap: 10px;
}

.feedback-item {
  border-radius: 14px;
  border: 1px solid var(--glass-border);
  background: color-mix(in srgb, var(--bg-secondary) 86%, transparent);
  padding: 14px;
}

.item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.author {
  font-size: 14px;
  color: var(--text-main);
}

.date {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}

.rating-stars {
  color: #c7862f;
  font-size: 14px;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.content {
  margin: 0;
  color: var(--text-main);
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.answer-box {
  margin-top: 12px;
  border-radius: 10px;
  padding: 10px;
  background: color-mix(in srgb, #6ea36a 16%, transparent);
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.7;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.answer-box.waiting {
  background: color-mix(in srgb, var(--accent-brown) 14%, transparent);
  color: var(--text-muted);
}

@media (max-width: 720px) {
  .feedback-panel {
    padding: 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
