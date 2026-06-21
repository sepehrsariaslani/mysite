var SBL_EDITOR_STYLES = `
.sbl-wrap { border: 1px solid var(--border-color); border-radius: 14px; padding: 12px; background: var(--fg-color); }
.sbl-hint { margin-bottom: 10px; color: var(--text-muted); font-size: 12px; }
.sbl-stage { position: relative; width: 100%; max-width: 980px; margin: 0 auto; border-radius: 12px; overflow: hidden; background: #f4f4f4; cursor: crosshair; }
.sbl-image { display: block; width: 100%; height: auto; user-select: none; pointer-events: none; }
.sbl-layer { position: absolute; inset: 0; }
.sbl-marker { position: absolute; width: 24px; height: 24px; border: 2px solid #fff; border-radius: 50%; background: rgba(0, 0, 0, 0.65); transform: translate(-50%, -50%); cursor: grab; box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.25); }
.sbl-marker.is-inactive { opacity: 0.4; }
.sbl-marker:active { cursor: grabbing; }
.sbl-marker::after { content: ''; position: absolute; inset: 6px; border-radius: 50%; background: #fff; }
.sbl-tooltip { position: absolute; right: 50%; bottom: calc(100% + 8px); transform: translateX(50%); min-width: 160px; max-width: 220px; border-radius: 10px; background: rgba(0, 0, 0, 0.85); color: #fff; padding: 8px 10px; font-size: 11px; line-height: 1.5; pointer-events: none; opacity: 0; transition: opacity 0.2s ease; }
.sbl-marker:hover .sbl-tooltip { opacity: 1; }
.sbl-tooltip strong { display: block; font-size: 12px; margin-bottom: 2px; }
.sbl-empty { text-align: center; color: var(--text-muted); padding: 24px 12px; border: 1px dashed var(--border-color); border-radius: 10px; }
`;

function formatToman(value) {
    const num = Number(value || 0);
    if (!Number.isFinite(num) || num <= 0) return 'تماس بگیرید';
    return `${num.toLocaleString('fa-IR')} تومان`;
}

function clampPercent(value) {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return 0;
    return Math.max(0, Math.min(100, num));
}

function ensureState(frm) {
    if (!frm.__sbl_state) {
        frm.__sbl_state = {
            previews: {},
            fetching: false,
        };
    }
    return frm.__sbl_state;
}

function getImageUrl(frm) {
    return frm.doc.cover_image || '';
}

function getRows(frm) {
    return (frm.doc.hotspots || []).slice().sort((a, b) => (a.idx || 0) - (b.idx || 0));
}

function bindItemQuery(frm) {
    const grid = frm.fields_dict.hotspots && frm.fields_dict.hotspots.grid;
    if (!grid) return;

    const field = grid.get_field('item_code');
    if (!field) return;

    field.get_query = () => ({
        filters: {
            show_on_site: 1,
            disabled: 0,
            is_stock_item: 1,
        },
    });
}

function fetchPreviews(frm) {
    const state = ensureState(frm);
    const rows = getRows(frm);
    const itemCodes = rows.map((row) => row.item_code).filter(Boolean);

    if (!itemCodes.length) {
        state.previews = {};
        renderEditor(frm);
        return;
    }

    if (state.fetching) return;
    state.fetching = true;

    frappe.call({
        method: 'mysite.www.mysite.shop_by_look_service.get_editor_item_previews',
        args: { item_codes: itemCodes },
        callback: (res) => {
            state.previews = (res && res.message) || {};
            state.fetching = false;
            renderEditor(frm);
        },
        error: () => {
            state.previews = {};
            state.fetching = false;
            renderEditor(frm);
        },
    });
}

function updateRowPosition(frm, rowName, xPercent, yPercent) {
    const row = (frm.doc.hotspots || []).find((entry) => entry.name === rowName);
    if (!row) return;

    row.x_percent = Number(clampPercent(xPercent).toFixed(2));
    row.y_percent = Number(clampPercent(yPercent).toFixed(2));
    frm.refresh_field('hotspots');
    frm.dirty();
}

function buildMarker(frm, row, stage, state) {
    const marker = document.createElement('div');
    marker.className = `sbl-marker ${row.is_active ? '' : 'is-inactive'}`;
    marker.style.left = `${clampPercent(row.x_percent)}%`;
    marker.style.top = `${clampPercent(row.y_percent)}%`;
    marker.dataset.rowName = row.name;

    const tooltip = document.createElement('div');
    tooltip.className = 'sbl-tooltip';

    const preview = state.previews[row.item_code] || {};
    const title = row.label || preview.item_name || row.item_code || 'بدون محصول';
    tooltip.innerHTML = `<strong>${frappe.utils.escape_html(title)}</strong>${formatToman(preview.base_price || 0)}`;
    marker.appendChild(tooltip);

    let dragging = false;

    marker.addEventListener('pointerdown', (event) => {
        event.preventDefault();
        event.stopPropagation();
        dragging = true;
        marker.setPointerCapture(event.pointerId);
    });

    marker.addEventListener('pointermove', (event) => {
        if (!dragging) return;
        const rect = stage.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        marker.style.left = `${clampPercent(x)}%`;
        marker.style.top = `${clampPercent(y)}%`;
        updateRowPosition(frm, row.name, x, y);
    });

    marker.addEventListener('pointerup', (event) => {
        dragging = false;
        marker.releasePointerCapture(event.pointerId);
    });

    marker.addEventListener('dblclick', (event) => {
        event.stopPropagation();
        frappe.set_route('Form', 'Shop By Look Scene', frm.doc.name);
    });

    return marker;
}

function renderEditor(frm) {
    const state = ensureState(frm);
    bindItemQuery(frm);

    if (!frm.fields_dict.editor_html) return;

    const wrapper = frm.fields_dict.editor_html.$wrapper;
    if (!wrapper) return;

    const imageUrl = getImageUrl(frm);
    const rows = getRows(frm);

    if (!imageUrl) {
        wrapper.html(`
            <style>${SBL_EDITOR_STYLES}</style>
            <div class="sbl-empty">ابتدا تصویر اصلی را انتخاب کنید، سپس روی تصویر کلیک کنید تا نقطه ساخته شود.</div>
        `);
        return;
    }

    wrapper.html(`
        <style>${SBL_EDITOR_STYLES}</style>
        <div class="sbl-wrap">
            <div class="sbl-hint">روی تصویر کلیک کنید تا Hotspot جدید ساخته شود. نقاط را بکشید تا موقعیت اصلاح شود.</div>
            <div class="sbl-stage" data-role="sbl-stage">
                <img class="sbl-image" src="${imageUrl}" alt="Shop by Look" />
                <div class="sbl-layer" data-role="sbl-layer"></div>
            </div>
        </div>
    `);

    const stage = wrapper.find('[data-role="sbl-stage"]')[0];
    const layer = wrapper.find('[data-role="sbl-layer"]')[0];
    if (!stage || !layer) return;

    rows.forEach((row) => {
        const marker = buildMarker(frm, row, stage, state);
        layer.appendChild(marker);
    });

    stage.addEventListener('click', (event) => {
        if (event.target && event.target.closest('.sbl-marker')) return;

        const rect = stage.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;

        frm.add_child('hotspots', {
            x_percent: Number(clampPercent(x).toFixed(2)),
            y_percent: Number(clampPercent(y).toFixed(2)),
            is_active: 1,
        });
        frm.refresh_field('hotspots');
        frm.dirty();
        fetchPreviews(frm);
        renderEditor(frm);
    });
}

if (!window.__mysite_shop_by_look_editor_registered) {
    window.__mysite_shop_by_look_editor_registered = true;

    frappe.ui.form.on('Shop By Look Scene', {
        setup(frm) {
            ensureState(frm);
            bindItemQuery(frm);
        },

        onload(frm) {
            bindItemQuery(frm);
        },

        refresh(frm) {
            bindItemQuery(frm);
            renderEditor(frm);
            fetchPreviews(frm);
        },

        cover_image(frm) {
            renderEditor(frm);
        },

        hotspots_add(frm) {
            renderEditor(frm);
            fetchPreviews(frm);
        },

        hotspots_remove(frm) {
            renderEditor(frm);
            fetchPreviews(frm);
        },
    });

    frappe.ui.form.on('Shop By Look Hotspot', {
        item_code(frm) {
            fetchPreviews(frm);
            renderEditor(frm);
        },

        x_percent(frm) {
            renderEditor(frm);
        },

        y_percent(frm) {
            renderEditor(frm);
        },

        label(frm) {
            renderEditor(frm);
        },

        is_active(frm) {
            renderEditor(frm);
        },
    });
}
