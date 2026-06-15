from frappe.model.document import Document
import frappe
from datetime import datetime

class StaffOnboarding(Document):
    def before_insert(self):
        self.generate_onboarding_checklist()
        self.validate_onboarding_dates()

    def generate_onboarding_checklist(self):
        checklist_items = frappe.get_all("Onboarding Checklist Item", fields=["name"])
        for item in checklist_items:
            checklist = frappe.new_doc("Onboarding Checklist Item")
            checklist.parent = self.name
            checklist.parenttype = "Staff Onboarding"
            checklist.item_name = item.name
            checklist.status = "Pending"
            checklist.insert()

    def validate_onboarding_dates(self):
        if self.start_date and self.completion_date:
            if self.completion_date < self.start_date:
                frappe.throw("Completion date cannot be before start date")

    def validate(self):
        self.validate_onboarding_dates()
        if self.status == "Completed" and not self.completion_date:
            self.completion_date = frappe.utils.today()

    def before_save(self):
        if self.status == "Completed" and not self.completion_date:
            self.completion_date = frappe.utils.today()