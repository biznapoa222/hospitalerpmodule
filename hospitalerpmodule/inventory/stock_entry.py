from frappe.model.document import Document
import frappe
from datetime import datetime

class StockEntry(Document):
    def before_insert(self):
        self.validate_stock_entry()

    def validate_stock_entry(self):
        if self.stock_entry_type == "Transfer":
            if not self.items or len(self.items) < 2:
                frappe.throw("Transfer stock entry must have at least two items")

    def validate(self):
        self.validate_stock_entry()
        if self.status == "Approved" and not self.approved_by:
            frappe.throw("Stock entry must be approved before completion")

    def after_insert(self):
        if self.status == "Approved":
            self.process_stock_entry()

    def process_stock_entry(self):
        for item in self.items:
            if item.item:
                self.update_item_stock(item.item, item.qty, item.warehouse)

    def update_item_stock(self, item_name, qty, warehouse):
        item = frappe.get_doc("Item", item_name)
        if not item.current_stock:
            item.current_stock = 0
        
        if self.stock_entry_type in ["Material Receipt", "Production"]:
            item.current_stock += qty
        elif self.stock_entry_type in ["Material Issue", "Transfer", "Scrap"]:
            if item.current_stock >= qty:
                item.current_stock -= qty
            else:
                frappe.throw(f"Insufficient stock for item {item.item_name}")
        
        item.save()

    def before_save(self):
        if self.status == "Completed" and not self.approved_on:
            self.approved_on = frappe.utils.today()