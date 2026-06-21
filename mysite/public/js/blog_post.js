(function () {
    if (window.__mysite_blog_post_form_registered) return;
    window.__mysite_blog_post_form_registered = true;

    const BLOCK_TEMPLATES = {
        heading_2: '<h2>تیتر بخش</h2>\n<p>توضیح این بخش را بنویسید.</p>',
        heading_3: '<h3>زیرتیتر</h3>\n<p>متن زیرتیتر را بنویسید.</p>',
        paragraph: '<p>این یک پاراگراف نمونه برای شروع نوشتن است.</p>',
        list: '<ul><li>نکته اول</li><li>نکته دوم</li><li>نکته سوم</li></ul>',
        quote: '<blockquote>یک نقل قول کوتاه یا نکته مهم در این بخش قرار می‌گیرد.</blockquote>',
        image: '<p><img src="/assets/mysite/img/placeholder.png" alt="تصویر مقاله"></p>',
        cta: '<div class="blog-inline-cta"><p>برای دریافت مشاوره خرید، با ما در ارتباط باشید.</p><a href="/consultation">درخواست مشاوره</a></div>',
        divider: '<hr>',
    };

    function ensureState(frm) {
        if (!frm.__blog_editor_state) {
            frm.__blog_editor_state = {
                saveTimer: null,
                skipRefresh: false,
            };
        }
        return frm.__blog_editor_state;
    }

    function normalizeText(value) {
        return String(value || '').trim();
    }

    function sanitizeHtml(rawHtml) {
        const tmp = document.createElement('div');
        tmp.innerHTML = String(rawHtml || '');
        tmp.querySelectorAll('script, style, iframe, object, embed, link, meta').forEach((el) => el.remove());
        return tmp.innerHTML;
    }

    function cleanBodyHtml(rawHtml) {
        let html = sanitizeHtml(rawHtml).trim();
        html = html
            .replace(/^<div><br><\/div>$/i, '')
            .replace(/^<p><br><\/p>$/i, '')
            .replace(/^<br>$/i, '')
            .trim();
        return html;
    }

    function htmlFromBody(rawText) {
        const text = normalizeText(rawText);
        if (!text) return '';
        if (/<[a-z][\s\S]*>/i.test(text)) return text;
        return text
            .split(/\n{2,}/)
            .map((part) => `<p>${frappe.utils.escape_html(part).replace(/\n/g, '<br>')}</p>`)
            .join('\n');
    }

    function appendBlock(frm, blockKey) {
        const template = BLOCK_TEMPLATES[blockKey];
        if (!template) return;
        const state = ensureState(frm);
        const current = normalizeText(frm.doc.custom_article_body);
        const nextValue = current ? `${current}\n\n${template}` : template;
        frm.doc.custom_article_body = nextValue;
        frm.dirty();
        state.skipRefresh = true;
        frm.refresh_field('custom_article_body');
        state.skipRefresh = false;
        renderEditorGuide(frm);
        renderLivePreview(frm);
    }

    function shortcutsHelpHtml() {
        return `
            <div style="margin-top:10px;border:1px dashed #e3dccf;border-radius:10px;padding:8px;background:#fff;">
                <div style="font-weight:700;font-size:12px;margin-bottom:6px;">Shortcuts (Notion-like)</div>
                <div class="bp-shortcuts-grid" style="font-size:12px;color:#666;">
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>2</kbd> = H2</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>3</kbd> = H3</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> = پاراگراف</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>L</kbd> = لیست</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>Q</kbd> = نقل قول</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>I</kbd> = تصویر</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd> = CTA</div>
                    <div><kbd>Option</kbd>/<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> = جداکننده</div>
                    <div><kbd>Command</kbd> + <kbd>Shift</kbd> + <kbd>2</kbd>/<kbd>3</kbd> = H2/H3</div>
                    <div><kbd>Command</kbd> + <kbd>Shift</kbd> + <kbd>P/L/Q/I/C/D</kbd> = بلوک‌ها</div>
                </div>
            </div>
        `;
    }

    function resolveShortcutBlock(event) {
        if (!event) return null;
        if (event.isComposing) return null;

        const hasModifierCombo =
            (event.altKey && event.shiftKey) ||
            (event.metaKey && event.shiftKey) ||
            (event.ctrlKey && event.altKey);
        if (!hasModifierCombo) return null;

        const codeMap = {
            Digit2: 'heading_2',
            Digit3: 'heading_3',
            KeyP: 'paragraph',
            KeyL: 'list',
            KeyQ: 'quote',
            KeyI: 'image',
            KeyC: 'cta',
            KeyD: 'divider',
        };
        const byCode = codeMap[String(event.code || '').trim()];
        if (byCode) return byCode;

        const keyMap = {
            '2': 'heading_2',
            '3': 'heading_3',
            p: 'paragraph',
            l: 'list',
            q: 'quote',
            i: 'image',
            c: 'cta',
            d: 'divider',
        };
        return keyMap[String(event.key || '').toLowerCase()] || null;
    }

    function syncPreviewField(frm, fieldname, value, applyMetaDefaults) {
        const state = ensureState(frm);
        if (fieldname === 'custom_article_body') {
            frm.doc.custom_article_body = cleanBodyHtml(value);
        } else {
            frm.doc[fieldname] = normalizeText(value);
        }
        frm.dirty();

        if (applyMetaDefaults) {
            const intro = normalizeText(frm.doc.blog_intro);
            const title = normalizeText(frm.doc.title);
            if (title && !normalizeText(frm.doc.meta_title)) {
                frm.doc.meta_title = title;
            }
            if (intro && !normalizeText(frm.doc.meta_description)) {
                frm.doc.meta_description = intro.slice(0, 300);
            }
        }

        clearTimeout(state.saveTimer);
        state.saveTimer = setTimeout(() => {
            state.skipRefresh = true;
            frm.refresh_field(fieldname);
            if (fieldname === 'title' && frm.doc.meta_title) frm.refresh_field('meta_title');
            if (fieldname === 'blog_intro' && frm.doc.meta_description) frm.refresh_field('meta_description');
            state.skipRefresh = false;
            renderEditorGuide(frm);
        }, 500);
    }

    function renderEditorGuide(frm) {
        const field = frm.get_field('custom_editor_guide');
        if (!field || !field.$wrapper) return;

        const hasBody = !!normalizeText(
            frm.doc.custom_article_body ||
            frm.doc.content_html ||
            frm.doc.content_md ||
            frm.doc.content
        );
        const hasIntro = !!normalizeText(frm.doc.blog_intro);
        const relatedRows = Array.isArray(frm.doc.custom_related_products) ? frm.doc.custom_related_products.length : 0;

        field.$wrapper.html(`
            <div style="border:1px solid var(--border-color);border-radius:12px;padding:12px;background:var(--fg-color);line-height:1.9;">
                <div style="font-weight:700;margin-bottom:8px;">راهنمای سریع انتشار بلاگ</div>
                <div>1) عنوان، دسته‌بندی و عکس کاور را پر کن.</div>
                <div>2) «خلاصه بلاگ» را بنویس (برای کارت لیست و سئو).</div>
                <div>3) از پالت کامپوننت‌ها، بلوک‌های مقاله را بساز.</div>
                <div>4) محصولات مرتبط را اضافه کن تا زیر مقاله نمایش داده شوند.</div>
                <hr style="border:none;border-top:1px solid var(--border-color);margin:10px 0;">
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <span style="padding:4px 8px;border-radius:999px;background:${hasIntro ? '#dff5e1' : '#ffe3e3'};">
                        خلاصه: ${hasIntro ? 'تکمیل' : 'خالی'}
                    </span>
                    <span style="padding:4px 8px;border-radius:999px;background:${hasBody ? '#dff5e1' : '#ffe3e3'};">
                        متن کامل: ${hasBody ? 'تکمیل' : 'خالی'}
                    </span>
                    <span style="padding:4px 8px;border-radius:999px;background:${relatedRows > 0 ? '#dff5e1' : '#fff3cd'};">
                        محصولات مرتبط: ${relatedRows}
                    </span>
                </div>
            </div>
        `);
    }

    function componentPaletteHtml() {
        return `
            <div style="border:1px solid #e8e2d7;border-radius:12px;padding:12px;background:#fff;">
                <div style="font-weight:700;margin-bottom:8px;">پالت کامپوننت‌ها (سبک Notion)</div>
                <div style="color:#7f7f7f;font-size:12px;margin-bottom:10px;">روی هر بلوک بزن تا انتهای «محتوای کامل بلاگ» اضافه شود.</div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;">
                    <button class="bp-block-btn" data-block="heading_2" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">تیتر H2</button>
                    <button class="bp-block-btn" data-block="heading_3" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">زیرتیتر H3</button>
                    <button class="bp-block-btn" data-block="paragraph" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">پاراگراف</button>
                    <button class="bp-block-btn" data-block="list" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">لیست</button>
                    <button class="bp-block-btn" data-block="quote" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">نقل قول</button>
                    <button class="bp-block-btn" data-block="image" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">تصویر</button>
                    <button class="bp-block-btn" data-block="cta" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">CTA</button>
                    <button class="bp-block-btn" data-block="divider" style="padding:8px;border:1px solid #e7e1d9;border-radius:10px;background:#f9f9f9;">جداکننده</button>
                </div>
                ${shortcutsHelpHtml()}
            </div>
        `;
    }

    function renderLivePreview(frm) {
        const field = frm.get_field('custom_live_preview');
        if (!field || !field.$wrapper) return;

        const title = normalizeText(frm.doc.title);
        const subtitle = normalizeText(frm.doc.custom_subtitle);
        const intro = normalizeText(frm.doc.blog_intro);
        const bodySource = normalizeText(
            frm.doc.custom_article_body ||
            frm.doc.content_html ||
            frm.doc.content_md ||
            frm.doc.content ||
            frm.doc.blog_intro ||
            frm.doc.meta_description
        );
        const bodyHtml = htmlFromBody(bodySource);
        const products = Array.isArray(frm.doc.custom_related_products)
            ? frm.doc.custom_related_products.filter((row) => normalizeText(row.item_code))
            : [];

        const productsHtml = products.length
            ? products.map((row) => `
                <div style="border:1px solid #e7e7e7;border-radius:10px;padding:10px;background:#fff;">
                    <div style="font-weight:700;margin-bottom:4px;">${frappe.utils.escape_html(row.custom_label || row.item_code)}</div>
                    <div style="font-size:12px;color:#777;">${frappe.utils.escape_html(row.note || '')}</div>
                </div>
            `).join('')
            : '<div style="color:#8b8b8b;font-size:12px;">محصول مرتبطی اضافه نشده است.</div>';

        field.$wrapper.html(`
            <style>
                .bp-canvas [contenteditable="true"] { outline: none; }
                .bp-editable {
                    border: 1px dashed transparent;
                    border-radius: 10px;
                    transition: border-color .15s ease, background .15s ease;
                    padding: 8px;
                }
                .bp-editable:hover { border-color: #e7e1d9; }
                .bp-editable:focus { border-color: #d6b98c; background: #fffdf8; }
                .bp-editable[data-placeholder]:empty:before {
                    content: attr(data-placeholder);
                    color: #a8a8a8;
                }
                .bp-edit-title { margin: 0 0 8px; font-size: 30px; line-height: 1.4; font-weight: 800; }
                .bp-edit-sub { margin: 0 0 10px; color: #444; line-height: 1.8; min-height: 32px; }
                .bp-edit-intro { margin: 0 0 16px; color: #666; line-height: 1.9; min-height: 40px; }
                .bp-edit-body { line-height: 2; color: #1f1f1f; min-height: 220px; }
                .bp-live-tip { color: #8a8a8a; font-size: 12px; margin-bottom: 10px; }
                .bp-canvas { box-sizing: border-box; width: 100%; padding: 14px 16px; }
                .bp-preview-shell { width: 100%; max-width: none; margin: 0; background:#fff; border:1px solid #ececec; border-radius:14px; padding:30px 34px; box-sizing:border-box; }
                .bp-edit-body { min-height: 480px; }
                .bp-canvas kbd {
                    border: 1px solid #d6d6d6;
                    background: #f4f4f4;
                    border-radius: 6px;
                    padding: 1px 6px;
                    font-size: 11px;
                    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
                }
                .bp-shortcuts-grid {
                    display:grid;
                    grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
                    gap:6px 12px;
                }
                @media (max-width: 1200px) {
                    .bp-preview-shell { padding: 22px 20px; }
                    .bp-edit-body { min-height: 380px; }
                }
                @media (max-width: 860px) {
                    .bp-canvas { padding: 10px; }
                    .bp-preview-shell { padding: 16px 14px; }
                    .bp-edit-title { font-size: 24px; }
                    .bp-edit-body { min-height: 320px; }
                    .bp-shortcuts-grid { grid-template-columns:1fr; }
                }
            </style>
            <div class="bp-canvas" style="border:1px solid var(--border-color);border-radius:14px;background:#f5f5f5;">
                <div style="font-weight:700;margin-bottom:10px;">پیش‌نمایش زنده (Notion-like Canvas)</div>
                <div class="bp-live-tip">اینجا مستقیم تایپ کن. تغییرات فوری روی فیلدهای پست اعمال می‌شود؛ برای انتشار نهایی، ذخیره فرم را بزن.</div>
                ${componentPaletteHtml()}
                <div class="bp-preview-shell" style="margin-top:12px;">
                    <div style="font-size:12px;color:#9b9b9b;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;">Blog Preview</div>
                    <div class="bp-editable bp-edit-title" contenteditable="true" data-blog-edit="title" data-placeholder="عنوان مقاله را اینجا بنویس...">${frappe.utils.escape_html(title)}</div>
                    <div class="bp-editable bp-edit-sub" contenteditable="true" data-blog-edit="custom_subtitle" data-placeholder="زیرتیتر (اختیاری)...">${frappe.utils.escape_html(subtitle)}</div>
                    <div class="bp-editable bp-edit-intro" contenteditable="true" data-blog-edit="blog_intro" data-placeholder="خلاصه مقاله را اینجا بنویس...">${frappe.utils.escape_html(intro)}</div>
                    <hr style="border:none;border-top:1px solid #ececec;margin:12px 0 18px;">
                    <div class="bp-editable bp-edit-body" contenteditable="true" data-blog-edit="custom_article_body" data-placeholder="متن اصلی مقاله را اینجا بنویس...">${bodyHtml}</div>
                    <div style="margin-top:22px;">
                        <div style="font-weight:700;margin-bottom:8px;">محصولات مرتبط</div>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;">${productsHtml}</div>
                    </div>
                </div>
            </div>
        `);

        const wrapper = field.$wrapper;
        wrapper.off('keydown', '.bp-edit-title, .bp-edit-sub');
        wrapper.off('keydown', '[data-blog-edit="custom_article_body"]');
        wrapper.off('input', '[data-blog-edit]');
        wrapper.off('blur', '[data-blog-edit]');
        wrapper.off('click', '.bp-block-btn');

        wrapper.on('keydown', '.bp-edit-title, .bp-edit-sub', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
            }
        });

        wrapper.on('keydown', '[data-blog-edit="custom_article_body"]', function (event) {
            const block = resolveShortcutBlock(event);
            if (!block) return;
            event.preventDefault();
            appendBlock(frm, block);
        });

        wrapper.on('click', '.bp-block-btn', function (event) {
            event.preventDefault();
            const blockKey = this.getAttribute('data-block');
            appendBlock(frm, blockKey);
        });

        wrapper.on('input', '[data-blog-edit]', function () {
            const editTarget = this.getAttribute('data-blog-edit');
            if (!editTarget) return;
            const rawValue = editTarget === 'custom_article_body' ? this.innerHTML : this.innerText;
            syncPreviewField(frm, editTarget, rawValue, true);
        });

        wrapper.on('blur', '[data-blog-edit]', function () {
            const editTarget = this.getAttribute('data-blog-edit');
            if (!editTarget) return;
            const state = ensureState(frm);
            clearTimeout(state.saveTimer);
            state.skipRefresh = true;
            frm.refresh_field(editTarget);
            if (editTarget === 'title' && frm.doc.meta_title) frm.refresh_field('meta_title');
            if (editTarget === 'blog_intro' && frm.doc.meta_description) frm.refresh_field('meta_description');
            state.skipRefresh = false;
            renderEditorGuide(frm);
        });
    }

    function refreshEditorPanels(frm) {
        renderEditorGuide(frm);
        if (typeof frm.toggle_display === 'function') {
            frm.toggle_display('custom_component_palette', false);
        }
        renderLivePreview(frm);
    }

    frappe.ui.form.on('Blog Post', {
        setup(frm) {
            frm.set_query('item_code', 'custom_related_products', () => ({
                filters: {
                    show_on_site: 1,
                    disabled: 0,
                    is_stock_item: 1,
                },
            }));
        },

        refresh(frm) {
            refreshEditorPanels(frm);

            if (!frm.is_new()) {
                frm.add_custom_button('پیش‌نمایش در سایت', () => {
                    const route = `/blog?post=${encodeURIComponent(frm.doc.name)}`;
                    window.open(route, '_blank');
                }, 'وب‌سایت');
            }
        },

        title(frm) {
            if (ensureState(frm).skipRefresh) return;
            const title = normalizeText(frm.doc.title);
            if (!title) return;
            if (!normalizeText(frm.doc.meta_title)) {
                frm.set_value('meta_title', title);
            }
            refreshEditorPanels(frm);
        },

        blog_intro(frm) {
            if (ensureState(frm).skipRefresh) return;
            const intro = normalizeText(frm.doc.blog_intro);
            if (intro && !normalizeText(frm.doc.meta_description)) {
                frm.set_value('meta_description', intro.slice(0, 300));
            }
            refreshEditorPanels(frm);
        },

        content(frm) {
            if (ensureState(frm).skipRefresh) return;
            refreshEditorPanels(frm);
        },

        custom_article_body(frm) {
            if (ensureState(frm).skipRefresh) return;
            refreshEditorPanels(frm);
        },

        custom_subtitle(frm) {
            if (ensureState(frm).skipRefresh) return;
            refreshEditorPanels(frm);
        },

        custom_related_products_add(frm) {
            refreshEditorPanels(frm);
        },

        custom_related_products_remove(frm) {
            refreshEditorPanels(frm);
        },
    });

    frappe.ui.form.on('Blog Post Product', {
        item_code(frm) {
            refreshEditorPanels(frm);
        },
        custom_label(frm) {
            refreshEditorPanels(frm);
        },
        note(frm) {
            refreshEditorPanels(frm);
        },
        is_active(frm) {
            refreshEditorPanels(frm);
        },
    });
})();
