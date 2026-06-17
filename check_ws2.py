import frappe, json, sys
frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()

ws = frappe.db.sql("SELECT name, module FROM tabWorkspace WHERE module='Healthcare'", as_dict=True)
print("Healthcare module workspaces:", len(ws))
for w in ws:
    print(" -", w['name'])

links = frappe.db.sql("SELECT parent, label, link_to, group_name FROM tabWorkspaceLink WHERE parent='Laboratory'", as_dict=True)
print("Laboratory workspace links:")
for l in links:
    print(" -", l['label'], "->", l['link_to'], "in", l['group_name'])

frappe.db.close()
