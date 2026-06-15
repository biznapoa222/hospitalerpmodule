from frappe.model.document import Document
import frappe
from datetime import datetime

class Competency(Document):
    def before_insert(self):
        self.validate_assessment_date()
        self.calculate_score_percentage()

    def validate_assessment_date(self):
        if self.assessment_date and self.assessment_date > frappe.utils.today():
            frappe.throw("Assessment date cannot be in the future")

    def calculate_score_percentage(self):
        if self.score and self.max_score and self.max_score > 0:
            self.score_percentage = (self.score / self.max_score) * 100

    def validate(self):
        self.validate_assessment_date()
        if self.current_level == "Expert" and self.target_level:
            frappe.throw("Cannot set target level for an expert competency")

    def after_insert(self):
        self.update_employee_competency_summary()

    def update_employee_competency_summary(self):
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.competency_summary:
            employee.competency_summary = {}
        
        if self.competency_type not in employee.competency_summary:
            employee.competency_summary[self.competency_type] = {
                "total": 0,
                "expert_count": 0,
                "advanced_count": 0,
                "intermediate_count": 0,
                "beginner_count": 0
            }
        
        employee.competency_summary[self.competency_type]["total"] += 1
        employee.competency_summary[self.competency_type][f"{self.current_level.lower()}_count"] += 1
        employee.save()