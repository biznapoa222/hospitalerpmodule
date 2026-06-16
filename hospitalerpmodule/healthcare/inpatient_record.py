from frappe.model.document import Document
import frappe

class InpatientRecord(Document):
    def before_insert(self):
        if not self.inpatient_code:
            year = frappe.utils.nowdate()[:4]
            count = frappe.db.count("Inpatient Record") + 1
            self.inpatient_code = f"IPD-{year}-{count:04d}"
    
    def validate(self):
        if self.status == "Admitted":
            self.update_service_unit_occupancy(1)
    
    def on_update(self):
        if self.status == "Discharged" and self.get_doc_before_save():
            old = self.get_doc_before_save()
            if old.status != "Discharged":
                self.update_service_unit_occupancy(-1)
    
    def update_service_unit_occupancy(self, change):
        if self.service_unit:
            unit = frappe.get_doc("Healthcare Service Unit", self.service_unit)
            unit.occupied = (unit.occupied or 0) + change
            unit.save(ignore_permissions=True)
