import frappe
frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()
mods = frappe.db.sql("SELECT name, app_name FROM `tabModule Def`", as_dict=True)
print('Modules:')
for m in mods:
    print('  ' + m.name + ' (app: ' + m.app_name + ')')
frappe.db.close()
