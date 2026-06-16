from frappe.model.document import Document
import frappe
from datetime import date

class Patient(Document):
    def before_insert(self):
        self.generate_patient_code()
        self.set_registration_date()

    def generate_patient_code(self):
        if not self.patient_code:
            year = date.today().strftime("%Y")
            month = date.today().strftime("%m")
            count = frappe.db.count("Patient") + 1
            self.patient_code = f"PAT-{year}{month}-{count:04d}"

    def set_registration_date(self):
        if not self.registration_date:
            self.registration_date = frappe.utils.today()

    def validate(self):
        self.calculate_age()
        self.validate_phone()
        self.validate_email()

    def calculate_age(self):
        if self.date_of_birth:
            dob = frappe.utils.getdate(self.date_of_birth)
            today = frappe.utils.today()
            delta = frappe.utils.date_diff(today, dob)
            years = delta // 365
            months = (delta % 365) // 30
            if years > 0:
                self.age = f"{years} yr {months} mo"
            else:
                self.age = f"{months} mo"

    def validate_phone(self):
        if self.phone:
            phone = self.phone.strip()
            if not phone.isdigit():
                frappe.throw("Phone number must contain only digits")

    def validate_email(self):
        if self.email and "@" not in self.email:
            frappe.throw("Invalid email address")

    def after_insert(self):
        self.create_customer_link()

    def create_customer_link(self):
        if frappe.db.exists("DocType", "Customer"):
            if not frappe.db.exists("Customer", {"customer_name": self.patient_name}):
                try:
                    customer = frappe.new_doc("Customer")
                    customer.customer_name = self.patient_name
                    customer.customer_type = "Individual"
                    customer.mobile_no = self.phone
                    customer.email_id = self.email
                    customer.insert(ignore_permissions=True)
                except Exception:
                    pass
