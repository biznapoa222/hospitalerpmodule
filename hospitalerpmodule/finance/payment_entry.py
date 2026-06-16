from frappe.model.document import Document
import frappe
from datetime import datetime

class PaymentEntry(Document):
    def before_insert(self):
        self.validate_payment_details()
        self.generate_reference_number()

    def validate_payment_details(self):
        if self.amount <= 0:
            frappe.throw("Payment amount must be greater than zero")
        if self.party_type and self.party:
            if not frappe.db.exists(self.party_type, self.party):
                frappe.throw(f"{self.party_type} '{self.party}' does not exist")

    def generate_reference_number(self):
        if not self.reference_no:
            prefix = self.payment_type[:3].upper()
            count = frappe.db.count("Payment Entry", {
                "payment_type": self.payment_type,
                "posting_date": [">=", frappe.utils.month_start()]
            })
            self.reference_no = f"{prefix}{datetime.now().year}{count:04d}"

    def validate(self):
        self.validate_payment_details()
        if self.status == "Approved" and not self.approved_by:
            frappe.throw("Payment must be approved by someone")

    def after_insert(self):
        if self.status == "Approved":
            self.process_payment()

    def process_payment(self):
        if self.payment_type == "Pay":
            self.update_supplier_balance()
        elif self.payment_type == "Receive":
            self.update_customer_balance()
        elif self.payment_type == "Transfer":
            self.transfer_between_accounts()

    def update_supplier_balance(self):
        supplier = frappe.get_doc("Supplier", self.party)
        if not supplier.balance:
            supplier.balance = 0
        supplier.balance -= self.amount
        supplier.save()

    def update_customer_balance(self):
        customer = frappe.get_doc("Customer", self.party)
        if not customer.balance:
            customer.balance = 0
        customer.balance += self.amount
        customer.save()

    def transfer_between_accounts(self):
        # Implement transfer logic between accounts
        pass

    def before_save(self):
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()

    def after_payment_cleared(self):
        if self.status == "Cleared":
            self.update_bank_balance()