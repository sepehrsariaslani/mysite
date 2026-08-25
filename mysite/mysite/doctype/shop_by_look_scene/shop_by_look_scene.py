import frappe
from frappe.model.document import Document


class ShopByLookScene(Document):
    def validate(self):
        self._validate_hotspots()
        self._apply_defaults()

    def _apply_defaults(self):
        self.editor_hint = (
            "برای افزودن نقطه روی تصویر کلیک کنید. برای جابه‌جایی، نقطه را Drag کنید. "
            "نقطه بدون محصول ذخیره نمی‌شود."
        )

    def _validate_hotspots(self):
        for row in self.hotspots or []:
            if not row.item_code:
                frappe.throw(f"ردیف {row.idx}: انتخاب محصول برای Hotspot الزامی است.")

            x = _to_float(row.x_percent)
            y = _to_float(row.y_percent)

            if x < 0 or x > 100:
                frappe.throw(f"ردیف {row.idx}: مقدار X باید بین 0 تا 100 باشد.")
            if y < 0 or y > 100:
                frappe.throw(f"ردیف {row.idx}: مقدار Y باید بین 0 تا 100 باشد.")

            row.x_percent = x
            row.y_percent = y



def _to_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0
