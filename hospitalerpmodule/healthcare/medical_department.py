from frappe.model.document import Document
import frappe

class MedicalDepartment(Document):
    def before_insert(self):
        if not self.department_code:
            count = frappe.db.count("Medical Department") + 1
            self.department_code = f"DEPT-{count:04d}"
