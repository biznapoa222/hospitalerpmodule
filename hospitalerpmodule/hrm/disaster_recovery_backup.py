from frappe.model.document import Document
import frappe
from datetime import datetime, timedelta
import hashlib
import os

class DisasterRecoveryBackup(Document):
    def before_insert(self):
        self.generate_backup_checksum()
        self.calculate_expiry_date()
        self.schedule_next_backup()

    def generate_backup_checksum(self):
        if self.backup_file:
            file_path = frappe.get_site_path("public", self.backup_file)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    self.backup_checksum = file_hash

    def calculate_expiry_date(self):
        if self.backup_date and self.retention_period:
            self.expiry_date = self.backup_date + timedelta(days=self.retention_period)

    def schedule_next_backup(self):
        if self.backup_schedule == "Daily":
            self.next_backup_date = self.backup_date + timedelta(days=1)
        elif self.backup_schedule == "Weekly":
            self.next_backup_date = self.backup_date + timedelta(days=7)
        elif self.backup_schedule == "Monthly":
            import calendar
            next_month = self.backup_date.month + 1
            next_year = self.backup_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            last_day = calendar.monthrange(next_year, next_month)[1]
            self.next_backup_date = self.backup_date.replace(month=next_month, year=next_year, day=min(self.backup_date.day, last_day))
        elif self.backup_schedule == "Custom":
            self.next_backup_date = self.backup_date + timedelta(days=30)

    def validate(self):
        self.validate_backup_schedule()
        if self.backup_status == "Completed" and not self.verification_status:
            self.verify_backup()

    def validate_backup_schedule(self):
        if self.backup_schedule == "Custom" and not self.next_backup_date:
            frappe.throw("Next backup date is required for Custom schedule")

    def verify_backup(self):
        if self.backup_file:
            file_path = frappe.get_site_path("public", self.backup_file)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    if file_hash == self.backup_checksum:
                        self.verification_status = "Verified"
                        self.verification_date = frappe.utils.today()
                    else:
                        self.verification_status = "Failed"
                        frappe.throw("Backup verification failed - checksum mismatch")

    def after_insert(self):
        if self.backup_status == "Completed":
            self.cleanup_expired_backups()

    def cleanup_expired_backups(self):
        if self.expiry_date and self.expiry_date < frappe.utils.today():
            frappe.db.delete("Disaster Recovery Backup", {
                "name": self.name,
                "expiry_date": ["<", frappe.utils.today()]
            })