import frappe
frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()
mods = frappe.db.sql("SELECT name, app_name FROM tabModuleDef WHERE app_name='hospitalerpmodule'", as_dict=True)
print('Modules from hospitalerpmodule:')
for m in mods:
    print(' -', m.name)
our_doctypes = ['Patient','Patient Appointment','Patient Encounter','Healthcare Practitioner',
    'Medical Department','Lab Test','Lab Test Template','Queue Ticket','Queue Counter',
    'Inpatient Record','Vital Signs','Clinical Procedure','Diagnosis','Appointment Type',
    'Healthcare Service Unit','Healthcare Service Unit Type','Therapy Type','Therapy Plan',
    'Therapy Session','Sample Collection','Fee Validity','Financial Report','Account',
    'General Ledger','Accounts Payable','Accounts Receivable','Payment Entry','Budget',
    'Cost Accounting','Item','Warehouse','Stock Entry','Purchase Order','Sales Order',
    'Employee','Leave','Leave Type','Shift Type','Shift Assignment','CME','Payroll',
    'P9 Form','Training','LMS']
existing = []
missing = []
for dt in our_doctypes:
    if frappe.db.exists('DocType', dt):
        existing.append(dt)
    else:
        missing.append(dt)
print(f'Existing ({len(existing)}):')
print('\n'.join(existing))
print(f'Missing ({len(missing)}):')
print('\n'.join(missing))
frappe.db.close()
