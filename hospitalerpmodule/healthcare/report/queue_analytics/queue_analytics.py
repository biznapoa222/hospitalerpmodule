import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Date"), "fieldname": "token_issued_date", "fieldtype": "Date", "width": 120},
        {"label": _("Service Type"), "fieldname": "queue_service_type", "fieldtype": "Data", "width": 150},
        {"label": _("Total Tickets"), "fieldname": "total", "fieldtype": "Int", "width": 100},
        {"label": _("Waiting"), "fieldname": "waiting", "fieldtype": "Int", "width": 100},
        {"label": _("Called"), "fieldname": "called", "fieldtype": "Int", "width": 100},
        {"label": _("In Consultation"), "fieldname": "in_consultation", "fieldtype": "Int", "width": 100},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Int", "width": 100},
        {"label": _("Skipped/No Show"), "fieldname": "skipped", "fieldtype": "Int", "width": 100},
        {"label": _("Cancelled"), "fieldname": "cancelled", "fieldtype": "Int", "width": 100},
        {"label": _("Avg Wait Time (min)"), "fieldname": "avg_wait_time", "fieldtype": "Float", "width": 120, "precision": 1},
        {"label": _("Avg Service Time (min)"), "fieldname": "avg_service_time", "fieldtype": "Float", "width": 120, "precision": 1}
    ]

    filters = filters or {}
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND token_issued_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND token_issued_date <= '{filters['to_date']}'"
    if filters.get("queue_service_type"):
        conditions += f" AND queue_service_type = '{filters['queue_service_type']}'"

    query = f"""
        SELECT
            token_issued_date,
            queue_service_type,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Waiting' THEN 1 ELSE 0 END) as waiting,
            SUM(CASE WHEN status = 'Called' THEN 1 ELSE 0 END) as called,
            SUM(CASE WHEN status = 'In Consultation' THEN 1 ELSE 0 END) as in_consultation,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status IN ('Skipped', 'No Show') THEN 1 ELSE 0 END) as skipped,
            SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
            AVG(COALESCE(waiting_time_minutes, 0)) as avg_wait_time,
            AVG(COALESCE(service_time_minutes, 0)) as avg_service_time
        FROM `tabQueue Ticket`
        WHERE {conditions}
        GROUP BY token_issued_date, queue_service_type
        ORDER BY token_issued_date DESC
    """

    data = frappe.db.sql(query, as_dict=1)

    return columns, data
