from frappe.model.document import Document
import frappe

class HealthcarePractitioner(Document):
    def before_insert(self):
        if not self.practitioner_code:
            count = frappe.db.count("Healthcare Practitioner") + 1
            self.practitioner_code = f"DOC-{count:04d}"
    
    def validate(self):
        if self.consultation_fee and self.consultation_fee < 0:
            frappe.throw("Consultation fee cannot be negative")
