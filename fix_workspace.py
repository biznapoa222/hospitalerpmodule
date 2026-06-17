import frappe, json, sys

frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()

# Check if Healthcare module exists
modules = frappe.db.sql("SELECT name, app_name FROM tabModuleDef WHERE app_name='hospitalerpmodule'", as_dict=True)
print('Modules from hospitalerpmodule:')
for m in modules:
    print(' -', m.name)

# Check existing workspaces from our app
ws = frappe.db.sql("SELECT w.name, w.module, md.app_name FROM tabWorkspace w LEFT JOIN tabModuleDef md ON w.module=md.name WHERE md.app_name='hospitalerpmodule'", as_dict=True)
print('Workspaces from our app:')
for w in ws:
    print(' -', w.name, 'module:', w.module)

# Try syncing workspaces
print('\nRunning sync...')
from frappe.modules.utils import sync_customizations
frappe.modules.utils.sync_workspaces = None

# Check if there's a migrate command that syncs workspaces
import frappe.desk.doctype.workspace.workspace as ws_module
if hasattr(ws_module, 'sync_workspaces'):
    print('Found sync_workspaces in workspace module')
else:
    print('No sync_workspaces found')

frappe.db.close()
