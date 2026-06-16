from frappe.model.document import Document
import frappe
from datetime import datetime

class Item(Document):
    def before_insert(self):
        self.validate_item_details()
        self.generate_item_code()

    def validate_item_details(self):
        if self.selling_unit_price < self.purchase_unit_price:
            frappe.throw("Selling price cannot be less than purchase price")
        if self.reorder_level > self.maximum_level:
            frappe.throw("Reorder level cannot be greater than maximum level")

    def generate_item_code(self):
        if not self.item_code and self.item_name:
            prefix = self.item_type[:3].upper()
            count = frappe.db.count("Item") + 1
            self.item_code = f"{prefix}{count:04d}"

    def validate(self):
        self.validate_item_details()

    def after_insert(self):
        self.create_initial_stock_entry()

    def create_initial_stock_entry(self):
        if self.current_stock and self.current_stock > 0:
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.item = self.name
            stock_entry.qty = self.current_stock
            stock_entry.warehouse = self.warehouse
            stock_entry.purpose = "Material Receipt"
            stock_entry.insert()

    def before_save(self):
        if self.current_stock != frappe.db.get_value("Item", self.name, "current_stock"):
            self.update_stock_levels()