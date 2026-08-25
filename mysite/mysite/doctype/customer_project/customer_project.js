frappe.ui.form.on('Customer Project', {
    setup(frm) {
        frm.set_query('item_code', 'products', () => ({
            filters: {
                show_on_site: 1,
                disabled: 0,
                is_stock_item: 1,
            },
        }));

        frm.set_query('cloth_item', 'products', () => ({
            filters: {
                disabled: 0,
                is_stock_item: 1,
                variant_of: 'پارچه',
                item_group: 'پارچه',
            },
        }));
    },
});
