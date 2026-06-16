import frappe
from frappe import _

@frappe.whitelist()
def get_queue_data():
    counters = frappe.get_all("Queue Counter",
        filters={"status": "Active"},
        fields=["name", "counter_name", "counter_number", "currently_serving", "location", "department"],
        order_by="counter_number asc"
    )

    result = []
    all_waiting = frappe.get_all("Queue Ticket",
        filters={
            "status": "Waiting",
            "token_issued_date": frappe.utils.today()
        },
        fields=["name", "ticket_number", "patient_name", "priority", "waiting_time_minutes", "counter", "department"],
        order_by="priority desc, creation asc"
    )

    for counter in counters:
        serving = None
        if counter.currently_serving:
            try:
                serving = frappe.get_doc("Queue Ticket", counter.currently_serving)
            except Exception:
                serving = None

        counter_waiting = [w for w in all_waiting if w.counter == counter.name]
        if not counter_waiting:
            counter_waiting = [w for w in all_waiting if not w.counter and w.department == counter.department][:10]

        result.append({
            "counter_name": counter.counter_name,
            "counter_number": counter.counter_number,
            "location": counter.location,
            "currently_serving": {
                "ticket_number": serving.ticket_number if serving else "---",
                "patient_name": serving.patient_name if serving else ""
            } if serving else {"ticket_number": "---", "patient_name": ""},
            "waiting": counter_waiting[:10],
            "waiting_count": len(counter_waiting)
        })

    stats = {
        "total_waiting": frappe.db.count("Queue Ticket", {
            "status": "Waiting",
            "token_issued_date": frappe.utils.today()
        }),
        "total_completed": frappe.db.count("Queue Ticket", {
            "status": "Completed",
            "token_issued_date": frappe.utils.today()
        }),
        "total_cancelled": frappe.db.count("Queue Ticket", {
            "status": "Cancelled",
            "token_issued_date": frappe.utils.today()
        })
    }

    return {
        "counters": result,
        "stats": stats,
        "hospital_name": get_hospital_name()
    }

@frappe.whitelist()
def get_hospital_name():
    name = frappe.db.get_single_value("Healthcare Settings", "disable")
    return "City Hospital & Medical Center"
