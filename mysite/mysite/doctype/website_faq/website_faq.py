import frappe
from frappe.model.document import Document


class WebsiteFAQ(Document):
    def validate(self):
        self._normalize_fields()

    def _normalize_fields(self):
        self.faq_question = " ".join(str(self.faq_question or "").split()).strip()
        if not self.faq_question:
            frappe.throw("ثبت سوال برای FAQ الزامی است.")

        answer_text = str(self.faq_answer or "").strip()
        if not answer_text:
            frappe.throw("ثبت پاسخ برای FAQ الزامی است.")

        if not self.faq_category:
            self.faq_category = "عمومی"
