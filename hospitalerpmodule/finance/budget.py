from frappe.model.document import Document
import frappe
from datetime import datetime

class Budget(Document):
    def before_insert(self):
        self.calculate_variance()
        self.validate_budget_dates()

    def calculate_variance(self):
        if self.actual_amount and self.budget_amount and self.budget_amount != 0:
            self.variance_amount = self.actual_amount - self.budget_amount
            self.variance_percentage = (self.variance_amount / self.budget_amount) * 100

    def validate_budget_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before start date")
            if self.start_date < frappe.utils.today():
                frappe.throw("Budget start date cannot be in the past")

    def validate(self):
        self.validate_budget_dates()
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()

    def after_insert(self):
        if self.status == "Approved":
            self.update_budget_status()

    def update_budget_status(self):
        if self.variance_percentage > 0:
            self.status = "Over Budget"
        elif self.variance_percentage < 0:
            self.status = "Under Budget"
        else:
            self.status = "Active"
        self.save()

    def before_save(self):
        self.calculate_variance()
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()