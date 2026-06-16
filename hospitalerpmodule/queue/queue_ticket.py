from frappe.model.document import Document
import frappe
from datetime import datetime

class QueueTicket(Document):
    def before_insert(self):
        self.generate_ticket_number()
        self.set_issued_time()
        self.set_service_type_defaults()

    def generate_ticket_number(self):
        if not self.ticket_number:
            service_type = frappe.get_doc("Queue Service Type", self.queue_service_type)
            prefix = service_type.prefix or "TK"
            today = frappe.utils.today()
            count = frappe.db.count("Queue Ticket", {
                "queue_service_type": self.queue_service_type,
                "token_issued_date": today
            }) + 1
            self.ticket_number = f"{prefix}-{count:04d}"

    def set_issued_time(self):
        if not self.token_issued_time:
            self.token_issued_time = frappe.utils.nowtime()
        if not self.token_issued_date:
            self.token_issued_date = frappe.utils.today()

    def set_service_type_defaults(self):
        if self.queue_service_type:
            st = frappe.get_cached_doc("Queue Service Type", self.queue_service_type)
            if st.department and not self.department:
                self.department = st.department

    def validate(self):
        self.calculate_waiting_time()
        self.validate_duplicate_ticket()

    def calculate_waiting_time(self):
        if self.status == "Waiting" and self.token_issued_time:
            try:
                issued = datetime.strptime(str(self.token_issued_time), "%H:%M:%S")
                now = datetime.strptime(str(frappe.utils.nowtime()), "%H:%M:%S")
                diff = (now - issued).seconds // 60
                self.waiting_time_minutes = diff
            except Exception:
                pass

    def validate_duplicate_ticket(self):
        if self.patient and self.token_issued_date:
            existing = frappe.db.exists("Queue Ticket", {
                "patient": self.patient,
                "token_issued_date": self.token_issued_date,
                "status": ["in", ["Waiting", "Called", "In Consultation"]],
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(f"Patient already has active ticket: {existing}")

    def on_update(self):
        self.update_counter_status()
        self.update_appointment_status()

    def update_counter_status(self):
        if self.status in ["Called", "In Consultation"] and self.counter:
            frappe.db.set_value("Queue Counter", self.counter, {
                "currently_serving": self.name,
                "serving_token": self.ticket_number
            })

    def update_appointment_status(self):
        if self.appointment:
            status_map = {
                "Called": "Checked In",
                "In Consultation": "In Consultation",
                "Completed": "Completed",
                "Cancelled": "Cancelled",
                "No Show": "No Show"
            }
            apt_status = status_map.get(self.status)
            if apt_status:
                frappe.db.set_value("Patient Appointment", self.appointment, "status", apt_status)

    def on_trash(self):
        if self.token_issued_date == frappe.utils.today():
            frappe.throw("Cannot delete today's queue tickets. Cancel them instead.")
