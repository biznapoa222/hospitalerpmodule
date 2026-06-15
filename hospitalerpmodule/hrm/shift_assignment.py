from frappe.model.document import Document

class ShiftAssignment(Document):
    def before_insert(self):
        self.validate_shift_assignment()

    def validate_shift_assignment(self):
        if self.shift_date and self.shift_type:
            existing_assignment = frappe.db.exists(
                "Shift Assignment",
                {
                    "employee": self.employee,
                    "shift_date": self.shift_date,
                    "name": ["!=", self.name] if self.name else None
                }
            )
            if existing_assignment:
                frappe.throw("Shift already assigned for this employee on this date")

    def validate(self):
        self.validate_shift_assignment()
        if self.clock_in_time and self.clock_out_time:
            if self.clock_out_time <= self.clock_in_time:
                frappe.throw("Clock out time must be after clock in time")

    def after_insert(self):
        self.calculate_shift_details()

    def calculate_shift_details(self):
        if self.clock_in_time and self.clock_out_time:
            from datetime import datetime, timedelta
            clock_in = datetime.combine(datetime.today(), self.clock_in_time)
            clock_out = datetime.combine(datetime.today(), self.clock_out_time)
            total_hours = (clock_out - clock_in).total_seconds() / 3600
            self.total_hours_worked = total_hours

            # Calculate overtime
            shift_type = frappe.get_doc("Shift Type", self.shift_type)
            if shift_type.overtime_allowed and shift_type.working_hours:
                overtime_threshold = shift_type.working_hours
                if total_hours > overtime_threshold:
                    overtime_rate = shift_type.overtime_rate or 1.5
                    self.overtime_hours = (total_hours - overtime_threshold) * overtime_rate
                else:
                    self.overtime_hours = 0

    def before_save(self):
        self.calculate_shift_details()