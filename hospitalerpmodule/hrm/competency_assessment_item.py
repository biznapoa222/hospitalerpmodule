from frappe.model.document import Document
import frappe
from datetime import datetime

class CompetencyAssessmentItem(Document):
    def before_insert(self):
        self.validate_assessment_item()
        self.calculate_score_percentage()

    def validate_assessment_item(self):
        if self.assessment_date and self.assessment_date > frappe.utils.today():
            frappe.throw("Assessment date cannot be in the future")
        if self.current_level == "Expert" and self.target_level:
            frappe.throw("Cannot set target level for an expert competency")

    def calculate_score_percentage(self):
        if self.score and self.max_score and self.max_score > 0:
            self.score_percentage = (self.score / self.max_score) * 100

    def validate(self):
        self.validate_assessment_item()
        if self.status == "Completed":
            self.update_competency_record()

    def update_competency_record(self):
        if self.parent and self.parenttype and self.competency_name:
            competency = frappe.new_doc("Competency")
            competency.employee = frappe.db.get_value(self.parenttype, self.parent, "employee")
            competency.competency_name = self.competency_name
            competency.competency_type = "Technical"  # Default, could be made configurable
            competency.current_level = self.current_level
            competency.target_level = self.target_level
            competency.assessment_date = self.assessment_date
            competency.assessor = self.assessor
            competency.score = self.score
            competency.max_score = self.max_score
            competency.comments = self.comments
            competency.next_steps = self.next_steps
            competency.training_required = self.training_required
            competency.insert()