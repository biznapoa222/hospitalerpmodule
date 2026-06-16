from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class AccountsPayable(Document):
    def before_insert(self):
        self.calculate_total_amount()
        self.validate_invoice_dates()
        self.check_payment_terms()

    def calculate_total_amount(self):
        self.total_amount = self.amount + self.tax_amount

    def validate_invoice_dates(self):
        if self.invoice_date and self.due_date:
            if self.due_date < self.invoice_date:
                frappe.throw("Due date cannot be before invoice date")
            if self.invoice_date > frappe.utils.today():
                frappe.throw("Invoice date cannot be in the future")

    def check_payment_terms(self):
        if self.payment_terms and self.due_date:
            if self.due_date < frappe.utils.today():
                frappe.throw("Invoice is past due")

    def validate(self):
        self.validate_invoice_dates()
        if self.status == "Paid" and not self.payment_date:
            self.payment_date = frappe.utils.today()
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()

    def after_insert(self):
        if self.status == "Approved":
            self.create_payment_entry()

    def create_payment_entry(self):
        if self.status == "Approved":
            payment = frappe.new_doc("Payment Entry")
            payment.payment_type = "Pay"
            payment.party_type = "Supplier"
            payment.party = self.supplier
            payment.amount = self.total_amount
            payment.posting_date = self.payment_date or frappe.utils.today()
            payment.mode_of_payment = self.payment_method
            payment.reference_no = self.invoice_number
            payment.reference_date = self.invoice_date
            payment.insert()

    def before_save(self):
        self.calculate_total_amount()

    def after_payment(self):
        if self.status == "Paid":
            self.update_supplier_balance()