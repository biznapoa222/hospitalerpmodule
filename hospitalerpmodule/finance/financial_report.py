from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta

class FinancialReport(Document):
    def before_insert(self):
        self.validate_report_parameters()
        self.generate_report()

    def validate_report_parameters(self):
        if self.report_type in ["Balance Sheet", "Income Statement", "Cash Flow Statement", "Trial Balance", "Profit & Loss"]:
            if not self.start_date or not self.end_date:
                frappe.throw("Start and end dates are required for financial statements")
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before start date")

    def generate_report(self):
        if self.status == "Draft" and self.report_name:
            if self.report_type == "Balance Sheet":
                self.generate_balance_sheet()
            elif self.report_type == "Income Statement":
                self.generate_income_statement()
            elif self.report_type == "Cash Flow Statement":
                self.generate_cash_flow_statement()
            elif self.report_type == "Trial Balance":
                self.generate_trial_balance()
            elif self.report_type == "Profit & Loss":
                self.generate_profit_loss()
            elif self.report_type == "Accounts Receivable Aging":
                self.generate_ar_aging()
            elif self.report_type == "Accounts Payable Aging":
                self.generate_ap_aging()
            elif self.report_type == "General Ledger":
                self.generate_general_ledger()

    def get_account_balance(self, account_name, as_on=None):
        filters = {"account": account_name}
        if as_on:
            filters["posting_date"] = ["<=", as_on]
        
        debit = frappe.db.get_all("General Ledger",
            filters={**filters, **{"debit_account": account_name}},
            fields=["COALESCE(SUM(amount), 0) as total"],
            pluck="total"
        ) or [0]
        
        credit = frappe.db.get_all("General Ledger",
            filters={**filters, **{"credit_account": account_name}},
            fields=["COALESCE(SUM(amount), 0) as total"],
            pluck="total"
        ) or [0]
        
        return float(debit[0]) - float(credit[0])

    def get_accounts_by_type(self, account_type):
        return frappe.get_all("Account",
            filters={"account_type": account_type, "is_group": 0},
            fields=["name", "account_name", "balance"]
        )

    def generate_balance_sheet(self):
        assets = self.get_accounts_by_type("Asset")
        liabilities = self.get_accounts_by_type("Liability")
        equity = self.get_accounts_by_type("Equity")
        
        total_assets = sum(a.get("balance", 0) or 0 for a in assets)
        total_liabilities = sum(l.get("balance", 0) or 0 for l in liabilities)
        total_equity = sum(e.get("balance", 0) or 0 for e in equity)
        
        report_data = {
            "report_type": "Balance Sheet",
            "as_on": self.end_date,
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "total_liabilities_equity": total_liabilities + total_equity
        }
        
        report_html = self.render_balance_sheet_html(report_data)
        self.report_file = report_html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def render_balance_sheet_html(self, data):
        html = f"""
        <h2>Balance Sheet</h2>
        <p>As on: {data['as_on']}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Assets</th><th style='text-align:right'>Amount</th></tr>
        """
        for a in data['assets']:
            html += f"<tr><td>{a['account_name']}</td><td style='text-align:right'>{a.get('balance', 0):,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total Assets</td><td style='text-align:right'>{data['total_assets']:,.2f}</td></tr>"
        html += f"<tr style='background:#f0f0f0'><th>Liabilities</th><th style='text-align:right'>Amount</th></tr>"
        for l in data['liabilities']:
            html += f"<tr><td>{l['account_name']}</td><td style='text-align:right'>{l.get('balance', 0):,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total Liabilities</td><td style='text-align:right'>{data['total_liabilities']:,.2f}</td></tr>"
        html += f"<tr style='background:#f0f0f0'><th>Equity</th><th style='text-align:right'>Amount</th></tr>"
        for e in data['equity']:
            html += f"<tr><td>{e['account_name']}</td><td style='text-align:right'>{e.get('balance', 0):,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total Equity</td><td style='text-align:right'>{data['total_equity']:,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold;background:#e8f5e9'><td>Total Liabilities + Equity</td><td style='text-align:right'>{data['total_liabilities_equity']:,.2f}</td></tr>"
        html += "</table>"
        return html

    def generate_income_statement(self):
        income = self.get_accounts_by_type("Income")
        expenses = self.get_accounts_by_type("Expense")
        
        total_income = sum(i.get("balance", 0) or 0 for i in income)
        total_expenses = sum(e.get("balance", 0) or 0 for e in expenses)
        net_income = total_income - total_expenses
        
        html = f"""
        <h2>Income Statement</h2>
        <p>Period: {self.start_date} to {self.end_date}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Income</th><th style='text-align:right'>Amount</th></tr>
        """
        for i in income:
            html += f"<tr><td>{i['account_name']}</td><td style='text-align:right'>{i.get('balance', 0):,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total Income</td><td style='text-align:right'>{total_income:,.2f}</td></tr>"
        html += f"<tr style='background:#f0f0f0'><th>Expenses</th><th style='text-align:right'>Amount</th></tr>"
        for e in expenses:
            html += f"<tr><td>{e['account_name']}</td><td style='text-align:right'>{e.get('balance', 0):,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total Expenses</td><td style='text-align:right'>{total_expenses:,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold;background:#e8f5e9'><td>Net Income</td><td style='text-align:right'>{net_income:,.2f}</td></tr>"
        html += "</table>"
        
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def generate_trial_balance(self):
        accounts = frappe.get_all("Account",
            filters={"is_group": 0},
            fields=["name", "account_name", "balance"]
        )
        
        total_debit = sum(a.get("balance", 0) or 0 for a in accounts if (a.get("balance", 0) or 0) > 0)
        total_credit = sum(abs(a.get("balance", 0) or 0) for a in accounts if (a.get("balance", 0) or 0) < 0)
        
        html = f"""
        <h2>Trial Balance</h2>
        <p>As on: {self.end_date}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Account</th><th style='text-align:right'>Debit</th><th style='text-align:right'>Credit</th></tr>
        """
        for a in accounts:
            bal = a.get("balance", 0) or 0
            debit = bal if bal > 0 else 0
            credit = abs(bal) if bal < 0 else 0
            html += f"<tr><td>{a['account_name']}</td><td style='text-align:right'>{debit:,.2f}</td><td style='text-align:right'>{credit:,.2f}</td></tr>"
        html += f"<tr style='font-weight:bold'><td>Total</td><td style='text-align:right'>{total_debit:,.2f}</td><td style='text-align:right'>{total_credit:,.2f}</td></tr>"
        html += "</table>"
        
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def generate_profit_loss(self):
        self.generate_income_statement()

    def generate_ar_aging(self):
        receivables = frappe.get_all("Accounts Receivable",
            fields=["customer", "invoice_number", "invoice_date", "due_date", "total_amount", "status"],
            filters={"status": ["!=", "Paid"]},
            order_by="due_date asc"
        )
        
        html = f"""
        <h2>Accounts Receivable Aging</h2>
        <p>As on: {self.end_date}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Customer</th><th>Invoice</th><th>Date</th><th>Due Date</th><th>Amount</th><th>Days Overdue</th><th>Status</th></tr>
        """
        for r in receivables:
            due = r.get("due_date") or frappe.utils.today()
            days = frappe.utils.date_diff(self.end_date, due)
            html += f"<tr><td>{r['customer']}</td><td>{r['invoice_number']}</td><td>{r['invoice_date']}</td><td>{r['due_date']}</td>"
            html += f"<td style='text-align:right'>{r['total_amount']:,.2f}</td><td style='text-align:right'>{days}</td><td>{r['status']}</td></tr>"
        html += "</table>"
        
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def generate_ap_aging(self):
        payables = frappe.get_all("Accounts Payable",
            fields=["supplier", "invoice_number", "invoice_date", "due_date", "total_amount", "status"],
            filters={"status": ["!=", "Paid"]},
            order_by="due_date asc"
        )
        
        html = f"""
        <h2>Accounts Payable Aging</h2>
        <p>As on: {self.end_date}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Supplier</th><th>Invoice</th><th>Date</th><th>Due Date</th><th>Amount</th><th>Days Overdue</th><th>Status</th></tr>
        """
        for p in payables:
            due = p.get("due_date") or frappe.utils.today()
            days = frappe.utils.date_diff(self.end_date, due)
            html += f"<tr><td>{p['supplier']}</td><td>{p['invoice_number']}</td><td>{p['invoice_date']}</td><td>{p['due_date']}</td>"
            html += f"<td style='text-align:right'>{p['total_amount']:,.2f}</td><td style='text-align:right'>{days}</td><td>{p['status']}</td></tr>"
        html += "</table>"
        
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def generate_cash_flow_statement(self):
        html = f"""
        <h2>Cash Flow Statement</h2>
        <p>Period: {self.start_date} to {self.end_date}</p>
        <p>Cash flow statement generation based on General Ledger entries.</p>
        """
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def generate_general_ledger(self):
        entries = frappe.get_all("General Ledger",
            fields=["posting_date", "debit_account", "credit_account", "amount", "description", "reference_name"],
            filters={"posting_date": ["between", [self.start_date, self.end_date]]},
            order_by="posting_date"
        )
        
        html = f"""
        <h2>General Ledger</h2>
        <p>Period: {self.start_date} to {self.end_date}</p>
        <table border='1' cellpadding='8' style='width:100%;border-collapse:collapse'>
            <tr style='background:#f0f0f0'><th>Date</th><th>Debit Account</th><th>Credit Account</th><th style='text-align:right'>Amount</th><th>Reference</th><th>Description</th></tr>
        """
        for e in entries:
            html += f"<tr><td>{e['posting_date']}</td><td>{e['debit_account']}</td><td>{e['credit_account']}</td>"
            html += f"<td style='text-align:right'>{e['amount']:,.2f}</td><td>{e['reference_name'] or ''}</td><td>{e.get('description', '')}</td></tr>"
        html += "</table>"
        
        self.report_file = html
        self.status = "Generated"
        self.generated_on = frappe.utils.today()

    def validate(self):
        self.validate_report_parameters()
        if self.status == "Generated" and not self.generated_on:
            self.generated_on = frappe.utils.today()

    def after_insert(self):
        if self.status == "Generated":
            self.email_report_if_requested()

    def email_report_if_requested(self):
        if self.email_report and self.email_addresses:
            pass

    def before_save(self):
        if self.status == "Generated" and not self.generated_on:
            self.generated_on = frappe.utils.today()
