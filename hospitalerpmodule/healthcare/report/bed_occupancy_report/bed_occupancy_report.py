import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Ward/Unit"), "fieldname": "service_unit", "fieldtype": "Link", "options": "Healthcare Service Unit", "width": 180},
        {"label": _("Unit Type"), "fieldname": "unit_type", "fieldtype": "Data", "width": 120},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": _("Total Capacity"), "fieldname": "capacity", "fieldtype": "Int", "width": 100},
        {"label": _("Currently Occupied"), "fieldname": "occupied", "fieldtype": "Int", "width": 100},
        {"label": _("Available"), "fieldname": "available", "fieldtype": "Int", "width": 100},
        {"label": _("Occupancy Rate (%)"), "fieldname": "occupancy_rate", "fieldtype": "Float", "width": 120, "precision": 1}
    ]

    units = frappe.get_all("Healthcare Service Unit",
        fields=["name", "service_unit_name", "service_unit_type", "department", "capacity", "occupied"],
        order_by="service_unit_name"
    )

    data = []
    for unit in units:
        unit_type_name = ""
        if unit.service_unit_type:
            ut = frappe.get_cached_doc("Healthcare Service Unit Type", unit.service_unit_type)
            unit_type_name = ut.service_unit_type_name

        capacity = unit.capacity or 1
        occupied = unit.occupied or 0
        available = max(0, capacity - occupied)
        occupancy_rate = round((occupied / capacity) * 100, 1) if capacity else 0

        data.append({
            "service_unit": unit.name,
            "unit_type": unit_type_name,
            "department": unit.department,
            "capacity": capacity,
            "occupied": occupied,
            "available": available,
            "occupancy_rate": occupancy_rate
        })

    chart = {
        "data": {
            "labels": [d["service_unit"] for d in data[:20]],
            "datasets": [
                {"name": "Occupancy Rate (%)", "values": [d["occupancy_rate"] for d in data[:20]]}
            ]
        },
        "type": "bar",
        "height": 250,
        "colors": ["#3b82f6"]
    }

    return columns, data, None, chart
