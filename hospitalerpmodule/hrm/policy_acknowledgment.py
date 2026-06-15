from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class PolicyAcknowledgment(Document):
    def before_insert(self):
        self.validate_acknowledgment_date()
        self.generate_acknowledgment_text()
        self.calculate_expiry_date()

    def validate_acknowledgment_date(self):
        if self.acknowledgment_date and self.acknowledgment_date > frappe.utils.today():
            frappe.throw("Acknowledgment date cannot be in the future")

    def generate_acknowledgment_text(self):
        if self.policy_name and self.acknowledged_by:
            self.acknowledgement_text = f"I, {self.acknowledged_by}, acknowledge and agree to comply with the {self.policy_name} policy."

    def calculate_expiry_date(self):
        if self.acknowledgment_date:
            self.expiry_date = self.acknowledgment_date.replace(year=self.acknowledgment_date.year + 1)
        if self.expiry_date:
            self.next_review_due = self.expiry_date.replace(year=self.expiry_date.year - 1)

    def validate(self):
        self.validate_acknowledgment_date()
        if self.status == "Acknowledged" and not self.acknowledgment_date:
            self.acknowledgment_date = frappe.utils.today()
        if self.status == "Expired" and self.acknowledgment_date:
            self.acknowledgment_date = self.acknowledgment_date.replace(year=self.acknowledgment_date.year - 1)

    def after_insert(self):
        if self.status == "Acknowledged":
            self.update_employee_compliance_status()

    def update_employee_compliance_status(self):
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.compliance_status:
            employee.compliance_status = {}
        
        employee.compliance_status[self.policy_name] = {
            "status": "Compliant",
            "acknowledged_date": self.acknowledgment_date,
            "expiry_date": self.expiry_date
        }
        employee.save()