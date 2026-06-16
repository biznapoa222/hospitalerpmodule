from frappe.model.document import Document
import frappe

class QueueServiceType(Document):
    def before_insert(self):
        if not self.starting_number:
            self.starting_number = 1
