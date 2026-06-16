from frappe.model.document import Document
import frappe

class PatientEncounter(Document):
    def before_insert(self):
        self.generate_encounter_code()
        self.set_defaults()

    def generate_encounter_code(self):
        if not self.encounter_code:
            today = frappe.utils.today()
            count = frappe.db.count("Patient Encounter", {"encounter_date": today}) + 1
            date_str = frappe.utils.formatdate(today, "ddMMyyyy")
            self.encounter_code = f"ENC-{date_str}-{count:04d}"

    def set_defaults(self):
        if not self.encounter_date:
            self.encounter_date = frappe.utils.today()
        if not self.encounter_time:
            self.encounter_time = frappe.utils.nowtime()

    def validate(self):
        self.validate_practitioner()
        self.update_appointment_status()

    def validate_practitioner(self):
        if self.practitioner and not frappe.db.exists("Healthcare Practitioner", self.practitioner):
            frappe.throw("Invalid Healthcare Practitioner")

    def update_appointment_status(self):
        if self.appointment:
            frappe.db.set_value("Patient Appointment", self.appointment, "status", "Completed")

    def after_insert(self):
        self.update_queue_ticket()
        self.create_vital_signs_entry()

    def update_queue_ticket(self):
        if self.appointment:
            tickets = frappe.get_all("Queue Ticket", {
                "appointment": self.appointment,
                "status": ["in", ["Called", "In Consultation"]]
            })
            for t in tickets:
                frappe.db.set_value("Queue Ticket", t.name, {
                    "status": "Completed",
                    "consultation_end_time": frappe.utils.nowtime()
                })

    def create_vital_signs_entry(self):
        if not self.vital_signs:
            vitals = frappe.new_doc("Vital Signs")
            vitals.patient = self.patient
            vitals.encounter = self.name
            vitals.date = self.encounter_date
            vitals.time = self.encounter_time
            vitals.recorded_by = self.practitioner
            vitals.flags.ignore_permissions = True
            vitals.insert()
