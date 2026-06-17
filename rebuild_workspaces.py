import frappe, json, os

frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()

all_dt = set(frappe.get_all('DocType', pluck='name'))
ws_dir = '/opt/frappe-bench/apps/hospitalerpmodule/hospitalerpmodule/workspace'

# Define valid workspaces with links using only existing doctypes
workspaces = {
    "Reception": {
        "label": "Reception",
        "icon": "hospital",
        "links": [
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Patient Visits", "type": "Link", "link_to": "Patient Visit", "link_type": "DocType"},
            {"label": "Vital Signs", "type": "Link", "link_to": "Vital Signs", "link_type": "DocType"},
            {"label": "Patient Queue", "type": "Link", "link_to": "Patient Queue", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Patient", "url": "/app/patient/new", "icon": "user-plus"},
            {"label": "New Appointment", "url": "/app/appointment/new", "icon": "calendar-plus"},
            {"label": "Queue Display", "url": "/app/queue-display", "icon": "tv"},
            {"label": "Patient Queue", "url": "/app/patient-queue", "icon": "list"},
        ]
    },
    "Clinical": {
        "label": "Clinical",
        "icon": "heartbeat",
        "links": [
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Patient Visits", "type": "Link", "link_to": "Patient Visit", "link_type": "DocType"},
            {"label": "Vital Signs", "type": "Link", "link_to": "Vital Signs", "link_type": "DocType"},
            {"label": "Admissions", "type": "Link", "link_to": "Admission", "link_type": "DocType"},
            {"label": "Therapy Plans", "type": "Link", "link_to": "Therapy Plan", "link_type": "DocType"},
            {"label": "Medical Records", "type": "Link", "link_to": "Medical Record", "link_type": "DocType"},
            {"label": "Patient Queue", "type": "Link", "link_to": "Patient Queue", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Visit", "url": "/app/patient-visit/new", "icon": "clipboard"},
            {"label": "Record Vitals", "url": "/app/vital-signs/new", "icon": "activity"},
            {"label": "Patient List", "url": "/app/patient", "icon": "users"},
        ]
    },
    "Laboratory": {
        "label": "Laboratory",
        "icon": "flask",
        "links": [
            {"label": "Lab Settings", "type": "Link", "link_to": "Lab Settings", "link_type": "DocType"},
            {"label": "Radiology Requests", "type": "Link", "link_to": "Radiology Request", "link_type": "DocType"},
            {"label": "Radiology Results", "type": "Link", "link_to": "Radiology Result", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Lab Request", "url": "/app/radiology-request/new", "icon": "plus-circle"},
            {"label": "Lab Settings", "url": "/app/lab-settings", "icon": "settings"},
        ]
    },
    "Pharmacy": {
        "label": "Pharmacy",
        "icon": "briefcase",
        "links": [
            {"label": "Pharmacy Dispensing", "type": "Link", "link_to": "Pharmacy Dispensing", "link_type": "DocType"},
            {"label": "Drug Master", "type": "Link", "link_to": "Drug Master", "link_type": "DocType"},
            {"label": "Drug Prescription", "type": "Link", "link_to": "Drug Prescription", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Dispensing", "url": "/app/pharmacy-dispensing/new", "icon": "plus"},
            {"label": "Drug Master", "url": "/app/drug-master", "icon": "database"},
        ]
    },
    "Theatre": {
        "label": "Theatre",
        "icon": "crosshairs",
        "links": [
            {"label": "Theatre", "type": "Link", "link_to": "Theatre", "link_type": "DocType"},
            {"label": "Equipment Category", "type": "Link", "link_to": "Equipment Category", "link_type": "DocType"},
            {"label": "Equipment Maintenance", "type": "Link", "link_to": "Equipment Maintenance", "link_type": "DocType"},
            {"label": "Medical Equipment", "type": "Link", "link_to": "Medical Equipment", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "Theatre Schedule", "url": "/app/theatre", "icon": "calendar"},
            {"label": "Equipment Check", "url": "/app/equipment-maintenance", "icon": "tool"},
        ]
    },
    "Maternity": {
        "label": "Maternity",
        "icon": "life-buoy",
        "links": [
            {"label": "Delivery Record", "type": "Link", "link_to": "Delivery Record", "link_type": "DocType"},
            {"label": "Newborn Record", "type": "Link", "link_to": "Newborn Record", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Admissions", "type": "Link", "link_to": "Admission", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Delivery", "url": "/app/delivery-record/new", "icon": "plus"},
            {"label": "Newborn Records", "url": "/app/newborn-record", "icon": "baby"},
        ]
    },
    "Radiology": {
        "label": "Radiology",
        "icon": "camera",
        "links": [
            {"label": "Radiology Request", "type": "Link", "link_to": "Radiology Request", "link_type": "DocType"},
            {"label": "Radiology Result", "type": "Link", "link_to": "Radiology Result", "link_type": "DocType"},
            {"label": "Radiology Template", "type": "Link", "link_to": "Radiology Template", "link_type": "DocType"},
            {"label": "Imaging Type", "type": "Link", "link_to": "Imaging Type", "link_type": "DocType"},
            {"label": "Lab Settings", "type": "Link", "link_to": "Lab Settings", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Radiology Request", "url": "/app/radiology-request/new", "icon": "plus"},
            {"label": "View Results", "url": "/app/radiology-result", "icon": "file-text"},
        ]
    },
    "Ward Management": {
        "label": "Ward Management",
        "icon": "home",
        "links": [
            {"label": "Ward", "type": "Link", "link_to": "Ward", "link_type": "DocType"},
            {"label": "Bed", "type": "Link", "link_to": "Bed", "link_type": "DocType"},
            {"label": "Bed Allocation", "type": "Link", "link_to": "Bed Allocation", "link_type": "DocType"},
            {"label": "Admissions", "type": "Link", "link_to": "Admission", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "Bed Allocation", "url": "/app/bed-allocation/new", "icon": "plus-square"},
            {"label": "Ward List", "url": "/app/ward", "icon": "list"},
        ]
    },
    "Health Records": {
        "label": "Health Records",
        "icon": "folder",
        "links": [
            {"label": "Medical Record", "type": "Link", "link_to": "Medical Record", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Patient Visits", "type": "Link", "link_to": "Patient Visit", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Vital Signs", "type": "Link", "link_to": "Vital Signs", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "All Records", "url": "/app/medical-record", "icon": "folder"},
            {"label": "Patient List", "url": "/app/patient", "icon": "users"},
        ]
    },
    "Queue Management": {
        "label": "Queue Management",
        "icon": "list",
        "links": [
            {"label": "Patient Queue", "type": "Link", "link_to": "Patient Queue", "link_type": "DocType"},
            {"label": "Queue Display", "type": "Link", "link_to": "Queue Display", "link_type": "DocType"},
            {"label": "Queue Settings", "type": "Link", "link_to": "Queue Settings", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "Queue Display", "url": "/app/queue-display", "icon": "tv"},
            {"label": "Patient Queue", "url": "/app/patient-queue", "icon": "list"},
        ]
    },
    "Accounting": {
        "label": "Accounting",
        "icon": "dollar-sign",
        "links": [
            {"label": "Account", "type": "Link", "link_to": "Account", "link_type": "DocType"},
            {"label": "Payment Entry", "type": "Link", "link_to": "Payment Entry", "link_type": "DocType"},
            {"label": "Financial Year", "type": "Link", "link_to": "Financial Year", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Payment", "url": "/app/payment-entry/new", "icon": "plus"},
            {"label": "Chart of Accounts", "url": "/app/account", "icon": "book"},
            {"label": "Financial Year", "url": "/app/financial-year", "icon": "calendar"},
        ]
    },
    "Purchase": {
        "label": "Purchase",
        "icon": "shopping-cart",
        "links": [
            {"label": "Batch", "type": "Link", "link_to": "Batch", "link_type": "DocType"},
            {"label": "Drug Master", "type": "Link", "link_to": "Drug Master", "link_type": "DocType"},
            {"label": "Equipment Category", "type": "Link", "link_to": "Equipment Category", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Batch", "url": "/app/batch/new", "icon": "plus"},
            {"label": "Drug Master", "url": "/app/drug-master", "icon": "database"},
        ]
    },
    "Medical Superintendent": {
        "label": "Medical Superintendent",
        "icon": "shield",
        "links": [
            {"label": "Employees", "type": "Link", "link_to": "Employee", "link_type": "DocType"},
            {"label": "Departments", "type": "Link", "link_to": "Department", "link_type": "DocType"},
            {"label": "Designations", "type": "Link", "link_to": "Designation", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Admissions", "type": "Link", "link_to": "Admission", "link_type": "DocType"},
            {"label": "Leave Applications", "type": "Link", "link_to": "Leave Application", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "Employees", "url": "/app/employee", "icon": "users"},
            {"label": "Departments", "url": "/app/department", "icon": "grid"},
            {"label": "Patients", "url": "/app/patient", "icon": "user"},
        ]
    },
    "Hospital Dashboard": {
        "label": "Hospital Dashboard",
        "icon": "activity",
        "links": [
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Appointments", "type": "Link", "link_to": "Appointment", "link_type": "DocType"},
            {"label": "Patient Visits", "type": "Link", "link_to": "Patient Visit", "link_type": "DocType"},
            {"label": "Vital Signs", "type": "Link", "link_to": "Vital Signs", "link_type": "DocType"},
            {"label": "Admissions", "type": "Link", "link_to": "Admission", "link_type": "DocType"},
            {"label": "Pharmacy Dispensing", "type": "Link", "link_to": "Pharmacy Dispensing", "link_type": "DocType"},
            {"label": "Radiology Requests", "type": "Link", "link_to": "Radiology Request", "link_type": "DocType"},
            {"label": "Queue Display", "type": "Link", "link_to": "Queue Display", "link_type": "DocType"},
            {"label": "Patient Queue", "type": "Link", "link_to": "Patient Queue", "link_type": "DocType"},
            {"label": "Medical Record", "type": "Link", "link_to": "Medical Record", "link_type": "DocType"},
            {"label": "Theatre", "type": "Link", "link_to": "Theatre", "link_type": "DocType"},
            {"label": "Delivery Records", "type": "Link", "link_to": "Delivery Record", "link_type": "DocType"},
            {"label": "Beds", "type": "Link", "link_to": "Bed", "link_type": "DocType"},
            {"label": "Accounts", "type": "Link", "link_to": "Account", "link_type": "DocType"},
            {"label": "Employees", "type": "Link", "link_to": "Employee", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Patient", "url": "/app/patient/new", "icon": "user-plus"},
            {"label": "New Appointment", "url": "/app/appointment/new", "icon": "calendar-plus"},
            {"label": "Queue Display", "url": "/app/queue-display", "icon": "tv"},
            {"label": "New Payment", "url": "/app/payment-entry/new", "icon": "dollar-sign"},
        ]
    },
    "HRM": {
        "label": "HRM",
        "icon": "users",
        "links": [
            {"label": "Employees", "type": "Link", "link_to": "Employee", "link_type": "DocType"},
            {"label": "Leave Application", "type": "Link", "link_to": "Leave Application", "link_type": "DocType"},
            {"label": "Leave Type", "type": "Link", "link_to": "Leave Type", "link_type": "DocType"},
            {"label": "Shift Type", "type": "Link", "link_to": "Shift Type", "link_type": "DocType"},
            {"label": "Shift Assignment", "type": "Link", "link_to": "Shift Assignment", "link_type": "DocType"},
            {"label": "Department", "type": "Link", "link_to": "Department", "link_type": "DocType"},
            {"label": "Designation", "type": "Link", "link_to": "Designation", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Employee", "url": "/app/employee/new", "icon": "user-plus"},
            {"label": "New Leave", "url": "/app/leave-application/new", "icon": "calendar"},
            {"label": "Shift Assignments", "url": "/app/shift-assignment", "icon": "clock"},
        ]
    },
    "Finance": {
        "label": "Finance",
        "icon": "dollar-sign",
        "links": [
            {"label": "Account", "type": "Link", "link_to": "Account", "link_type": "DocType"},
            {"label": "Payment Entry", "type": "Link", "link_to": "Payment Entry", "link_type": "DocType"},
            {"label": "Financial Year", "type": "Link", "link_to": "Financial Year", "link_type": "DocType"},
            {"label": "Patients", "type": "Link", "link_to": "Patient", "link_type": "DocType"},
            {"label": "Employees", "type": "Link", "link_to": "Employee", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "New Payment", "url": "/app/payment-entry/new", "icon": "plus"},
            {"label": "Chart of Accounts", "url": "/app/account", "icon": "book"},
        ]
    },
    "Inventory": {
        "label": "Inventory",
        "icon": "package",
        "links": [
            {"label": "Drug Master", "type": "Link", "link_to": "Drug Master", "link_type": "DocType"},
            {"label": "Batch", "type": "Link", "link_to": "Batch", "link_type": "DocType"},
            {"label": "Equipment Category", "type": "Link", "link_to": "Equipment Category", "link_type": "DocType"},
            {"label": "Medical Equipment", "type": "Link", "link_to": "Medical Equipment", "link_type": "DocType"},
        ],
        "shortcuts": [
            {"label": "Drug Master", "url": "/app/drug-master", "icon": "database"},
            {"label": "Equipment", "url": "/app/medical-equipment", "icon": "tool"},
        ]
    }
}

# Write workspace files
os.makedirs(ws_dir, exist_ok=True)
for fname in os.listdir(ws_dir):
    fpath = os.path.join(ws_dir, fname)
    if fname.endswith('.json'):
        os.remove(fpath)
        print(f'Removed old: {fname}')

# Map filenames
name_map = {
    "Reception": "Reception", "Clinical": "Clinical",
    "Laboratory": "Laboratory", "Pharmacy": "Pharmacy",
    "Theatre": "Theatre", "Maternity": "Maternity",
    "Radiology": "Radiology", "Ward Management": "WardManagement",
    "Health Records": "HealthRecords", "Queue Management": "QueueManagement",
    "Accounting": "Accounting", "Purchase": "Purchase",
    "Medical Superintendent": "MedicalSuperintendent",
    "Hospital Dashboard": "HospitalDashboard",
    "HRM": "HRM", "Finance": "Finance", "Inventory": "Inventory"
}

for label, ws_data in workspaces.items():
    fname = name_map[label] + '.json'
    fpath = os.path.join(ws_dir, fname)
    
    doc = {
        "doctype": "Workspace",
        "name": fname.replace('.json', ''),
        "title": ws_data["label"],
        "label": ws_data["label"],
        "module": "Biznapoa Healthcare",
        "category": "Modules",
        "icon": ws_data["icon"],
        "links": ws_data["links"],
        "shortcuts": ws_data["shortcuts"],
        "charts": []
    }
    
    with open(fpath, 'w') as f:
        json.dump(doc, f, indent=2)
    link_count = len(ws_data["links"])
    sc_count = len(ws_data["shortcuts"])
    print(f'Created {fname} ({link_count} links, {sc_count} shortcuts)')

print('\nAll workspace files rebuilt successfully!')

# Now sync them to the database
print('\nSyncing workspaces to database...')
for label, ws_data in workspaces.items():
    fname = name_map[label] + '.json'
    
    # Check by label first, then by name
    existing_name = frappe.db.get_value('Workspace', {'label': ws_data['label']}, 'name')
    if not existing_name:
        existing_name = frappe.db.get_value('Workspace', {'name': fname.replace('.json', '')}, 'name')
    
    if existing_name:
        doc = frappe.get_doc('Workspace', existing_name)
    else:
        doc = frappe.new_doc('Workspace')
    
    doc.title = ws_data["label"]
    doc.label = ws_data["label"]
    doc.module = "Biznapoa Healthcare"
    doc.category = "Modules"
    doc.icon = ws_data["icon"]
    
    # Clear and set links
    doc.links = []
    for link_data in ws_data["links"]:
        dt = link_data["link_to"]
        if dt in all_dt:
            doc.append("links", {
                "label": link_data["label"],
                "type": "Link",
                "link_to": dt,
                "link_type": "DocType",
                "is_query_report": False
            })
        else:
            print(f'WARNING: {dt} not found for {label}')
    
    doc.shortcuts = []
    for sc in ws_data["shortcuts"]:
        doc.append("shortcuts", sc)
    
    doc.charts = []
    
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    doc.save()
    print(f'  Synced: {doc.name} ({len(doc.links)} links)')

frappe.db.commit()
print('\nAll workspaces synced to database!')
frappe.db.close()
