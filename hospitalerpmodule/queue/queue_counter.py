from frappe.model.document import Document
import frappe

class QueueCounter(Document):
    def validate(self):
        if self.status == "Active" and not self.counter_name:
            frappe.throw("Counter Name is required")
