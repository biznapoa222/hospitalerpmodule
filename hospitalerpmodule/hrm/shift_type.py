from frappe.model.document import Document

class ShiftType(Document):
    def before_insert(self):
        self.validate_shift_timing()
        self.calculate_working_hours()

    def validate_shift_timing(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                frappe.throw("End time must be after start time")

    def calculate_working_hours(self):
        if self.start_time and self.end_time and self.break_duration:
            from datetime import datetime, timedelta
            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            total_hours = (end - start).total_seconds() / 3600
            self.working_hours = total_hours - (self.break_duration / 60)

    def validate(self):
        self.validate_shift_timing()
        if self.break_start_time and self.break_end_time:
            if self.break_end_time <= self.break_start_time:
                frappe.throw("Break end time must be after break start time")

    def after_insert(self):
        self.create_shift_assignments()

    def create_shift_assignments(self):
        # Create default shift assignments for employees
        employees = frappe.get_all("Employee", fields=["name"])
        for employee in employees:
            shift_assignment = frappe.new_doc("Shift Assignment")
            shift_assignment.employee = employee.name
            shift_assignment.shift_type = self.name
            shift_assignment.shift_date = frappe.utils.today()
            shift_assignment.insert()