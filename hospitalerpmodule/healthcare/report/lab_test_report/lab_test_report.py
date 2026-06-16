import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Test Name"), "fieldname": "test_name", "fieldtype": "Data", "width": 180},
        {"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 150},
        {"label": _("Patient Name"), "fieldname": "patient_name", "fieldtype": "Data", "width": 150},
        {"label": _("Practitioner"), "fieldname": "practitioner", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 150},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Result Date"), "fieldname": "result_date", "fieldtype": "Date", "width": 100},
        {"label": _("Is Abnormal"), "fieldname": "is_abnormal", "fieldtype": "Check", "width": 80},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Billing Status"), "fieldname": "billing_status", "fieldtype": "Data", "width": 100}
    ]

    filters = filters or {}
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND date <= '{filters['to_date']}'"
    if filters.get("status"):
        conditions += f" AND status = '{filters['status']}'"
    if filters.get("lab_test_template"):
        conditions += f" AND lab_test_template = '{filters['lab_test_template']}'"

    query = f"""
        SELECT
            test_name,
            patient,
            patient_name,
            practitioner,
            date,
            status,
            result_date,
            is_abnormal,
            amount,
            billing_status
        FROM `tabLab Test`
        WHERE {conditions}
        ORDER BY date DESC
    """

    data = frappe.db.sql(query, as_dict=1)

    chart = {
        "data": {
            "labels": ["Pending", "Sample Collected", "In Progress", "Completed", "Verified", "Cancelled"],
            "datasets": [
                {
                    "name": "Lab Tests by Status",
                    "values": [
                        frappe.db.count("Lab Test", {"status": "Pending"}),
                        frappe.db.count("Lab Test", {"status": "Sample Collected"}),
                        frappe.db.count("Lab Test", {"status": "In Progress"}),
                        frappe.db.count("Lab Test", {"status": "Completed"}),
                        frappe.db.count("Lab Test", {"status": "Verified"}),
                        frappe.db.count("Lab Test", {"status": "Cancelled"})
                    ]
                }
            ]
        },
        "type": "donut",
        "height": 250,
        "colors": ["#f59e0b", "#8b5cf6", "#3b82f6", "#34d399", "#06b6d4", "#ef4444"]
    }

    return columns, data, None, chart
