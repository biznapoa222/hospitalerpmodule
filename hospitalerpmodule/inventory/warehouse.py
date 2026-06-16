from frappe.model.document import Document
import frappe
from datetime import datetime

class Warehouse(Document):
    def before_insert(self):
        self.generate_warehouse_code()

    def generate_warehouse_code(self):
        if not self.warehouse_code and self.warehouse_name:
            prefix = "WH"
            count = frappe.db.count("Warehouse") + 1
            self.warehouse_code = f"{prefix}{count:03d}"

    def validate(self):
        if self.warehouse_name and self.location:
            existing = frappe.db.exists("Warehouse", {
                "warehouse_name": self.warehouse_name,
                "location": self.location,
                "name": ["!=", self.name] if self.name else None
            })
            if existing:
                frappe.throw("Warehouse with this name and location already exists")