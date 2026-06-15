from frappe.model.document import Document
import frappe
from datetime import datetime

class OnboardingChecklistItem(Document):
    def before_insert(self):
        self.validate_checklist_item()

    def validate_checklist_item(self):
        if self.due_date and self.due_date < frappe.utils.today():
            frappe.throw("Due date cannot be in the past")

    def validate(self):
        self.validate_checklist_item()
        if self.status == "Completed" and not self.completion_date:
            self.completion_date = frappe.utils.today()
        if self.status == "Completed" and self.due_date and self.completion_date > self.due_date:
            frappe.throw("Completion date cannot be after due date")

    def after_insert(self):
        self.update_parent_onboarding_status()

    def update_parent_onboarding_status(self):
        if self.parent and self.parenttype:
            parent = frappe.get_doc(self.parenttype, self.parent)
            if hasattr(parent, 'onboarding_checklist'):
                all_completed = True
                for item in parent.onboarding_checklist:
                    if item.status != "Completed":
                        all_completed = False
                        break
                
                if all_completed:
                    parent.status = "Completed"
                    parent.save()