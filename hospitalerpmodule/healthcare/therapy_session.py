from frappe.model.document import Document
import frappe

class TherapySession(Document):
    def before_insert(self):
        if not self.session_code:
            count = frappe.db.count("Therapy Session") + 1
            self.session_code = f"THR-{count:04d}"
    
    def validate(self):
        if self.start_time and self.end_time:
            from datetime import datetime
            start = datetime.strptime(str(self.start_time), "%H:%M:%S")
            end = datetime.strptime(str(self.end_time), "%H:%M:%S")
            self.duration = int((end - start).seconds / 60)
