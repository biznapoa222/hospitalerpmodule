from frappe.model.document import Document
import frappe
from datetime import datetime

class CME(Document):
    def before_insert(self):
        self.validate_activity_date()
        self.calculate_year_to_date_credits()

    def validate_activity_date(self):
        if self.activity_date and self.activity_date > frappe.utils.today():
            frappe.throw("Activity date cannot be in the future")

    def calculate_year_to_date_credits(self):
        current_year = frappe.utils.today().year
        existing_credits = frappe.db.sum("CME", {
            "employee": self.employee,
            "activity_date": ["like", f"{current_year}%"]
        }) or 0
        
        self.total_credits_year_to_date = existing_credits + self.cme_credits_earned
        
        if self.total_credits_year_to_date > self.remaining_credits_limit:
            frappe.throw(f"Total credits exceed the limit of {self.remaining_credits_limit}")

    def validate(self):
        self.validate_activity_date()
        if self.status == "Approved" and not self.approval_date:
            self.approval_date = frappe.utils.today()

    def after_insert(self):
        if self.status == "Approved":
            self.update_employee_cme_summary()

    def update_employee_cme_summary(self):
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.cme_summary:
            employee.cme_summary = {}
        
        if not employee.cme_summary.get("total_credits", 0):
            employee.cme_summary["total_credits"] = 0
        
        employee.cme_summary["total_credits"] += self.cme_credits_earned
        employee.save()