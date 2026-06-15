from frappe.model.document import Document
import frappe
from datetime import datetime

class Employee(Document):
    def before_insert(self):
        self.validate_employee_id()
        self.generate_employee_code()
        self.validate_employment_dates()

    def validate_employee_id(self):
        if self.employee_id:
            existing = frappe.db.exists("Employee", {"employee_id": self.employee_id, "name": ["!=", self.name] if self.name else None})
            if existing:
                frappe.throw("Employee ID must be unique")

    def generate_employee_code(self):
        if not self.employee_code and self.first_name and self.last_name:
            first_initial = self.first_name[0].upper()
            last_initial = self.last_name[0].upper()
            count = frappe.db.count("Employee") + 1
            self.employee_code = f"{first_initial}{last_initial}{count:04d}"

    def validate_employment_dates(self):
        if self.date_of_joining and self.relieving_date:
            if self.relieving_date < self.date_of_joining:
                frappe.throw("Relieving date cannot be before joining date")

    def validate(self):
        self.validate_employee_id()
        if self.email and "@" not in self.email:
            frappe.throw("Invalid email address")
        if self.phone and not self.phone.isdigit():
            frappe.throw("Phone number must contain only digits")

    def after_insert(self):
        self.create_default_shift_assignment()

    def create_default_shift_assignment(self):
        shift_type = frappe.db.exists("Shift Type", {"is_default": 1})
        if shift_type:
            shift_assignment = frappe.new_doc("Shift Assignment")
            shift_assignment.employee = self.name
            shift_assignment.shift_type = shift_type
            shift_assignment.shift_date = frappe.utils.today()
            shift_assignment.insert()