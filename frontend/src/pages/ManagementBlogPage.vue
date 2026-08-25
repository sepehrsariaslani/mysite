<template>
  <div class="blog-admin-page" dir="rtl">
    <div class="blog-admin-shell">
      <aside class="sidebar">
        <div class="brand-row">
          <div class="brand-dot">ب</div>
          <div>
            <strong>مدیریت بلاگ</strong>
            <small>نوشتن و انتشار مقاله</small>
          </div>
        </div>

        <nav class="side-nav">
          <a class="nav-item" href="/mysite/management">مدیریت صفحات</a>
          <a class="nav-item" href="/mysite/management-products">مدیریت محصولات</a>
          <a class="nav-item active" href="/mysite/management-blog">مدیریت بلاگ</a>
          <a class="nav-item" href="/mysite/management-analytics">آنالیتیکس</a>
        </nav>

        <div class="side-note">
          <p>
            وضعیت‌های مقاله از قوانین سیستم پیروی می‌کند: پیش‌نویس، منتشرشده و ویژه.
          </p>
        </div>
      </aside>

      <section class="list-area">
        <header class="list-header">
          <div>
            <h1>مقاله‌ها</h1>
            <p>تعداد کل: {{ toFa(total) }}</p>
          </div>
          <div class="header-actions">
            <ManagementProductViewSwitcher v-model="listViewMode" />
            <button class="ghost" :disabled="loadingList || saving || !canEditContent" @click="createNewDraft">
              پیش‌نویس جدید
            </button>
            <button class="ghost" :disabled="loadingList" @click="loadPosts(true)">
              {{ loadingList ? 'در حال دریافت...' : 'بروزرسانی' }}
            </button>
          </div>
        </header>

        <div class="filters">
          <input
            v-model.trim="filters.search"
            placeholder="جستجو در عنوان، مسیر یا متن"
            @keydown.enter.prevent="loadPosts(true)"
          />
          <select v-model="filters.status" @change="loadPosts(true)">
            <option value="all">همه وضعیت‌ها</option>
            <option value="draft">پیش‌نویس</option>
            <option value="published">منتشرشده</option>
            <option value="featured">ویژه</option>
          </select>
          <select v-model="filters.category" @change="loadPosts(true)">
            <option value="all">همه دسته‌ها</option>
            <option v-for="cat in categories" :key="`cat-${cat}`" :value="cat">{{ cat }}</option>
          </select>
        </div>

        <div v-if="loadingList" class="state">در حال دریافت لیست بلاگ‌ها...</div>
        <div v-else-if="listError" class="state error">{{ listError }}</div>
        <div v-else-if="!posts.length" class="state">مقاله‌ای یافت نشد.</div>

        <div v-else-if="listViewMode === 'list'" class="post-list">
          <article
            v-for="row in posts"
            :key="row.name"
            class="post-card"
            :class="{ active: selectedName === row.name }"
            @click="selectedName = row.name"
          >
            <div class="post-top">
              <h3>{{ row.title || 'بدون عنوان' }}</h3>
              <span class="status" :class="row.status_key">{{ row.status_label }}</span>
            </div>
            <p class="excerpt">{{ row.excerpt || 'بدون خلاصه' }}</p>
            <div class="post-meta">
              <small>{{ row.blog_category || 'بدون دسته' }}</small>
              <small>{{ row.published_on ? formatDate(row.published_on) : 'بدون تاریخ انتشار' }}</small>
              <small>{{ toFa(row.word_count || 0) }} کلمه</small>
            </div>
          </article>
        </div>

        <div v-else-if="listViewMode === 'grid'" class="post-grid">
          <article
            v-for="row in posts"
            :key="row.name"
            class="post-card"
            :class="{ active: selectedName === row.name }"
            @click="selectedName = row.name"
          >
            <div class="post-top">
              <h3>{{ row.title || 'بدون عنوان' }}</h3>
              <span class="status" :class="row.status_key">{{ row.status_label }}</span>
            </div>
            <p class="excerpt">{{ row.excerpt || 'بدون خلاصه' }}</p>
            <div class="post-meta">
              <small>{{ row.blog_category || 'بدون دسته' }}</small>
              <small>{{ row.published_on ? formatDate(row.published_on) : 'بدون تاریخ انتشار' }}</small>
              <small>{{ toFa(row.word_count || 0) }} کلمه</small>
            </div>
          </article>
        </div>

        <div v-else class="post-table-wrap">
          <table>
            <thead>
              <tr>
                <th>عنوان</th>
                <th>دسته</th>
                <th>وضعیت</th>
                <th>تاریخ انتشار</th>
                <th>کلمات</th>
                <th>اقدام</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in posts"
                :key="row.name"
                :class="{ active: selectedName === row.name }"
                @click="selectedName = row.name"
              >
                <td class="title-cell">{{ row.title || 'بدون عنوان' }}</td>
                <td>{{ row.blog_category || 'بدون دسته' }}</td>
                <td><span class="status" :class="row.status_key">{{ row.status_label }}</span></td>
                <td>{{ row.published_on ? formatDate(row.published_on) : 'بدون تاریخ انتشار' }}</td>
                <td>{{ toFa(row.word_count || 0) }}</td>
                <td><button class="mini" type="button" @click.stop="selectedName = row.name">انتخاب</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="editor-area">
        <div v-if="!selectedName" class="state">برای شروع، یک پیش‌نویس جدید بسازید یا مقاله‌ای را انتخاب کنید.</div>

        <template v-else>
          <header class="editor-header">
            <div>
              <h2>{{ form.title || 'مقاله بدون عنوان' }}</h2>
              <a v-if="form.preview_url" :href="form.preview_url" target="_blank" rel="noreferrer">پیش‌نمایش صفحه بلاگ</a>
              <p v-if="workflowRef.name" class="muted">
                وضعیت گردش‌کار: <b>{{ workflowRef.state || 'Draft' }}</b> | درخواست: {{ workflowRef.name }}
              </p>
            </div>
            <div class="editor-actions">
              <button class="ghost" :disabled="saving || loadingDetail || !canEditContent" @click="savePost()">
                {{ saving ? 'در حال ذخیره...' : 'ذخیره پیش‌نویس' }}
              </button>
              <button
                class="ghost"
                :disabled="saving || loadingDetail || !canEditContent"
                @click="togglePublishState"
              >
                {{ form.published ? 'برگشت به پیش‌نویس' : 'انتشار' }}
              </button>
              <button class="mini danger" :disabled="deleting || saving || !canEditContent" @click="deletePost">
                {{ deleting ? 'در حال حذف...' : 'حذف مقاله' }}
              </button>
            </div>
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

          <p v-if="detailError" class="save-msg error">{{ detailError }}</p>
          <p v-else-if="saveError" class="save-msg error">{{ saveError }}</p>
          <p v-else-if="saveSuccess" class="save-msg success">{{ saveSuccess }}</p>

          <div class="meta-grid">
            <label>
              <span>عنوان</span>
              <input v-model.trim="form.title" placeholder="عنوان مقاله" />
            </label>
            <label>
              <span>مسیر</span>
              <input v-model.trim="form.route" dir="ltr" placeholder="blog-post-route" />
            </label>
            <label>
              <span>دسته‌بندی</span>
              <input v-model.trim="form.blog_category" list="blog-category-list" placeholder="دسته" />
              <datalist id="blog-category-list">
                <option v-for="cat in categories" :key="`cat-opt-${cat}`" :value="cat" />
              </datalist>
            </label>
            <label>
              <span>تاریخ انتشار</span>
              <input v-model="form.published_on" type="date" />
            </label>
          </div>

          <div class="switch-row">
            <label class="switch"><input type="checkbox" v-model="form.published" /><span>منتشر شود</span></label>
            <label class="switch"><input type="checkbox" v-model="form.featured" /><span>ویژه</span></label>
            <label class="switch"><input type="checkbox" v-model="form.disable_comments" /><span>بستن دیدگاه</span></label>
            <label class="switch"><input type="checkbox" v-model="form.disable_likes" /><span>بستن لایک</span></label>
            <label class="switch"><input type="checkbox" v-model="form.hide_cta" /><span>عدم نمایش CTA</span></label>
          </div>

          <article class="editor-card">
            <div class="editor-toolbar">
              <button type="button" @click="formatBlock('h2')">H2</button>
              <button type="button" @click="formatBlock('h3')">H3</button>
              <button type="button" @click="execCommand('bold')">B</button>
              <button type="button" @click="execCommand('italic')">I</button>
              <button type="button" @click="execCommand('insertUnorderedList')">• لیست</button>
              <button type="button" @click="formatBlock('blockquote')">نقل‌قول</button>
              <button type="button" @click="insertDivider">خط جداکننده</button>
              <button type="button" @click="insertImageByPrompt">تصویر</button>
              <button type="button" @click="insertLinkByPrompt">لینک</button>
            </div>

            <div class="editor-surface">
              <div
                ref="editorRef"
                class="notion-editor"
                contenteditable="true"
                data-placeholder="شروع نوشتن... با / می‌توانید از ابزارها استفاده کنید"
                @input="onEditorInput"
              ></div>
            </div>
          </article>

          <article class="settings-card">
            <h3>تنظیمات تکمیلی مقاله</h3>
            <div class="meta-grid two-col">
              <label>
                <span>خلاصه (intro)</span>
                <textarea v-model.trim="form.blog_intro" rows="3"></textarea>
              </label>
              <label>
                <span>زیرتیتر</span>
                <textarea v-model.trim="form.subtitle" rows="3"></textarea>
              </label>
              <label>
                <span>Meta Title</span>
                <input v-model.trim="form.meta_title" />
              </label>
              <label>
                <span>Meta Description</span>
                <textarea v-model.trim="form.meta_description" rows="3"></textarea>
              </label>
              <label>
                <span>Meta Image</span>
                <input v-model.trim="form.meta_image" dir="ltr" />
              </label>
              <label>
                <span>اعتبار عکس کاور</span>
                <input v-model.trim="form.cover_credit" />
              </label>
              <label>
                <span>CTA Label</span>
                <input v-model.trim="form.cta_label" />
              </label>
              <label>
                <span>CTA Link</span>
                <input v-model.trim="form.cta_link" dir="ltr" />
              </label>
              <label>
                <span>Focus Keyword</span>
                <input v-model.trim="form.focus_keyword" />
              </label>
              <label>
                <span>Secondary Keywords</span>
                <input v-model.trim="form.secondary_keywords" />
              </label>
              <label>
                <span>زمان مطالعه</span>
                <input v-model.trim="form.read_time" placeholder="مثال: ۶ دقیقه" />
              </label>
            </div>

            <div class="meta-actions">
              <button class="ghost" :disabled="mediaUploading" @click="openUploadPicker('meta')">
                {{ mediaUploading ? 'در حال آپلود...' : 'آپلود تصویر کاور/متا' }}
              </button>
              <button class="ghost" :disabled="mediaUploading" @click="openUploadPicker('editor')">
                {{ mediaUploading ? 'در حال آپلود...' : 'آپلود و درج در محتوا' }}
              </button>
              <button class="ghost" :disabled="mediaLoading" @click="toggleMediaBrowser">
                {{ showMediaBrowser ? 'بستن فایل‌های سیستم' : 'انتخاب از فایل‌های سیستم' }}
              </button>
              <input ref="mediaUploadInput" class="hidden-file" type="file" accept="image/*" @change="uploadImage" />
            </div>

            <p v-if="mediaError" class="save-msg error">{{ mediaError }}</p>
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
                  @click="useMediaImage(row.file_url)"
                >
                  <img :src="row.file_url" :alt="row.file_name || 'تصویر'" />
                  <small>{{ row.file_name || row.file_url }}</small>
                </button>
              </div>
            </div>
          </article>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import ManagementProductViewSwitcher from '../components/management/ManagementProductViewSwitcher.vue'
import { hasManagementCapability } from '../utils/managementAccess'

const loadingList = ref(false)
const loadingDetail = ref(false)
const saving = ref(false)
const deleting = ref(false)
const mediaLoading = ref(false)
const mediaUploading = ref(false)

const listError = ref('')
const detailError = ref('')
const saveError = ref('')
const saveSuccess = ref('')
const mediaError = ref('')

const posts = ref([])
const categories = ref([])
const total = ref(0)
const selectedName = ref('')
const listViewMode = ref('list')
const LIST_VIEW_STORAGE_KEY = 'mysite.management.blog.list_view_mode'

const filters = ref({
  search: '',
  status: 'all',
  category: 'all',
  limit: 80,
  offset: 0,
})

const form = ref({
  name: '',
  title: '',
  route: '',
  blog_category: '',
  published: false,
  published_on: '',
  featured: false,
  disable_comments: false,
  disable_likes: false,
  hide_cta: false,
  blog_intro: '',
  subtitle: '',
  meta_title: '',
  meta_description: '',
  meta_image: '',
  cover_credit: '',
  cta_label: '',
  cta_link: '',
  focus_keyword: '',
  secondary_keywords: '',
  read_time: '',
  preview_url: '',
})

const editorRef = ref(null)
const editorHtml = ref('<p></p>')

const showMediaBrowser = ref(false)
const mediaSearch = ref('')
const mediaFiles = ref([])
const mediaUploadInput = ref(null)
const pendingUploadTarget = ref('meta')
const workflowRef = ref({ name: '', state: '' })
const workflowLoading = ref(false)

const canEditContent = computed(() => hasManagementCapability('content.edit'))
const canReviewContent = computed(() => hasManagementCapability('content.review'))
const canPublishContent = computed(() => hasManagementCapability('content.publish'))

const WORKFLOW_ACTION_META = {
  submit_review: { key: 'submit_review', label: 'ارسال برای بازبینی', danger: false },
  return_to_draft: { key: 'return_to_draft', label: 'بازگشت به پیش‌نویس', danger: false },
  approve: { key: 'approve', label: 'تایید', danger: false },
  reject: { key: 'reject', label: 'رد', danger: true },
  publish: { key: 'publish', label: 'انتشار', danger: false },
  cancel: { key: 'cancel', label: 'لغو', danger: true },
}

const toFa = (value) => Number(value || 0).toLocaleString('fa-IR')

const workflowActions = computed(() => {
  const state = String(workflowRef.value?.state || '').trim()
  if (!workflowRef.value?.name || !state) return []
  if (state === 'Draft') {
    return canEditContent.value ? [WORKFLOW_ACTION_META.submit_review, WORKFLOW_ACTION_META.cancel] : []
  }
  if (state === 'In Review') {
    const actions = []
    if (canReviewContent.value) {
      actions.push(WORKFLOW_ACTION_META.return_to_draft, WORKFLOW_ACTION_META.approve, WORKFLOW_ACTION_META.reject)
    }
    if (canPublishContent.value) {
      actions.push(WORKFLOW_ACTION_META.cancel)
    }
    return actions
  }
  if (state === 'Approved') {
    const actions = []
    if (canPublishContent.value) {
      actions.push(WORKFLOW_ACTION_META.publish, WORKFLOW_ACTION_META.cancel)
    }
    return actions
  }
  return []
})

function formatDate(value) {
  if (!value) return 'بدون تاریخ'
  try {
    return new Date(value).toLocaleDateString('fa-IR')
  } catch (error) {
    return value
  }
}

function normalizeHtml(html) {
  const raw = String(html || '')
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
    .trim()
  return raw || '<p></p>'
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

function matchesCurrentBlogRequest(row) {
  const targetType = String(row?.target_type || '')
  if (!['blog_post', 'blog_delete'].includes(targetType)) return false
  const key = String(row?.target_key || '').trim()
  if (!key) return false
  return key === String(selectedName.value || '').trim() || key === String(form.value.title || '').trim()
}

async function loadLatestWorkflowRequest() {
  if (!canEditContent.value) return
  if (!selectedName.value && !form.value.title) {
    workflowRef.value = { name: '', state: '' }
    return
  }
  try {
    const result = await getJson('/api/method/mysite.api.list_management_change_requests?module_key=content&limit=120')
    const rows = Array.isArray(result?.items) ? result.items : []
    const found = rows.find((row) => matchesCurrentBlogRequest(row))
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
      if (selectedName.value) {
        await loadPostDetail(selectedName.value)
      }
      await loadPosts(false)
    }
  } catch (error) {
    saveError.value = error?.message || 'خطا در تغییر وضعیت درخواست.'
  } finally {
    workflowLoading.value = false
  }
}

function fillForm(post) {
  if (!post) {
    form.value = {
      name: '',
      title: '',
      route: '',
      blog_category: '',
      published: false,
      published_on: '',
      featured: false,
      disable_comments: false,
      disable_likes: false,
      hide_cta: false,
      blog_intro: '',
      subtitle: '',
      meta_title: '',
      meta_description: '',
      meta_image: '',
      cover_credit: '',
      cta_label: '',
      cta_link: '',
      focus_keyword: '',
      secondary_keywords: '',
      read_time: '',
      preview_url: '',
    }
    editorHtml.value = '<p></p>'
    return
  }

  form.value = {
    name: post.name || '',
    title: post.title || '',
    route: post.route || '',
    blog_category: post.blog_category || '',
    published: Boolean(post.published),
    published_on: post.published_on ? String(post.published_on).slice(0, 10) : '',
    featured: Boolean(post.featured),
    disable_comments: Boolean(post.disable_comments),
    disable_likes: Boolean(post.disable_likes),
    hide_cta: Boolean(post.hide_cta),
    blog_intro: post.blog_intro || '',
    subtitle: post.subtitle || '',
    meta_title: post.meta_title || '',
    meta_description: post.meta_description || '',
    meta_image: post.meta_image || '',
    cover_credit: post.cover_credit || '',
    cta_label: post.cta_label || '',
    cta_link: post.cta_link || '',
    focus_keyword: post.focus_keyword || '',
    secondary_keywords: post.secondary_keywords || '',
    read_time: post.read_time || '',
    preview_url: post.preview_url || '',
  }
  editorHtml.value = normalizeHtml(post.body_html)
}

async function syncEditorSurface() {
  await nextTick()
  if (!editorRef.value) return
  editorRef.value.innerHTML = normalizeHtml(editorHtml.value)
}

function onEditorInput() {
  if (!editorRef.value) return
  editorHtml.value = normalizeHtml(editorRef.value.innerHTML)
}

function focusEditor() {
  if (!editorRef.value) return
  editorRef.value.focus()
}

function execCommand(command, value = null) {
  focusEditor()
  document.execCommand(command, false, value)
  onEditorInput()
}

function formatBlock(tag) {
  execCommand('formatBlock', tag)
}

function insertDivider() {
  execCommand('insertHTML', '<hr />')
}

function insertImageByPrompt() {
  const imageUrl = window.prompt('نشانی تصویر را وارد کنید:')
  if (!imageUrl) return
  execCommand('insertHTML', `<p><img src="${imageUrl}" alt="" /></p>`)
}

function insertLinkByPrompt() {
  const linkUrl = window.prompt('نشانی لینک را وارد کنید:')
  if (!linkUrl) return
  execCommand('createLink', linkUrl)
}

async function loadPosts(resetOffset = false) {
  loadingList.value = true
  listError.value = ''
  saveSuccess.value = ''

  try {
    if (resetOffset) filters.value.offset = 0
    const params = new URLSearchParams({
      search: filters.value.search || '',
      status: filters.value.status || 'all',
      category: filters.value.category || 'all',
      limit: String(filters.value.limit || 80),
      offset: String(filters.value.offset || 0),
    })
    const result = await getJson(`/api/method/mysite.api.get_management_blog_posts?${params.toString()}`)
    posts.value = Array.isArray(result.items) ? result.items : []
    total.value = Number(result.total || 0)
    categories.value = Array.isArray(result.categories) ? result.categories : []

    if (!selectedName.value && posts.value.length) {
      selectedName.value = posts.value[0].name
    } else if (selectedName.value && !posts.value.some((row) => row.name === selectedName.value)) {
      selectedName.value = posts.value[0]?.name || ''
    }
  } catch (error) {
    listError.value = error?.message || 'خطا در دریافت لیست بلاگ‌ها.'
  } finally {
    loadingList.value = false
  }
}

async function loadPostDetail(postName) {
  const name = String(postName || '').trim()
  if (!name) {
    fillForm(null)
    await syncEditorSurface()
    return
  }

  loadingDetail.value = true
  detailError.value = ''
  try {
    const result = await getJson(`/api/method/mysite.api.get_management_blog_post_detail?name=${encodeURIComponent(name)}`)
    if (!result?.post) {
      throw new Error('جزئیات مقاله پیدا نشد.')
    }
    fillForm(result.post)
    await syncEditorSurface()
    await loadLatestWorkflowRequest()
  } catch (error) {
    detailError.value = error?.message || 'خطا در دریافت جزئیات مقاله.'
  } finally {
    loadingDetail.value = false
  }
}

async function savePost(publishOverride = null) {
  if (!canEditContent.value) return
  if (!selectedName.value && !form.value.title?.trim()) {
    saveError.value = 'برای ذخیره، عنوان مقاله الزامی است.'
    return
  }

  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const payload = {
      name: form.value.name,
      title: form.value.title,
      route: form.value.route,
      blog_category: form.value.blog_category,
      published: publishOverride === null ? Boolean(form.value.published) : Boolean(publishOverride),
      published_on: form.value.published_on || '',
      featured: Boolean(form.value.featured),
      disable_comments: Boolean(form.value.disable_comments),
      disable_likes: Boolean(form.value.disable_likes),
      hide_cta: Boolean(form.value.hide_cta),
      blog_intro: form.value.blog_intro,
      meta_title: form.value.meta_title,
      meta_description: form.value.meta_description,
      meta_image: form.value.meta_image,
      custom_subtitle: form.value.subtitle,
      custom_cover_credit: form.value.cover_credit,
      custom_cta_label: form.value.cta_label,
      custom_cta_link: form.value.cta_link,
      custom_focus_keyword: form.value.focus_keyword,
      custom_secondary_keywords: form.value.secondary_keywords,
      custom_read_time: form.value.read_time,
      body_html: editorHtml.value,
    }
    const result = await postJson('/api/method/mysite.api.save_management_blog_post', {
      name: selectedName.value,
      payload,
    })

    if (applyWorkflowResponse(result, '')) {
      return
    }

    const saved = result?.post
    if (saved?.name) {
      selectedName.value = saved.name
      fillForm(saved)
      await syncEditorSurface()
      await loadPosts(false)
      await loadLatestWorkflowRequest()
    }

    saveSuccess.value = payload.published ? 'مقاله با وضعیت منتشرشده ذخیره شد.' : 'پیش‌نویس ذخیره شد.'
  } catch (error) {
    saveError.value = error?.message || 'ذخیره مقاله با خطا مواجه شد.'
  } finally {
    saving.value = false
  }
}

async function togglePublishState() {
  if (!canEditContent.value) return
  const target = !form.value.published
  if (target && !form.value.published_on) {
    form.value.published_on = new Date().toISOString().slice(0, 10)
  }
  await savePost(target)
}

async function createNewDraft() {
  if (!canEditContent.value) return
  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const now = new Date()
    const titleSeed = `پیش‌نویس جدید ${now.toLocaleDateString('fa-IR')}`
    const result = await postJson('/api/method/mysite.api.save_management_blog_post', {
      payload: {
        title: titleSeed,
        published: false,
        body_html: '<p></p>',
      },
    })
    if (applyWorkflowResponse(result, '')) {
      return
    }
    if (result?.post?.name) {
      selectedName.value = result.post.name
      await loadPosts(false)
      await loadPostDetail(result.post.name)
      saveSuccess.value = 'پیش‌نویس جدید ساخته شد.'
    }
  } catch (error) {
    saveError.value = error?.message || 'ساخت پیش‌نویس جدید با خطا مواجه شد.'
  } finally {
    saving.value = false
  }
}

async function deletePost() {
  if (!canEditContent.value) return
  if (!selectedName.value) return
  const ok = window.confirm('این مقاله حذف شود؟ این عملیات قابل بازگشت نیست.')
  if (!ok) return

  deleting.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const result = await postJson('/api/method/mysite.api.delete_management_blog_post', { name: selectedName.value })
    if (applyWorkflowResponse(result, '')) {
      return
    }
    const removedName = selectedName.value
    selectedName.value = ''
    workflowRef.value = { name: '', state: '' }
    await loadPosts(false)
    if (!selectedName.value && posts.value.length) {
      selectedName.value = posts.value[0].name
    }
    saveSuccess.value = `مقاله ${removedName} حذف شد.`
  } catch (error) {
    saveError.value = error?.message || 'حذف مقاله با خطا مواجه شد.'
  } finally {
    deleting.value = false
  }
}

function openUploadPicker(target = 'meta') {
  pendingUploadTarget.value = target
  mediaError.value = ''
  if (!mediaUploadInput.value) return
  mediaUploadInput.value.value = ''
  mediaUploadInput.value.click()
}

async function uploadImage(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  mediaUploading.value = true
  mediaError.value = ''

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
      throw new Error(payload?.message || 'آپلود فایل با خطا مواجه شد.')
    }

    const uploaded = payload.message || payload
    const fileUrl = String(uploaded?.file_url || '').trim()
    if (!fileUrl) {
      throw new Error('نشانی فایل آپلودشده دریافت نشد.')
    }

    if (pendingUploadTarget.value === 'editor') {
      execCommand('insertHTML', `<p><img src="${fileUrl}" alt="" /></p>`)
    } else {
      form.value.meta_image = fileUrl
    }

    if (showMediaBrowser.value) {
      await loadMediaFiles()
    }
  } catch (error) {
    mediaError.value = error?.message || 'آپلود فایل با خطا مواجه شد.'
  } finally {
    mediaUploading.value = false
  }
}

async function loadMediaFiles() {
  mediaLoading.value = true
  mediaError.value = ''
  try {
    const params = new URLSearchParams({
      limit: '120',
      search: mediaSearch.value || '',
    })
    const result = await getJson(`/api/method/mysite.api.list_management_media_images?${params.toString()}`)
    mediaFiles.value = Array.isArray(result.items) ? result.items : []
  } catch (error) {
    mediaFiles.value = []
    mediaError.value = error?.message || 'دریافت فایل‌ها با خطا مواجه شد.'
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

function useMediaImage(fileUrl) {
  const normalized = String(fileUrl || '').trim().replace('/private/files/', '/files/')
  if (!normalized) return

  if (pendingUploadTarget.value === 'editor') {
    execCommand('insertHTML', `<p><img src="${normalized}" alt="" /></p>`)
  } else {
    form.value.meta_image = normalized
  }
}

watch(selectedName, (value) => {
  detailError.value = ''
  saveError.value = ''
  saveSuccess.value = ''
  workflowRef.value = { name: '', state: '' }
  loadPostDetail(value)
}, { immediate: false })

onMounted(async () => {
  try {
    const savedMode = localStorage.getItem(LIST_VIEW_STORAGE_KEY)
    if (savedMode === 'grid' || savedMode === 'list' || savedMode === 'table') {
      listViewMode.value = savedMode
    }
  } catch (error) {
    // Ignore storage errors.
  }
  await loadPosts(true)
  if (selectedName.value) {
    await loadPostDetail(selectedName.value)
  }
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
.blog-admin-page {
  min-height: 100vh;
  background: var(--admin-bg);
  color: var(--text-main);
}

.blog-admin-shell {
  max-width: 1860px;
  margin: 0 auto;
  padding: 16px;
  display: grid;
  grid-template-columns: 250px 360px 1fr;
  gap: 12px;
}

.sidebar,
.list-area,
.editor-area {
  background: var(--admin-panel-bg);
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.sidebar {
  padding: 14px;
  display: grid;
  align-content: start;
  gap: 12px;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.brand-dot {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(140deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.brand-row strong {
  display: block;
  font-size: 0.92rem;
}

.brand-row small {
  color: var(--admin-text-soft);
  font-size: 11px;
}

.side-nav {
  display: grid;
  gap: 6px;
}

.nav-item {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: 10px;
  min-height: 38px;
  text-decoration: none;
  font-family: inherit;
  font-size: 13px;
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
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--admin-chip-bg);
}

.side-note p {
  margin: 0;
  font-size: 12px;
  color: var(--admin-text-soft);
  line-height: 1.8;
}

.list-area {
  padding: 14px;
  display: grid;
  align-content: start;
  gap: 10px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.list-header h1 {
  margin: 0;
  font-size: 1.3rem;
}

.list-header p {
  margin: 5px 0 0;
  color: var(--admin-text-soft);
  font-size: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filters {
  display: grid;
  grid-template-columns: 1fr 120px 130px;
  gap: 8px;
}

.filters input,
.filters select,
.ghost {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: 10px;
  min-height: 38px;
  padding: 0 10px;
  font-family: inherit;
}

.ghost {
  cursor: pointer;
  font-weight: 700;
}

.post-list {
  display: grid;
  gap: 8px;
  max-height: calc(100vh - 180px);
  overflow: auto;
  padding-left: 2px;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
  max-height: calc(100vh - 180px);
  overflow: auto;
  padding-left: 2px;
}

.post-card {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  padding: 10px;
  background: var(--admin-chip-bg);
  cursor: pointer;
  display: grid;
  gap: 6px;
}

.post-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 34%, transparent);
}

.post-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: flex-start;
}

.post-top h3 {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.excerpt {
  margin: 0;
  font-size: 12px;
  color: var(--admin-text-soft);
  line-height: 1.8;
}

.post-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.post-meta small {
  font-size: 11px;
  color: var(--admin-text-soft);
}

.status {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--admin-border);
  white-space: nowrap;
}

.status.published,
.status.featured {
  color: #bbf7d0;
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.12);
}

.status.draft,
.status.featured_draft {
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.12);
}

.post-table-wrap {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-chip-bg);
  overflow: auto;
  max-height: calc(100vh - 180px);
}

.post-table-wrap table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
}

.post-table-wrap th,
.post-table-wrap td {
  border-bottom: 1px solid var(--admin-border);
  padding: 8px 9px;
  font-size: 12px;
  text-align: right;
  white-space: nowrap;
}

.post-table-wrap th {
  position: sticky;
  top: 0;
  background: var(--admin-panel-bg);
  color: var(--admin-text-soft);
  z-index: 1;
}

.post-table-wrap tbody tr {
  cursor: pointer;
}

.post-table-wrap tbody tr:hover td {
  background: rgba(255, 255, 255, 0.03);
}

.post-table-wrap tbody tr.active td {
  background: color-mix(in srgb, var(--accent-gold) 14%, transparent);
}

.post-table-wrap tbody tr:last-child td {
  border-bottom: none;
}

.title-cell {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.editor-area {
  padding: 14px;
  display: grid;
  align-content: start;
  gap: 10px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.editor-header h2 {
  margin: 0;
  font-size: 1.08rem;
}

.editor-header a {
  font-size: 12px;
  color: var(--accent-gold);
  text-decoration: none;
}

.editor-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.workflow-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.meta-grid.two-col {
  grid-template-columns: 1fr 1fr;
}

.meta-grid label {
  display: grid;
  gap: 4px;
}

.meta-grid span {
  color: var(--admin-text-soft);
  font-size: 12px;
}

.meta-grid input,
.meta-grid textarea {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: 10px;
  min-height: 38px;
  padding: 8px 10px;
  font-family: inherit;
  font-size: 13px;
}

.meta-grid textarea {
  min-height: 80px;
  resize: vertical;
}

.switch-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.switch {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
}

.switch input {
  width: 16px;
  height: 16px;
}

.editor-card,
.settings-card {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-chip-bg);
  padding: 10px;
  display: grid;
  gap: 8px;
}

.settings-card h3 {
  margin: 0;
  font-size: 0.95rem;
}

.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.editor-toolbar button {
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-input-bg);
  color: var(--text-main);
  min-height: 30px;
  padding: 0 9px;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}

.editor-surface {
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--admin-input-bg) 62%, #ffffff 38%);
  min-height: 420px;
  max-height: calc(100vh - 360px);
  overflow: auto;
}

.notion-editor {
  min-height: 420px;
  padding: 22px 26px;
  outline: none;
  line-height: 2;
  font-size: 15px;
  color: var(--text-main);
}

.notion-editor:empty::before {
  content: attr(data-placeholder);
  color: var(--admin-text-soft);
}

.notion-editor :deep(h1),
.notion-editor :deep(h2),
.notion-editor :deep(h3) {
  margin: 1em 0 0.45em;
}

.notion-editor :deep(blockquote) {
  border-right: 3px solid color-mix(in srgb, var(--admin-tab-active-start) 65%, transparent);
  padding: 4px 12px;
  margin: 12px 0;
  color: var(--admin-text-soft);
}

.notion-editor :deep(img) {
  max-width: 100%;
  border-radius: 10px;
}

.notion-editor :deep(hr) {
  border: 0;
  border-top: 1px dashed var(--admin-border);
  margin: 16px 0;
}

.meta-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.hidden-file {
  display: none;
}

.media-browser {
  border-top: 1px dashed var(--admin-border);
  padding-top: 8px;
  display: grid;
  gap: 8px;
}

.media-toolbar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.media-toolbar input {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: 10px;
  min-height: 38px;
  padding: 0 10px;
  font-family: inherit;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
  max-height: 280px;
  overflow: auto;
}

.media-card {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: 10px;
  padding: 6px;
  display: grid;
  gap: 6px;
  text-align: right;
  cursor: pointer;
}

.media-card img {
  width: 100%;
  height: 84px;
  object-fit: cover;
  border-radius: 8px;
}

.media-card small {
  font-size: 10px;
  color: var(--admin-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini {
  border: 1px solid var(--admin-border);
  border-radius: 8px;
  background: var(--admin-panel-bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: 11px;
  min-height: 30px;
  padding: 0 8px;
  cursor: pointer;
}

.mini.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.save-msg {
  margin: 0;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 12px;
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
  border-radius: 12px;
  text-align: center;
  color: var(--admin-text-soft);
  padding: 18px;
}

.state.error {
  color: #fecaca;
}

@media (max-width: 1600px) {
  .blog-admin-shell {
    grid-template-columns: 230px 330px 1fr;
  }
}

@media (max-width: 1320px) {
  .blog-admin-shell {
    grid-template-columns: 1fr;
  }

  .post-list {
    max-height: none;
  }

  .editor-surface {
    max-height: none;
  }
}

@media (max-width: 760px) {
  .filters,
  .meta-grid,
  .meta-grid.two-col,
  .media-toolbar {
    grid-template-columns: 1fr;
  }

  .switch-row,
  .header-actions,
  .editor-actions,
  .meta-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .post-grid {
    grid-template-columns: 1fr;
  }
}
</style>
