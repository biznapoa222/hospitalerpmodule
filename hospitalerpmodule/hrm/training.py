from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class Training(Document):
    def before_insert(self):
        self.calculate_duration()
        self.validate_training_dates()

    def calculate_duration(self):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.duration_hours = (delta.days + 1) * 8  # Assuming 8 hours per day

    def validate_training_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before start date")
            if self.start_date < frappe.utils.today():
                frappe.throw("Cannot schedule past training sessions")

    def validate(self):
        self.validate_training_dates()
        if self.status == "Completed":
            self.generate_certificate()

    def generate_certificate(self):
        if self.employee and self.training_name:
            employee = frappe.get_doc("Employee", self.employee)
            certificate = frappe.new_doc("Training Certificate")
            certificate.employee = self.employee
            certificate.training_name = self.training_name
            certificate.trainer = self.trainer
            certificate.completion_date = frappe.utils.today()
            certificate.cme_credits = self.cme_credits
            certificate.insert()

    def before_save(self):
        self.calculate_duration()