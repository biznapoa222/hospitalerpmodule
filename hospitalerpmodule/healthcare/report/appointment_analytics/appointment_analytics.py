import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Appointment Date"), "fieldname": "appointment_date", "fieldtype": "Date", "width": 120},
        {"label": _("Practitioner"), "fieldname": "practitioner", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 180},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Medical Department", "width": 150},
        {"label": _("Total Appointments"), "fieldname": "total", "fieldtype": "Int", "width": 100},
        {"label": _("Scheduled"), "fieldname": "scheduled", "fieldtype": "Int", "width": 100},
        {"label": _("Checked In"), "fieldname": "checked_in", "fieldtype": "Int", "width": 100},
        {"label": _("In Consultation"), "fieldname": "in_consultation", "fieldtype": "Int", "width": 100},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Int", "width": 100},
        {"label": _("Cancelled"), "fieldname": "cancelled", "fieldtype": "Int", "width": 100},
        {"label": _("No Show"), "fieldname": "no_show", "fieldtype": "Int", "width": 100},
        {"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120}
    ]

    data = []
    filters = filters or {}
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND appointment_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND appointment_date <= '{filters['to_date']}'"
    if filters.get("practitioner"):
        conditions += f" AND practitioner = '{filters['practitioner']}'"
    if filters.get("department"):
        conditions += f" AND department = '{filters['department']}'"

    query = f"""
        SELECT
            appointment_date,
            practitioner,
            department,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Scheduled' THEN 1 ELSE 0 END) as scheduled,
            SUM(CASE WHEN status = 'Checked In' THEN 1 ELSE 0 END) as checked_in,
            SUM(CASE WHEN status = 'In Consultation' THEN 1 ELSE 0 END) as in_consultation,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN status = 'No Show' THEN 1 ELSE 0 END) as no_show,
            SUM(COALESCE(amount, 0)) as revenue
        FROM `tabPatient Appointment`
        WHERE {conditions}
        GROUP BY appointment_date, practitioner, department
        ORDER BY appointment_date DESC
    """

    data = frappe.db.sql(query, as_dict=1)

    chart = {
        "data": {
            "labels": [d.appointment_date.strftime('%d-%m-%Y') if d.appointment_date else '' for d in data[:30]],
            "datasets": [
                {"name": "Completed", "values": [d.completed or 0 for d in data[:30]]},
                {"name": "Cancelled", "values": [d.cancelled or 0 for d in data[:30]]},
                {"name": "No Show", "values": [d.no_show or 0 for d in data[:30]]}
            ]
        },
        "type": "line",
        "height": 300,
        "colors": ["#34d399", "#ef4444", "#f59e0b"]
    }

    return columns, data, None, chart
