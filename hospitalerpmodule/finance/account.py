from frappe.model.document import Document
import frappe
from datetime import datetime

class Account(Document):
    def before_insert(self):
        self.validate_account_structure()
        self.generate_account_code()
        self.set_initial_balance()

    def validate_account_structure(self):
        if self.parent_account and self.is_group:
            parent = frappe.get_doc("Account", self.parent_account)
            if not parent.is_group:
                frappe.throw("Parent account must be a group account")

    def generate_account_code(self):
        if not self.account_code and self.account_name:
            # Generate a simple account code based on account type and name
            type_prefix = {"Asset": "1", "Liability": "2", "Equity": "3", "Income": "4", "Expense": "5"}
            prefix = type_prefix.get(self.account_type, "0")
            name_part = self.account_name[:3].upper()
            count = frappe.db.count("Account") + 1
            self.account_code = f"{prefix}{name_part}{count:03d}"

    def set_initial_balance(self):
        if self.opening_balance and self.account_type in ["Asset", "Expense"]:
            # Debit balance
            self.current_debit = self.opening_balance
        elif self.account_type in ["Liability", "Equity", "Income"]:
            # Credit balance
            self.current_credit = self.opening_balance

    def validate(self):
        self.validate_account_structure()
        if self.parent_account == self.name:
            frappe.throw("Account cannot be its own parent")

    def after_insert(self):
        self.update_parent_account_balances()

    def update_parent_account_balances(self):
        if self.parent_account:
            parent = frappe.get_doc("Account", self.parent_account)
            if parent.is_group:
                parent.current_debit = (parent.current_debit or 0) + (self.current_debit or 0)
                parent.current_credit = (parent.current_credit or 0) + (self.current_credit or 0)
                parent.save()

    def before_save(self):
        self.calculate_balance()

    def calculate_balance(self):
        if self.account_type in ["Asset", "Expense"]:
            # Debit balance
            self.balance = self.current_debit - (self.current_credit or 0)
        else:
            # Credit balance
            self.balance = self.current_credit - (self.current_debit or 0)