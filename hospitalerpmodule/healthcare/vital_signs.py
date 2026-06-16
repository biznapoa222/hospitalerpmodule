from frappe.model.document import Document
import frappe

class VitalSigns(Document):
    def validate(self):
        self.calculate_bmi()

    def calculate_bmi(self):
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100
            self.bmi = round(self.weight / (height_m * height_m), 1)

    def before_insert(self):
        if not self.date:
            self.date = frappe.utils.today()
        if not self.time:
            self.time = frappe.utils.nowtime()
