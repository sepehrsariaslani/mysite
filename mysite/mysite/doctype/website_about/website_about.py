import frappe
from frappe.model.document import Document


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip()


class WebsiteAbout(Document):
    def validate(self):
        self._normalize_fields()
        self._validate_required_sections()
        self._normalize_values()
        self._normalize_timeline()

    def _normalize_fields(self):
        self.title = _normalize_text(self.title)
        self.mission_title = _normalize_text(self.mission_title)
        self.vision_title = _normalize_text(self.vision_title)
        self.history_title = _normalize_text(self.history_title)

    def _validate_required_sections(self):
        if not self.title:
            frappe.throw("عنوان صفحه درباره ما الزامی است.")
        if not self.mission_title or not str(self.mission_body or "").strip():
            frappe.throw("بخش ماموریت باید کامل ثبت شود.")
        if not self.vision_title or not str(self.vision_body or "").strip():
            frappe.throw("بخش چشم‌انداز باید کامل ثبت شود.")
        if not self.history_title or not str(self.history_body or "").strip():
            frappe.throw("بخش تاریخچه باید کامل ثبت شود.")

    def _normalize_values(self):
        for index, row in enumerate(self.get("core_values") or []):
            row.value_title = _normalize_text(row.value_title)
            row.value_description = str(row.value_description or "").strip()
            row.icon = _normalize_text(row.icon)
            if row.sort_order in (None, ""):
                row.sort_order = (index + 1) * 10

    def _normalize_timeline(self):
        for index, row in enumerate(self.get("history_timeline") or []):
            row.year_label = _normalize_text(row.year_label)
            row.milestone_title = _normalize_text(row.milestone_title)
            row.milestone_description = str(row.milestone_description or "").strip()
            if row.sort_order in (None, ""):
                row.sort_order = (index + 1) * 10
