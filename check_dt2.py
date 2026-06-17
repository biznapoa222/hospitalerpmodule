import frappe, json
frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()
all_dt = frappe.get_all('DocType', pluck='name')
print(json.dumps(sorted(all_dt), indent=2))
frappe.db.close()
