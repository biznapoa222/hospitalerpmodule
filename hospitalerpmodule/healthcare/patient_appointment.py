from frappe.model.document import Document
import frappe

class PatientAppointment(Document):
    def before_insert(self):
        self.generate_appointment_code()
        self.validate_availability()

    def generate_appointment_code(self):
        if not self.appointment_code:
            today = frappe.utils.today()
            count = frappe.db.count("Patient Appointment", {
                "appointment_date": today
            }) + 1
            date_str = frappe.utils.formatdate(today, "ddMMyyyy")
            self.appointment_code = f"APT-{date_str}-{count:04d}"

    def validate(self):
        self.validate_appointment_time()
        self.set_duration_from_type()

    def validate_appointment_time(self):
        if not self.appointment_date or not self.appointment_time:
            frappe.throw("Appointment date and time are required")

    def set_duration_from_type(self):
        if self.appointment_type and not self.duration:
            apt_type = frappe.get_cached_doc("Appointment Type", self.appointment_type)
            self.duration = apt_type.duration

    def validate_availability(self):
        if not self.practitioner or not self.appointment_date:
            return
        existing = frappe.db.count("Patient Appointment", {
            "practitioner": self.practitioner,
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time,
            "status": ["!=", "Cancelled"],
            "name": ["!=", self.name]
        })
        if existing:
            frappe.throw(f"Time slot already booked for {self.appointment_time}")

    def on_update(self):
        self.update_queue_ticket()

    def update_queue_ticket(self):
        if self.status == "Cancelled" and self.get_doc_before_save():
            old = self.get_doc_before_save()
            if old.status != "Cancelled":
                queue_tickets = frappe.get_all("Queue Ticket", {
                    "appointment": self.name,
                    "status": "Waiting"
                })
                for qt in queue_tickets:
                    frappe.db.set_value("Queue Ticket", qt.name, "status", "Cancelled")

    def after_insert(self):
        self.create_queue_ticket()

    def create_queue_ticket(self):
        if frappe.db.get_single_value("Queue Settings", "enable_queue_management"):
            queue_ticket = frappe.new_doc("Queue Ticket")
            queue_ticket.patient = self.patient
            queue_ticket.patient_name = self.patient_name
            queue_ticket.appointment = self.name
            queue_ticket.practitioner = self.practitioner
            queue_ticket.department = self.department
            queue_ticket.priority = "Emergency" if self.is_emergency else "Normal"
            queue_ticket.status = "Waiting"
            queue_ticket.token_issued_date = self.appointment_date
            queue_ticket.insert(ignore_permissions=True)
