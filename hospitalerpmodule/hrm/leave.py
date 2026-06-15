from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class Leave(Document):
    def before_insert(self):
        self.calculate_total_days()
        self.validate_leave_dates()
        self.check_leave_balance()

    def calculate_total_days(self):
        if self.from_date and self.to_date:
            delta = self.to_date - self.from_date
            self.total_days = delta.days + 1

    def validate_leave_dates(self):
        if self.from_date and self.to_date:
            if self.to_date < self.from_date:
                frappe.throw("To date cannot be before from date")
            if self.from_date < frappe.utils.today():
                frappe.throw("Cannot apply for past dates")

    def check_leave_balance(self):
        if self.employee and self.leave_type and self.from_date and self.to_date:
            leave_type = frappe.get_doc("Leave Type", self.leave_type)
            employee = frappe.get_doc("Employee", self.employee)
            
            total_leave_days = self.total_days
            remaining_balance = leave_type.total_leaves - leave_type.used_leaves
            
            if total_leave_days > remaining_balance:
                frappe.throw(f"Insufficient leave balance. Available: {remaining_balance} days")

    def validate(self):
        self.validate_leave_dates()
        if self.status == "Approved":
            self.after_approve()

    def after_approve(self):
        if self.employee and self.leave_type:
            leave_type = frappe.get_doc("Leave Type", self.leave_type)
            leave_type.used_leaves += self.total_days
            leave_type.save()

    def before_save(self):
        self.calculate_total_days()