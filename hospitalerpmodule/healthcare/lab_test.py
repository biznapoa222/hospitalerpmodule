from frappe.model.document import Document
import frappe

class LabTest(Document):
    def before_insert(self):
        if not self.test_name and self.lab_test_template:
            template = frappe.get_cached_doc("Lab Test Template", self.lab_test_template)
            self.test_name = template.test_name
    
    def validate(self):
        self.check_abnormal_results()
    
    def check_abnormal_results(self):
        if self.results:
            for row in self.results:
                if row.is_abnormal:
                    self.is_abnormal = 1
                    return
        self.is_abnormal = 0
    
    def on_update(self):
        if self.status == "Completed" and not self.result_date:
            self.result_date = frappe.utils.today()
            self.result_time = frappe.utils.nowtime()
