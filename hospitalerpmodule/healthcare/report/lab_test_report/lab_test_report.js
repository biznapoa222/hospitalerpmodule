frappe.query_reports["Lab Test Report"] = {
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
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPending\nSample Collected\nIn Progress\nCompleted\nVerified\nCancelled"
        },
        {
            "fieldname": "lab_test_template",
            "label": __("Test Template"),
            "fieldtype": "Link",
            "options": "Lab Test Template"
        }
    ]
};
