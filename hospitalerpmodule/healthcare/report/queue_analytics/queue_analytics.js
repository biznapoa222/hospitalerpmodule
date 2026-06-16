frappe.query_reports["Queue Analytics"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "queue_service_type",
            "label": __("Service Type"),
            "fieldtype": "Link",
            "options": "Queue Service Type"
        }
    ]
};
