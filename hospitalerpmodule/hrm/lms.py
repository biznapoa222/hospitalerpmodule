from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class LMS(Document):
    def before_insert(self):
        self.calculate_duration()
        self.validate_course_dates()

    def calculate_duration(self):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.duration_hours = (delta.days + 1) * 8  # Assuming 8 hours per day

    def validate_course_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before start date")
            if self.start_date < frappe.utils.today():
                frappe.throw("Cannot enroll for past courses")

    def validate(self):
        self.validate_course_dates()
        if self.status == "Completed":
            self.generate_certificate()

    def generate_certificate(self):
        if self.employee and self.course_name:
            employee = frappe.get_doc("Employee", self.employee)
            training_certificate = frappe.new_doc("Training Certificate")
            training_certificate.employee = self.employee
            training_certificate.training_name = self.course_name
            training_certificate.completion_date = frappe.utils.today()
            training_certificate.cme_credits = self.cme_credits
            training_certificate.insert()

    def before_save(self):
        self.calculate_duration()