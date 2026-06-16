from frappe.model.document import Document
import frappe

class Diagnosis(Document):
    def before_insert(self):
        if self.medical_code:
            code = frappe.get_cached_doc("Medical Code", self.medical_code)
            self.diagnosis_code = code.code
