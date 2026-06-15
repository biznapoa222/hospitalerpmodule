from frappe.model.document import Document
import frappe
from datetime import datetime

class LeaveType(Document):
    def before_insert(self):
        self.calculate_remaining_leaves()

    def calculate_remaining_leaves(self):
        if self.total_leaves and self.used_leaves:
            self.remaining_leaves = self.total_leaves - self.used_leaves

    def after_insert(self):
        self.initialize_employee_balances()

    def initialize_employee_balances(self):
        employees = frappe.get_all("Employee", fields=["name"])
        for employee in employees:
            balance = frappe.new_doc("Employee Leave Balance")
            balance.employee = employee.name
            balance.leave_type = self.name
            balance.total_leaves = self.total_leaves
            balance.used_leaves = 0
            balance.remaining_leaves = self.total_leaves
            balance.insert()