<template>
  <div class="products-page" dir="rtl">
<div class="products-shell">
      <aside class="sidebar">
        <div class="brand-row">
          <div class="brand-dot">ک</div>
          <div>
            <strong>مدیریت محصولات</strong>
            <small>ویرایش سریع کاتالوگ</small>
          </div>
        </div>

        <nav class="side-nav">
          <a class="nav-item" href="/management">مدیریت صفحات</a>
          <a class="nav-item active" href="/management-products">مدیریت محصولات</a>
          <a class="nav-item" href="/management-blog">مدیریت بلاگ</a>
          <a class="nav-item" href="/management-analytics">آنالیتیکس</a>
        </nav>

        <div class="side-note">
          <p>این بخش برای تیم داخلی است: مشاهده، ویرایش و مدیریت تصاویر محصولات.</p>
        </div>
      </aside>

      <section class="list-area">
        <header class="list-header">
          <div>
            <h1>لیست محصولات</h1>
            <p>تعداد کل: {{ toFa(total) }}</p>
          </div>
          <div class="list-header-actions">
            <ManagementProductViewSwitcher v-model="listViewMode" />
            <button class="ghost" :disabled="loading" @click="loadProducts()">
              {{ loading ? 'در حال دریافت...' : 'بروزرسانی' }}
            </button>
          </div>
        </header>

        <div class="filters">
          <input
            v-model.trim="filters.search"
            placeholder="جستجو (کد/نام/مدل)"
            @keydown.enter.prevent="loadProducts(true)"
          />
          <select v-model="filters.status" @change="loadProducts(true)">
            <option value="all">همه وضعیت‌ها</option>
            <option value="active">فعال</option>
            <option value="hidden">مخفی در سایت</option>
            <option value="disabled">غیرفعال</option>
          </select>
          <select v-model="filters.item_group" @change="loadProducts(true)">
            <option value="">همه گروه‌ها</option>
            <option v-for="row in itemGroups" :key="`grp-${row.item_group}`" :value="row.item_group">
              {{ row.item_group }} ({{ toFa(row.count) }})
            </option>
          </select>
          <button class="ghost" :disabled="loading" @click="loadProducts(true)">اعمال فیلتر</button>
        </div>

        <div v-if="loading" class="state">در حال دریافت محصولات...</div>
        <div v-else-if="error" class="state error">{{ error }}</div>
        <div v-else-if="!products.length" class="state">محصولی یافت نشد.</div>

        <ManagementProductGridView
          v-else-if="listViewMode === 'grid'"
          :items="products"
          :selected-code="selectedCode"
          @select="onSelectProduct"
        />
        <ManagementProductListView
          v-else-if="listViewMode === 'list'"
          :items="products"
          :selected-code="selectedCode"
          @select="onSelectProduct"
        />
        <ManagementProductTableView
          v-else
          :items="products"
          :selected-code="selectedCode"
          @select="onSelectProduct"
        />
      </section>

      <!-- Desktop detail area -->
      <section class="detail-area" v-if="!isMobile">
        <div v-if="!selectedProduct" class="state">یک محصول را از لیست انتخاب کنید.</div>

        <template v-else>
          <header class="detail-header">
            <div>
              <h2>{{ selectedProduct.item_name || selectedProduct.item_code }}</h2>
              <code>{{ selectedProduct.item_code }}</code>
              <p v-if="workflowRef.name" class="hint">
                وضعیت گردش‌کار: <b>{{ workflowRef.state || 'Draft' }}</b> | درخواست: {{ workflowRef.name }}
              </p>
            </div>
            <button class="ghost" :disabled="saving || !canEditProduct" @click="saveProduct()">
              {{ saving ? 'در حال ذخیره...' : 'ذخیره پیش‌نویس' }}
            </button>
          </header>

          <div v-if="workflowRef.name" class="workflow-actions">
            <button
              v-for="action in workflowActions"
              :key="action.key"
              class="mini"
              :class="{ danger: action.danger }"
              :disabled="workflowLoading"
              @click="runWorkflowAction(action.key)"
            >
              {{ action.label }}
            </button>
          </div>

          <p v-if="saveError" class="save-msg error">{{ saveError }}</p>
          <p v-else-if="saveSuccess" class="save-msg success">{{ saveSuccess }}</p>

          <div class="form-grid">
            <label>
              <span>نام محصول</span>
              <input v-model="form.item_name" />
            </label>
            <label>
              <span>گروه محصول</span>
              <input v-model="form.item_group" list="item-groups-list" />
              <datalist id="item-groups-list">
                <option v-for="row in itemGroups" :key="`grp-opt-${row.item_group}`" :value="row.item_group" />
              </datalist>
            </label>
            <label class="wide">
              <span>توضیحات</span>
              <textarea v-model="form.description" rows="4"></textarea>
            </label>
            <label class="switch">
              <input type="checkbox" v-model="form.show_on_site" />
              <span>نمایش در سایت</span>
            </label>
            <label class="switch">
              <input type="checkbox" v-model="form.disabled" />
              <span>غیرفعال</span>
            </label>
          </div>

          <article class="settings-box">
            <div class="settings-head">
              <h3>قیمت‌ها</h3>
              <button class="ghost mini-add" type="button" @click="addPriceRow">افزودن قیمت</button>
            </div>
            <div v-if="!form.price_rows.length" class="hint">هنوز قیمتی ثبت نشده است.</div>
            <div v-else class="rows-stack">
              <div v-for="(row, idx) in form.price_rows" :key="row.name || `pr-${idx}`" class="setting-row price-row">
                <select v-model="row.price_list">
                  <option value="">لیست قیمت</option>
                  <option v-for="pl in priceLists" :key="`pl-${pl.name}`" :value="pl.name">{{ pl.title || pl.name }}</option>
                </select>
                <input v-model.number="row.rate" type="number" min="0" placeholder="قیمت (ریال)" />
                <input v-model.trim="row.currency" placeholder="ارز (مثال: IRR)" />
                <button class="mini danger" type="button" @click="removePriceRow(idx)">حذف</button>
              </div>
            </div>
            <p class="hint">در صورت خالی‌بودن ارز، ارز پیش‌فرض لیست قیمت استفاده می‌شود.</p>
          </article>

          <article class="settings-box">
            <div class="settings-head">
              <h3>جدول ویژگی‌ها</h3>
              <button class="ghost mini-add" type="button" @click="addFeatureRow">افزودن ردیف</button>
            </div>
            <div v-if="!form.feature_rows.length" class="hint">هنوز ویژگی سفارشی ثبت نشده است.</div>
            <div v-else class="rows-stack">
              <div v-for="(row, idx) in form.feature_rows" :key="`ft-${idx}`" class="setting-row feature-row">
                <input v-model.trim="row.label" placeholder="عنوان ویژگی (مثلا جنس بدنه)" />
                <input v-model.trim="row.value" placeholder="مقدار ویژگی (مثلا چوب راش)" />
                <button class="mini danger" type="button" @click="removeFeatureRow(idx)">حذف</button>
              </div>
            </div>
          </article>

          <article class="images-box">
            <div class="images-head">
              <h3>تصاویر محصول</h3>
              <div class="actions">
                <button class="ghost" :disabled="uploadingImage || !canEditProduct" @click="openUploadPicker">
                  {{ uploadingImage ? 'در حال آپلود...' : 'آپلود تصویر' }}
                </button>
                <button class="ghost" :disabled="mediaLoading || !canEditProduct" @click="toggleMediaBrowser">
                  {{ showMediaBrowser ? 'بستن فایل‌های سیستم' : 'انتخاب از فایل‌های سیستم' }}
                </button>
                <input ref="fileInput" class="hidden-file" type="file" accept="image/*" @change="uploadAndAttachImage" />
              </div>
            </div>

            <p v-if="imageError" class="save-msg error">{{ imageError }}</p>

            <div v-if="selectedProduct.images?.length" class="images-grid">
              <article v-for="img in selectedProduct.images" :key="img.name || img.file_url" class="image-card">
                <img :src="img.file_url" :alt="img.file_name || 'تصویر محصول'" @error="onImgError" />
                <small :title="img.file_name">{{ img.file_name || img.file_url }}</small>
                <div class="image-actions">
                  <button
                    class="mini"
                    :class="{ primary: normalizeUrl(form.image) === normalizeUrl(img.file_url) }"
                    :disabled="!canEditProduct"
                    @click="setPrimaryImage(img.file_url)"
                  >
                    تصویر اصلی
                  </button>
                  <button class="mini danger" :disabled="!canEditProduct" @click="removeImage(img)">حذف</button>
                </div>
              </article>
            </div>
            <p v-else class="hint">برای این محصول هنوز تصویری ثبت نشده است.</p>

            <div v-if="showMediaBrowser" class="media-browser">
              <div class="media-toolbar">
                <input v-model.trim="mediaSearch" placeholder="جستجو در فایل‌های سیستم" @keydown.enter.prevent="loadMediaFiles" />
                <button class="ghost" :disabled="mediaLoading" @click="loadMediaFiles">
                  {{ mediaLoading ? 'در حال دریافت...' : 'جستجو' }}
                </button>
              </div>
              <div v-if="mediaLoading" class="state">در حال دریافت فایل‌ها...</div>
              <div v-else-if="!mediaFiles.length" class="state">فایل تصویری یافت نشد.</div>
              <div v-else class="media-grid">
                <button
                  v-for="row in mediaFiles"
                  :key="row.name"
                  class="media-card"
                  @click="attachExistingImage(row.file_url)"
                >
                  <img :src="row.file_url" :alt="row.file_name || 'تصویر'" @error="onImgError" />
                  <small>{{ row.file_name || row.file_url }}</small>
                </button>
              </div>
            </div>
          </article>
        </template>
      </section>
    </div>

    <!-- Mobile product detail overlay -->
    <ManagementProductDetail
      v-if="isMobile && selectedProduct"
      :product="selectedProduct"
      :item-groups="itemGroups"
      :price-lists="priceLists"
      @close="selectedCode = ''"
      @save="onProductSave"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import ManagementProductViewSwitcher from '../components/management/ManagementProductViewSwitcher.vue'
import ManagementProductGridView from '../components/management/ManagementProductGridView.vue'
import ManagementProductListView from '../components/management/ManagementProductListView.vue'
import ManagementProductTableView from '../components/management/ManagementProductTableView.vue'
import ManagementProductDetail from '../components/management/ManagementProductDetail.vue'

const isMobile = ref(window.innerWidth <= 900)

function checkMobile() {
  isMobile.value = window.innerWidth <= 900
}

onMounted(() => {
  window.addEventListener('resize', checkMobile)
})

function onSelectProduct(code) {
  selectedCode.value = code
}

async function onProductSave(formData, onSuccess, onError) {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.save_management_product', {
      item_code: selectedProduct.value.item_code,
      payload: {
        item_name: formData.item_name,
        item_group: formData.item_group,
        description: formData.description,
        show_on_site: formData.show_on_site,
        disabled: formData.disabled,
        image: formData.image,
        price_rows: formData.price_rows,
        deleted_price_names: deletedPriceNames.value,
        feature_rows: formData.feature_rows,
      },
    })
    upsertProduct(result.product)
    fillForm(result.product)
    deletedPriceNames.value = []
    saveSuccess.value = 'تغییرات ذخیره شد.'
    onSuccess?.()
  } catch (err) {
    saveError.value = err?.message || 'ذخیره با خطا مواجه شد.'
    onError?.(err?.message)
  } finally {
    saving.value = false
  }
}
import { hasManagementCapability } from '../utils/managementAccess'

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const saveError = ref('')
const saveSuccess = ref('')
const imageError = ref('')

const products = ref([])
const total = ref(0)
const itemGroups = ref([])
const priceLists = ref([])
const selectedCode = ref('')
const listViewMode = ref('grid')
const deletedPriceNames = ref([])
const LIST_VIEW_STORAGE_KEY = 'mysite.management.products.list_view_mode'

const filters = ref({
  search: '',
  status: 'all',
  item_group: '',
  limit: 120,
  offset: 0,
})

const form = ref({
  item_name: '',
  item_group: '',
  description: '',
  show_on_site: true,
  disabled: false,
  image: '',
  price_rows: [],
  feature_rows: [],
})

const showMediaBrowser = ref(false)
const mediaLoading = ref(false)
const mediaSearch = ref('')
const mediaFiles = ref([])
const fileInput = ref(null)
const uploadingImage = ref(false)
const workflowRef = ref({ name: '', state: '' })
const workflowLoading = ref(false)

const canEditProduct = computed(() => hasManagementCapability('product.edit'))
const canReviewProduct = computed(() => hasManagementCapability('product.review'))
const canPublishProduct = computed(() => hasManagementCapability('product.publish'))

const WORKFLOW_ACTION_META = {
  submit_review: { key: 'submit_review', label: 'ارسال برای بازبینی', danger: false },
  return_to_draft: { key: 'return_to_draft', label: 'بازگشت به پیش‌نویس', danger: false },
  approve: { key: 'approve', label: 'تایید', danger: false },
  reject: { key: 'reject', label: 'رد', danger: true },
  publish: { key: 'publish', label: 'انتشار', danger: false },
  cancel: { key: 'cancel', label: 'لغو', danger: true },
}

const selectedProduct = computed(() => products.value.find((row) => row.item_code === selectedCode.value) || null)
const workflowActions = computed(() => {
  const state = String(workflowRef.value?.state || '').trim()
  if (!workflowRef.value?.name || !state) return []
  if (state === 'Draft') {
    return canEditProduct.value ? [WORKFLOW_ACTION_META.submit_review, WORKFLOW_ACTION_META.cancel] : []
  }
  if (state === 'In Review') {
    const actions = []
    if (canReviewProduct.value) {
      actions.push(WORKFLOW_ACTION_META.return_to_draft, WORKFLOW_ACTION_META.approve, WORKFLOW_ACTION_META.reject)
    }
    if (canPublishProduct.value) {
      actions.push(WORKFLOW_ACTION_META.cancel)
    }
    return actions
  }
  if (state === 'Approved') {
    return canPublishProduct.value ? [WORKFLOW_ACTION_META.publish, WORKFLOW_ACTION_META.cancel] : []
  }
  return []
})

const toFa = (value) => Number(value || 0).toLocaleString('fa-IR')

function normalizeUrl(value) {
  return String(value || '').trim().replace('/private/files/', '/files/')
}

function onImgError(event) {
  if (!event?.target) return
  event.target.style.display = 'none'
}

function normalizeFeatureRows(rows) {
  if (!Array.isArray(rows)) return []
  return rows
    .map((row) => ({
      label: String(row?.label || row?.name || '').trim(),
      value: String(row?.value || row?.content || '').trim(),
    }))
    .filter((row) => row.label || row.value)
}

function normalizePriceRows(rows) {
  if (!Array.isArray(rows)) return []
  return rows
    .map((row) => ({
      name: String(row?.name || '').trim(),
      price_list: String(row?.price_list || '').trim(),
      rate: Number(row?.rate || 0),
      currency: String(row?.currency || '').trim(),
      uom: String(row?.uom || '').trim(),
      selling: row?.selling !== false,
      buying: Boolean(row?.buying),
    }))
    .filter((row) => row.price_list)
}

function fillForm(product) {
  if (!product) {
    form.value = {
      item_name: '',
      item_group: '',
      description: '',
      show_on_site: true,
      disabled: false,
      image: '',
      price_rows: [],
      feature_rows: [],
    }
    return
  }
  form.value = {
    item_name: product.item_name || '',
    item_group: product.item_group || '',
    description: product.description || '',
    show_on_site: Boolean(product.show_on_site),
    disabled: Boolean(product.disabled),
    image: normalizeUrl(product.image || ''),
    price_rows: normalizePriceRows(product.price_rows || []),
    feature_rows: normalizeFeatureRows(product.feature_rows || []),
  }
}

function upsertProduct(product) {
  if (!product || !product.item_code) return
  const idx = products.value.findIndex((row) => row.item_code === product.item_code)
  if (idx === -1) {
    products.value.unshift(product)
  } else {
    products.value[idx] = product
  }
}

async function getJson(url) {
  const response = await fetch(url, { credentials: 'same-origin' })
  const payload = await response.json()
  if (!response.ok || payload.exception || payload.exc_type) {
    throw new Error(payload?.message || 'request_failed')
  }
  return payload.message || payload
}

async function postJson(url, body = {}) {
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
    },
    body: JSON.stringify(body),
  })
  const payload = await response.json()
  if (!response.ok || payload.exception || payload.exc_type) {
    throw new Error(payload?.message || 'request_failed')
  }
  return payload.message || payload
}

function applyWorkflowResponse(result, fallbackMessage) {
  if (result?.workflow_enforced && result?.change_request) {
    workflowRef.value = {
      name: String(result.change_request || '').trim(),
      state: String(result.state || 'Draft').trim() || 'Draft',
    }
    saveSuccess.value = `درخواست تغییر ${workflowRef.value.name} با وضعیت ${workflowRef.value.state} ثبت شد.`
    return true
  }
  if (fallbackMessage) {
    saveSuccess.value = fallbackMessage
  }
  return false
}

function matchesCurrentProductRequest(row) {
  const targetType = String(row?.target_type || '')
  if (!targetType.startsWith('product_')) return false
  return String(row?.target_key || '').trim() === String(selectedCode.value || '').trim()
}

async function loadLatestWorkflowRequest() {
  if (!selectedCode.value || !canEditProduct.value) {
    workflowRef.value = { name: '', state: '' }
    return
  }
  try {
    const result = await getJson('/api/method/mysite.api.list_management_change_requests?module_key=product&limit=120')
    const rows = Array.isArray(result?.items) ? result.items : []
    const found = rows.find((row) => matchesCurrentProductRequest(row))
    workflowRef.value = found
      ? { name: String(found.name || ''), state: String(found.state || '') }
      : { name: '', state: '' }
  } catch (error) {
    // ignore background lookup failures
  }
}

async function runWorkflowAction(action) {
  const requestName = String(workflowRef.value?.name || '').trim()
  if (!requestName || !action) return
  workflowLoading.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.transition_management_change_request', {
      name: requestName,
      action,
    })
    const state = String(result?.change_request?.state || '').trim()
    if (state) {
      workflowRef.value = { ...workflowRef.value, state }
    }
    saveSuccess.value = `وضعیت درخواست به ${state || 'نامشخص'} تغییر کرد.`
    if (action === 'publish') {
      await loadProducts(false)
    }
  } catch (error) {
    saveError.value = error?.message || 'خطا در تغییر وضعیت درخواست.'
  } finally {
    workflowLoading.value = false
  }
}

async function loadProducts(forceReset = false) {
  loading.value = true
  error.value = ''
  try {
    if (forceReset) filters.value.offset = 0
    const params = new URLSearchParams({
      search: filters.value.search || '',
      status: filters.value.status || 'all',
      item_group: filters.value.item_group || '',
      limit: String(filters.value.limit || 120),
      offset: String(filters.value.offset || 0),
    })
    const result = await getJson(`/api/method/mysite.api.get_management_products?${params.toString()}`)
    products.value = Array.isArray(result.items) ? result.items : []
    total.value = Number(result.total || 0)
    itemGroups.value = Array.isArray(result.item_groups) ? result.item_groups : []
    priceLists.value = Array.isArray(result.price_lists) ? result.price_lists : []

    if (!selectedCode.value && products.value.length) {
      selectedCode.value = products.value[0].item_code
    } else if (selectedCode.value && !products.value.some((row) => row.item_code === selectedCode.value)) {
      selectedCode.value = products.value[0]?.item_code || ''
    }
  } catch (err) {
    error.value = err?.message || 'خطا در دریافت لیست محصولات.'
  } finally {
    loading.value = false
  }
}

async function saveProduct() {
  if (!canEditProduct.value) return
  if (!selectedProduct.value) return
  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  const sanitizedPrices = normalizePriceRows(form.value.price_rows || [])
  const sanitizedFeatures = normalizeFeatureRows(form.value.feature_rows || [])
  try {
    const result = await postJson('/api/method/mysite.api.save_management_product', {
      item_code: selectedProduct.value.item_code,
      payload: {
        item_name: form.value.item_name,
        item_group: form.value.item_group,
        description: form.value.description,
        show_on_site: Boolean(form.value.show_on_site),
        disabled: Boolean(form.value.disabled),
        image: normalizeUrl(form.value.image || ''),
        price_rows: sanitizedPrices,
        deleted_price_names: deletedPriceNames.value,
        feature_rows: sanitizedFeatures,
      },
    })
    if (applyWorkflowResponse(result, '')) {
      await loadLatestWorkflowRequest()
      return
    }
    upsertProduct(result.product)
    fillForm(result.product)
    deletedPriceNames.value = []
    saveSuccess.value = 'تغییرات محصول ذخیره شد.'
    await loadLatestWorkflowRequest()
  } catch (err) {
    saveError.value = err?.message || 'ذخیره محصول با خطا مواجه شد.'
  } finally {
    saving.value = false
  }
}

function addPriceRow() {
  const fallbackPriceList = priceLists.value.find((row) => row?.is_default)?.name || priceLists.value[0]?.name || ''
  form.value.price_rows.push({
    name: '',
    price_list: fallbackPriceList,
    rate: 0,
    currency: 'IRR',
    uom: '',
    selling: true,
    buying: false,
  })
}

function removePriceRow(index) {
  const row = form.value.price_rows[index]
  if (!row) return
  if (row.name) {
    deletedPriceNames.value.push(row.name)
  }
  form.value.price_rows.splice(index, 1)
}

function addFeatureRow() {
  form.value.feature_rows.push({ label: '', value: '' })
}

function removeFeatureRow(index) {
  form.value.feature_rows.splice(index, 1)
}

async function setPrimaryImage(fileUrl) {
  if (!canEditProduct.value) return
  if (!selectedProduct.value || !fileUrl) return
  imageError.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.set_management_product_primary_image', {
      item_code: selectedProduct.value.item_code,
      payload: { item_code: selectedProduct.value.item_code, file_url: normalizeUrl(fileUrl) },
    })
    if (applyWorkflowResponse(result, '')) {
      await loadLatestWorkflowRequest()
      return
    }
    upsertProduct(result.product)
    fillForm(result.product)
    await loadLatestWorkflowRequest()
  } catch (err) {
    imageError.value = err?.message || 'تنظیم تصویر اصلی با خطا مواجه شد.'
  }
}

async function attachExistingImage(fileUrl) {
  if (!canEditProduct.value) return
  if (!selectedProduct.value || !fileUrl) return
  imageError.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.attach_management_product_image', {
      item_code: selectedProduct.value.item_code,
      file_url: normalizeUrl(fileUrl),
      is_primary: !selectedProduct.value.image,
    })
    if (applyWorkflowResponse(result, '')) {
      await loadLatestWorkflowRequest()
      return
    }
    upsertProduct(result.product)
    fillForm(result.product)
    saveSuccess.value = 'تصویر به محصول اضافه شد.'
    await loadLatestWorkflowRequest()
  } catch (err) {
    imageError.value = err?.message || 'افزودن تصویر با خطا مواجه شد.'
  }
}

async function removeImage(imageRow) {
  if (!canEditProduct.value) return
  if (!selectedProduct.value || !imageRow) return
  imageError.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.remove_management_product_image', {
      item_code: selectedProduct.value.item_code,
      file_name: imageRow.name || '',
      file_url: normalizeUrl(imageRow.file_url || ''),
    })
    if (applyWorkflowResponse(result, '')) {
      await loadLatestWorkflowRequest()
      return
    }
    upsertProduct(result.product)
    fillForm(result.product)
    saveSuccess.value = 'تصویر حذف شد.'
    await loadLatestWorkflowRequest()
  } catch (err) {
    imageError.value = err?.message || 'حذف تصویر با خطا مواجه شد.'
  }
}

function openUploadPicker() {
  if (!canEditProduct.value) return
  imageError.value = ''
  if (!fileInput.value) return
  fileInput.value.value = ''
  fileInput.value.click()
}

async function uploadAndAttachImage(event) {
  if (!canEditProduct.value) return
  const file = event?.target?.files?.[0]
  if (!file || !selectedProduct.value) return
  uploadingImage.value = true
  imageError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', '0')
    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: formData,
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'آپلود تصویر با خطا مواجه شد.')
    }
    const uploaded = payload.message || payload
    const fileUrl = uploaded?.file_url || ''
    if (!fileUrl) {
      throw new Error('نشانی فایل آپلودشده دریافت نشد.')
    }
    await attachExistingImage(fileUrl)
    if (showMediaBrowser.value) {
      await loadMediaFiles()
    }
  } catch (err) {
    imageError.value = err?.message || 'آپلود تصویر با خطا مواجه شد.'
  } finally {
    uploadingImage.value = false
  }
}

async function loadMediaFiles() {
  mediaLoading.value = true
  imageError.value = ''
  try {
    const params = new URLSearchParams({
      limit: '120',
      search: mediaSearch.value || '',
    })
    const result = await getJson(`/api/method/mysite.api.list_management_media_images?${params.toString()}`)
    mediaFiles.value = Array.isArray(result.items) ? result.items : []
  } catch (err) {
    mediaFiles.value = []
    imageError.value = err?.message || 'دریافت فایل‌های سیستم با خطا مواجه شد.'
  } finally {
    mediaLoading.value = false
  }
}

async function toggleMediaBrowser() {
  showMediaBrowser.value = !showMediaBrowser.value
  if (showMediaBrowser.value && !mediaFiles.value.length) {
    await loadMediaFiles()
  }
}

watch(selectedProduct, (product) => {
  fillForm(product)
  deletedPriceNames.value = []
  saveError.value = ''
  saveSuccess.value = ''
  imageError.value = ''
  workflowRef.value = { name: '', state: '' }
  if (product?.item_code) {
    loadLatestWorkflowRequest()
  }
}, { immediate: true })

onMounted(() => {
  try {
    const savedMode = localStorage.getItem(LIST_VIEW_STORAGE_KEY)
    if (savedMode === 'grid' || savedMode === 'list' || savedMode === 'table') {
      listViewMode.value = savedMode
    }
  } catch (error) {
    // Ignore storage errors.
  }
  loadProducts()
})

watch(listViewMode, (value) => {
  try {
    localStorage.setItem(LIST_VIEW_STORAGE_KEY, value)
  } catch (error) {
    // Ignore storage errors.
  }
})
</script>

<style scoped>
.products-page {
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  max-width: 100vw;
  background: var(--admin-bg);
  color: var(--text-main);
}

.products-shell {
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-4);
  display: grid;
  grid-template-columns: 260px 1fr 480px;
  gap: var(--space-3);
  overflow-x: hidden;
  box-sizing: border-box;
}

.sidebar,
.list-area,
.detail-area {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.sidebar {
  padding: var(--space-4);
  display: grid;
  align-content: start;
  gap: var(--space-3);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-dot {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.brand-row strong {
  display: block;
  font-size: var(--text-md);
}

.brand-row small {
  color: var(--admin-text-soft);
  font-size: var(--text-xs);
}

.side-nav {
  display: grid;
  gap: var(--space-2);
}

.nav-item {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  text-decoration: none;
  font-family: inherit;
  font-size: var(--text-base);
  padding: 0 10px;
  display: flex;
  align-items: center;
}

.nav-item.active {
  border-color: transparent;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}

.side-note {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  background: var(--admin-chip-bg);
}

.side-note p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
  line-height: 1.8;
}

.list-area {
  padding: var(--space-4);
  display: grid;
  align-content: start;
  gap: var(--space-3);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-2);
}

.list-header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.list-header h1 {
  margin: 0;
  font-size: var(--text-2xl);
}

.list-header p {
  margin: 6px 0 0;
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
}

.filters {
  display: grid;
  grid-template-columns: minmax(140px, 1fr) minmax(0, 150px) minmax(0, 180px) auto;
  gap: var(--space-2);
  min-width: 0;
}

.filters input,
.filters select,
.ghost {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
}

.ghost {
  cursor: pointer;
  font-weight: 700;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: var(--space-3);
}

.product-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  cursor: pointer;
}

.product-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.thumb {
  height: 106px;
  border-radius: var(--radius-md);
  border: 1px solid var(--admin-border);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
}

.product-card h3 {
  margin: 0;
  font-size: var(--text-md);
  line-height: 1.5;
}

.code,
.group {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.code {
  direction: ltr;
  text-align: left;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-row small {
  color: var(--admin-text-soft);
  font-size: var(--text-xs);
}

.price-chip {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--accent-gold);
  font-weight: 700;
}

.status {
  border-radius: var(--radius-pill);
  padding: 2px 8px;
  font-size: var(--text-xs);
  border: 1px solid var(--admin-border);
}

.status.active {
  color: #bbf7d0;
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.12);
}

.status.hidden {
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.12);
}

.status.disabled {
  color: #fecaca;
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
}

.detail-area {
  padding: var(--space-4);
  display: grid;
  align-content: start;
  gap: var(--space-3);
  position: sticky;
  top: 12px;
  max-height: calc(100vh - 24px);
  overflow: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-2);
}

.detail-header h2 {
  margin: 0;
  font-size: var(--text-lg);
}

.detail-header code {
  display: block;
  margin-top: 4px;
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.workflow-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}

.form-grid label {
  display: grid;
  gap: var(--space-1);
}

.form-grid .wide {
  grid-column: 1 / -1;
}

.form-grid span {
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.form-grid input,
.form-grid textarea {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
  font-size: var(--text-base);
}

.form-grid textarea {
  min-height: var(--touch-min);
  resize: vertical;
}

.switch {
  display: inline-flex !important;
  align-items: center;
  gap: 7px !important;
}

.switch input {
  min-height: auto;
  width: 17px;
  height: 17px;
}

.settings-box {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.settings-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.settings-head h3 {
  margin: 0;
  font-size: var(--text-md);
}

.mini-add {
  min-height: var(--touch-min);
  padding: 0 10px;
  font-size: var(--text-sm);
}

.rows-stack {
  display: grid;
  gap: var(--space-2);
}

.setting-row {
  display: grid;
  gap: var(--space-2);
}

.setting-row input,
.setting-row select {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  min-height: var(--touch-min);
  padding: 0 9px;
  font-family: inherit;
  font-size: var(--text-sm);
}

.price-row {
  grid-template-columns: minmax(130px, 1fr) minmax(120px, 1fr) minmax(90px, 110px) auto;
}

.feature-row {
  grid-template-columns: minmax(110px, 0.7fr) minmax(0, 1fr) auto;
}

.images-box {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.images-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.images-head h3 {
  margin: 0;
  font-size: var(--text-md);
}

.actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.hidden-file {
  display: none;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: var(--space-2);
}

.image-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  padding: var(--space-1);
  display: grid;
  gap: var(--space-2);
}

.image-card img {
  width: 100%;
  height: 84px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.image-card small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-actions {
  display: flex;
  gap: var(--space-2);
}

.mini {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-sm);
  background: var(--admin-panel-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: var(--text-xs);
  min-height: var(--touch-min);
  padding: 0 8px;
  cursor: pointer;
}

.mini.primary {
  border-color: rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.14);
}

.mini.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.media-browser {
  border-top: 1px dashed var(--admin-border);
  padding-top: 8px;
  display: grid;
  gap: var(--space-2);
}

.media-toolbar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-2);
}

.media-toolbar input {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-2);
  max-height: 320px;
  overflow: auto;
}

.media-card {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: var(--radius-md);
  padding: var(--space-1);
  display: grid;
  gap: var(--space-2);
  cursor: pointer;
  text-align: right;
}

.media-card img {
  width: 100%;
  height: 74px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.media-card small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.save-msg {
  margin: 0;
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.save-msg.error {
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.save-msg.success {
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
}

.state {
  border: 1px dashed var(--admin-border);
  border-radius: var(--radius-lg);
  text-align: center;
  color: var(--admin-text-soft);
  padding: var(--space-5);
}

.state.error {
  color: #fecaca;
}

.hint {
  margin: 0;
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
}

@media (max-width: 1560px) {
  .products-shell {
    grid-template-columns: 220px 1fr;
  }

  .detail-area {
    grid-column: 1 / -1;
    position: static;
    max-height: none;
  }
}

@media (max-width: 1020px) {
  .products-shell {
    grid-template-columns: 1fr;
    padding: var(--space-3);
  }

  .sidebar {
    display: none;
  }

  .list-header {
    flex-direction: column;
  }

  .list-header-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .filters {
    grid-template-columns: 1fr 1fr;
  }

  .filters input {
    grid-column: 1 / -1;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .price-row,
  .feature-row {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    gap: var(--space-2);
  }

  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .media-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .products-shell {
    padding: var(--space-1);
    gap: var(--space-2);
  }

  .filters {
    grid-template-columns: 1fr;
  }

  .list-area,
  .detail-area {
    padding: var(--space-2);
  }

  .list-header h1 {
    font-size: var(--text-xl);
  }

  .images-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2);
  }

  .image-card img {
    height: 80px;
  }

  .media-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .media-card img {
    height: 56px;
  }

  .settings-box {
    padding: var(--space-2);
  }

  .price-row,
  .feature-row {
    grid-template-columns: 1fr;
    gap: var(--space-1);
  }

  .price-row select,
  .price-row input,
  .feature-row input {
    min-height: var(--touch-min);
  }
}
</style>
