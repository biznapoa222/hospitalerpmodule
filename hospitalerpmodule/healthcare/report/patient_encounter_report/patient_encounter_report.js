frappe.query_reports["Patient Encounter Report"] = {
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
            "fieldname": "practitioner",
            "label": __("Practitioner"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Medical Department"
        },
        {
            "fieldname": "type",
            "label": __("Encounter Type"),
            "fieldtype": "Select",
            "options": "\nOPD\nIPD\nEmergency\nFollow Up\nTelemedicine"
        }
    ]
};
