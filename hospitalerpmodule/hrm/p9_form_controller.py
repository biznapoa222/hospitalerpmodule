from frappe.model.document import Document
import frappe
from datetime import datetime

class P9Form(Document):
    def before_insert(self):
        self.calculate_gross_pay()
        self.calculate_taxable_income()
        self.calculate_paye()
        self.calculate_sha()
        self.calculate_housing_levy()
        self.calculate_net_pay()
        self.generate_form_url()

    def calculate_gross_pay(self):
        self.gross_pay = self.basic_salary + self.allowances

    def calculate_taxable_income(self):
        self.taxable_income = self.gross_pay

    def calculate_paye(self):
        taxable_income = self.taxable_income
        
        # Kenya PAYE tax bands (2024)
        if taxable_income <= 12298:
            self.paye = 0
        elif taxable_income <= 23885:
            self.paye = (taxable_income - 12298) * 0.1
        elif taxable_income <= 35472:
            self.paye = 11587 * 0.1 + (taxable_income - 23885) * 0.25
        elif taxable_income <= 47059:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + (taxable_income - 35472) * 0.3
        elif taxable_income <= 58646:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + 11587 * 0.3 + (taxable_income - 47059) * 0.325
        elif taxable_income <= 70233:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + 11587 * 0.3 + 11587 * 0.325 + (taxable_income - 58646) * 0.35
        elif taxable_income <= 81820:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + 11587 * 0.3 + 11587 * 0.325 + 11587 * 0.35 + (taxable_income - 70233) * 0.375
        elif taxable_income <= 93407:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + 11587 * 0.3 + 11587 * 0.325 + 11587 * 0.35 + 11587 * 0.375 + (taxable_income - 81820) * 0.4
        else:
            self.paye = 11587 * 0.1 + 11587 * 0.25 + 11587 * 0.3 + 11587 * 0.325 + 11587 * 0.35 + 11587 * 0.375 + 11587 * 0.4 + (taxable_income - 93407) * 0.45

    def calculate_sha(self):
        # SHA contribution: 7.5% of basic salary (capped at 750,000 KES)
        sha_rate = 0.075
        max_sha_base = 750000
        sha_base = min(self.basic_salary, max_sha_base)
        self.sha = sha_base * sha_rate

    def calculate_housing_levy(self):
        # Housing Levy: 2.75% for employees earning > 50,000 KES
        if self.basic_salary > 50000:
            self.housing_levy = self.basic_salary * 0.0275
        else:
            self.housing_levy = 0

    def calculate_net_pay(self):
        self.net_pay = self.gross_pay - self.paye - self.sha - self.housing_levy

    def generate_form_url(self):
        self.form_url = f"/app/p9-form/{self.name}"

    def validate(self):
        if self.basic_salary < 0:
            frappe.throw("Basic salary cannot be negative")
        if self.allowances < 0:
            frappe.throw("Allowances cannot be negative")
        if not self.tax_year.isdigit() or len(self.tax_year) != 4:
            frappe.throw("Tax year must be a 4-digit number")