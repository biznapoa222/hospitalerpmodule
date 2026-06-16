import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Encounter Date"), "fieldname": "encounter_date", "fieldtype": "Date", "width": 120},
        {"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 150},
        {"label": _("Patient Name"), "fieldname": "patient_name", "fieldtype": "Data", "width": 150},
        {"label": _("Practitioner"), "fieldname": "practitioner", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 180},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Medical Department", "width": 150},
        {"label": _("Type"), "fieldname": "type", "fieldtype": "Data", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Billing Status"), "fieldname": "billing_status", "fieldtype": "Data", "width": 100},
        {"label": _("Follow Up Date"), "fieldname": "follow_up_date", "fieldtype": "Date", "width": 100}
    ]

    filters = filters or {}
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND encounter_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND encounter_date <= '{filters['to_date']}'"
    if filters.get("practitioner"):
        conditions += f" AND practitioner = '{filters['practitioner']}'"
    if filters.get("department"):
        conditions += f" AND department = '{filters['department']}'"
    if filters.get("type"):
        conditions += f" AND type = '{filters['type']}'"

    query = f"""
        SELECT
            encounter_date,
            patient,
            patient_name,
            practitioner,
            department,
            type,
            status,
            billing_status,
            follow_up_date
        FROM `tabPatient Encounter`
        WHERE {conditions}
        ORDER BY encounter_date DESC
    """

    data = frappe.db.sql(query, as_dict=1)

    chart = {
        "data": {
            "labels": ["OPD", "IPD", "Emergency", "Follow Up", "Telemedicine"],
            "datasets": [
                {
                    "name": "Encounters by Type",
                    "values": [
                        frappe.db.count("Patient Encounter", {"type": "OPD"}),
                        frappe.db.count("Patient Encounter", {"type": "IPD"}),
                        frappe.db.count("Patient Encounter", {"type": "Emergency"}),
                        frappe.db.count("Patient Encounter", {"type": "Follow Up"}),
                        frappe.db.count("Patient Encounter", {"type": "Telemedicine"})
                    ]
                }
            ]
        },
        "type": "bar",
        "height": 250,
        "colors": ["#3b82f6"]
    }

    return columns, data, None, chart
