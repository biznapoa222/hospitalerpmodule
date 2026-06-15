from frappe.model.document import Document
import frappe
from datetime import datetime

class TrainingCertificate(Document):
    def before_insert(self):
        self.generate_certificate_url()
        self.update_employee_cme_credits()

    def generate_certificate_url(self):
        self.certificate_url = f"/app/training-certificate/{self.name}"

    def update_employee_cme_credits(self):
        if self.employee:
            employee = frappe.get_doc("Employee", self.employee)
            if not employee.cme_credits_total:
                employee.cme_credits_total = 0
            employee.cme_credits_total += self.cme_credits
            employee.save()

    def validate(self):
        if self.completion_date:
            self.training_year = str(self.completion_date.year)