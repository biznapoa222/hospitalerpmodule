from frappe.model.document import Document
import frappe

class ClinicalProcedure(Document):
    def before_insert(self):
        if not self.procedure_name and self.procedure_template:
            template = frappe.get_cached_doc("Clinical Procedure Template", self.procedure_template)
            self.procedure_name = f"{template.template_name} - {frappe.utils.nowdate()}"
