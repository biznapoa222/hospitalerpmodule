from frappe.model.document import Document
import frappe
from datetime import datetime

class GeneralLedger(Document):
    def before_insert(self):
        self.validate_account_balance()
        self.generate_reference_number()

    def validate_account_balance(self):
        if self.account and self.amount:
            account = frappe.get_doc("Account", self.account)
            if not account.initialized:
                frappe.throw(f"Account {account.name} has not been initialized")

    def generate_reference_number(self):
        if not self.reference_name and self.reference_type:
            prefix = self.reference_type[:3].upper()
            count = frappe.db.count("General Ledger", {
                "reference_type": self.reference_type,
                "posting_date": [">=", frappe.utils.month_start()]
            })
            self.reference_name = f"{prefix}{datetime.now().year}{count:04d}"

    def validate(self):
        self.validate_account_balance()
        if self.status == "Posted" and not self.approved_by:
            frappe.throw("General Ledger entry must be approved before posting")

    def after_insert(self):
        if self.status == "Posted":
            self.update_account_balances()

    def update_account_balances(self):
        if self.debit_account:
            debit_account = frappe.get_doc("Account", self.debit_account)
            debit_account.current_debit = (debit_account.current_debit or 0) + self.amount
            debit_account.save()

        if self.credit_account:
            credit_account = frappe.get_doc("Account", self.credit_account)
            credit_account.current_credit = (credit_account.current_credit or 0) + self.amount
            credit_account.save()

    def before_save(self):
        if self.status == "Cancelled" and not self.cancel_reason:
            frappe.throw("Cancel reason is required to cancel a transaction")