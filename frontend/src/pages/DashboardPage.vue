<template>
  <div class="dashboard-page" dir="rtl">
    <div class="liquid-bg">
      <div class="blob b1"></div>
      <div class="blob b2"></div>
      <div class="blob b3"></div>
    </div>

    <div class="dash-shell">
      <header class="glass-panel dash-header">
        <div>
          <p class="eyebrow">پورتال مشتری</p>
          <h1>مدیریت مشتری</h1>
          <p class="sub">{{ session?.full_name || 'کاربر' }}</p>
        </div>
        <div class="head-actions">
          <label class="field">
            <span>مشتری</span>
            <select v-model="selectedCustomer">
              <option value="">همه مشتری‌ها</option>
              <option v-for="c in session?.customers || []" :key="c.name" :value="c.name">
                {{ c.customer_name || c.name }}
              </option>
            </select>
          </label>
          <button class="ghost-btn" @click="logout">خروج</button>
        </div>
      </header>

      <div v-if="sessionLoading" class="glass-panel state-card">در حال بارگذاری نشست کاربر...</div>
      <div v-else-if="sessionError" class="glass-panel state-card error">{{ sessionError }}</div>

      <template v-else>
        <div class="glass-panel tabs-wrap">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <section v-if="activeTab === 'overview'" class="overview">
          <div class="kpis">
            <article class="glass-panel kpi">
              <p>درخواست پیش‌فاکتور</p>
              <h3>{{ summary?.counts?.quotation_requests || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>پیش‌فاکتور</p>
              <h3>{{ summary?.counts?.quotations || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>سفارش</p>
              <h3>{{ summary?.counts?.sales_orders || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>تحویل</p>
              <h3>{{ summary?.counts?.deliveries || 0 }}</h3>
            </article>
          </div>

          <div class="kpis">
            <article class="glass-panel kpi">
              <p>جمع فاکتور</p>
              <h3>{{ formatCurrency(summary?.total_invoiced || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>مانده بدهی</p>
              <h3>{{ formatCurrency(summary?.total_outstanding || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>فاکتور باز</p>
              <h3>{{ summary?.unpaid_count || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>فاکتور سررسید گذشته</p>
              <h3>{{ summary?.overdue_count || 0 }}</h3>
            </article>
          </div>

          <div class="kpis">
            <article class="glass-panel kpi">
              <p>دریافت پرداخت</p>
              <h3>{{ formatCurrency(summary?.payments_summary?.total_received || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>تعداد پرداخت</p>
              <h3>{{ summary?.payments_summary?.payment_count || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>جمع بدهکار دفترکل</p>
              <h3>{{ formatCurrency(summary?.ledger_summary?.total_debit || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>مانده دفترکل</p>
              <h3>{{ formatCurrency(summary?.ledger_summary?.net_balance || 0) }}</h3>
            </article>
          </div>

          <div class="overview-grid">
            <div class="glass-panel list-card">
              <div class="card-head">
                <h3>آخرین فعالیت‌ها</h3>
              </div>
              <div v-if="summaryLoading" class="state-card">در حال بارگذاری...</div>
              <div v-else-if="!summary?.recent_activity?.length" class="state-card">فعالیتی یافت نشد.</div>
              <div v-else class="rows">
                <div v-for="row in summary.recent_activity" :key="`${row.section}-${row.name}`" class="row">
                  <div>
                    <strong>{{ sectionLabels[row.section] || row.section }}</strong>
                    <p>{{ row.name }}</p>
                  </div>
                  <div class="row-meta">
                    <span>{{ row.status || '-' }}</span>
                    <small>{{ formatDate(row.date) }}</small>
                  </div>
                </div>
              </div>
            </div>

            <div class="glass-panel list-card">
              <div class="card-head">
                <h3>محصولات پرتکرار (پیش‌نمایش)</h3>
              </div>
              <div v-if="summaryLoading" class="state-card">در حال بارگذاری...</div>
              <div v-else-if="!summary?.insights_preview?.length" class="state-card">داده‌ای برای نمایش نیست.</div>
              <div v-else class="rows">
                <div v-for="item in summary.insights_preview" :key="`${item.item_code}-${item.item_name}`" class="row">
                  <div>
                    <strong>{{ item.item_name || item.item_code || '-' }}</strong>
                    <p>{{ item.item_code || '-' }}</p>
                  </div>
                  <div class="row-meta">
                    <span>{{ Number(item.total_qty || 0).toLocaleString('fa-IR') }} عدد</span>
                    <small>{{ formatCurrency(item.total_amount || 0) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="isDocumentTab(activeTab)" class="glass-panel doc-panel">
          <div class="controls">
            <label class="field compact">
              <span>وضعیت</span>
              <input v-model="activeDocState.status" placeholder="مثال: پرداخت‌نشده یا پیش‌نویس" />
            </label>
            <label class="field compact">
              <span>جستجو</span>
              <input v-model="activeDocState.search" placeholder="شماره سند..." />
            </label>
            <label class="field compact">
              <span>از تاریخ</span>
              <input v-model="activeDocState.fromDate" type="date" />
            </label>
            <label class="field compact">
              <span>تا تاریخ</span>
              <input v-model="activeDocState.toDate" type="date" />
            </label>
            <button class="ghost-btn" @click="applyDocFilters(activeTab)">اعمال فیلتر</button>
          </div>

          <div v-if="activeDocState.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="activeDocState.error" class="state-card error">{{ activeDocState.error }}</div>
          <div v-else-if="!activeDocState.items.length" class="state-card">رکوردی یافت نشد.</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>سند</th>
                  <th>تاریخ</th>
                  <th>مشتری</th>
                  <th>وضعیت</th>
                  <th>مبلغ</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in activeDocState.items" :key="row.name">
                  <td>{{ row.name }}</td>
                  <td>{{ formatDate(row.posting_date || row.transaction_date || row.creation) }}</td>
                  <td>{{ row.customer || row.customer_name || '-' }}</td>
                  <td>{{ row.status || '-' }}</td>
                  <td>{{ formatCurrency(row.grand_total || row.outstanding_amount || 0) }}</td>
                  <td class="actions">
                    <button class="mini-btn" @click="openDetail(activeTab, row.name)">جزئیات</button>
                    <button
                      v-if="activeTab === 'quotation_requests'"
                      class="mini-btn"
                      @click="openRequestEditor(row.name)"
                    >
                      مدیریت کامل
                    </button>
                    <button class="mini-btn gold" @click="openPdf(activeTab, row.name)">PDF</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <button class="ghost-btn" :disabled="!activeDocState.hasPrev" @click="changePage(activeTab, -1)">قبلی</button>
            <span>صفحه {{ activeDocState.page }} از {{ activeDocState.totalPages || 1 }}</span>
            <button class="ghost-btn" :disabled="!activeDocState.hasNext" @click="changePage(activeTab, 1)">بعدی</button>
          </div>
        </section>

        <section v-else-if="activeTab === 'support_tickets'" class="glass-panel doc-panel">
          <div v-if="supportState.runtimeError" class="state-card error">{{ supportState.runtimeError }}</div>
          <template v-else>
            <div class="controls support-controls">
              <label class="field compact">
                <span>وضعیت</span>
                <input v-model="supportState.status" placeholder="مثال: باز یا در حال پیگیری" />
              </label>
              <button class="ghost-btn" @click="applySupportFilters">اعمال فیلتر</button>
              <button class="ghost-btn gold" :disabled="supportState.chatOpening" @click="openSupportChat">
                {{ supportState.chatOpening ? 'در حال اتصال...' : 'چت پشتیبانی' }}
              </button>
            </div>

            <div class="support-create">
              <h3>ثبت تیکت جدید</h3>
              <div class="support-create-grid">
                <label class="field">
                  <span>عنوان</span>
                  <input v-model="supportState.createSubject" placeholder="مثال: پیگیری سفارش" />
                </label>
                <label class="field">
                  <span>کد کالا (اختیاری)</span>
                  <input v-model="supportState.createItemCode" placeholder="ITEM-0001" dir="ltr" />
                </label>
              </div>
              <label class="field">
                <span>توضیحات</span>
                <textarea v-model="supportState.createDescription" rows="3" placeholder="شرح کامل مشکل یا درخواست"></textarea>
              </label>
              <div class="actions">
                <button class="ghost-btn gold" :disabled="supportState.createLoading" @click="createSupportTicket">
                  {{ supportState.createLoading ? 'در حال ثبت...' : 'ثبت تیکت' }}
                </button>
              </div>
              <div v-if="supportState.createError" class="state-card error">{{ supportState.createError }}</div>
              <div v-else-if="supportState.createSuccess" class="state-card">{{ supportState.createSuccess }}</div>
            </div>

            <div class="support-layout">
              <div class="support-list">
                <div v-if="supportState.loading" class="state-card">در حال بارگذاری تیکت‌ها...</div>
                <div v-else-if="supportState.error" class="state-card error">{{ supportState.error }}</div>
                <div v-else-if="!supportState.items.length" class="state-card">تیکتی ثبت نشده است.</div>
                <div v-else class="rows">
                  <button
                    v-for="ticket in supportState.items"
                    :key="ticket.name"
                    class="support-ticket-row"
                    :class="{ active: supportState.selectedName === ticket.name }"
                    @click="selectSupportTicket(ticket.name)"
                  >
                    <strong>{{ ticket.subject }}</strong>
                    <small>{{ ticket.name }}</small>
                    <small>{{ formatSupportStatus(ticket.status) }} | {{ ticket.assigned_to || 'در صف' }}</small>
                  </button>
                </div>
              </div>

              <div class="support-detail">
                <div v-if="supportState.detailLoading" class="state-card">در حال دریافت جزئیات تیکت...</div>
                <div v-else-if="supportState.detailError" class="state-card error">{{ supportState.detailError }}</div>
                <div v-else-if="!supportState.detail || !supportState.detail.ticket" class="state-card">یک تیکت را برای مشاهده انتخاب کنید.</div>
                <div v-else>
                  <h3>{{ supportState.detail.ticket.subject }}</h3>
                  <p class="support-ticket-meta">{{ supportState.detail.ticket.name }} | {{ formatSupportStatus(supportState.detail.ticket.status) }}</p>
                  <div class="support-description" v-html="supportState.detail.ticket.description"></div>

                  <h4>گفتگو</h4>
                  <div v-if="!(supportState.detail.communications || []).length" class="state-card">هنوز پیامی ثبت نشده است.</div>
                  <div v-else class="support-conversation">
                    <article
                      v-for="comm in supportState.detail.communications"
                      :key="comm.name"
                      class="support-bubble"
                      :class="{ sent: comm.sent_or_received === 'Sent' }"
                    >
                      <small>{{ comm.sender || '-' }} | {{ formatDate(comm.creation) }}</small>
                      <p>{{ comm.content }}</p>
                    </article>
                  </div>

                  <label class="field">
                    <span>پاسخ شما</span>
                    <textarea v-model="supportState.replyMessage" rows="3" placeholder="ثبت پاسخ روی همین تیکت"></textarea>
                  </label>
                  <div class="actions">
                    <button class="ghost-btn gold" :disabled="supportState.replyLoading" @click="sendSupportReply">
                      {{ supportState.replyLoading ? 'در حال ارسال...' : 'ارسال پاسخ' }}
                    </button>
                  </div>
                  <div v-if="supportState.replyError" class="state-card error">{{ supportState.replyError }}</div>
                  <div v-else-if="supportState.replySuccess" class="state-card">{{ supportState.replySuccess }}</div>
                </div>
              </div>
            </div>

            <div class="pager">
              <button class="ghost-btn" :disabled="!supportState.hasPrev" @click="changeSupportPage(-1)">قبلی</button>
              <span>صفحه {{ supportState.page }} از {{ supportState.totalPages || 1 }}</span>
              <button class="ghost-btn" :disabled="!supportState.hasNext" @click="changeSupportPage(1)">بعدی</button>
            </div>

            <div class="support-chat-panel">
              <h3>چت‌های پشتیبانی</h3>
              <div class="support-chat-grid">
                <div class="support-chat-list">
                  <div class="actions">
                    <button class="ghost-btn" :disabled="supportState.chatListLoading" @click="loadSupportChats">بروزرسانی چت‌ها</button>
                  </div>
                  <div v-if="supportState.chatListLoading" class="state-card">در حال دریافت چت‌ها...</div>
                  <div v-else-if="supportState.chatListError" class="state-card error">{{ supportState.chatListError }}</div>
                  <div v-else-if="!supportState.chats.length" class="state-card">چتی ثبت نشده است.</div>
                  <div v-else class="rows">
                    <button
                      v-for="chat in supportState.chats"
                      :key="chat.name"
                      class="support-ticket-row"
                      :class="{ active: supportState.selectedChat?.name === chat.name }"
                      @click="supportState.selectedChat = chat"
                    >
                      <strong>{{ chat.ticket_subject || chat.ticket }}</strong>
                      <small>{{ formatSupportStatus(chat.status) }} | {{ chat.agent_user || 'در صف' }}</small>
                      <small>{{ chat.last_message || '-' }}</small>
                    </button>
                  </div>
                </div>
                <div class="support-chat-detail">
                  <div v-if="!supportState.selectedChat" class="state-card">یک چت را انتخاب کنید.</div>
                  <template v-else>
                    <p class="support-ticket-meta">{{ supportState.selectedChat.ticket }} | {{ formatSupportStatus(supportState.selectedChat.status) }}</p>
                    <p class="support-description">{{ supportState.selectedChat.last_message || '-' }}</p>
                    <label class="field">
                      <span>پیام چت</span>
                      <textarea v-model="supportState.chatMessage" rows="3" placeholder="پیام برای تیم پشتیبانی"></textarea>
                    </label>
                    <div class="actions">
                      <button class="ghost-btn gold" :disabled="supportState.chatSending" @click="sendSupportChatMessage">
                        {{ supportState.chatSending ? 'در حال ارسال...' : 'ارسال پیام چت' }}
                      </button>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <div class="support-pref-panel">
              <h3>تنظیمات اعلان پشتیبانی</h3>
              <div class="pref-grid">
                <label class="inline"><input type="checkbox" v-model="supportState.pref.enable_sound" /> صدای اعلان</label>
                <label class="inline"><input type="checkbox" v-model="supportState.pref.notify_ticket_status_changed" /> تغییر وضعیت تیکت</label>
                <label class="inline"><input type="checkbox" v-model="supportState.pref.notify_ticket_agent_reply" /> پاسخ کارشناس</label>
                <label class="inline"><input type="checkbox" v-model="supportState.pref.notify_chat_message" /> پیام چت</label>
              </div>
              <div class="actions">
                <button class="ghost-btn" :disabled="supportState.prefSaving" @click="saveSupportPreferences">ذخیره تنظیمات اعلان</button>
                <button class="ghost-btn" @click="markSupportNotificationsSeen">علامت‌گذاری اعلان‌ها به‌عنوان خوانده‌شده</button>
              </div>
              <div v-if="supportState.prefError" class="state-card error">{{ supportState.prefError }}</div>
            </div>
          </template>
        </section>

        <section v-else-if="activeTab === 'addresses'" class="glass-panel doc-panel">
          <div class="card-head">
            <h3>آدرس‌ها</h3>
            <button class="ghost-btn gold" @click="openAddressModal()">افزودن آدرس</button>
          </div>

          <div v-if="addressesLoading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="addressesError" class="state-card error">{{ addressesError }}</div>
          <div v-else-if="!addresses.length" class="state-card">آدرسی ثبت نشده است.</div>
          <div v-else class="address-grid">
            <article v-for="address in addresses" :key="address.name" class="address-card">
              <div class="top">
                <strong>{{ address.address_title || address.name }}</strong>
                <span>{{ address.address_type }}</span>
              </div>
              <p>{{ address.display || composeAddress(address) }}</p>
              <div class="badges">
                <span v-if="address.customers?.length" class="badge">{{ address.customers.join('، ') }}</span>
                <span v-if="address.is_primary_address" class="badge">اصلی</span>
                <span v-if="address.is_shipping_address" class="badge">ارسال</span>
              </div>
              <div class="actions">
                <button class="mini-btn" @click="openAddressModal(address)">ویرایش</button>
                <button class="mini-btn danger" @click="deleteAddress(address.name)">حذف</button>
              </div>
            </article>
          </div>
        </section>

        <section v-else-if="activeTab === 'statement'" class="glass-panel doc-panel">
          <div class="kpis">
            <article class="glass-panel kpi">
              <p>جمع فاکتور</p>
              <h3>{{ formatCurrency(summary?.total_invoiced || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>مانده بدهی</p>
              <h3>{{ formatCurrency(summary?.total_outstanding || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>فاکتور باز</p>
              <h3>{{ summary?.unpaid_count || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>سررسید گذشته</p>
              <h3>{{ summary?.overdue_count || 0 }}</h3>
            </article>
          </div>

          <div class="table-wrap" v-if="summary?.open_invoices?.length">
            <table>
              <thead>
                <tr>
                  <th>فاکتور</th>
                  <th>تاریخ</th>
                  <th>سررسید</th>
                  <th>وضعیت</th>
                  <th>مانده</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in summary.open_invoices" :key="inv.name">
                  <td>{{ inv.name }}</td>
                  <td>{{ formatDate(inv.posting_date) }}</td>
                  <td>{{ formatDate(inv.due_date) }}</td>
                  <td>{{ inv.status }}</td>
                  <td>{{ formatCurrency(inv.outstanding_amount || 0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="state-card">فاکتور بازی برای نمایش وجود ندارد.</div>
        </section>

        <section v-else-if="activeTab === 'insights'" class="glass-panel doc-panel">
          <div class="controls">
            <label class="field compact">
              <span>از تاریخ</span>
              <input v-model="insightsState.fromDate" type="date" />
            </label>
            <label class="field compact">
              <span>تا تاریخ</span>
              <input v-model="insightsState.toDate" type="date" />
            </label>
            <label class="field compact">
              <span>تعداد</span>
              <input v-model.number="insightsState.limit" type="number" min="1" max="30" />
            </label>
            <div class="field compact">
              <span>بازه فعال</span>
              <input :value="formatRange(insightsState.range)" disabled />
            </div>
            <button class="ghost-btn" @click="applyInsightsFilters">اعمال فیلتر</button>
          </div>

          <div class="kpis">
            <article class="glass-panel kpi">
              <p>تعداد محصولات</p>
              <h3>{{ insightsState.kpis.products_count || 0 }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>تعداد کل خرید</p>
              <h3>{{ Number(insightsState.kpis.total_qty || 0).toLocaleString('fa-IR') }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>مبلغ کل خرید</p>
              <h3>{{ formatCurrency(insightsState.kpis.total_amount || 0) }}</h3>
            </article>
          </div>

          <div v-if="insightsState.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="insightsState.error" class="state-card error">{{ insightsState.error }}</div>
          <div v-else-if="!insightsState.items.length" class="state-card">محصول پرتکراری یافت نشد.</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>کد</th>
                  <th>نام آیتم</th>
                  <th>تعداد خرید</th>
                  <th>مبلغ کل</th>
                  <th>تعداد فاکتور</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in insightsState.items" :key="`${item.item_code}-${item.item_name}`">
                  <td>{{ item.item_code || '-' }}</td>
                  <td>{{ item.item_name || '-' }}</td>
                  <td>{{ Number(item.total_qty || 0).toLocaleString('fa-IR') }}</td>
                  <td>{{ formatCurrency(item.total_amount || 0) }}</td>
                  <td>{{ Number(item.invoice_count || 0).toLocaleString('fa-IR') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-else-if="activeTab === 'funnel'" class="glass-panel doc-panel">
          <div class="controls">
            <label class="field compact">
              <span>بازه (روز)</span>
              <input v-model.number="funnelState.days" type="number" min="1" max="365" />
            </label>
            <button class="ghost-btn" @click="applyFunnelFilters">بروزرسانی قیف</button>
          </div>

          <div class="kpis kpis-compact">
            <article class="glass-panel kpi">
              <p>بازدید محصول (Session)</p>
              <h3>{{ Number(funnelState.data?.sessions?.product_view || 0).toLocaleString('fa-IR') }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>افزودن به سبد (Session)</p>
              <h3>{{ Number(funnelState.data?.sessions?.add_to_cart || 0).toLocaleString('fa-IR') }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>ثبت سفارش (Session)</p>
              <h3>{{ Number(funnelState.data?.sessions?.order_submit || 0).toLocaleString('fa-IR') }}</h3>
            </article>
          </div>

          <div class="kpis kpis-compact">
            <article class="glass-panel kpi">
              <p>نرخ تبدیل بازدید ← سبد</p>
              <h3>{{ Number(funnelState.data?.conversion_rate?.view_to_cart_percent || 0).toLocaleString('fa-IR') }}%</h3>
            </article>
            <article class="glass-panel kpi">
              <p>نرخ تبدیل سبد ← سفارش</p>
              <h3>{{ Number(funnelState.data?.conversion_rate?.cart_to_order_percent || 0).toLocaleString('fa-IR') }}%</h3>
            </article>
            <article class="glass-panel kpi">
              <p>نرخ تبدیل بازدید ← سفارش</p>
              <h3>{{ Number(funnelState.data?.conversion_rate?.view_to_order_percent || 0).toLocaleString('fa-IR') }}%</h3>
            </article>
          </div>

          <div v-if="funnelState.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="funnelState.error" class="state-card error">{{ funnelState.error }}</div>
          <div v-else-if="!funnelState.data" class="state-card">داده‌ای برای نمایش وجود ندارد.</div>
          <div v-else class="overview-grid">
            <div class="glass-panel list-card">
              <div class="card-head">
                <h3>مدل‌های پربازدید</h3>
              </div>
              <div v-if="!(funnelState.data?.top_models?.product_view || []).length" class="state-card">موردی ثبت نشده.</div>
              <div v-else class="rows">
                <div v-for="row in funnelState.data.top_models.product_view" :key="`view-${row.model_name}`" class="row">
                  <div><strong>{{ row.model_name }}</strong></div>
                  <div class="row-meta"><span>{{ Number(row.count || 0).toLocaleString('fa-IR') }}</span></div>
                </div>
              </div>
            </div>
            <div class="glass-panel list-card">
              <div class="card-head">
                <h3>مدل‌های پرفروش قیف</h3>
              </div>
              <div v-if="!(funnelState.data?.top_models?.order_submit || []).length" class="state-card">موردی ثبت نشده.</div>
              <div v-else class="rows">
                <div v-for="row in funnelState.data.top_models.order_submit" :key="`order-${row.model_name}`" class="row">
                  <div><strong>{{ row.model_name }}</strong></div>
                  <div class="row-meta"><span>{{ Number(row.count || 0).toLocaleString('fa-IR') }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="activeTab === 'payments'" class="glass-panel doc-panel">
          <div class="controls">
            <label class="field compact">
              <span>جستجو</span>
              <input v-model="paymentsState.search" placeholder="شماره پرداخت، روش پرداخت..." />
            </label>
            <label class="field compact">
              <span>از تاریخ</span>
              <input v-model="paymentsState.fromDate" type="date" />
            </label>
            <label class="field compact">
              <span>تا تاریخ</span>
              <input v-model="paymentsState.toDate" type="date" />
            </label>
            <div class="field compact">
              <span>بازه فعال</span>
              <input :value="formatRange(paymentsState.range)" disabled />
            </div>
            <button class="ghost-btn" @click="applyFinanceFilters('payments')">اعمال فیلتر</button>
          </div>

          <div class="kpis kpis-compact">
            <article class="glass-panel kpi">
              <p>جمع دریافتی</p>
              <h3>{{ formatCurrency(paymentsState.kpis.total_received || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>تعداد پرداخت</p>
              <h3>{{ paymentsState.kpis.payment_count || 0 }}</h3>
            </article>
          </div>

          <div v-if="paymentsState.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="paymentsState.error" class="state-card error">{{ paymentsState.error }}</div>
          <div v-else-if="!paymentsState.items.length" class="state-card">پرداختی برای نمایش نیست.</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>سند</th>
                  <th>تاریخ</th>
                  <th>مشتری</th>
                  <th>نوع</th>
                  <th>روش</th>
                  <th>دریافتی</th>
                  <th>وضعیت</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in paymentsState.items" :key="row.name">
                  <td>{{ row.name }}</td>
                  <td>{{ formatDate(row.posting_date) }}</td>
                  <td>{{ row.party_name || row.customer || '-' }}</td>
                  <td>{{ row.payment_type || '-' }}</td>
                  <td>{{ row.mode_of_payment || '-' }}</td>
                  <td>{{ formatCurrency((row.received_amount || row.paid_amount || 0)) }}</td>
                  <td>{{ row.status || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <button class="ghost-btn" :disabled="!paymentsState.hasPrev" @click="changeFinancePage('payments', -1)">قبلی</button>
            <span>صفحه {{ paymentsState.page }} از {{ paymentsState.totalPages || 1 }}</span>
            <button class="ghost-btn" :disabled="!paymentsState.hasNext" @click="changeFinancePage('payments', 1)">بعدی</button>
          </div>
        </section>

        <section v-else-if="activeTab === 'ledger'" class="glass-panel doc-panel">
          <div class="controls">
            <label class="field compact">
              <span>جستجو</span>
              <input v-model="ledgerState.search" placeholder="شماره سند، حساب، شرح..." />
            </label>
            <label class="field compact">
              <span>از تاریخ</span>
              <input v-model="ledgerState.fromDate" type="date" />
            </label>
            <label class="field compact">
              <span>تا تاریخ</span>
              <input v-model="ledgerState.toDate" type="date" />
            </label>
            <div class="field compact">
              <span>بازه فعال</span>
              <input :value="formatRange(ledgerState.range)" disabled />
            </div>
            <button class="ghost-btn" @click="applyFinanceFilters('ledger')">اعمال فیلتر</button>
          </div>

          <div class="kpis kpis-compact">
            <article class="glass-panel kpi">
              <p>بدهکار</p>
              <h3>{{ formatCurrency(ledgerState.kpis.total_debit || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>بستانکار</p>
              <h3>{{ formatCurrency(ledgerState.kpis.total_credit || 0) }}</h3>
            </article>
            <article class="glass-panel kpi">
              <p>مانده</p>
              <h3>{{ formatCurrency(ledgerState.kpis.net_balance || 0) }}</h3>
            </article>
          </div>

          <div v-if="ledgerState.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="ledgerState.error" class="state-card error">{{ ledgerState.error }}</div>
          <div v-else-if="!ledgerState.items.length" class="state-card">رکورد دفترکل یافت نشد.</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>تاریخ</th>
                  <th>حساب</th>
                  <th>سند</th>
                  <th>بدهکار</th>
                  <th>بستانکار</th>
                  <th>مانده تجمعی</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in ledgerState.items" :key="row.name">
                  <td>{{ formatDate(row.posting_date) }}</td>
                  <td>{{ row.account || '-' }}</td>
                  <td>{{ row.voucher_no || row.name }}</td>
                  <td>{{ formatCurrency(row.debit || 0) }}</td>
                  <td>{{ formatCurrency(row.credit || 0) }}</td>
                  <td>{{ formatCurrency(row.running_balance || 0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <button class="ghost-btn" :disabled="!ledgerState.hasPrev" @click="changeFinancePage('ledger', -1)">قبلی</button>
            <span>صفحه {{ ledgerState.page }} از {{ ledgerState.totalPages || 1 }}</span>
            <button class="ghost-btn" :disabled="!ledgerState.hasNext" @click="changeFinancePage('ledger', 1)">بعدی</button>
          </div>
        </section>
      </template>
    </div>

    <transition name="fade">
      <div v-if="detailModal.open" class="modal-wrap" @click.self="closeDetail">
        <div class="glass-panel modal-card">
          <div class="card-head">
            <h3>جزئیات {{ sectionLabels[detailModal.section] || detailModal.section }}</h3>
            <button class="ghost-btn" @click="closeDetail">بستن</button>
          </div>
          <div v-if="detailModal.loading" class="state-card">در حال بارگذاری...</div>
          <div v-else-if="detailModal.error" class="state-card error">{{ detailModal.error }}</div>
          <template v-else-if="detailModal.data">
            <div class="doc-meta">
              <div><span>شماره:</span> <strong>{{ detailModal.data.document.name }}</strong></div>
              <div><span>وضعیت:</span> <strong>{{ detailModal.data.document.status || '-' }}</strong></div>
              <div><span>مبلغ:</span> <strong>{{ formatCurrency(detailModal.data.document.grand_total || 0) }}</strong></div>
            </div>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>کد</th>
                    <th>نام آیتم</th>
                    <th>تعداد</th>
                    <th>نرخ</th>
                    <th>مبلغ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in detailModal.data.items || []" :key="`${item.idx}-${item.item_code}`">
                    <td>{{ item.item_code || '-' }}</td>
                    <td>{{ item.item_name || '-' }}</td>
                    <td>{{ item.qty || 0 }}</td>
                    <td>{{ formatCurrency(item.rate || item.price || 0) }}</td>
                    <td>{{ formatCurrency(item.amount || 0) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="addressModal.open" class="modal-wrap" @click.self="closeAddressModal">
        <div class="glass-panel modal-card address-modal">
          <div class="card-head">
            <h3>{{ addressModal.form.name ? 'ویرایش آدرس' : 'افزودن آدرس' }}</h3>
            <button class="ghost-btn" @click="closeAddressModal">بستن</button>
          </div>
          <div class="address-form">
            <label class="field" v-if="(session?.customers || []).length > 1">
              <span>مشتری</span>
              <select v-model="addressModal.form.customer">
                <option value="" disabled>انتخاب مشتری</option>
                <option v-for="c in session?.customers || []" :key="`address-${c.name}`" :value="c.name">
                  {{ c.customer_name || c.name }}
                </option>
              </select>
            </label>
            <label class="field"><span>عنوان آدرس</span><input v-model="addressModal.form.address_title" /></label>
            <label class="field"><span>نوع آدرس</span><input v-model="addressModal.form.address_type" placeholder="Shipping / Billing" /></label>
            <label class="field"><span>آدرس خط ۱</span><input v-model="addressModal.form.address_line1" /></label>
            <label class="field"><span>آدرس خط ۲</span><input v-model="addressModal.form.address_line2" /></label>
            <label class="field"><span>شهر</span><input v-model="addressModal.form.city" /></label>
            <label class="field"><span>استان</span><input v-model="addressModal.form.state" /></label>
            <label class="field"><span>کشور</span><input v-model="addressModal.form.country" /></label>
            <label class="field"><span>کدپستی</span><input v-model="addressModal.form.pincode" /></label>
            <label class="field"><span>تلفن</span><input v-model="addressModal.form.phone" /></label>
            <label class="field"><span>ایمیل</span><input v-model="addressModal.form.email_id" /></label>
            <label class="check"><input type="checkbox" v-model="addressModal.form.is_primary_address" /> آدرس اصلی</label>
            <label class="check"><input type="checkbox" v-model="addressModal.form.is_shipping_address" /> آدرس ارسال</label>
          </div>
          <div v-if="addressModal.error" class="state-card error">{{ addressModal.error }}</div>
          <div class="actions end">
            <button class="ghost-btn gold" :disabled="addressModal.saving" @click="saveAddress">
              {{ addressModal.saving ? 'در حال ذخیره...' : 'ذخیره آدرس' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="requestEditor.open" class="modal-wrap" @click.self="closeRequestEditor">
        <div class="glass-panel modal-card request-editor-modal">
          <div class="card-head">
            <h3>مدیریت کامل درخواست پیش‌فاکتور</h3>
            <button class="ghost-btn" @click="closeRequestEditor">بستن</button>
          </div>

          <div v-if="requestEditor.loading" class="state-card">در حال بارگذاری درخواست...</div>
          <div v-else class="request-editor-content">
            <div class="doc-meta request-meta-grid">
              <div><span>شماره:</span> <strong>{{ requestEditor.form.name || '-' }}</strong></div>
              <div><span>وضعیت:</span> <strong>{{ requestEditor.form.status || '-' }}</strong></div>
              <div>
                <span>پیش‌فاکتور:</span>
                <strong>{{ requestEditor.form.quotation || 'ایجاد نشده' }}</strong>
              </div>
            </div>

            <div class="address-form request-head-form">
              <label class="field">
                <span>نام مشتری</span>
                <input v-model="requestEditor.form.customer_name" />
              </label>
              <label class="field">
                <span>تلفن</span>
                <input v-model="requestEditor.form.phone" />
              </label>
              <label class="field">
                <span>ایمیل</span>
                <input v-model="requestEditor.form.email" />
              </label>
              <label class="field">
                <span>وضعیت</span>
                <select v-model="requestEditor.form.status">
                  <option value="Submitted">Submitted</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Quoted">Quoted</option>
                  <option value="Closed">Closed</option>
                </select>
              </label>
            </div>

            <label class="field">
              <span>توضیحات درخواست</span>
              <textarea v-model="requestEditor.form.request_note" rows="4" placeholder="نیازها، توضیحات یا نکات کاربر..."></textarea>
            </label>

            <div class="card-head request-items-head">
              <h3>آیتم‌های درخواست</h3>
              <button class="ghost-btn" @click="addRequestItem">افزودن آیتم</button>
            </div>

            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>کد کالا</th>
                    <th>نام کالا</th>
                    <th>تعداد</th>
                    <th>قیمت</th>
                    <th>توضیحات</th>
                    <th>حذف</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in requestEditor.form.items" :key="`rq-item-${index}`">
                    <td><input v-model="item.item_code" class="table-input" /></td>
                    <td><input v-model="item.item_name" class="table-input" /></td>
                    <td><input v-model.number="item.qty" type="number" min="1" class="table-input" /></td>
                    <td><input v-model.number="item.price" type="number" min="0" class="table-input" /></td>
                    <td><textarea v-model="item.configuration" rows="2" class="table-input"></textarea></td>
                    <td>
                      <button class="mini-btn danger" @click="removeRequestItem(index)" :disabled="requestEditor.form.items.length <= 1">حذف</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="requestEditor.error" class="state-card error">{{ requestEditor.error }}</div>
            <div v-if="requestEditor.success" class="state-card">{{ requestEditor.success }}</div>

            <div class="actions end">
              <button class="ghost-btn" :disabled="requestEditor.makingQuotation" @click="makeQuotationFromRequest">
                {{ requestEditor.makingQuotation ? 'در حال ساخت پیش‌فاکتور...' : 'ساخت پیش‌فاکتور از این درخواست' }}
              </button>
              <button class="ghost-btn gold" :disabled="requestEditor.saving" @click="saveRequestEditor">
                {{ requestEditor.saving ? 'در حال ذخیره...' : 'ذخیره تغییرات درخواست' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { usePortalStore } from '../stores/portalStore'

const tabs = [
  { id: 'overview', label: 'نمای کلی' },
  { id: 'quotation_requests', label: 'درخواست پیش‌فاکتور' },
  { id: 'quotations', label: 'پیش‌فاکتور' },
  { id: 'sales_orders', label: 'سفارش‌ها' },
  { id: 'sales_invoices', label: 'فاکتورها' },
  { id: 'deliveries', label: 'تحویل‌ها' },
  { id: 'support_tickets', label: 'تیکت‌ها' },
  { id: 'addresses', label: 'آدرس‌ها' },
  { id: 'statement', label: 'صورت‌حساب' },
  { id: 'insights', label: 'محصولات پرتکرار' },
  { id: 'funnel', label: 'قیف تبدیل سایت' },
  { id: 'payments', label: 'پرداختی‌ها' },
  { id: 'ledger', label: 'دفترکل' }
]

const sectionLabels = {
  quotation_requests: 'درخواست پیش‌فاکتور',
  quotations: 'پیش‌فاکتور',
  sales_orders: 'سفارش',
  sales_invoices: 'فاکتور',
  deliveries: 'تحویل',
  addresses: 'آدرس'
}

const documentTabs = ['quotation_requests', 'quotations', 'sales_orders', 'sales_invoices', 'deliveries']

function createDocState() {
  return {
    items: [],
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 1,
    hasNext: false,
    hasPrev: false,
    loading: false,
    error: '',
    status: '',
    search: '',
    fromDate: '',
    toDate: ''
  }
}

function createFinanceState() {
  return {
    items: [],
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 1,
    hasNext: false,
    hasPrev: false,
    loading: false,
    error: '',
    search: '',
    fromDate: '',
    toDate: '',
    kpis: {}
  }
}

const { selectedCustomer: persistedCustomer, setSelectedCustomer, clearSelectedCustomer } = usePortalStore()

const session = ref(null)
const sessionLoading = ref(true)
const sessionError = ref('')
const selectedCustomer = ref(persistedCustomer.value || '')
const activeTab = ref('overview')

const summary = ref(null)
const summaryLoading = ref(false)

const docStates = reactive({
  quotation_requests: createDocState(),
  quotations: createDocState(),
  sales_orders: createDocState(),
  sales_invoices: createDocState(),
  deliveries: createDocState()
})

const supportState = reactive({
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  totalPages: 1,
  hasNext: false,
  hasPrev: false,
  loading: false,
  error: '',
  status: '',
  selectedName: '',
  detail: null,
  detailLoading: false,
  detailError: '',
  createSubject: '',
  createDescription: '',
  createItemCode: '',
  createLoading: false,
  createError: '',
  createSuccess: '',
  replyMessage: '',
  replyLoading: false,
  replyError: '',
  replySuccess: '',
  runtimeError: '',
  chats: [],
  selectedChat: null,
  chatListLoading: false,
  chatListError: '',
  chatMessage: '',
  chatSending: false,
  chatOpening: false,
  pref: {
    enable_in_app: true,
    enable_sound: true,
    notify_ticket_status_changed: true,
    notify_ticket_agent_reply: true,
    notify_chat_message: true,
  },
  prefSaving: false,
  prefError: ''
})

const addresses = ref([])
const addressesLoading = ref(false)
const addressesError = ref('')

const insightsState = reactive({
  items: [],
  kpis: {
    products_count: 0,
    total_qty: 0,
    total_amount: 0
  },
  range: {
    from_date: '',
    to_date: ''
  },
  fromDate: '',
  toDate: '',
  limit: 10,
  loading: false,
  error: ''
})

const funnelState = reactive({
  days: 30,
  loading: false,
  error: '',
  data: null
})

const financeStates = reactive({
  payments: createFinanceState(),
  ledger: createFinanceState()
})

const detailModal = reactive({
  open: false,
  loading: false,
  error: '',
  section: '',
  data: null
})

const addressModal = reactive({
  open: false,
  saving: false,
  error: '',
  form: {
    name: '',
    customer: '',
    address_title: '',
    address_type: 'Shipping',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    country: 'Iran',
    pincode: '',
    phone: '',
    email_id: '',
    is_primary_address: false,
    is_shipping_address: true
  }
})

const requestEditor = reactive({
  open: false,
  loading: false,
  saving: false,
  makingQuotation: false,
  error: '',
  success: '',
  form: {
    name: '',
    customer: '',
    customer_name: '',
    phone: '',
    email: '',
    status: 'Submitted',
    request_note: '',
    quotation: '',
    items: []
  }
})

const activeDocState = computed(() => docStates[activeTab.value] || createDocState())
const paymentsState = computed(() => financeStates.payments)
const ledgerState = computed(() => financeStates.ledger)

function isDocumentTab(tab) {
  return documentTabs.includes(tab)
}

function formatCurrency(value) {
  return `${Math.round(Number(value || 0)).toLocaleString('fa-IR')} تومان`
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('fa-IR')
}

const supportStatusMap = {
  open: 'باز',
  closed: 'بسته',
  resolved: 'حل‌شده',
  paused: 'متوقف',
  'in progress': 'در حال پیگیری',
  'on hold': 'در انتظار',
  'first response due': 'مهلت پاسخ اولیه',
  'resolution due': 'مهلت حل',
  failed: 'ناموفق',
  fulfilled: 'موفق',
}
const supportStatusReverseMap = {
  باز: 'Open',
  بسته: 'Closed',
  'حل‌شده': 'Resolved',
  متوقف: 'Paused',
  'در حال پیگیری': 'In Progress',
  'در انتظار': 'On Hold',
  'مهلت پاسخ اولیه': 'First Response Due',
  'مهلت حل': 'Resolution Due',
  ناموفق: 'Failed',
  موفق: 'Fulfilled',
}

function formatSupportStatus(value) {
  const text = String(value || '').trim()
  if (!text) return '-'
  return supportStatusMap[text.toLowerCase()] || text
}

function normalizeSupportStatusFilter(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  return supportStatusReverseMap[text] || text
}

function formatRange(range) {
  if (!range?.from_date || !range?.to_date) return '-'
  return `${range.from_date} تا ${range.to_date}`
}

function composeAddress(address) {
  return [
    address.address_line1,
    address.address_line2,
    address.city,
    address.state,
    address.country
  ].filter(Boolean).join('، ')
}

function redirectToLogin() {
  window.location.href = `/mysite/login?next=${encodeURIComponent('/mysite/dashboard')}`
}

async function apiCall(method, params = {}, options = {}) {
  const requestMethod = options.method || 'GET'
  const headers = {}
  let body

  if (requestMethod !== 'GET') {
    headers['Content-Type'] = 'application/json'
    headers['X-Frappe-CSRF-Token'] = window.csrf_token || ''
    body = JSON.stringify(options.body || {})
  }

  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, value)
    }
  })

  const endpoint = `/api/method/mysite.portal_api.${method}${query.toString() ? `?${query.toString()}` : ''}`
  const response = await fetch(endpoint, {
    method: requestMethod,
    headers,
    body,
    credentials: 'same-origin'
  })

  const text = await response.text()
  let payload = {}
  try {
    payload = JSON.parse(text)
  } catch (error) {
    payload = {}
  }

  if (!response.ok || payload.exception || payload.exc_type) {
    throw new Error('خطا در دریافت اطلاعات از سرور.')
  }

  return payload.message || payload
}

async function loadSession() {
  sessionLoading.value = true
  sessionError.value = ''
  try {
    const data = await apiCall('portal_session', {
      customer: selectedCustomer.value || undefined
    })
    if (!data.authenticated) {
      redirectToLogin()
      return
    }

    session.value = data

    if (!data.can_switch_customer) {
      selectedCustomer.value = data.selected_customer || data.default_customer || ''
    } else if (selectedCustomer.value && !(data.customers || []).some((c) => c.name === selectedCustomer.value)) {
      selectedCustomer.value = data.selected_customer || ''
    }

    if (selectedCustomer.value) {
      setSelectedCustomer(selectedCustomer.value)
    } else {
      clearSelectedCustomer()
    }
  } catch (error) {
    sessionError.value = 'خطا در بارگذاری نشست کاربر.'
  } finally {
    sessionLoading.value = false
  }
}

async function loadSummary() {
  summaryLoading.value = true
  try {
    summary.value = await apiCall('portal_dashboard_summary', {
      customer: selectedCustomer.value || undefined
    })
  } catch (error) {
    summary.value = null
  } finally {
    summaryLoading.value = false
  }
}

async function loadDocumentSection(section) {
  const state = docStates[section]
  if (!state) return

  state.loading = true
  state.error = ''
  try {
    const result = await apiCall('portal_documents', {
      section,
      customer: selectedCustomer.value || undefined,
      page: state.page,
      page_size: state.pageSize,
      status: state.status,
      search: state.search,
      from_date: state.fromDate,
      to_date: state.toDate
    })
    state.items = result.items || []
    state.total = result.total || 0
    state.totalPages = result.total_pages || 1
    state.hasNext = !!result.has_next
    state.hasPrev = !!result.has_prev
  } catch (error) {
    state.error = 'خطا در بارگذاری لیست.'
  } finally {
    state.loading = false
  }
}

async function loadSupportTickets() {
  supportState.runtimeError = ''
  try {
    const health = await fetch('/api/method/mysite.api.get_support_runtime_health', { credentials: 'same-origin' })
    const healthPayload = await health.json()
    const healthData = healthPayload?.message || healthPayload || {}
    if (health.ok && healthData && healthData.ready === false) {
      supportState.runtimeError = healthData.message || 'زیرساخت پشتیبانی آماده نیست.'
      supportState.items = []
      supportState.detail = null
      return
    }
  } catch (error) {
    // ignore health-check failures and continue with main API call
  }

  supportState.loading = true
  supportState.error = ''
  supportState.createSuccess = ''
  try {
    const result = await apiCall('portal_list_support_tickets', {
      customer: selectedCustomer.value || undefined,
      page: supportState.page,
      page_size: supportState.pageSize,
      status: normalizeSupportStatusFilter(supportState.status) || undefined
    })
    supportState.items = result.items || []
    supportState.total = result.total || 0
    supportState.totalPages = result.total_pages || 1
    supportState.hasNext = !!result.has_next
    supportState.hasPrev = !!result.has_prev

    const stillVisible = supportState.items.some((row) => row.name === supportState.selectedName)
    if (!supportState.selectedName && supportState.items.length) {
      await selectSupportTicket(supportState.items[0].name)
    } else if (supportState.selectedName && !stillVisible) {
      supportState.selectedName = ''
      supportState.detail = null
    }
  } catch (error) {
    supportState.error = 'خطا در دریافت تیکت‌ها.'
  } finally {
    supportState.loading = false
  }
}

async function loadSupportChats() {
  supportState.chatListLoading = true
  supportState.chatListError = ''
  try {
    const result = await apiCall('portal_list_support_chats', {
      page: 1,
      page_size: 100
    })
    supportState.chats = Array.isArray(result.items) ? result.items : []
    if (!supportState.selectedChat && supportState.chats.length) {
      supportState.selectedChat = supportState.chats[0]
    }
  } catch (error) {
    supportState.chatListError = 'خطا در دریافت چت‌ها.'
  } finally {
    supportState.chatListLoading = false
  }
}

async function openSupportChat() {
  supportState.chatOpening = true
  supportState.chatListError = ''
  try {
    const result = await apiCall('portal_open_support_chat', {}, {
      method: 'POST',
      body: {
        customer: selectedCustomer.value || undefined,
        ticket_name: supportState.selectedName || undefined,
        subject: supportState.createSubject || 'درخواست گفتگوی پشتیبانی',
        initial_message: supportState.chatMessage || supportState.createDescription || undefined,
        source_page: '/mysite/dashboard'
      }
    })
    if (result.ticket && !supportState.selectedName) {
      supportState.selectedName = result.ticket
    }
    if (result.online === false && result.message) {
      supportState.chatListError = result.message
    }
    await Promise.all([loadSupportChats(), loadSupportTickets()])
    if (supportState.selectedName) {
      await selectSupportTicket(supportState.selectedName)
    }
  } catch (error) {
    supportState.chatListError = 'شروع چت انجام نشد.'
  } finally {
    supportState.chatOpening = false
  }
}

async function sendSupportChatMessage() {
  const text = String(supportState.chatMessage || '').trim()
  if (!text) return
  supportState.chatSending = true
  supportState.chatListError = ''
  try {
    await apiCall('portal_send_support_chat_message', {}, {
      method: 'POST',
      body: {
        channel_id: supportState.selectedChat?.raven_channel || undefined,
        ticket_name: supportState.selectedChat?.ticket || supportState.selectedName || undefined,
        message: text
      }
    })
    supportState.chatMessage = ''
    await Promise.all([loadSupportChats(), loadSupportTickets()])
    if (supportState.selectedName) {
      await selectSupportTicket(supportState.selectedName)
    }
  } catch (error) {
    supportState.chatListError = 'ارسال پیام چت انجام نشد.'
  } finally {
    supportState.chatSending = false
  }
}

async function loadSupportPreferences() {
  supportState.prefError = ''
  try {
    const pref = await fetch('/api/method/mysite.api.get_support_notification_preferences', { credentials: 'same-origin' })
    const payload = await pref.json()
    const data = payload?.message || payload || {}
    supportState.pref.enable_in_app = !!Number(data.enable_in_app ?? 1)
    supportState.pref.enable_sound = !!Number(data.enable_sound ?? 1)
    supportState.pref.notify_ticket_status_changed = !!Number(data.notify_ticket_status_changed ?? 1)
    supportState.pref.notify_ticket_agent_reply = !!Number(data.notify_ticket_agent_reply ?? 1)
    supportState.pref.notify_chat_message = !!Number(data.notify_chat_message ?? 1)
  } catch (error) {
    supportState.prefError = 'خطا در دریافت تنظیمات اعلان.'
  }
}

async function saveSupportPreferences() {
  supportState.prefSaving = true
  supportState.prefError = ''
  try {
    await fetch('/api/method/mysite.api.set_support_notification_preferences', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || ''
      },
      body: JSON.stringify(supportState.pref)
    })
  } catch (error) {
    supportState.prefError = 'ذخیره تنظیمات اعلان انجام نشد.'
  } finally {
    supportState.prefSaving = false
  }
}

async function markSupportNotificationsSeen() {
  try {
    await fetch('/api/method/mysite.api.mark_support_notifications_seen', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
    })
  } catch (error) {
    supportState.prefError = 'علامت‌گذاری اعلان‌ها انجام نشد.'
  }
}

async function selectSupportTicket(name) {
  if (!name) return
  supportState.selectedName = name
  supportState.detailLoading = true
  supportState.detailError = ''
  supportState.replyError = ''
  supportState.replySuccess = ''
  try {
    const detail = await apiCall('portal_get_support_ticket', {
      name
    })
    supportState.detail = detail || null
  } catch (error) {
    supportState.detail = null
    supportState.detailError = 'خطا در دریافت جزئیات تیکت.'
  } finally {
    supportState.detailLoading = false
  }
}

async function createSupportTicket() {
  supportState.createError = ''
  supportState.createSuccess = ''
  supportState.createLoading = true
  try {
    await apiCall('portal_create_support_ticket', {}, {
      method: 'POST',
      body: {
        customer: selectedCustomer.value || undefined,
        payload: {
          subject: supportState.createSubject,
          description: supportState.createDescription,
          item_code: supportState.createItemCode || undefined,
          source_page: '/mysite/dashboard'
        }
      }
    })
    supportState.createSubject = ''
    supportState.createDescription = ''
    supportState.createItemCode = ''
    supportState.createSuccess = 'تیکت با موفقیت ثبت شد.'
    supportState.page = 1
    await loadSupportTickets()
  } catch (error) {
    supportState.createError = 'ثبت تیکت انجام نشد.'
  } finally {
    supportState.createLoading = false
  }
}

async function sendSupportReply() {
  if (!supportState.selectedName) return
  supportState.replyLoading = true
  supportState.replyError = ''
  supportState.replySuccess = ''
  try {
    await apiCall('portal_reply_support_ticket', {}, {
      method: 'POST',
      body: {
        name: supportState.selectedName,
        message: supportState.replyMessage
      }
    })
    supportState.replyMessage = ''
    supportState.replySuccess = 'پاسخ شما ثبت شد.'
    await selectSupportTicket(supportState.selectedName)
    await loadSupportTickets()
  } catch (error) {
    supportState.replyError = 'ثبت پاسخ انجام نشد.'
  } finally {
    supportState.replyLoading = false
  }
}

function applySupportFilters() {
  supportState.page = 1
  loadSupportTickets()
}

function changeSupportPage(delta) {
  const nextPage = supportState.page + delta
  if (nextPage < 1 || nextPage > supportState.totalPages) return
  supportState.page = nextPage
  loadSupportTickets()
}

async function loadAddresses() {
  addressesLoading.value = true
  addressesError.value = ''
  try {
    const result = await apiCall('portal_addresses', {
      customer: selectedCustomer.value || undefined
    })
    addresses.value = result.items || []
  } catch (error) {
    addressesError.value = 'خطا در بارگذاری آدرس‌ها.'
  } finally {
    addressesLoading.value = false
  }
}

async function loadInsights() {
  insightsState.loading = true
  insightsState.error = ''
  try {
    const result = await apiCall('portal_customer_insights', {
      customer: selectedCustomer.value || undefined,
      from_date: insightsState.fromDate,
      to_date: insightsState.toDate,
      limit: insightsState.limit || 10
    })
    insightsState.items = result.top_products || []
    insightsState.kpis = result.kpis || { products_count: 0, total_qty: 0, total_amount: 0 }
    insightsState.range = result.range || { from_date: '', to_date: '' }

    if (!insightsState.fromDate && insightsState.range.from_date) {
      insightsState.fromDate = insightsState.range.from_date
    }
    if (!insightsState.toDate && insightsState.range.to_date) {
      insightsState.toDate = insightsState.range.to_date
    }
  } catch (error) {
    insightsState.error = 'خطا در دریافت آمار محصولات.'
  } finally {
    insightsState.loading = false
  }
}

async function loadFunnelAnalytics() {
  funnelState.loading = true
  funnelState.error = ''
  try {
    const response = await fetch(
      `/api/method/mysite.www.mysite.product.get_funnel_analytics?days=${encodeURIComponent(funnelState.days || 30)}`,
      { credentials: 'same-origin' }
    )
    const payload = await response.json()
    if (!response.ok || payload.exception || payload.exc_type) {
      throw new Error('funnel_analytics_failed')
    }
    funnelState.data = payload.message || payload
  } catch (error) {
    funnelState.data = null
    funnelState.error = 'خطا در دریافت آمار قیف تبدیل.'
  } finally {
    funnelState.loading = false
  }
}

async function loadFinancialSection(section) {
  const state = financeStates[section]
  if (!state) return

  state.loading = true
  state.error = ''
  try {
    const result = await apiCall('portal_financial_entries', {
      entry_type: section,
      customer: selectedCustomer.value || undefined,
      from_date: state.fromDate,
      to_date: state.toDate,
      search: state.search,
      page: state.page,
      page_size: state.pageSize
    })

    state.items = result.items || []
    state.kpis = result.kpis || {}
    state.total = result.total || 0
    state.totalPages = result.total_pages || 1
    state.hasNext = !!result.has_next
    state.hasPrev = !!result.has_prev
    state.range = result.range || { from_date: '', to_date: '' }

    if (!state.fromDate && state.range.from_date) {
      state.fromDate = state.range.from_date
    }
    if (!state.toDate && state.range.to_date) {
      state.toDate = state.range.to_date
    }
  } catch (error) {
    state.error = 'خطا در دریافت اطلاعات مالی.'
  } finally {
    state.loading = false
  }
}

function applyDocFilters(section) {
  const state = docStates[section]
  if (!state) return
  state.page = 1
  loadDocumentSection(section)
}

function applyInsightsFilters() {
  insightsState.limit = Math.min(Math.max(Number(insightsState.limit || 10), 1), 30)
  loadInsights()
}

function applyFunnelFilters() {
  funnelState.days = Math.min(Math.max(Number(funnelState.days || 30), 1), 365)
  loadFunnelAnalytics()
}

function applyFinanceFilters(section) {
  const state = financeStates[section]
  if (!state) return
  state.page = 1
  loadFinancialSection(section)
}

function changePage(section, delta) {
  const state = docStates[section]
  if (!state) return
  const nextPage = state.page + delta
  if (nextPage < 1 || nextPage > state.totalPages) return
  state.page = nextPage
  loadDocumentSection(section)
}

function changeFinancePage(section, delta) {
  const state = financeStates[section]
  if (!state) return
  const nextPage = state.page + delta
  if (nextPage < 1 || nextPage > state.totalPages) return
  state.page = nextPage
  loadFinancialSection(section)
}

async function openDetail(section, name) {
  detailModal.open = true
  detailModal.loading = true
  detailModal.error = ''
  detailModal.section = section
  detailModal.data = null
  try {
    detailModal.data = await apiCall('portal_document_detail', {
      section,
      name,
      customer: selectedCustomer.value || undefined
    })
  } catch (error) {
    detailModal.error = 'خطا در دریافت جزئیات سند.'
  } finally {
    detailModal.loading = false
  }
}

function closeDetail() {
  detailModal.open = false
}

async function openPdf(section, name) {
  try {
    const result = await apiCall('portal_document_pdf_url', {
      section,
      name,
      customer: selectedCustomer.value || undefined
    })
    if (result?.url) {
      window.open(result.url, '_blank', 'noopener,noreferrer')
    }
  } catch (error) {
    // Keep UX silent.
  }
}

function openAddressModal(address = null) {
  addressModal.error = ''
  if (!address && !selectedCustomer.value && (session.value?.customers || []).length > 1) {
    addressesError.value = 'برای افزودن آدرس جدید، ابتدا یک مشتری را انتخاب کنید.'
    return
  }

  addressModal.open = true
  addressModal.form = {
    name: address?.name || '',
    customer: (address?.customers && address.customers[0]) || selectedCustomer.value || '',
    address_title: address?.address_title || '',
    address_type: address?.address_type || 'Shipping',
    address_line1: address?.address_line1 || '',
    address_line2: address?.address_line2 || '',
    city: address?.city || '',
    state: address?.state || '',
    country: address?.country || 'Iran',
    pincode: address?.pincode || '',
    phone: address?.phone || '',
    email_id: address?.email_id || '',
    is_primary_address: !!address?.is_primary_address,
    is_shipping_address: !!address?.is_shipping_address
  }
}

function closeAddressModal() {
  addressModal.open = false
}

async function saveAddress() {
  const targetCustomer = addressModal.form.customer || selectedCustomer.value
  if (!targetCustomer) {
    addressModal.error = 'برای ذخیره آدرس، مشتری را انتخاب کنید.'
    return
  }

  addressModal.saving = true
  addressModal.error = ''
  try {
    await apiCall('portal_save_address', {}, {
      method: 'POST',
      body: {
        customer: targetCustomer,
        payload: addressModal.form
      }
    })
    closeAddressModal()
    await loadAddresses()
  } catch (error) {
    addressModal.error = 'ذخیره آدرس انجام نشد.'
  } finally {
    addressModal.saving = false
  }
}

async function deleteAddress(name) {
  if (!confirm('آدرس حذف شود؟')) return
  try {
    await apiCall('portal_delete_address', {}, {
      method: 'POST',
      body: { address_name: name }
    })
    await loadAddresses()
  } catch (error) {
    // Keep UX silent.
  }
}

function newRequestItem() {
  return {
    item_code: '',
    item_name: '',
    qty: 1,
    price: 0,
    configuration: ''
  }
}

async function openRequestEditor(name) {
  requestEditor.open = true
  requestEditor.loading = true
  requestEditor.error = ''
  requestEditor.success = ''

  try {
    const result = await apiCall('portal_quotation_request_editor', {
      name,
      customer: selectedCustomer.value || undefined
    })
    requestEditor.form = {
      name: result.name,
      customer: result.customer || '',
      customer_name: result.customer_name || '',
      phone: result.phone || '',
      email: result.email || '',
      status: result.status || 'Submitted',
      request_note: result.request_note || '',
      quotation: result.quotation || '',
      items: (result.items || []).length ? result.items.map((item) => ({ ...item })) : [newRequestItem()]
    }
  } catch (error) {
    requestEditor.error = 'دریافت اطلاعات درخواست انجام نشد.'
  } finally {
    requestEditor.loading = false
  }
}

function closeRequestEditor() {
  requestEditor.open = false
  requestEditor.error = ''
  requestEditor.success = ''
}

function addRequestItem() {
  requestEditor.form.items.push(newRequestItem())
}

function removeRequestItem(index) {
  if (requestEditor.form.items.length <= 1) return
  requestEditor.form.items.splice(index, 1)
}

async function saveRequestEditor() {
  requestEditor.error = ''
  requestEditor.success = ''
  requestEditor.saving = true
  try {
    await apiCall('portal_save_quotation_request', {}, {
      method: 'POST',
      body: {
        name: requestEditor.form.name,
        customer: selectedCustomer.value || requestEditor.form.customer || undefined,
        payload: {
          customer: requestEditor.form.customer || undefined,
          customer_name: requestEditor.form.customer_name,
          phone: requestEditor.form.phone,
          email: requestEditor.form.email,
          status: requestEditor.form.status,
          request_note: requestEditor.form.request_note,
          items: requestEditor.form.items
        }
      }
    })
    requestEditor.success = 'درخواست با موفقیت ذخیره شد.'
    await loadDocumentSection('quotation_requests')
    await loadSummary()
  } catch (error) {
    requestEditor.error = 'ذخیره تغییرات انجام نشد.'
  } finally {
    requestEditor.saving = false
  }
}

async function makeQuotationFromRequest() {
  requestEditor.error = ''
  requestEditor.success = ''
  requestEditor.makingQuotation = true
  try {
    const result = await apiCall('portal_make_quotation_from_request', {
      name: requestEditor.form.name,
      customer: selectedCustomer.value || requestEditor.form.customer || undefined
    })
    requestEditor.form.quotation = result.quotation
    requestEditor.form.status = 'Quoted'
    requestEditor.success = `پیش‌فاکتور ${result.quotation} با موفقیت ساخته شد.`
    await loadDocumentSection('quotation_requests')
    await loadSummary()
  } catch (error) {
    requestEditor.error = 'ساخت پیش‌فاکتور انجام نشد.'
  } finally {
    requestEditor.makingQuotation = false
  }
}

async function logout() {
  try {
    await fetch('/api/method/logout', {
      method: 'POST',
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token || ''
      },
      credentials: 'same-origin'
    })
  } catch (error) {
    // ignore
  }
  clearSelectedCustomer()
  window.location.href = '/mysite/login'
}

watch(selectedCustomer, async (value, oldValue) => {
  if (value === oldValue) return

  if (value) {
    setSelectedCustomer(value)
  } else {
    clearSelectedCustomer()
  }

  await loadSummary()

  if (isDocumentTab(activeTab.value)) {
    docStates[activeTab.value].page = 1
    await loadDocumentSection(activeTab.value)
  } else if (activeTab.value === 'support_tickets') {
    supportState.page = 1
    supportState.selectedName = ''
    supportState.selectedChat = null
    supportState.detail = null
    await Promise.all([loadSupportTickets(), loadSupportChats(), loadSupportPreferences()])
  } else if (activeTab.value === 'addresses') {
    await loadAddresses()
  } else if (activeTab.value === 'insights') {
    await loadInsights()
  } else if (activeTab.value === 'funnel') {
    await loadFunnelAnalytics()
  } else if (activeTab.value === 'payments' || activeTab.value === 'ledger') {
    financeStates[activeTab.value].page = 1
    await loadFinancialSection(activeTab.value)
  }
})

watch(activeTab, async (tab) => {
  if (isDocumentTab(tab)) {
    await loadDocumentSection(tab)
  } else if (tab === 'support_tickets') {
    await Promise.all([loadSupportTickets(), loadSupportChats(), loadSupportPreferences()])
  } else if (tab === 'addresses') {
    await loadAddresses()
  } else if (tab === 'insights') {
    await loadInsights()
  } else if (tab === 'funnel') {
    await loadFunnelAnalytics()
  } else if (tab === 'payments' || tab === 'ledger') {
    await loadFinancialSection(tab)
  } else if (tab === 'statement' || tab === 'overview') {
    await loadSummary()
  }
})

onMounted(async () => {
  await loadSession()
  if (session.value?.authenticated) {
    await loadSummary()
    const params = new URLSearchParams(window.location.search)
    if (params.get('tab') === 'support_tickets') {
      activeTab.value = 'support_tickets'
    }
    if (params.get('open_chat') === '1') {
      activeTab.value = 'support_tickets'
      await openSupportChat()
    }
  }
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg-main);
  color: var(--text-main);
  position: relative;
  overflow-x: hidden;
}

.liquid-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.blob { position: absolute; border-radius: 50%; filter: blur(90px); opacity: var(--blob-opacity); }
.b1 { width: 560px; height: 560px; background: var(--blob-1); top: -120px; right: -180px; }
.b2 { width: 640px; height: 640px; background: var(--blob-2); bottom: -120px; left: -180px; }
.b3 { width: 420px; height: 420px; background: var(--blob-3); top: 35%; left: 34%; }

.dash-shell {
  position: relative;
  z-index: 2;
  max-width: 1300px;
  margin: 0 auto;
  padding: 34px 18px 110px;
}

.glass-panel {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 22px;
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
}

.dash-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--accent-gold);
  font-weight: 800;
  letter-spacing: 0.08em;
  font-size: 11px;
}

.dash-header h1 {
  margin: 0;
  font-size: clamp(1.6rem, 4vw, 2.3rem);
  font-weight: 900;
}

.sub {
  margin: 7px 0 0;
  color: var(--text-muted);
  font-weight: 600;
}

.head-actions {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.tabs-wrap {
  margin-top: 14px;
  padding: 10px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.tab-btn {
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-muted);
  padding: 9px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  white-space: nowrap;
}

.tab-btn.active {
  background: rgba(242, 201, 126, 0.16);
  color: var(--accent-gold);
  border-color: rgba(242, 201, 126, 0.45);
}

.overview, .doc-panel {
  margin-top: 14px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.kpis-compact {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.kpi {
  padding: 16px;
}

.kpi p {
  margin: 0 0 8px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 13px;
}

.kpi h3 {
  margin: 0;
  font-size: clamp(1.1rem, 2.4vw, 1.5rem);
  font-weight: 900;
}

.list-card {
  padding: 14px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.card-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

.rows {
  display: grid;
  gap: 8px;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 10px 12px;
}

.row p {
  margin: 2px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

.row-meta {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.row-meta span {
  color: var(--accent-gold);
  font-weight: 700;
  font-size: 12px;
}

.row-meta small {
  color: var(--text-muted);
}

.doc-panel {
  padding: 14px;
}

.support-controls {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.support-create {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 12px;
}

.support-create h3 {
  margin: 0 0 10px;
  font-size: 1rem;
}

.support-create-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.support-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 12px;
}

.support-list {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 10px;
  min-height: 260px;
}

.support-ticket-row {
  width: 100%;
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px;
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
}

.support-ticket-row.active {
  border-color: rgba(242, 201, 126, 0.5);
}

.support-ticket-row small {
  color: var(--text-muted);
  font-size: 12px;
}

.support-detail {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 12px;
  min-height: 260px;
}

.support-ticket-meta {
  margin: 2px 0 8px;
  color: var(--text-muted);
  font-size: 12px;
}

.support-description {
  line-height: 1.9;
  margin-bottom: 12px;
}

.support-conversation {
  display: grid;
  gap: 8px;
  max-height: 280px;
  overflow: auto;
  margin-bottom: 10px;
}

.support-bubble {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 8px 10px;
}

.support-bubble.sent {
  border-color: rgba(242, 201, 126, 0.45);
}

.support-bubble small {
  color: var(--text-muted);
}

.support-bubble p {
  margin: 6px 0 0;
  line-height: 1.8;
}

.support-chat-panel,
.support-pref-panel {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 12px;
  margin-top: 12px;
}

.support-chat-panel h3,
.support-pref-panel h3 {
  margin: 0 0 10px;
}

.support-chat-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 12px;
}

.support-chat-list,
.support-chat-detail {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 10px;
}

.pref-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.controls {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field span {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 700;
}

.field input,
.field select,
.field textarea,
.table-input {
  border: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-main);
  padding: 10px 12px;
  border-radius: 12px;
  font-family: inherit;
  font-size: 13px;
}

.field input:disabled,
.field select:disabled {
  opacity: 0.7;
}

.field textarea {
  min-height: 96px;
  resize: vertical;
}

.compact input {
  min-height: 40px;
}

.ghost-btn {
  border: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  font-family: inherit;
  font-weight: 700;
}

.ghost-btn.gold {
  border-color: rgba(242, 201, 126, 0.5);
  color: var(--accent-gold);
}

.ghost-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.table-wrap {
  width: 100%;
  overflow: auto;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

th, td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--glass-border);
  text-align: right;
  font-size: 13px;
  vertical-align: top;
}

thead th {
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.actions.end {
  justify-content: flex-end;
}

.mini-btn {
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-main);
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.mini-btn.gold { color: var(--accent-gold); border-color: rgba(242, 201, 126, 0.5); }
.mini-btn.danger { color: #ff8f8f; border-color: rgba(255, 80, 80, 0.5); }

.pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  gap: 10px;
}

.pager span {
  color: var(--text-muted);
  font-size: 13px;
}

.state-card {
  padding: 18px;
  text-align: center;
  color: var(--text-muted);
}

.state-card.error {
  color: #ffc3c3;
}

.address-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.address-card {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 12px;
}

.address-card .top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.address-card .top span {
  color: var(--text-muted);
  font-size: 12px;
}

.address-card p {
  margin: 10px 0;
  color: var(--text-muted);
  line-height: 1.9;
  font-size: 13px;
}

.badges {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.badge {
  font-size: 11px;
  border: 1px solid rgba(242, 201, 126, 0.35);
  color: var(--accent-gold);
  padding: 3px 8px;
  border-radius: 999px;
}

.modal-wrap {
  position: fixed;
  inset: 0;
  z-index: 900;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-card {
  width: min(980px, 100%);
  max-height: 88vh;
  overflow: auto;
  padding: 16px;
}

.address-modal {
  width: min(740px, 100%);
}

.request-editor-modal {
  width: min(1320px, 100%);
}

.request-editor-content {
  display: grid;
  gap: 12px;
}

.request-meta-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.request-head-form {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.request-items-head {
  margin-top: 4px;
}

.table-input {
  width: 100%;
  min-height: 40px;
}

.doc-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}

.doc-meta div {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 10px;
  font-size: 13px;
  color: var(--text-muted);
}

.doc-meta strong {
  color: var(--text-main);
}

.address-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.check {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-main);
  font-size: 13px;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 1200px) {
  .overview-grid { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
  .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .kpis-compact { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .controls { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .support-layout { grid-template-columns: 1fr; }
  .support-chat-grid { grid-template-columns: 1fr; }
}

@media (max-width: 720px) {
  .dash-shell { padding: 20px 12px 110px; }
  .dash-header { flex-direction: column; align-items: stretch; }
  .head-actions { flex-direction: column; align-items: stretch; }
  .address-grid { grid-template-columns: 1fr; }
  .doc-meta { grid-template-columns: 1fr; }
  .address-form { grid-template-columns: 1fr; }
  .request-head-form { grid-template-columns: 1fr; }
  .kpis { grid-template-columns: 1fr; }
  .kpis-compact { grid-template-columns: 1fr; }
  .controls { grid-template-columns: 1fr; }
  .support-create-grid { grid-template-columns: 1fr; }
}
</style>
