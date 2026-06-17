import frappe, json, os

frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()

all_dt = set(frappe.get_all('DocType', pluck='name'))
ws_dir = '/opt/frappe-bench/apps/hospitalerpmodule/hospitalerpmodule/workspace'

key_doctypes = [
    'Patient', 'Appointment', 'Patient Visit', 'Vital Signs', 'Admission',
    'Bed', 'Bed Allocation', 'Ward', 'Pharmacy Dispensing', 'Drug Master',
    'Drug Prescription', 'Lab Settings', 'Radiology Request', 'Radiology Result',
    'Radiology Template', 'Imaging Type', 'Theatre', 'Therapy Plan',
    'Delivery Record', 'Newborn Record', 'Medical Record', 'Diagnosis',
    'Equipment Category', 'Equipment Maintenance', 'Medical Equipment',
    'Queue Display', 'Queue Settings', 'Patient Queue', 'Employee',
    'Leave Application', 'Leave Type', 'Shift Type', 'Shift Assignment',
    'Account', 'Payment Entry', 'Financial Year', 'Item', 'Batch',
    'Department', 'Designation', 'Insurance Company', 'Claim'
]

for dt in key_doctypes:
    status = 'EXISTS' if dt in all_dt else 'MISSING'
    print(f'{status}: {dt}')

frappe.db.close()
