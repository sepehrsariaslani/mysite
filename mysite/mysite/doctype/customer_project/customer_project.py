import frappe
from frappe.model.document import Document


class CustomerProject(Document):
    def validate(self):
        self._normalize_fields()
        self._validate_images()
        self._validate_products()

    def _normalize_fields(self):
        self.title = (self.title or "").strip()
        self.customer_name = (self.customer_name or "").strip()
        self.location = (self.location or "").strip()
        self.project_type_custom = (self.project_type_custom or "").strip()
        self.short_description = (self.short_description or "").strip()
        self.client_request = (self.client_request or "").strip()

        self.project_area_sqm = _to_float(self.project_area_sqm, default=0.0)
        if self.project_area_sqm < 0:
            self.project_area_sqm = 0.0

        if self.project_type != "سایر":
            self.project_type_custom = ""

    def _validate_images(self):
        for row in self.project_images or []:
            if not row.image:
                frappe.throw(f"ردیف تصویر {row.idx}: انتخاب تصویر الزامی است.")
            row.caption = (row.caption or "").strip()
            row.sort_order = _to_int(row.sort_order, default=0)

    def _validate_products(self):
        for row in self.products or []:
            if not row.item_code:
                frappe.throw(f"ردیف {row.idx}: انتخاب محصول الزامی است.")

            qty = _to_int(row.qty, default=1)
            if qty <= 0:
                qty = 1

            row.qty = qty
            row.sort_order = _to_int(row.sort_order, default=0)
            row.note = (row.note or "").strip()


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except Exception:
        return int(default)


def _to_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return float(default)
