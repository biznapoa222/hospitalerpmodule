import frappe

def before_install():
    pass

def after_install():
    create_healthcare_settings()

def create_healthcare_settings():
    if not frappe.db.exists("Healthcare Settings"):
        settings = frappe.new_doc("Healthcare Settings")
        settings.disable = 0
        settings.insert()
