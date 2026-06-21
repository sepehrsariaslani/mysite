<template>
  <div class="product-detail-overlay" @click.self="$emit('close')">
    <div class="product-detail-panel" dir="rtl">
      <!-- Header -->
      <header class="detail-top">
        <button class="back-btn" @click="$emit('close')">
          <ArrowRight :size="20" />
        </button>
        <h2 class="detail-title">{{ product.item_name || product.item_code }}</h2>
        <button class="save-btn" :disabled="saving" @click="handleSave">
          {{ saving ? 'در حال ذخیره...' : 'ذخیره' }}
        </button>
      </header>

      <div class="detail-scroll">
        <!-- Image -->
        <div class="image-section">
          <div class="main-image" v-if="form.image">
            <img :src="form.image" :alt="form.item_name" />
          </div>
          <div class="main-image placeholder" v-else>
            <Package :size="48" />
            <span>بدون تصویر</span>
          </div>
          <div class="thumb-strip" v-if="product.images?.length">
            <button
              v-for="img in product.images"
              :key="img.file_url"
              class="thumb-item"
              :class="{ active: form.image === img.file_url }"
              @click="form.image = img.file_url"
            >
              <img :src="img.file_url" :alt="img.file_name" />
            </button>
          </div>
        </div>

        <!-- Basic Info -->
        <section class="section">
          <h3 class="section-title">اطلاعات پایه</h3>
          <div class="field">
            <label>نام محصول</label>
            <input v-model="form.item_name" placeholder="نام محصول" />
          </div>
          <div class="field">
            <label>گروه محصول</label>
            <input v-model="form.item_group" placeholder="گروه محصول" list="mobile-item-groups" />
            <datalist id="mobile-item-groups">
              <option v-for="row in itemGroups" :key="`mg-${row.item_group}`" :value="row.item_group" />
            </datalist>
          </div>
          <div class="field">
            <label>توضیحات</label>
            <textarea v-model="form.description" rows="3" placeholder="توضیحات محصول"></textarea>
          </div>
        </section>

        <!-- Status -->
        <section class="section">
          <h3 class="section-title">وضعیت</h3>
          <div class="switch-row">
            <span>نمایش در سایت</span>
            <button class="toggle" :class="{ on: form.show_on_site }" @click="form.show_on_site = !form.show_on_site">
              <span class="knob"></span>
            </button>
          </div>
          <div class="switch-row">
            <span>غیرفعال</span>
            <button class="toggle" :class="{ on: form.disabled }" @click="form.disabled = !form.disabled">
              <span class="knob"></span>
            </button>
          </div>
        </section>

        <!-- Prices -->
        <section class="section">
          <div class="section-head">
            <h3 class="section-title">قیمت‌ها</h3>
            <button class="add-btn" @click="addPriceRow">
              <Plus :size="14" />
              افزودن
            </button>
          </div>
          <div v-if="!form.price_rows.length" class="empty-hint">هنوز قیمتی ثبت نشده</div>
          <div v-else class="price-list">
            <div v-for="(row, idx) in form.price_rows" :key="idx" class="price-card">
              <div class="price-card-top">
                <select v-model="row.price_list">
                  <option value="">لیست قیمت</option>
                  <option v-for="pl in priceLists" :key="`mpl-${pl.name}`" :value="pl.name">
                    {{ pl.title || pl.name }}
                  </option>
                </select>
                <button class="remove-btn" @click="removePriceRow(idx)">
                  <Trash2 :size="14" />
                </button>
              </div>
              <div class="price-card-fields">
                <input v-model.number="row.rate" type="number" placeholder="قیمت (ریال)" />
                <input v-model.trim="row.currency" placeholder="ارز" />
              </div>
            </div>
          </div>
        </section>

        <!-- Features -->
        <section class="section">
          <div class="section-head">
            <h3 class="section-title">ویژگی‌ها</h3>
            <button class="add-btn" @click="addFeatureRow">
              <Plus :size="14" />
              افزودن
            </button>
          </div>
          <div v-if="!form.feature_rows.length" class="empty-hint">هنوز ویژگی‌ای ثبت نشده</div>
          <div v-else class="feature-list">
            <div v-for="(row, idx) in form.feature_rows" :key="idx" class="feature-card">
              <div class="feature-card-fields">
                <input v-model.trim="row.label" placeholder="عنوان (مثلا جنس بدنه)" />
                <input v-model.trim="row.value" placeholder="مقدار (مثلا چوب راش)" />
              </div>
              <button class="remove-btn" @click="removeFeatureRow(idx)">
                <Trash2 :size="14" />
              </button>
            </div>
          </div>
        </section>

        <!-- Images Management -->
        <section class="section">
          <div class="section-head">
            <h3 class="section-title">تصاویر</h3>
            <button class="add-btn" :disabled="uploadingImage" @click="openUploadPicker">
              <Plus :size="14" />
              {{ uploadingImage ? 'در حال آپلود...' : 'آپلود' }}
            </button>
            <input ref="fileInput" type="file" accept="image/*" class="hidden-file" @change="uploadImage" />
          </div>
          <div v-if="product.images?.length" class="images-grid">
            <div v-for="img in product.images" :key="img.file_url" class="img-card">
              <img :src="img.file_url" :alt="img.file_name" />
              <div class="img-card-actions">
                <button
                  class="mini-btn"
                  :class="{ primary: form.image === img.file_url }"
                  @click="setPrimary(img.file_url)"
                >
                  {{ form.image === img.file_url ? 'اصلی' : 'تنظیم اصلی' }}
                </button>
                <button class="mini-btn danger" @click="removeImg(img)">
                  <Trash2 :size="12" />
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">تصویری ثبت نشده</div>
        </section>

        <!-- Save -->
        <div class="bottom-save">
          <button class="full-save" :disabled="saving" @click="handleSave">
            {{ saving ? 'در حال ذخیره...' : 'ذخیره تغییرات' }}
          </button>
        </div>
      </div>

      <!-- Toast -->
      <Transition name="toast">
        <div v-if="toast" class="toast" :class="toast.type">{{ toast.message }}</div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { ArrowRight, Package, Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  product: { type: Object, required: true },
  itemGroups: { type: Array, default: () => [] },
  priceLists: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'save'])

const saving = ref(false)
const uploadingImage = ref(false)
const fileInput = ref(null)
const toast = ref(null)

const form = reactive({
  item_name: '',
  item_group: '',
  description: '',
  show_on_site: true,
  disabled: false,
  image: '',
  price_rows: [],
  feature_rows: [],
})

function fillForm() {
  if (!props.product) return
  form.item_name = props.product.item_name || ''
  form.item_group = props.product.item_group || ''
  form.description = props.product.description || ''
  form.show_on_site = Boolean(props.product.show_on_site)
  form.disabled = Boolean(props.product.disabled)
  form.image = (props.product.image || '').replace('/private/files/', '/files/')
  form.price_rows = Array.isArray(props.product.price_rows)
    ? props.product.price_rows.map(r => ({ ...r }))
    : []
  form.feature_rows = Array.isArray(props.product.feature_rows)
    ? props.product.feature_rows.map(r => ({ ...r }))
    : []
}

watch(() => props.product, fillForm, { immediate: true })

function addPriceRow() {
  const fallbackPL = props.priceLists.find(r => r?.is_default)?.name || props.priceLists[0]?.name || ''
  form.price_rows.push({ name: '', price_list: fallbackPL, rate: 0, currency: 'IRR', uom: '', selling: true, buying: false })
}

function removePriceRow(idx) {
  form.price_rows.splice(idx, 1)
}

function addFeatureRow() {
  form.feature_rows.push({ label: '', value: '' })
}

function removeFeatureRow(idx) {
  form.feature_rows.splice(idx, 1)
}

function setPrimary(url) {
  form.image = url
}

function openUploadPicker() {
  fileInput.value?.click()
}

async function uploadImage(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('is_private', '0')
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: fd,
    })
    const payload = await res.json()
    if (!res.ok || payload.exception) throw new Error(payload?.message || 'آپلود ناموفق')
    const fileUrl = (payload.message || payload)?.file_url || ''
    if (fileUrl) {
      // attach to product
      await fetch('/api/method/mysite.api.attach_management_product_image', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.csrf_token || '' },
        body: JSON.stringify({ item_code: props.product.item_code, file_url: fileUrl, is_primary: !form.image }),
      })
      if (!form.image) form.image = fileUrl
      showToast('تصویر آپلود شد', 'success')
      emit('save', form, () => {}, () => {})
    }
  } catch (err) {
    showToast(err?.message || 'خطا در آپلود', 'error')
  } finally {
    uploadingImage.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function removeImg(img) {
  try {
    await fetch('/api/method/mysite.api.remove_management_product_image', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: JSON.stringify({
        item_code: props.product.item_code,
        file_name: img.name || '',
        file_url: (img.file_url || '').replace('/private/files/', '/files/'),
      }),
    })
    if (form.image === img.file_url) form.image = ''
    showToast('تصویر حذف شد', 'success')
    emit('save', form, () => {}, () => {})
  } catch (err) {
    showToast(err?.message || 'خطا در حذف تصویر', 'error')
  }
}

async function handleSave() {
  saving.value = true
  try {
    emit('save', { ...form }, () => {
      showToast('تغییرات ذخیره شد', 'success')
    }, (errMsg) => {
      showToast(errMsg || 'خطا در ذخیره', 'error')
    })
  } finally {
    saving.value = false
  }
}

function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 2500)
}
</script>

<style scoped>
.product-detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.product-detail-panel {
  width: 100%;
  max-width: 100%;
  max-height: 92vh;
  background: var(--admin-bg);
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
  overflow: hidden;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.detail-top {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-panel-bg);
  flex-shrink: 0;
}

.back-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.detail-title {
  flex: 1;
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.save-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
}

.save-btn:disabled {
  opacity: 0.6;
}

.detail-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding: 14px;
  padding-bottom: 30px;
}

/* Image Section */
.image-section {
  margin-bottom: 16px;
}

.main-image {
  width: 100%;
  height: 200px;
  border-radius: 14px;
  border: 1px solid var(--admin-border);
  overflow: hidden;
  background: var(--admin-chip-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.main-image.placeholder {
  flex-direction: column;
  gap: 8px;
  color: var(--admin-text-soft);
  font-size: 0.85rem;
}

.thumb-strip {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 4px;
}

.thumb-item {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  border: 2px solid transparent;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
  padding: 0;
  background: none;
}

.thumb-item.active {
  border-color: var(--admin-tab-active-start);
}

.thumb-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Sections */
.section {
  margin-bottom: 18px;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-panel-bg);
  padding: 12px;
}

.section-title {
  margin: 0 0 10px;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-main);
}

.section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.section-head .section-title {
  margin: 0;
  flex: 1;
}

.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.field {
  margin-bottom: 10px;
}

.field label {
  display: block;
  font-size: 0.78rem;
  color: var(--admin-text-soft);
  margin-bottom: 4px;
  font-weight: 600;
}

.field input,
.field textarea,
.field select {
  width: 100%;
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: 10px;
  min-height: 40px;
  padding: 0 12px;
  font-family: inherit;
  font-size: 0.85rem;
  box-sizing: border-box;
}

.field textarea {
  padding: 10px 12px;
  resize: vertical;
}

/* Switch */
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--admin-border);
}

.switch-row:last-child {
  border-bottom: none;
}

.switch-row span {
  font-size: 0.85rem;
  font-weight: 600;
}

.toggle {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  border: none;
  background: var(--admin-border);
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}

.toggle.on {
  background: var(--admin-tab-active-start);
}

.toggle .knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s;
}

.toggle.on .knob {
  transform: translateX(20px);
}

/* Price Cards */
.empty-hint {
  color: var(--admin-text-soft);
  font-size: 0.82rem;
  text-align: center;
  padding: 12px;
}

.price-list,
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-card,
.feature-card {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-input-bg);
  padding: 10px;
}

.price-card-top {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.price-card-top select {
  flex: 1;
  border: 1px solid var(--admin-border);
  background: var(--admin-panel-bg);
  color: var(--text-main);
  border-radius: 8px;
  min-height: 36px;
  padding: 0 8px;
  font-family: inherit;
  font-size: 0.8rem;
}

.price-card-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.price-card-fields input,
.feature-card-fields input {
  border: 1px solid var(--admin-border);
  background: var(--admin-panel-bg);
  color: var(--text-main);
  border-radius: 8px;
  min-height: 36px;
  padding: 0 10px;
  font-family: inherit;
  font-size: 0.8rem;
  width: 100%;
  box-sizing: border-box;
}

.feature-card {
  display: flex;
  gap: 6px;
  align-items: flex-start;
}

.feature-card-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.remove-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  color: #fecaca;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

/* Images Grid */
.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.img-card {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  overflow: hidden;
  background: var(--admin-input-bg);
}

.img-card img {
  width: 100%;
  height: 80px;
  object-fit: cover;
}

.img-card-actions {
  display: flex;
  gap: 4px;
  padding: 6px;
}

.mini-btn {
  flex: 1;
  border: 1px solid var(--admin-border);
  border-radius: 6px;
  background: var(--admin-panel-bg);
  color: var(--text-main);
  font-size: 0.68rem;
  font-weight: 600;
  padding: 5px 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.mini-btn.primary {
  border-color: rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.14);
  color: var(--admin-tab-active-start);
}

.mini-btn.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
  flex: 0;
  width: 30px;
  padding: 5px;
}

/* Bottom Save */
.bottom-save {
  margin-top: 8px;
}

.full-save {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
}

.full-save:disabled {
  opacity: 0.6;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  z-index: 600;
  white-space: nowrap;
}

.toast.success {
  background: rgba(34, 197, 94, 0.9);
  color: #fff;
}

.toast.error {
  background: rgba(239, 68, 68, 0.9);
  color: #fff;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.hidden-file {
  display: none;
}
</style>
