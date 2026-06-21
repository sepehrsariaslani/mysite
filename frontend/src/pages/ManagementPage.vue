<template>
  <div class="builder-page" dir="rtl">
    <div class="builder-shell">
      <aside class="sidebar">
        <div class="brand-row">
          <div class="brand-dot">م</div>
          <div>
            <strong>مدیریت صفحات</strong>
            <small>سازنده داخلی</small>
          </div>
        </div>

        <nav class="main-nav">
          <button class="nav-item" :class="{ active: activeFolder === 'all' }" @click="activeFolder = 'all'">
            همه صفحات
            <b>{{ toFa(allPages.length) }}</b>
          </button>
          <a class="nav-item" href="/management-products">محصولات</a>
          <a class="nav-item" href="/management-blog">بلاگ</a>
          <a class="nav-item" href="/management-support">پشتیبانی</a>
          <a class="nav-item" href="/management-analytics-traffic">آنالیتیکس</a>
        </nav>

        <div class="folder-head">
          <h4>دسته‌ها</h4>
        </div>
        <div class="folder-list">
          <button
            v-for="folder in folderBuckets"
            :key="folder.key"
            class="folder-item"
            :class="{ active: activeFolder === folder.key }"
            @click="activeFolder = folder.key"
          >
            <span>{{ folder.label }}</span>
            <b>{{ toFa(folder.count) }}</b>
          </button>
        </div>
      </aside>

      <section class="list-area">
        <header class="list-header">
          <div>
            <h1>همه صفحات</h1>
            <p v-if="data?.meta?.generated_at">آخرین بروزرسانی: {{ formatDate(data.meta.generated_at) }}</p>
          </div>

          <div class="toolbar">
            <input v-model.trim="query" placeholder="جستجو بر اساس عنوان یا مسیر" />
            <select v-model="sourceFilter">
              <option value="all">مشاهده همه</option>
              <option value="website">فقط صفحات وب‌سایت</option>
              <option value="frontend">فقط مسیرهای فرانت</option>
              <option value="mixed">ترکیبی</option>
              <option value="tracked">فقط ردیابی‌شده</option>
            </select>
            <select v-model="sortBy">
              <option value="latest">آخرین بروزرسانی</option>
              <option value="views">بیشترین بازدید</option>
              <option value="title">نام صفحه</option>
            </select>
            <ManagementProductViewSwitcher v-model="listViewMode" />
            <button class="ghost" :disabled="loading" @click="loadData">{{ loading ? 'در حال دریافت...' : 'بروزرسانی' }}</button>
            <button class="ghost" :disabled="autoMetaLoading" @click="generateMetaForAllPages">
              {{ autoMetaLoading ? 'در حال تولید متا...' : 'تولید توضیحات متا برای همه صفحات' }}
            </button>
          </div>
        </header>

        <div v-if="batchMetaError" class="state error">{{ batchMetaError }}</div>
        <div v-else-if="batchMetaSuccess" class="state success">{{ batchMetaSuccess }}</div>

        <div v-if="loading" class="state">در حال دریافت لیست صفحات...</div>
        <div v-else-if="error" class="state error">{{ error }}</div>
        <div v-else-if="!filteredPages.length" class="state">صفحه‌ای پیدا نشد.</div>

        <div v-else-if="listViewMode === 'grid'" class="cards-grid">
          <article
            v-for="page in filteredPages"
            :key="page.route"
            class="page-card"
            :class="{ active: selectedRoute === page.route }"
            @click="selectedRoute = page.route"
          >
            <div class="thumb">
              <img v-if="page.meta_image" :src="resolveManagementImageSrc(page.meta_image)" alt="پیش‌نمایش" @error="onImgError" />
              <div v-else class="thumb-placeholder">{{ shortLabel(page.title) }}</div>
            </div>
            <h3>{{ page.title }}</h3>
            <p class="route">{{ page.route }}</p>
            <div class="card-meta">
              <span>{{ page.source_label }}</span>
              <span>{{ page.modified_at ? `ویرایش: ${relativeDate(page.modified_at)}` : 'بدون تاریخ ویرایش' }}</span>
            </div>
            <div class="card-stats">
              <small>بازدید: {{ toFa(page.views) }}</small>
              <small>نشست: {{ toFa(page.unique_sessions) }}</small>
              <small v-if="page.content_override_count">ویرایش محتوا: {{ toFa(page.content_override_count) }}</small>
            </div>
          </article>
        </div>

        <div v-else-if="listViewMode === 'list'" class="pages-list">
          <article
            v-for="page in filteredPages"
            :key="page.route"
            class="page-row"
            :class="{ active: selectedRoute === page.route }"
            @click="selectedRoute = page.route"
          >
            <div class="row-thumb">
              <img v-if="page.meta_image" :src="resolveManagementImageSrc(page.meta_image)" alt="پیش‌نمایش" @error="onImgError" />
              <div v-else class="thumb-placeholder">{{ shortLabel(page.title) }}</div>
            </div>
            <div class="row-main">
              <h3>{{ page.title }}</h3>
              <p class="route">{{ page.route }}</p>
              <small>{{ page.modified_at ? `ویرایش: ${relativeDate(page.modified_at)}` : 'بدون تاریخ ویرایش' }}</small>
            </div>
            <div class="row-meta">
              <span>{{ page.source_label }}</span>
              <small>بازدید: {{ toFa(page.views) }}</small>
              <small>نشست: {{ toFa(page.unique_sessions) }}</small>
              <small v-if="page.content_override_count">ویرایش محتوا: {{ toFa(page.content_override_count) }}</small>
            </div>
          </article>
        </div>

        <div v-else class="pages-table-wrap">
          <table>
            <thead>
              <tr>
                <th>عنوان</th>
                <th>مسیر</th>
                <th>منبع</th>
                <th>بازدید</th>
                <th>نشست</th>
                <th>ویرایش محتوا</th>
                <th>آخرین ویرایش</th>
                <th>اقدام</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="page in filteredPages"
                :key="page.route"
                :class="{ active: selectedRoute === page.route }"
                @click="selectedRoute = page.route"
              >
                <td class="title-cell">{{ page.title }}</td>
                <td class="route-cell">{{ page.route }}</td>
                <td>{{ page.source_label }}</td>
                <td>{{ toFa(page.views) }}</td>
                <td>{{ toFa(page.unique_sessions) }}</td>
                <td>{{ toFa(page.content_override_count || 0) }}</td>
                <td>{{ page.modified_at ? relativeDate(page.modified_at) : 'نامشخص' }}</td>
                <td><button class="mini-select" type="button" @click.stop="selectedRoute = page.route">انتخاب</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <section v-if="!loading && !error" class="components-area">
          <header class="components-head">
            <h3>کامپوننت‌های قابل ادیت</h3>
            <div class="components-tools">
              <input v-model.trim="componentQuery" placeholder="جستجو در نام یا مسیر کامپوننت" />
              <select v-model="componentGroup">
                <option value="all">همه گروه‌ها</option>
                <option v-for="group in componentGroups" :key="group.key" :value="group.key">
                  {{ group.label }} ({{ toFa(group.count) }})
                </option>
              </select>
            </div>
          </header>

          <div v-if="!filteredComponents.length" class="state small">کامپوننتی برای نمایش پیدا نشد.</div>
          <div v-else class="components-grid">
            <article
              v-for="component in filteredComponents"
              :key="component.file"
              class="component-card"
              :class="{ active: selectedComponentFile === component.file }"
              @click="selectedComponentFile = component.file"
            >
              <div class="component-card-head">
                <strong>{{ component.name }}</strong>
                <small>{{ component.group_label }}</small>
              </div>
              <p class="route">{{ component.file }}</p>
              <div class="component-meta">
                <small>استفاده در صفحات: {{ toFa(component.usage_count) }}</small>
                <small>{{ component.modified_at ? `ویرایش: ${relativeDate(component.modified_at)}` : 'بدون تاریخ ویرایش' }}</small>
              </div>
              <div class="component-actions">
                <button class="ghost mini" type="button" @click.stop="openComponentEditor(component)">ادیت کامپوننت</button>
                <a
                  v-if="component.primary_route"
                  class="ghost ghost-link mini"
                  :href="component.primary_route"
                  target="_blank"
                  rel="noreferrer"
                >
                  نمایش صفحه استفاده
                </a>
              </div>
            </article>
          </div>
        </section>
      </section>

      <section class="detail-area" v-if="selectedPage">
        <header class="detail-header">
          <div>
            <h2>{{ selectedPage.title }}</h2>
            <code>{{ selectedPage.route }}</code>
          </div>
          <div class="detail-tabs">
            <button :class="{ active: detailTab === 'design' }" @click="detailTab = 'design'">طراحی بصری</button>
            <button :class="{ active: detailTab === 'general' }" @click="detailTab = 'general'">عمومی</button>
            <button :class="{ active: detailTab === 'analytics' }" @click="detailTab = 'analytics'">آمار</button>
            <button :class="{ active: detailTab === 'content' }" @click="detailTab = 'content'">محتوا</button>
            <button :class="{ active: detailTab === 'meta' }" @click="detailTab = 'meta'">متا</button>
          </div>
        </header>

        <div v-if="workflowRef.name" class="workflow-row">
          <small>گردش‌کار: {{ workflowRef.state || 'Draft' }} | درخواست: {{ workflowRef.name }}</small>
          <div class="workflow-actions">
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
        </div>

        <div v-if="detailTab === 'design'" class="detail-body">
          <h3>ادیتور بصری مستقل</h3>
          <p class="hint">
            ابتدا اطلاعات صفحه را مشاهده کنید. برای ادیت کامل، صفحه‌ی جداگانه‌ی ادیتور باز می‌شود و روی همین صفحه overlay نمایش داده نمی‌شود.
          </p>
          <p v-if="visualError" class="save-msg error">{{ visualError }}</p>
          <p v-else-if="visualSuccess" class="save-msg success">{{ visualSuccess }}</p>
          <div class="design-toolbar">
            <button class="ghost" :disabled="!selectedPage" @click="openVisualEditorPage">
              باز کردن ادیتور صفحه جدا
            </button>
            <a class="ghost ghost-link" :href="selectedPage.full_url" target="_blank" rel="noreferrer">نمایش صفحه</a>
          </div>
          <div class="builder-quick-info">
            <small>تعداد تغییرات بصری ذخیره‌شده: {{ toFa(selectedPage.visual_override_count || 0) }}</small>
            <small>ادیت کامل CSS / کد در صفحه جدا انجام می‌شود.</small>
            <small>صفحه انتخابی: {{ selectedPage.route }}</small>
          </div>
        </div>

        <div v-else-if="detailTab === 'general'" class="detail-body">
          <h3>تنظیمات صفحه</h3>
          <p v-if="saveError" class="save-msg error">{{ saveError }}</p>
          <p v-else-if="saveSuccess" class="save-msg success">{{ saveSuccess }}</p>
          <div class="form-grid two">
            <label>
              <span>عنوان صفحه</span>
              <input v-model="generalForm.title" />
            </label>
            <label>
              <span>مسیر صفحه</span>
              <input :value="selectedPage.route_key" readonly dir="ltr" />
            </label>
          </div>

          <div class="line-item">
            <span>نشانی</span>
            <a :href="selectedPage.full_url" target="_blank" rel="noreferrer">{{ selectedPage.full_url }}</a>
          </div>
          <div class="line-item">
            <span>وضعیت</span>
            <b class="status" :class="selectedPage.status_key">{{ selectedPage.status_label }}</b>
          </div>
          <div class="line-item">
            <span>منبع</span>
            <b>{{ selectedPage.source_label }}</b>
          </div>
          <div class="line-item">
            <span>دسته</span>
            <b>{{ selectedPage.folder_label }}</b>
          </div>
          <div class="line-item switches">
            <span>صفحه محافظت‌شده</span>
            <input type="checkbox" v-model="generalForm.protected_page" />
          </div>
          <div class="line-item switches">
            <span>غیرفعال‌سازی ایندکس</span>
            <input type="checkbox" v-model="generalForm.noindex" />
          </div>
          <div class="save-row">
            <button class="ghost" :disabled="saveLoading || !canContentEdit" @click="savePageConfig">
              {{ saveLoading ? 'در حال ذخیره...' : 'ذخیره تنظیمات صفحه' }}
            </button>
          </div>
        </div>

        <div v-else-if="detailTab === 'analytics'" class="detail-body">
          <div class="analytics-head">
            <h3>آمار بازدید صفحه</h3>
            <select v-model="analyticsRange">
              <option value="7d">۷ روز</option>
              <option value="30d">۳۰ روز</option>
              <option value="90d">۳ ماه</option>
              <option value="180d">۶ ماه</option>
              <option value="365d">۱ سال</option>
              <option value="today">امروز</option>
            </select>
          </div>

          <div v-if="statsLoading" class="state">در حال دریافت آمار...</div>
          <div v-else>
            <div class="kpis two">
              <article>
                <p>بازدیدکننده یکتا</p>
                <strong>{{ toFa(selectedMetrics.unique_sessions) }}</strong>
              </article>
              <article>
                <p>کل بازدید صفحه</p>
                <strong>{{ toFa(selectedMetrics.views) }}</strong>
              </article>
              <article>
                <p>میانگین حضور</p>
                <strong>{{ toFa2(selectedMetrics.avg_time_spent_seconds) }} ثانیه</strong>
              </article>
              <article>
                <p>نرخ خروج</p>
                <strong>{{ toFa2(selectedMetrics.exit_rate) }}%</strong>
              </article>
            </div>

            <article class="chart-box">
              <h4>روند بازدید روزانه</h4>
              <div v-if="selectedDaily.length" class="spark-wrap">
                <div class="sparkline">
                  <div v-for="row in selectedDaily" :key="row.date" class="spark-col">
                    <div class="spark-bar" :style="{ height: `${heightByMax(row.views, dailyMax)}%` }"></div>
                    <small>{{ shortDate(row.date) }}</small>
                  </div>
                </div>
              </div>
              <p v-else class="hint">داده‌ای برای این بازه ثبت نشده است.</p>
            </article>

            <article class="chart-box">
              <h4>منابع برتر</h4>
              <table>
                <thead><tr><th>دامنه</th><th>تعداد</th></tr></thead>
                <tbody>
                  <tr v-for="row in selectedSources" :key="row.source_channel">
                    <td>{{ sourceName(row.source_channel) }}</td>
                    <td>{{ toFa(row.views) }}</td>
                  </tr>
                </tbody>
              </table>
            </article>
          </div>
        </div>

        <div v-else-if="detailTab === 'content'" class="detail-body">
          <h3>ویرایش محتوای صفحه</h3>
          <p class="hint">
            متن‌های این صفحه و کامپوننت‌های متصل به‌صورت خودکار اسکن شده‌اند. متن جدید را وارد کنید تا روی خود سایت اعمال شود.
          </p>
          <p v-if="contentError" class="save-msg error">{{ contentError }}</p>
          <p v-else-if="contentSuccess" class="save-msg success">{{ contentSuccess }}</p>

          <div class="content-toolbar">
            <input v-model.trim="contentSearch" placeholder="جستجو در متن فعلی یا متن جدید" />
            <label class="content-changed-only">
              <input type="checkbox" v-model="contentOnlyChanged" />
              <span>فقط تغییرات</span>
            </label>
            <button class="ghost" :disabled="contentLoading" @click="loadPageContentSchema">
              {{ contentLoading ? 'در حال اسکن...' : 'اسکن مجدد' }}
            </button>
            <button class="ghost" :disabled="contentSaving || contentLoading || !canContentEdit" @click="savePageContentOverrides">
              {{ contentSaving ? 'در حال ذخیره...' : `ذخیره محتوا (${toFa(contentChangedCount)})` }}
            </button>
          </div>

          <div v-if="contentLoading" class="state">در حال اسکن محتوای صفحه...</div>
          <div v-else-if="contentSources.length" class="content-sources">
            <small v-for="source in contentSources" :key="`${source.scope}-${source.file}`">
              {{ source.scope_label }}: {{ source.file }} ({{ toFa(source.count) }})
            </small>
          </div>
          <div v-else-if="!contentRows.length" class="state">متن ثابتی برای این صفحه پیدا نشد.</div>

          <div v-if="!contentLoading && contentRows.length" class="content-list">
            <article v-for="row in filteredContentRows" :key="row.key" class="content-item">
              <div class="content-item-head">
                <small>{{ row.scope_label || 'متن' }} - {{ row.source_file || '-' }}</small>
                <span class="content-badge" :class="{ changed: row.has_override }">
                  {{ row.has_override ? 'تغییر یافته' : 'پیش‌فرض' }}
                </span>
              </div>
              <label>
                <span>متن فعلی</span>
                <textarea :value="row.source_text" rows="2" readonly></textarea>
              </label>
              <label>
                <span>متن جدید</span>
                <textarea
                  :value="row.replacement_text"
                  rows="2"
                  @input="onContentReplacementInput(row.key, $event.target.value)"
                ></textarea>
              </label>
            </article>
          </div>
        </div>

        <div v-else class="detail-body">
          <h3>متا</h3>
          <p v-if="saveError" class="save-msg error">{{ saveError }}</p>
          <p v-else-if="saveSuccess" class="save-msg success">{{ saveSuccess }}</p>
          <div class="form-grid">
            <label>
              <span>عنوان</span>
              <input v-model="metaForm.title" />
            </label>
            <label>
              <span>توضیحات</span>
              <textarea v-model="metaForm.meta_description" rows="4"></textarea>
            </label>
            <label>
              <span>تصویر متا</span>
              <input v-model="metaForm.meta_image" dir="ltr" />
            </label>
            <label>
              <span>نشانی کانونیکال</span>
              <input v-model="metaForm.canonical_url" dir="ltr" />
            </label>
          </div>
          <div class="meta-actions">
            <button class="ghost" :disabled="mediaUploading" @click="openUploadPicker">
              {{ mediaUploading ? 'در حال آپلود...' : 'آپلود تصویر متا' }}
            </button>
            <button class="ghost" :disabled="mediaLoading" @click="toggleMediaBrowser">
              {{ showMediaBrowser ? 'بستن فایل‌های سیستم' : 'انتخاب از فایل‌های سیستم' }}
            </button>
            <input ref="metaImageInput" class="hidden-file" type="file" accept="image/*" @change="uploadMetaImage" />
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
            <div v-else-if="!mediaFiles.length" class="state">تصویری یافت نشد.</div>
            <div v-else class="media-grid">
              <button
                v-for="file in mediaFiles"
                :key="file.name"
                class="media-card"
                :class="{ active: metaForm.meta_image === file.file_url }"
                @click="selectMetaImage(file.file_url)"
              >
                <img :src="resolveManagementImageSrc(file.file_url)" :alt="file.file_name || 'تصویر'" @error="onImgError" />
                <small>{{ file.file_name || file.file_url }}</small>
              </button>
            </div>
          </div>

          <article class="social-preview">
            <h4>پیش‌نمایش شبکه اجتماعی</h4>
            <div class="preview-card">
              <div class="preview-image">
                <img v-if="metaForm.meta_image" :src="resolveManagementImageSrc(metaForm.meta_image)" alt="پیش‌نمایش اجتماعی" @error="onImgError" />
              </div>
              <div class="preview-copy">
                <p>{{ selectedPage.route_key }}</p>
                <strong>{{ metaForm.title || generalForm.title || selectedPage.title }}</strong>
                <small>{{ metaForm.meta_description || 'توضیحات متا برای این صفحه ثبت نشده است.' }}</small>
              </div>
            </div>
          </article>
          <div class="save-row">
            <button class="ghost" :disabled="saveLoading || !canContentEdit" @click="savePageConfig">
              {{ saveLoading ? 'در حال ذخیره...' : 'ذخیره اطلاعات متا' }}
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ManagementProductViewSwitcher from '../components/management/ManagementProductViewSwitcher.vue'
import { hasManagementCapability } from '../utils/managementAccess'

const loading = ref(false)
const error = ref('')
const data = ref(null)

const query = ref('')
const componentQuery = ref('')
const sourceFilter = ref('all')
const componentGroup = ref('all')
const sortBy = ref('latest')
const listViewMode = ref('grid')
const activeFolder = ref('all')
const detailTab = ref('general')
const LIST_VIEW_STORAGE_KEY = 'mysite.management.pages.list_view_mode'

const selectedRoute = ref('')
const selectedComponentFile = ref('')
const analyticsRange = ref('30d')
const statsLoading = ref(false)
const pageStats = ref(null)
const saveLoading = ref(false)
const saveError = ref('')
const saveSuccess = ref('')
const contentLoading = ref(false)
const contentSaving = ref(false)
const contentError = ref('')
const contentSuccess = ref('')
const contentRows = ref([])
const contentSources = ref([])
const contentSearch = ref('')
const contentOnlyChanged = ref(false)
const autoMetaLoading = ref(false)
const batchMetaError = ref('')
const batchMetaSuccess = ref('')
const showMediaBrowser = ref(false)
const mediaLoading = ref(false)
const mediaUploading = ref(false)
const mediaError = ref('')
const mediaSearch = ref('')
const mediaFiles = ref([])
const metaImageInput = ref(null)
const visualLoading = ref(false)
const visualSaving = ref(false)
const visualError = ref('')
const visualSuccess = ref('')
const visualPreviewFrame = ref(null)
const visualPreviewSrc = ref('')
const visualLayerQuery = ref('')
const visualLayers = ref([])
const visualLayerIndex = ref({})
const visualSelectedId = ref('')
const visualOverridesMap = ref({})
const visualProps = ref({
  text_content: '',
  color: '',
  backgroundColor: '',
  fontSize: '',
  borderRadius: '',
  padding: '',
  margin: '',
  display: '',
  justifyContent: '',
  alignItems: '',
  gap: '',
})
const workflowRef = ref({ name: '', state: '', target_type: '', target_key: '' })
const workflowLoading = ref(false)

const canContentEdit = computed(() => hasManagementCapability('content.edit'))
const canContentReview = computed(() => hasManagementCapability('content.review'))
const canContentPublish = computed(() => hasManagementCapability('content.publish'))

const WORKFLOW_ACTION_META = {
  submit_review: { key: 'submit_review', label: 'ارسال برای بازبینی', danger: false },
  return_to_draft: { key: 'return_to_draft', label: 'بازگشت به پیش‌نویس', danger: false },
  approve: { key: 'approve', label: 'تایید', danger: false },
  reject: { key: 'reject', label: 'رد', danger: true },
  publish: { key: 'publish', label: 'انتشار', danger: false },
  cancel: { key: 'cancel', label: 'لغو', danger: true },
}

const VISUAL_NODE_ATTR = 'data-mysite-node'
let visualFrameDocument = null
let visualSelectedElement = null
let visualFrameClickHandler = null

const generalForm = ref({
  title: '',
  noindex: false,
  protected_page: false,
})

const metaForm = ref({
  title: '',
  meta_description: '',
  canonical_url: '',
  meta_image: '',
})

const toFa = (v) => Number(v || 0).toLocaleString('fa-IR')
const toFa2 = (v) => Number(v || 0).toLocaleString('fa-IR', { maximumFractionDigits: 2 })

const workflowActions = computed(() => {
  const state = String(workflowRef.value?.state || '').trim()
  if (!workflowRef.value?.name || !state) return []
  if (state === 'Draft') {
    return canContentEdit.value ? [WORKFLOW_ACTION_META.submit_review, WORKFLOW_ACTION_META.cancel] : []
  }
  if (state === 'In Review') {
    const actions = []
    if (canContentReview.value) {
      actions.push(WORKFLOW_ACTION_META.return_to_draft, WORKFLOW_ACTION_META.approve, WORKFLOW_ACTION_META.reject)
    }
    if (canContentPublish.value) {
      actions.push(WORKFLOW_ACTION_META.cancel)
    }
    return actions
  }
  if (state === 'Approved') {
    return canContentPublish.value ? [WORKFLOW_ACTION_META.publish, WORKFLOW_ACTION_META.cancel] : []
  }
  return []
})

function activeSuccessChannel() {
  if (detailTab.value === 'content') return 'content'
  if (detailTab.value === 'design') return 'visual'
  return 'general'
}

function resetWorkflowMessages() {
  saveError.value = ''
  contentError.value = ''
  visualError.value = ''
}

function setWorkflowSuccessMessage(message) {
  if (activeSuccessChannel() === 'content') {
    contentSuccess.value = message
    saveSuccess.value = ''
    visualSuccess.value = ''
    return
  }
  if (activeSuccessChannel() === 'visual') {
    visualSuccess.value = message
    saveSuccess.value = ''
    contentSuccess.value = ''
    return
  }
  saveSuccess.value = message
  contentSuccess.value = ''
  visualSuccess.value = ''
}

const formatDate = (value) => {
  if (!value) return '-'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return dt.toLocaleString('fa-IR')
}

const relativeDate = (value) => {
  if (!value) return 'نامشخص'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return dt.toLocaleDateString('fa-IR')
}

const shortDate = (value) => {
  if (!value) return '-'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return dt.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' })
}

const sourceName = (key) => ({
  direct: 'مستقیم',
  google: 'گوگل',
  instagram: 'اینستاگرام',
  telegram: 'تلگرام',
  other: 'سایر',
}[key] || key || '-')

const toBool = (value, fallback = false) => {
  if (typeof value === 'boolean') return value
  if (value === null || value === undefined) return fallback
  if (typeof value === 'number') return value !== 0
  const text = String(value).trim().toLowerCase()
  if (['1', 'true', 'yes', 'on'].includes(text)) return true
  if (['0', 'false', 'no', 'off', ''].includes(text)) return false
  return fallback
}

const routeFolder = (route) => {
  const path = String(route || '')
  if (path === '/mysite') return { key: 'home', label: 'صفحه اصلی' }
  if (path.startsWith('/product') || path.startsWith('/sofa') || path.startsWith('/sofas')) return { key: 'sofas', label: 'مبلمان' }
  if (path.startsWith('/blog') || path.startsWith('/special-edition') || path.startsWith('/outlet')) return { key: 'blog', label: 'بلاگ و محتوا' }
  if (path.startsWith('/projects') || path.startsWith('/project') || path.startsWith('/gallery') || path.startsWith('/shop-by-look')) return { key: 'projects', label: 'پروژه‌ها' }
  if (path.startsWith('/consultation') || path.startsWith('/about') || path.startsWith('/faq') || path.startsWith('/dealers') || path.startsWith('/downloads')) return { key: 'services', label: 'خدمات' }
  if (path.startsWith('/management') || path.startsWith('/dashboard') || path.startsWith('/login') || path.startsWith('/cart')) return { key: 'system', label: 'سیستمی' }
  return { key: 'other', label: 'سایر' }
}

const componentFolder = (filePath) => {
  const raw = String(filePath || '').replace(/\\/g, '/')
  const marker = '/frontend/src/components/'
  const idx = raw.indexOf(marker)
  const relative = idx >= 0 ? raw.slice(idx + marker.length) : raw
  const first = relative.split('/').filter(Boolean)[0] || ''
  if (!first || first.endsWith('.vue')) return { key: 'general', label: 'عمومی' }
  if (first === 'analytics') return { key: 'analytics', label: 'آنالیتیکس' }
  if (first === 'admin' || first === 'management') return { key: 'admin', label: 'مدیریت' }
  return { key: first, label: first }
}

const inferTitleFromRoute = (route) => {
  if (!route) return 'بدون عنوان'
  const parts = route.split('/').filter(Boolean)
  if (!parts.length) return 'صفحه اصلی'
  const last = decodeURIComponent(parts[parts.length - 1] || '')
  return last || 'بدون عنوان'
}

const allPages = computed(() => {
  if (!data.value) return []

  const websitePages = data.value?.backend?.website_pages || []
  const websiteByRoute = new Map(websitePages.map((row) => [row.route, row]))
  const pageOverrides = data.value?.backend?.page_overrides || {}
  const routes = data.value?.url_settings?.routes || []
  const rows = []

  for (const row of routes) {
    const route = row.route
    if (!route || route.startsWith('/management-analytics') || route === '/management') continue

    const website = websiteByRoute.get(route) || {}
    const override = pageOverrides?.[route] || {}
    const sourceText = String(row.source || '')
    let sourceKey = 'tracked'
    if (sourceText.includes('صفحات وب‌سایت')) sourceKey = sourceText.includes('مسیر فرانت') ? 'mixed' : 'website'
    else if (sourceText.includes('مسیر فرانت')) sourceKey = 'frontend'

    const folder = routeFolder(route)

    rows.push({
      route,
      route_key: route.replace('/', '') || 'home',
      title: override.title || website.title || row.title || inferTitleFromRoute(route),
      source_label: row.source || 'ردیابی‌شده',
      source_key: sourceKey,
      file: row.file || row.component || website.html_file || '-',
      html_file: website.html_file || '',
      py_file: website.py_file || '',
      modified_at: website.modified_at || '',
      views: Number(row.views || 0),
      unique_sessions: Number(row.unique_sessions || 0),
      avg_time_spent_seconds: Number(row.avg_time_spent_seconds || 0),
      avg_scroll_depth: Number(row.avg_scroll_depth || 0),
      exits: Number(row.exits || 0),
      noindex: toBool(override.noindex, Boolean(website.noindex)),
      protected_page: toBool(override.protected_page, route.startsWith('/dashboard') || route.startsWith('/management')),
      status_key: override.status_key || 'published',
      status_label: override.status_label || 'منتشر شده',
      content_override_count: Number(override.content_override_count || 0),
      visual_override_count: Number(override.visual_override_count || 0),
      meta_title: override.title || website.title || row.title || inferTitleFromRoute(route),
      meta_description: override.meta_description || website.meta_description || '',
      canonical_url: override.canonical_url || website.canonical_url || '',
      meta_image: override.meta_image || website.meta_image || '',
      folder_key: folder.key,
      folder_label: folder.label,
      full_url: `${data.value?.url_settings?.base_url || ''}${route}` || route,
    })
  }

  const uniqueMap = new Map()
  for (const row of rows) {
    uniqueMap.set(row.route, row)
  }
  return Array.from(uniqueMap.values())
})

const folderBuckets = computed(() => {
  const counter = new Map()
  for (const page of allPages.value) {
    const key = page.folder_key || 'other'
    const label = page.folder_label || 'سایر'
    if (!counter.has(key)) counter.set(key, { key, label, count: 0 })
    counter.get(key).count += 1
  }
  return Array.from(counter.values()).sort((a, b) => a.label.localeCompare(b.label, 'fa'))
})

const filteredPages = computed(() => {
  const q = query.value.trim().toLowerCase()
  let rows = [...allPages.value]

  if (activeFolder.value !== 'all') {
    rows = rows.filter((row) => row.folder_key === activeFolder.value)
  }

  if (sourceFilter.value !== 'all') {
    rows = rows.filter((row) => row.source_key === sourceFilter.value)
  }

  if (q) {
    rows = rows.filter((row) => {
      const hay = `${row.title} ${row.route} ${row.file}`.toLowerCase()
      return hay.includes(q)
    })
  }

  if (sortBy.value === 'views') {
    rows.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'title') {
    rows.sort((a, b) => a.title.localeCompare(b.title, 'fa'))
  } else {
    rows.sort((a, b) => {
      const ad = new Date(a.modified_at || 0).getTime()
      const bd = new Date(b.modified_at || 0).getTime()
      return bd - ad
    })
  }

  return rows
})

const allComponents = computed(() => {
  const rows = Array.isArray(data.value?.frontend?.components) ? data.value.frontend.components : []
  return rows.map((row) => {
    const file = String(row?.file || '').trim()
    const folder = componentFolder(file)
    const routes = (Array.isArray(row?.routes) ? row.routes : [])
      .map((routeValue) => String(routeValue || '').trim())
      .filter((routeValue) => routeValue.startsWith('/mysite') && !routeValue.startsWith('/management'))
    const rawPrimaryRoute = String(row?.primary_route || '').trim()
    const primaryRoute = rawPrimaryRoute.startsWith('/mysite') && !rawPrimaryRoute.startsWith('/management')
      ? rawPrimaryRoute
      : (routes[0] || '')
    return {
      name: String(row?.name || '').trim() || 'Component',
      file,
      modified_at: String(row?.modified_at || ''),
      routes,
      usage_count: Number(row?.usage_count || routes.length || 0),
      primary_route: primaryRoute,
      group_key: folder.key,
      group_label: folder.label,
    }
  })
})

const componentGroups = computed(() => {
  const map = new Map()
  for (const row of allComponents.value) {
    const key = row.group_key || 'general'
    const label = row.group_label || 'عمومی'
    if (!map.has(key)) map.set(key, { key, label, count: 0 })
    map.get(key).count += 1
  }
  return Array.from(map.values()).sort((a, b) => String(a.label || '').localeCompare(String(b.label || ''), 'fa'))
})

const filteredComponents = computed(() => {
  const term = componentQuery.value.trim().toLowerCase()
  let rows = [...allComponents.value]
  if (componentGroup.value !== 'all') {
    rows = rows.filter((row) => row.group_key === componentGroup.value)
  }
  if (term) {
    rows = rows.filter((row) => {
      const hay = `${row.name} ${row.file} ${(row.routes || []).join(' ')}`.toLowerCase()
      return hay.includes(term)
    })
  }
  if (sortBy.value === 'title') {
    rows.sort((a, b) => a.name.localeCompare(b.name, 'fa'))
  } else if (sortBy.value === 'views') {
    rows.sort((a, b) => Number(b.usage_count || 0) - Number(a.usage_count || 0))
  } else {
    rows.sort((a, b) => new Date(b.modified_at || 0).getTime() - new Date(a.modified_at || 0).getTime())
  }
  return rows
})

const selectedPage = computed(() => filteredPages.value.find((row) => row.route === selectedRoute.value) || null)
const selectedMetrics = computed(() => pageStats.value?.selected_page?.metrics || selectedPage.value || {})
const selectedDaily = computed(() => pageStats.value?.selected_page?.daily_views || [])
const selectedSources = computed(() => pageStats.value?.selected_page?.source_breakdown || [])
const dailyMax = computed(() => Math.max(1, ...selectedDaily.value.map((row) => Number(row.views || 0))))
const filteredContentRows = computed(() => {
  const searchTerm = contentSearch.value.trim().toLowerCase()
  let rows = [...contentRows.value]

  if (contentOnlyChanged.value) {
    rows = rows.filter((row) => Boolean(row.has_override))
  }

  if (searchTerm) {
    rows = rows.filter((row) => {
      const hay = `${row.source_text || ''} ${row.replacement_text || ''} ${row.source_file || ''}`.toLowerCase()
      return hay.includes(searchTerm)
    })
  }
  return rows
})
const contentChangedCount = computed(() => contentRows.value.filter((row) => Boolean(row.has_override)).length)
const filteredVisualLayers = computed(() => {
  const term = visualLayerQuery.value.trim().toLowerCase()
  const rows = Array.isArray(visualLayers.value) ? visualLayers.value : []
  if (!term) return rows
  return rows.filter((row) => {
    const hay = `${row.label || ''} ${row.tag || ''} ${row.selector || ''}`.toLowerCase()
    return hay.includes(term)
  })
})
const visualSelectedLayer = computed(() => {
  if (!visualSelectedId.value) return null
  return visualLayerIndex.value?.[visualSelectedId.value] || null
})
const visualOverrideCount = computed(() => Object.keys(visualOverridesMap.value || {}).length)

const shortLabel = (title) => {
  const text = String(title || '').trim()
  return text.slice(0, 2) || 'صف'
}

const heightByMax = (value, maxValue) => {
  const ratio = (Number(value || 0) / Number(maxValue || 1)) * 100
  return Math.max(8, Math.min(100, ratio))
}

const onImgError = (event) => {
  if (!event?.target) return
  event.target.style.display = 'none'
}

const resolveManagementImageSrc = (rawUrl) => {
  const value = String(rawUrl || '').trim()
  if (!value) return ''
  if (value.startsWith('data:') || value.startsWith('blob:')) return value
  if (value.startsWith('//')) {
    return `/api/method/mysite.api.management_image_proxy?url=${encodeURIComponent(`https:${value}`)}`
  }
  if (/^https?:\/\//i.test(value)) {
    return `/api/method/mysite.api.management_image_proxy?url=${encodeURIComponent(value)}`
  }
  return value
}

const normalizeContentText = (value) => String(value || '').replace(/\s+/g, ' ').trim()

const fillFormsFromPage = (page) => {
  if (!page) {
    generalForm.value = { title: '', noindex: false, protected_page: false }
    metaForm.value = { title: '', meta_description: '', canonical_url: '', meta_image: '' }
    return
  }

  generalForm.value = {
    title: page.title || '',
    noindex: Boolean(page.noindex),
    protected_page: Boolean(page.protected_page),
  }
  metaForm.value = {
    title: page.meta_title || page.title || '',
    meta_description: page.meta_description || '',
    canonical_url: page.canonical_url || '',
    meta_image: page.meta_image || '',
  }
}

function resetVisualProps() {
  visualProps.value = {
    text_content: '',
    color: '',
    backgroundColor: '',
    fontSize: '',
    borderRadius: '',
    padding: '',
    margin: '',
    display: '',
    justifyContent: '',
    alignItems: '',
    gap: '',
  }
}

function clearVisualSelection() {
  if (visualSelectedElement) {
    visualSelectedElement.classList.remove('mysite-visual-selected')
  }
  visualSelectedElement = null
  visualSelectedId.value = ''
  resetVisualProps()
}

function escapeCssIdent(value) {
  return String(value || '')
    .replace(/[^a-zA-Z0-9\-_]/g, (char) => `\\${char}`)
}

function isVisualEditableElement(node) {
  if (!node || node.nodeType !== 1) return false
  const tag = String(node.tagName || '').toLowerCase()
  if (!tag) return false
  if (['script', 'style', 'meta', 'link', 'noscript'].includes(tag)) return false
  return true
}

function ensureVisualNodeId(element) {
  const current = String(element.getAttribute(VISUAL_NODE_ATTR) || '').trim()
  if (current) return current
  const generated = `node-${Math.random().toString(36).slice(2, 10)}`
  element.setAttribute(VISUAL_NODE_ATTR, generated)
  return generated
}

function nthOfTypeIndex(element) {
  if (!element || !element.parentElement) return 1
  const tag = element.tagName
  let idx = 1
  let node = element
  while (node.previousElementSibling) {
    node = node.previousElementSibling
    if (node.tagName === tag) idx += 1
  }
  return idx
}

function buildCssSelector(element) {
  if (!element || !element.ownerDocument) return ''
  if (element.id) return `#${escapeCssIdent(element.id)}`

  const parts = []
  let node = element
  while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== 'html') {
    const tag = node.tagName.toLowerCase()
    const part = `${tag}:nth-of-type(${nthOfTypeIndex(node)})`
    parts.unshift(part)
    if (node.tagName.toLowerCase() === 'body') break
    node = node.parentElement
  }
  return parts.join(' > ')
}

function nodeLabel(element) {
  const tag = String(element?.tagName || '').toLowerCase()
  const id = String(element?.id || '').trim()
  const cls = String(element?.className || '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .join('.')
  const text = String(element?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 28)
  const suffix = text ? ` · ${text}` : ''
  if (id) return `${tag}#${id}${suffix}`
  if (cls) return `${tag}.${cls}${suffix}`
  return `${tag}${suffix}`
}

function injectVisualEditorStyles(doc) {
  if (!doc || !doc.head) return
  const styleId = 'mysite-visual-editor-style'
  if (doc.getElementById(styleId)) return
  const style = doc.createElement('style')
  style.id = styleId
  style.textContent = `
    .mysite-visual-selected {
      outline: 2px solid #4f9df5 !important;
      outline-offset: 1px !important;
      box-shadow: 0 0 0 2px rgba(79, 157, 245, 0.22) !important;
      cursor: crosshair !important;
    }
    [${VISUAL_NODE_ATTR}] {
      transition: outline-color .12s ease;
    }
  `
  doc.head.appendChild(style)
}

function buildVisualLayerTree(doc) {
  const rows = []
  const index = {}
  const maxNodes = 900

  function walk(element, depth) {
    if (!isVisualEditableElement(element)) return
    if (rows.length >= maxNodes) return

    const id = ensureVisualNodeId(element)
    const selector = buildCssSelector(element)
    const layer = {
      id,
      depth,
      tag: String(element.tagName || '').toLowerCase(),
      label: nodeLabel(element),
      selector,
      original_text: String(element.innerText || ''),
    }
    rows.push(layer)
    index[id] = layer

    const children = Array.from(element.children || [])
    for (const child of children) {
      walk(child, depth + 1)
      if (rows.length >= maxNodes) break
    }
  }

  const body = doc?.body
  if (!body) {
    visualLayers.value = []
    visualLayerIndex.value = {}
    return
  }
  const bodyChildren = Array.from(body.children || [])
  for (const child of bodyChildren) {
    walk(child, 0)
    if (rows.length >= maxNodes) break
  }

  visualLayers.value = rows
  visualLayerIndex.value = index
}

function getVisualElementById(nodeId) {
  if (!visualFrameDocument || !nodeId) return null
  try {
    return visualFrameDocument.querySelector(`[${VISUAL_NODE_ATTR}="${CSS.escape(nodeId)}"]`)
  } catch (error) {
    return visualFrameDocument.querySelector(`[${VISUAL_NODE_ATTR}="${nodeId.replace(/"/g, '\\"')}"]`)
  }
}

function syncVisualPropsFromElement(element) {
  if (!element || !window.getComputedStyle) {
    resetVisualProps()
    return
  }
  const computedStyle = window.getComputedStyle(element)
  visualProps.value = {
    text_content: String(element.innerText || ''),
    color: String(element.style.color || computedStyle.color || ''),
    backgroundColor: String(element.style.backgroundColor || computedStyle.backgroundColor || ''),
    fontSize: String(element.style.fontSize || computedStyle.fontSize || ''),
    borderRadius: String(element.style.borderRadius || computedStyle.borderRadius || ''),
    padding: String(element.style.padding || computedStyle.padding || ''),
    margin: String(element.style.margin || computedStyle.margin || ''),
    display: String(element.style.display || computedStyle.display || ''),
    justifyContent: String(element.style.justifyContent || computedStyle.justifyContent || ''),
    alignItems: String(element.style.alignItems || computedStyle.alignItems || ''),
    gap: String(element.style.gap || computedStyle.gap || ''),
  }
}

function selectVisualLayer(nodeId) {
  if (!nodeId) return
  const element = getVisualElementById(nodeId)
  if (!element) return

  if (visualSelectedElement && visualSelectedElement !== element) {
    visualSelectedElement.classList.remove('mysite-visual-selected')
  }
  visualSelectedElement = element
  visualSelectedElement.classList.add('mysite-visual-selected')
  visualSelectedId.value = nodeId
  syncVisualPropsFromElement(element)
}

function normalizeVisualOverrideItem(row) {
  const selector = String(row?.selector || '').trim()
  if (!selector) return null
  const styles = {}
  const rawStyles = row?.styles
  if (rawStyles && typeof rawStyles === 'object' && !Array.isArray(rawStyles)) {
    for (const [rawKey, rawValue] of Object.entries(rawStyles)) {
      const key = String(rawKey || '').trim()
      const value = String(rawValue || '').trim()
      if (!key || !value) continue
      styles[key] = value
    }
  }
  const applyText = Boolean(row?.apply_text)
  const textContent = String(row?.text_content ?? '')
  if (!Object.keys(styles).length && !applyText) return null
  return {
    selector,
    tag: String(row?.tag || '').trim(),
    label: String(row?.label || '').trim(),
    styles,
    apply_text: applyText,
    text_content: applyText ? textContent : '',
  }
}

function applyVisualOverridesToDocument(doc) {
  const rows = Object.values(visualOverridesMap.value || {})
  if (!rows.length || !doc) return
  for (const row of rows) {
    const selector = String(row?.selector || '').trim()
    if (!selector) continue
    let elements = []
    try {
      elements = Array.from(doc.querySelectorAll(selector))
    } catch (error) {
      elements = []
    }
    if (!elements.length) continue
    for (const element of elements) {
      if (row.apply_text) {
        element.innerText = String(row.text_content ?? '')
      }
      const styles = row.styles || {}
      for (const [key, value] of Object.entries(styles)) {
        if (!value) continue
        element.style[key] = value
      }
    }
  }
}

function onVisualFrameClick(event) {
  if (!event?.target) return
  const target = event.target.closest('*')
  if (!isVisualEditableElement(target)) return
  const anchor = target.closest('a[href]')
  if (anchor) {
    event.preventDefault()
  }
  event.stopPropagation()
  const nodeId = ensureVisualNodeId(target)
  if (!visualLayerIndex.value[nodeId]) {
    buildVisualLayerTree(visualFrameDocument)
  }
  selectVisualLayer(nodeId)
}

function bindVisualFrameEvents(doc, previousDoc = null) {
  if (!doc) return
  if (visualFrameClickHandler && previousDoc) {
    previousDoc.removeEventListener('click', visualFrameClickHandler, true)
  }
  visualFrameClickHandler = onVisualFrameClick
  doc.addEventListener('click', visualFrameClickHandler, true)
}

function applyVisualField(field, value) {
  if (!visualSelectedElement || !visualSelectedLayer.value) return
  visualSuccess.value = ''
  const nextValue = String(value ?? '')

  const selector = visualSelectedLayer.value.selector
  const map = { ...(visualOverridesMap.value || {}) }
  const existing = map[selector]
    ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
    : {
        selector,
        tag: visualSelectedLayer.value.tag,
        label: visualSelectedLayer.value.label,
        styles: {},
        apply_text: false,
        text_content: '',
      }

  if (field === 'text_content') {
    visualProps.value.text_content = nextValue
    visualSelectedElement.innerText = nextValue
    if (nextValue === String(visualSelectedLayer.value.original_text || '')) {
      existing.apply_text = false
      existing.text_content = ''
    } else {
      existing.apply_text = true
      existing.text_content = nextValue
    }
  } else {
    visualProps.value[field] = nextValue
    if (nextValue.trim()) {
      existing.styles[field] = nextValue
      visualSelectedElement.style[field] = nextValue
    } else {
      delete existing.styles[field]
      visualSelectedElement.style[field] = ''
    }
  }

  if (!existing.apply_text && !Object.keys(existing.styles || {}).length) {
    delete map[selector]
  } else {
    map[selector] = existing
  }
  visualOverridesMap.value = map
}

function resetSelectedVisualLayer() {
  if (!visualSelectedLayer.value) return
  const selector = visualSelectedLayer.value.selector
  const map = { ...(visualOverridesMap.value || {}) }
  if (map[selector]) {
    delete map[selector]
    visualOverridesMap.value = map
  }
  reloadVisualPreview()
}

async function loadVisualOverrides() {
  if (!selectedRoute.value) {
    visualOverridesMap.value = {}
    return
  }
  visualError.value = ''
  try {
    const params = new URLSearchParams({ route: selectedRoute.value })
    const response = await fetch(`/api/method/mysite.api.get_management_page_visual_overrides?${params.toString()}`, {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'دریافت تنظیمات بصری با خطا مواجه شد.')
    }
    const result = payload.message || payload
    const nextMap = {}
    for (const row of Array.isArray(result?.items) ? result.items : []) {
      const normalized = normalizeVisualOverrideItem(row)
      if (!normalized) continue
      nextMap[normalized.selector] = normalized
    }
    visualOverridesMap.value = nextMap
  } catch (err) {
    visualOverridesMap.value = {}
    visualError.value = err?.message || 'خطا در دریافت تنظیمات بصری.'
  }
}

function applyWorkflowResponse(result, targetType, targetKey) {
  if (!(result?.workflow_enforced && result?.change_request)) {
    return false
  }
  workflowRef.value = {
    name: String(result.change_request || '').trim(),
    state: String(result.state || 'Draft').trim() || 'Draft',
    target_type: String(targetType || '').trim(),
    target_key: String(targetKey || '').trim(),
  }
  setWorkflowSuccessMessage(`درخواست تغییر ${workflowRef.value.name} با وضعیت ${workflowRef.value.state} ثبت شد.`)
  return true
}

function isCurrentPageWorkflowRow(row) {
  const targetType = String(row?.target_type || '')
  const key = String(row?.target_key || '').trim()
  if (!key || key !== String(selectedRoute.value || '').trim()) return false
  return ['page_config', 'page_content_override', 'page_visual_override', 'visual_source'].includes(targetType)
}

async function loadLatestPageWorkflowRequest() {
  if (!selectedRoute.value || !canContentEdit.value) {
    workflowRef.value = { name: '', state: '', target_type: '', target_key: '' }
    return
  }
  try {
    const response = await fetch('/api/method/mysite.api.list_management_change_requests?module_key=content&limit=200', {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      return
    }
    const rows = Array.isArray(payload?.message?.items) ? payload.message.items : (Array.isArray(payload?.items) ? payload.items : [])
    const found = rows.find((row) => isCurrentPageWorkflowRow(row))
    workflowRef.value = found
      ? {
          name: String(found.name || ''),
          state: String(found.state || ''),
          target_type: String(found.target_type || ''),
          target_key: String(found.target_key || ''),
        }
      : { name: '', state: '', target_type: '', target_key: '' }
  } catch (error) {
    // ignore lookup errors
  }
}

async function runWorkflowAction(action) {
  const requestName = String(workflowRef.value?.name || '').trim()
  if (!requestName || !action) return
  workflowLoading.value = true
  resetWorkflowMessages()
  try {
    const response = await fetch('/api/method/mysite.api.transition_management_change_request', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: JSON.stringify({
        name: requestName,
        action,
      }),
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'تغییر وضعیت درخواست با خطا مواجه شد.')
    }
    const result = payload.message || payload
    const state = String(result?.change_request?.state || '').trim()
    if (state) {
      workflowRef.value = { ...workflowRef.value, state }
    }
    setWorkflowSuccessMessage(`وضعیت درخواست به ${state || 'نامشخص'} تغییر کرد.`)
    if (action === 'publish') {
      await loadData()
      await loadPageContentSchema()
      await loadVisualOverrides()
    }
  } catch (error) {
    const message = error?.message || 'خطا در تغییر وضعیت درخواست.'
    if (activeSuccessChannel() === 'content') contentError.value = message
    else if (activeSuccessChannel() === 'visual') visualError.value = message
    else saveError.value = message
  } finally {
    workflowLoading.value = false
  }
}

async function saveVisualOverrides() {
  if (!selectedRoute.value) return
  visualSaving.value = true
  visualError.value = ''
  visualSuccess.value = ''
  try {
    const items = Object.values(visualOverridesMap.value || {}).map((row) => ({
      selector: row.selector,
      tag: row.tag || '',
      label: row.label || '',
      styles: row.styles || {},
      apply_text: Boolean(row.apply_text),
      text_content: row.apply_text ? String(row.text_content ?? '') : '',
      enabled: true,
    }))
    const response = await fetch('/api/method/mysite.api.save_management_page_visual_overrides', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: JSON.stringify({
        route: selectedRoute.value,
        items,
      }),
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'ذخیره تغییرات بصری با خطا مواجه شد.')
    }
    const result = payload.message || payload
    if (applyWorkflowResponse(result, 'page_visual_override', selectedRoute.value)) {
      await loadLatestPageWorkflowRequest()
      return
    }
    visualSuccess.value = `تغییرات بصری ذخیره شد. موارد فعال: ${toFa(result.active_items || 0)}`
    await loadData()
  } catch (err) {
    visualError.value = err?.message || 'خطا در ذخیره تغییرات بصری.'
  } finally {
    visualSaving.value = false
  }
}

function buildVisualPreviewUrl() {
  const route = String(selectedRoute.value || '').trim()
  if (!route) return ''
  const separator = route.includes('?') ? '&' : '?'
  return `${route}${separator}management_preview=1&_mt=${Date.now()}`
}

async function reloadVisualPreview() {
  if (!selectedRoute.value) return
  visualLoading.value = true
  visualError.value = ''
  visualSuccess.value = ''
  clearVisualSelection()
  visualPreviewSrc.value = buildVisualPreviewUrl()
}

async function onVisualFrameLoad() {
  const iframe = visualPreviewFrame.value
  if (!iframe) return
  const doc = iframe.contentDocument
  if (!doc || !doc.body) {
    visualLoading.value = false
    visualError.value = 'پیش‌نمایش صفحه قابل دسترس نیست.'
    return
  }
  const previousFrameDoc = visualFrameDocument
  visualFrameDocument = doc
  injectVisualEditorStyles(doc)
  bindVisualFrameEvents(doc, previousFrameDoc)
  buildVisualLayerTree(doc)
  applyVisualOverridesToDocument(doc)
  if (visualLayers.value.length) {
    selectVisualLayer(visualLayers.value[0].id)
  } else {
    clearVisualSelection()
  }
  visualLoading.value = false
}

function openVisualEditorPage() {
  if (!selectedRoute.value) return
  const params = new URLSearchParams({ route: selectedRoute.value })
  window.location.href = `/management-editor?${params.toString()}`
}

function openComponentEditor(componentRow) {
  const file = String(componentRow?.file || '').trim()
  if (!file) return
  selectedComponentFile.value = file
  const selectedRouteValue = String(selectedRoute.value || '').trim()
  const normalizedSelectedRoute = (selectedRouteValue.startsWith('/mysite') && !selectedRouteValue.startsWith('/management'))
    ? selectedRouteValue
    : ''
  const candidateRoute = String(componentRow?.primary_route || '').trim()
  const normalizedCandidateRoute = (candidateRoute.startsWith('/mysite') && !candidateRoute.startsWith('/management'))
    ? candidateRoute
    : ''
  const preferredRoute = normalizedCandidateRoute || normalizedSelectedRoute || '/mysite'
  const params = new URLSearchParams({
    route: preferredRoute,
    target_file: file,
  })
  window.location.href = `/management-editor?${params.toString()}`
}

function normalizeContentRow(row) {
  const sourceText = String(row?.source_text || '').trim()
  const replacementText = String(row?.replacement_text || '').trim()
  return {
    key: String(row?.key || '').trim(),
    scope: String(row?.scope || 'page').trim(),
    scope_label: String(row?.scope_label || '').trim(),
    source_file: String(row?.source_file || '').trim(),
    source_text: sourceText,
    replacement_text: replacementText,
    stale: Boolean(row?.stale),
    has_override: Boolean(replacementText && normalizeContentText(replacementText) !== normalizeContentText(sourceText)),
  }
}

function onContentReplacementInput(key, nextValue) {
  const idx = contentRows.value.findIndex((row) => row.key === key)
  if (idx === -1) return
  const current = contentRows.value[idx]
  const updated = normalizeContentRow({ ...current, replacement_text: String(nextValue || '') })
  contentRows.value[idx] = updated
  contentError.value = ''
  contentSuccess.value = ''
}

async function loadPageContentSchema() {
  if (!selectedRoute.value) {
    contentRows.value = []
    contentSources.value = []
    return
  }
  contentLoading.value = true
  contentError.value = ''
  try {
    const params = new URLSearchParams({ route: selectedRoute.value })
    const response = await fetch(`/api/method/mysite.api.get_management_page_content_schema?${params.toString()}`, {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'اسکن محتوا با خطا مواجه شد.')
    }
    const result = payload.message || payload
    const baseRows = Array.isArray(result?.items) ? result.items : []
    const staleRows = Array.isArray(result?.stale_items) ? result.stale_items : []
    contentRows.value = [...baseRows, ...staleRows].map((row) => normalizeContentRow(row))
    contentSources.value = Array.isArray(result?.sources) ? result.sources : []
  } catch (err) {
    contentRows.value = []
    contentSources.value = []
    contentError.value = err?.message || 'خطا در اسکن محتوای صفحه.'
  } finally {
    contentLoading.value = false
  }
}

async function savePageContentOverrides() {
  if (!selectedRoute.value) return
  contentSaving.value = true
  contentError.value = ''
  contentSuccess.value = ''
  try {
    const items = contentRows.value.map((row) => ({
      key: row.key,
      scope: row.scope,
      scope_label: row.scope_label,
      source_file: row.source_file,
      source_text: row.source_text,
      replacement_text: row.replacement_text,
      enabled: row.has_override,
    }))
    const response = await fetch('/api/method/mysite.api.save_management_page_content_overrides', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: JSON.stringify({
        route: selectedRoute.value,
        items,
      }),
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'ذخیره محتوای صفحه با خطا مواجه شد.')
    }
    const result = payload.message || payload
    if (applyWorkflowResponse(result, 'page_content_override', selectedRoute.value)) {
      await loadLatestPageWorkflowRequest()
      return
    }
    contentSuccess.value = `محتوای صفحه ذخیره شد. تعداد تغییرات فعال: ${toFa(result.active_items || 0)}`
    await loadPageContentSchema()
  } catch (err) {
    contentError.value = err?.message || 'خطا در ذخیره محتوای صفحه.'
  } finally {
    contentSaving.value = false
  }
}

async function generateMetaForAllPages() {
  autoMetaLoading.value = true
  batchMetaError.value = ''
  batchMetaSuccess.value = ''
  try {
    const response = await fetch('/api/method/mysite.api.generate_management_meta_descriptions', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: JSON.stringify({ overwrite: false }),
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'تولید توضیحات متا با خطا مواجه شد.')
    }
    const result = payload.message || payload
    const updated = Number(result.updated_count || 0)
    batchMetaSuccess.value = `توضیحات متا برای ${toFa(updated)} صفحه ایجاد یا تکمیل شد.`
    await loadData()
  } catch (err) {
    batchMetaError.value = err?.message || 'خطا در تولید توضیحات متا.'
  } finally {
    autoMetaLoading.value = false
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
    const response = await fetch(`/api/method/mysite.api.list_management_media_images?${params.toString()}`, {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'دریافت فایل‌های سیستم با خطا مواجه شد.')
    }
    const result = payload.message || payload
    mediaFiles.value = Array.isArray(result?.items) ? result.items : []
  } catch (err) {
    mediaFiles.value = []
    mediaError.value = err?.message || 'خطا در دریافت فایل‌های سیستم.'
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

function selectMetaImage(fileUrl) {
  metaForm.value.meta_image = fileUrl || ''
  saveSuccess.value = ''
  saveError.value = ''
}

function openUploadPicker() {
  mediaError.value = ''
  if (!metaImageInput.value) return
  metaImageInput.value.value = ''
  metaImageInput.value.click()
}

async function uploadMetaImage(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  mediaUploading.value = true
  mediaError.value = ''
  try {
    const form = new FormData()
    form.append('file', file)
    form.append('is_private', '0')
    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: form,
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'آپلود تصویر متا با خطا مواجه شد.')
    }
    const result = payload.message || payload
    const fileUrl = result?.file_url || ''
    if (!fileUrl) {
      throw new Error('نشانی فایل آپلودشده دریافت نشد.')
    }
    metaForm.value.meta_image = fileUrl
    if (showMediaBrowser.value) {
      await loadMediaFiles()
    }
  } catch (err) {
    mediaError.value = err?.message || 'خطا در آپلود تصویر.'
  } finally {
    mediaUploading.value = false
  }
}

async function savePageConfig() {
  if (!selectedPage.value) return

  saveLoading.value = true
  saveError.value = ''
  saveSuccess.value = ''

  const keepRoute = selectedRoute.value
  const keepTab = detailTab.value

  try {
    const response = await fetch('/api/method/mysite.api.save_management_page_config', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: JSON.stringify({
        route: keepRoute,
        payload: {
          title: (metaForm.value.title || generalForm.value.title || '').trim(),
          meta_description: (metaForm.value.meta_description || '').trim(),
          canonical_url: (metaForm.value.canonical_url || '').trim(),
          meta_image: (metaForm.value.meta_image || '').trim(),
          noindex: Boolean(generalForm.value.noindex),
          protected_page: Boolean(generalForm.value.protected_page),
        },
      }),
    })

    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error(payload?.message || 'ذخیره تنظیمات صفحه با خطا مواجه شد.')
    }
    const result = payload.message || payload
    if (applyWorkflowResponse(result, 'page_config', keepRoute)) {
      await loadLatestPageWorkflowRequest()
      return
    }

    await loadData()
    selectedRoute.value = keepRoute
    detailTab.value = keepTab
    saveSuccess.value = 'تنظیمات صفحه ذخیره شد.'
  } catch (err) {
    saveError.value = err?.message || 'خطا در ذخیره تنظیمات صفحه.'
  } finally {
    saveLoading.value = false
  }
}

async function loadPageAnalytics() {
  if (!selectedRoute.value) {
    pageStats.value = null
    return
  }

  statsLoading.value = true
  try {
    const params = new URLSearchParams({
      range_key: analyticsRange.value,
      group_key: '__all__',
      page_path: selectedRoute.value,
      limit: '20',
    })
    const response = await fetch(`/api/method/mysite.analytics_api.get_site_traffic?${params.toString()}`, {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error('دریافت آمار صفحه با خطا مواجه شد.')
    }
    pageStats.value = payload.message || payload
  } catch (e) {
    pageStats.value = null
  } finally {
    statsLoading.value = false
  }
}

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/method/mysite.api.get_management_panel_data', {
      credentials: 'same-origin',
    })
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      if (response.status === 403) throw new Error('دسترسی به پنل مدیریت ندارید.')
      throw new Error('دریافت اطلاعات مدیریت با خطا مواجه شد.')
    }
    data.value = payload.message || payload
    if (!selectedRoute.value && allPages.value.length) {
      selectedRoute.value = allPages.value[0].route
    }
    if (!selectedComponentFile.value && allComponents.value.length) {
      selectedComponentFile.value = allComponents.value[0].file
    }
  } catch (err) {
    error.value = err?.message || 'خطا در دریافت اطلاعات مدیریت.'
  } finally {
    loading.value = false
  }
}

watch(filteredPages, (rows) => {
  if (!rows.length) {
    selectedRoute.value = ''
    return
  }
  if (!rows.some((row) => row.route === selectedRoute.value)) {
    selectedRoute.value = rows[0].route
  }
})

watch(filteredComponents, (rows) => {
  if (!rows.length) {
    selectedComponentFile.value = ''
    return
  }
  if (!rows.some((row) => row.file === selectedComponentFile.value)) {
    selectedComponentFile.value = rows[0].file
  }
})

watch([selectedRoute, analyticsRange], () => {
  loadPageAnalytics()
})

watch(selectedPage, (page) => {
  fillFormsFromPage(page)
  saveError.value = ''
  saveSuccess.value = ''
  contentError.value = ''
  contentSuccess.value = ''
  mediaError.value = ''
}, { immediate: true })

watch(selectedRoute, () => {
  if (!selectedRoute.value) {
    detailTab.value = 'general'
    if (visualFrameClickHandler && visualFrameDocument) {
      visualFrameDocument.removeEventListener('click', visualFrameClickHandler, true)
    }
    visualFrameDocument = null
    visualLayers.value = []
    visualLayerIndex.value = {}
    visualOverridesMap.value = {}
    visualLayerQuery.value = ''
    visualPreviewSrc.value = ''
    visualError.value = ''
    visualSuccess.value = ''
    workflowRef.value = { name: '', state: '', target_type: '', target_key: '' }
    clearVisualSelection()
    return
  }
  detailTab.value = 'general'
  contentRows.value = []
  contentSources.value = []
  contentSearch.value = ''
  contentOnlyChanged.value = false
  visualLayerQuery.value = ''
  visualLayers.value = []
  visualLayerIndex.value = {}
  visualOverridesMap.value = {}
  visualPreviewSrc.value = ''
  visualError.value = ''
  visualSuccess.value = ''
  if (visualFrameClickHandler && visualFrameDocument) {
    visualFrameDocument.removeEventListener('click', visualFrameClickHandler, true)
  }
  visualFrameDocument = null
  workflowRef.value = { name: '', state: '', target_type: '', target_key: '' }
  clearVisualSelection()
  loadPageContentSchema()
  loadLatestPageWorkflowRequest()
})

onMounted(() => {
  try {
    const savedMode = localStorage.getItem(LIST_VIEW_STORAGE_KEY)
    if (savedMode === 'grid' || savedMode === 'list' || savedMode === 'table') {
      listViewMode.value = savedMode
    }
  } catch (error) {
    // Ignore storage errors.
  }
  loadData()
})

onBeforeUnmount(() => {
  if (visualFrameClickHandler && visualFrameDocument) {
    visualFrameDocument.removeEventListener('click', visualFrameClickHandler, true)
  }
  visualFrameClickHandler = null
  visualFrameDocument = null
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
.builder-page {
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  max-width: 100vw;
  background: var(--admin-bg);
  color: var(--text-main);
}

.builder-shell {
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-4);
  display: grid;
  grid-template-columns: minmax(0, 260px) 1fr minmax(0, 470px);
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

.main-nav,
.folder-list {
  display: grid;
  gap: var(--space-2);
}

.nav-item,
.folder-item {
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
  justify-content: space-between;
  cursor: pointer;
}

.nav-item.active,
.folder-item.active {
  border-color: transparent;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}

.folder-head h4 {
  margin: 0;
  color: var(--admin-text-soft);
  font-size: var(--text-sm);
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
  gap: var(--space-3);
  align-items: flex-start;
}

.list-header h1 {
  margin: 0;
  font-size: 1.55rem;
}

.list-header p {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.toolbar {
  display: grid;
  grid-template-columns: minmax(140px, 1fr) minmax(0, 170px) minmax(0, 150px) auto auto auto;
  gap: var(--space-2);
  min-width: 0;
}

.toolbar input,
.toolbar select,
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

.ghost-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}

.page-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  cursor: pointer;
}

.page-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.thumb {
  height: 110px;
  border-radius: var(--radius-md);
  border: 1px solid var(--admin-border);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.3);
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
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: var(--admin-text-soft);
  background: linear-gradient(150deg, rgba(75, 55, 45, 0.2) 0%, rgba(35, 52, 79, 0.2) 100%);
}

.page-card h3 {
  margin: 0;
  font-size: var(--text-md);
  line-height: 1.6;
  min-height: var(--touch-min);
}

.route {
  margin: 0;
  direction: ltr;
  text-align: left;
  font-size: var(--text-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta,
.card-stats {
  display: grid;
  gap: var(--space-1);
}

.card-meta span,
.card-stats small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.pages-list {
  display: grid;
  gap: var(--space-2);
}

.page-row {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-2);
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) auto;
  gap: var(--space-3);
  align-items: center;
  cursor: pointer;
}

.page-row.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.row-thumb {
  height: 70px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--admin-border);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.row-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-main {
  min-width: 0;
  display: grid;
  gap: var(--space-1);
}

.row-main h3 {
  margin: 0;
  font-size: 0.93rem;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-main small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.row-meta {
  display: grid;
  justify-items: end;
  gap: var(--space-1);
}

.row-meta span,
.row-meta small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.pages-table-wrap {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
}

.pages-table-wrap table {
  width: 100%;
  min-width: 0;
  border-collapse: collapse;
}

.pages-table-wrap th,
.pages-table-wrap td {
  border-bottom: 1px solid var(--admin-border);
  padding: 8px 9px;
  font-size: var(--text-sm);
  text-align: right;
  white-space: nowrap;
}

.pages-table-wrap th {
  position: sticky;
  top: 0;
  background: var(--admin-panel-bg);
  color: var(--admin-text-soft);
  z-index: 1;
}

.pages-table-wrap tbody tr {
  cursor: pointer;
}

.pages-table-wrap tbody tr:hover td {
  background: rgba(255, 255, 255, 0.03);
}

.pages-table-wrap tbody tr.active td {
  background: color-mix(in srgb, var(--accent-gold) 14%, transparent);
}

.pages-table-wrap tbody tr:last-child td {
  border-bottom: none;
}

.pages-table-wrap .title-cell {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pages-table-wrap .route-cell {
  direction: ltr;
  text-align: left;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-select {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-sm);
  background: var(--admin-input-bg);
  color: var(--text-main);
  min-height: var(--touch-min);
  padding: 0 8px;
  font-family: inherit;
  font-size: var(--text-xs);
  cursor: pointer;
}

.components-area {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-3);
}

.components-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.components-head h3 {
  margin: 0;
  font-size: 1rem;
}

.components-tools {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 160px;
  gap: var(--space-2);
}

.components-tools input,
.components-tools select {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
}

.components-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-2);
}

.component-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-input-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  cursor: pointer;
}

.component-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.component-card-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  align-items: center;
}

.component-card-head strong {
  font-size: var(--text-base);
}

.component-card-head small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.component-meta {
  display: grid;
  gap: var(--space-1);
}

.component-meta small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
}

.component-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.ghost.mini {
  min-height: var(--touch-min);
  font-size: var(--text-xs);
  padding: 0 8px;
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
  gap: var(--space-2);
  align-items: flex-start;
}

.detail-header h2 {
  margin: 0;
  font-size: var(--text-lg);
}

.detail-header code {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.detail-tabs {
  display: inline-flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.detail-tabs button {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  border-radius: var(--radius-sm);
  min-height: var(--touch-min);
  padding: 0 9px;
  font-family: inherit;
  font-size: var(--text-sm);
  color: var(--text-main);
  cursor: pointer;
}

.detail-tabs button.active {
  border-color: transparent;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}

.workflow-row {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-chip-bg);
  padding: var(--space-2);
  display: grid;
  gap: var(--space-2);
}

.workflow-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.detail-body {
  display: grid;
  gap: var(--space-3);
}

.detail-body h3 {
  margin: 0;
  font-size: var(--text-lg);
}

.form-grid {
  display: grid;
  gap: var(--space-2);
}

.form-grid.two {
  grid-template-columns: 1fr 1fr;
}

.form-grid label {
  display: grid;
  gap: var(--space-1);
}

.form-grid span {
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.form-grid input,
.form-grid textarea,
.analytics-head select {
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
  min-height: 100px;
  resize: vertical;
}

.line-item {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: var(--space-2) var(--space-3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  font-size: var(--text-base);
}

.line-item span {
  color: var(--admin-text-soft);
}

.line-item a {
  direction: ltr;
  text-align: left;
  color: var(--text-main);
}

.line-item.switches input {
  width: 18px;
  height: 18px;
}

.save-row {
  display: flex;
  justify-content: flex-end;
}

.design-toolbar {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.builder-quick-info {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.builder-quick-info small {
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
  direction: ltr;
  text-align: left;
}

.meta-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.content-toolbar {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto auto auto;
  gap: var(--space-2);
  align-items: center;
}

.content-toolbar input {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
}

.content-changed-only {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-md);
  background: var(--admin-input-bg);
  min-height: var(--touch-min);
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.content-sources {
  border: 1px dashed var(--admin-border);
  border-radius: var(--radius-md);
  padding: var(--space-2);
  display: grid;
  gap: var(--space-1);
}

.content-sources small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
  direction: ltr;
  text-align: left;
}

.content-list {
  display: grid;
  gap: var(--space-2);
  max-height: 540px;
  overflow: auto;
}

.content-item {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.content-item-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  align-items: center;
}

.content-item-head small {
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
  direction: ltr;
  text-align: left;
}

.content-badge {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-pill);
  padding: 2px 8px;
  font-size: var(--text-xs);
  color: var(--admin-text-soft);
  white-space: nowrap;
}

.content-badge.changed {
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
}

.content-item label {
  display: grid;
  gap: var(--space-1);
}

.content-item span {
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.content-item textarea {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
  font-size: var(--text-base);
  resize: vertical;
}

.hidden-file {
  display: none;
}

.media-browser {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
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
  max-height: 330px;
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

.media-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-gold) 35%, transparent);
}

.media-card img {
  width: 100%;
  height: 76px;
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

.status {
  border-radius: var(--radius-pill);
  padding: 3px 10px;
  font-size: var(--text-xs);
  border: 1px solid var(--admin-border);
}

.analytics-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpis {
  display: grid;
  gap: var(--space-2);
}

.kpis.two {
  grid-template-columns: 1fr 1fr;
}

.kpis article {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: 9px;
}

.kpis p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.kpis strong {
  margin-top: 6px;
  display: block;
  font-size: var(--text-xl);
}

.chart-box {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  overflow-x: auto;
  max-width: 100%;
}

.chart-box h4 {
  margin: 0;
  font-size: var(--text-md);
}

.chart-box table {
  width: 100%;
  max-width: 100%;
  table-layout: auto;
  word-break: break-word;
}

.spark-wrap {
  display: grid;
  gap: var(--space-2);
}

.sparkline {
  min-height: 170px;
  display: flex;
  align-items: flex-end;
  gap: 5px;
  overflow-x: auto;
}

.spark-col {
  display: grid;
  gap: 5px;
  justify-items: center;
  min-width: 16px;
}

.spark-bar {
  width: 12px;
  border-radius: 6px 6px 0 0;
  background: linear-gradient(180deg, rgba(67, 111, 186, 0.22), #2f6fba);
}

.spark-col small {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--admin-border);
  padding: 7px 5px;
  font-size: var(--text-sm);
  text-align: right;
}

th {
  color: var(--admin-text-soft);
  font-weight: 700;
}

.social-preview {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-chip-bg);
  padding: var(--space-3);
}

.social-preview h4 {
  margin: 0 0 8px;
  font-size: 0.9rem;
}

.preview-card {
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--admin-input-bg);
}

.preview-image {
  height: 160px;
  background: rgba(255, 255, 255, 0.2);
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-copy {
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.preview-copy p,
.preview-copy small {
  margin: 0;
  color: var(--text-muted);
}

.preview-copy strong {
  line-height: 1.5;
}

.state {
  border: 1px dashed var(--admin-border);
  border-radius: var(--radius-lg);
  text-align: center;
  color: var(--admin-text-soft);
  padding: var(--space-5);
}

.state.error {
  color: #fca5a5;
}

.state.success {
  color: #86efac;
}

.hint {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.visual-editor-overlay {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(8, 12, 20, 0.76);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  padding: var(--space-3);
  box-sizing: border-box;
  overflow: hidden;
}

.visual-editor-panel {
  width: 100%;
  max-width: 1600px;
  height: calc(100vh - var(--space-3) * 2);
  margin: 0 auto;
  border: 1px solid var(--admin-border);
  border-radius: var(--radius-lg);
  background: var(--admin-panel-bg);
  display: grid;
  grid-template-rows: auto 1fr;
  overflow: hidden;
  box-sizing: border-box;
}

.visual-editor-header {
  border-bottom: 1px solid var(--admin-border);
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  align-items: center;
}

.visual-editor-header h3 {
  margin: 0;
  font-size: 1rem;
}

.visual-editor-header small {
  color: var(--text-muted);
  direction: ltr;
  text-align: left;
  display: block;
  margin-top: 4px;
}

.visual-editor-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.visual-editor-body-grid {
  min-height: 0;
  display: grid;
  grid-template-columns: 280px 1fr 360px;
  gap: 0;
}

.ve-left,
.ve-right {
  background: var(--admin-chip-bg);
  border-inline-end: 1px solid var(--admin-border);
  min-height: 0;
  display: grid;
  grid-template-rows: auto 1fr;
}

.ve-right {
  border-inline-end: none;
  border-inline-start: 1px solid var(--admin-border);
}

.ve-search {
  padding: var(--space-3);
  border-bottom: 1px solid var(--admin-border);
}

.ve-search input {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
  width: 100%;
}

.ve-layer-list {
  min-height: 0;
  overflow: auto;
  padding: var(--space-2);
  display: grid;
  align-content: start;
  gap: var(--space-2);
}

.ve-layer-item {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: 0 10px;
  font-family: inherit;
  font-size: var(--text-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: right;
  cursor: pointer;
}

.ve-layer-item.active {
  border-color: transparent;
  background: linear-gradient(130deg, var(--admin-tab-active-start), var(--admin-tab-active-end));
  color: #fff;
}

.ve-layer-item small {
  opacity: 0.75;
}

.ve-center {
  min-height: 0;
  background: color-mix(in srgb, var(--admin-panel-bg) 82%, #0b1321 18%);
  padding: var(--space-3);
}

.ve-right {
  padding: var(--space-3);
}

.ve-props {
  min-height: 0;
  overflow: auto;
  display: grid;
  align-content: start;
  gap: var(--space-2);
}

.ve-props h4 {
  margin: 0;
  font-size: 1rem;
}

.ve-props small {
  direction: ltr;
  text-align: left;
  color: var(--admin-text-soft);
  font-size: var(--text-xs);
}

.ve-props label {
  display: grid;
  gap: var(--space-1);
}

.ve-props span {
  font-size: var(--text-sm);
  color: var(--admin-text-soft);
}

.ve-props input,
.ve-props textarea {
  border: 1px solid var(--admin-border);
  background: var(--admin-input-bg);
  color: var(--text-main);
  border-radius: var(--radius-md);
  min-height: var(--touch-min);
  padding: var(--space-2) var(--space-3);
  font-family: inherit;
  font-size: var(--text-base);
}

.ve-props textarea {
  min-height: 88px;
  resize: vertical;
}

.ve-prop-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.visual-editor-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

@media (max-width: 1560px) {
  .builder-shell {
    grid-template-columns: 220px 1fr;
  }

  .detail-area {
    grid-column: 1 / -1;
    position: static;
    max-height: none;
  }
}

@media (max-width: 1020px) {
  .builder-shell {
    grid-template-columns: 1fr;
    padding: var(--space-3);
    padding-bottom: 70px; /* space for bottom tab bar */
  }

  .sidebar {
    display: none;
  }

  .toolbar {
    grid-template-columns: 1fr 1fr;
  }

  .toolbar input {
    grid-column: 1 / -1;
  }

  .list-header {
    flex-direction: column;
  }

  .page-row {
    grid-template-columns: 70px minmax(0, 1fr);
  }

  .row-meta {
    grid-column: 1 / -1;
    justify-items: start;
    grid-auto-flow: column;
    align-items: center;
    gap: var(--space-2);
    padding-top: 4px;
    border-top: 1px dashed var(--admin-border);
  }

  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .thumb {
    height: 80px;
  }

  .form-grid.two,
  .kpis.two {
    grid-template-columns: 1fr;
  }

  .content-toolbar {
    grid-template-columns: 1fr 1fr;
  }

  .content-toolbar input {
    grid-column: 1 / -1;
  }

  .components-tools {
    grid-template-columns: 1fr;
  }

  .components-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .detail-tabs {
    display: flex;
    overflow-x: auto;
    gap: var(--space-1);
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
  }

  .detail-tabs button {
    white-space: nowrap;
    flex-shrink: 0;
  }

  .pages-table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .line-item {
    flex-wrap: wrap;
    gap: var(--space-1);
  }

  .visual-editor-overlay {
    padding: 0;
  }

  .visual-editor-panel {
    width: 100%;
    height: 100vh;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  .visual-editor-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .visual-editor-actions {
    width: 100%;
  }

  .visual-editor-body-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(260px, 44vh) auto;
  }

  .ve-left,
  .ve-right {
    border-inline: none;
  }

  .ve-left {
    border-bottom: 1px solid var(--admin-border);
  }

  .ve-right {
    border-top: 1px solid var(--admin-border);
  }
}

@media (max-width: 480px) {
  .builder-shell {
    padding: var(--space-1);
    gap: var(--space-2);
  }

  .toolbar {
    grid-template-columns: 1fr;
  }

  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2);
  }

  .page-card {
    padding: var(--space-1);
  }

  .thumb {
    height: 60px;
  }

  .page-card h3 {
    font-size: var(--text-sm);
    min-height: var(--touch-min);
  }

  .content-toolbar {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    gap: var(--space-2);
  }

  .detail-header h2 {
    font-size: var(--text-md);
  }

  .list-area,
  .detail-area {
    padding: var(--space-2);
  }

  .list-header h1 {
    font-size: var(--text-xl);
  }

  .ghost {
    min-height: var(--touch-min);
    font-size: var(--text-sm);
  }

  .media-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .media-card img {
    height: 56px;
  }

  .sparkline {
    min-height: 120px;
  }

  .kpis.two article {
    padding: var(--space-1);
  }

  .kpis strong {
    font-size: 1rem;
  }
}
</style>
