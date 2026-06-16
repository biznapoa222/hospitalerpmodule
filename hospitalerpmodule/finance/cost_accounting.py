from frappe.model.document import Document
import frappe
from datetime import datetime

class CostAccounting(Document):
    def before_insert(self):
        self.calculate_unit_cost()
        self.validate_cost_details()

    def calculate_unit_cost(self):
        if self.quantity and self.cost_amount and self.quantity != 0:
            self.unit_cost = self.cost_amount / self.quantity

    def validate_cost_details(self):
        if self.cost_date and self.cost_date > frappe.utils.today():
            frappe.throw("Cost date cannot be in the future")

    def validate(self):
        self.validate_cost_details()
        if self.approval_status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()

    def after_insert(self):
        if self.approval_status == "Approved":
            self.update_cost_records()

    def update_cost_records(self):
        # Update cost accounting records and generate reports
        pass

    def before_save(self):
        self.calculate_unit_cost()

    def after_approval(self):
        if self.approval_status == "Approved":
            self.generate_cost_report()