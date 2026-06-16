from frappe.model.document import Document
import frappe
from datetime import datetime

class PurchaseOrder(Document):
    def before_insert(self):
        self.generate_po_number()
        self.validate_order_dates()

    def generate_po_number(self):
        if not self.po_number:
            prefix = "PO"
            count = frappe.db.count("Purchase Order", {
                "order_date": [">=", frappe.utils.month_start()]
            }) + 1
            self.po_number = f"{prefix}{datetime.now().year}{count:04d}"

    def validate_order_dates(self):
        if self.order_date and self.expected_delivery_date:
            if self.expected_delivery_date < self.order_date:
                frappe.throw("Expected delivery date cannot be before order date")

    def validate(self):
        self.validate_order_dates()
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()

    def after_insert(self):
        if self.status == "Approved":
            self.create_stock_entries()

    def create_stock_entries(self):
        if self.status == "Approved":
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.stock_entry_type = "Material Receipt"
            stock_entry.posting_date = frappe.utils.today()
            stock_entry.reference_name = self.name
            stock_entry.purpose = "Material Receipt"
            stock_entry.status = "Draft"
            
            for item in self.items:
                if item.item and item.qty:
                    stock_item = frappe.new_doc("Stock Entry Item")
                    stock_item.item = item.item
                    stock_item.qty = item.qty
                    stock_item.warehouse = frappe.db.get_value("Item", item.item, "warehouse")
                    stock_entry.append("items", stock_item)
            
            stock_entry.insert()

    def before_save(self):
        if self.status == "Completed" and not self.approved_on:
            self.approved_on = frappe.utils.today()