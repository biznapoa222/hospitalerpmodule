import frappe, json, os

frappe.init('/opt/frappe-bench/sites/kuva.biznapoa.com')
frappe.connect()

all_dt = set(frappe.get_all('DocType', pluck='name'))
ws_dir = '/opt/frappe-bench/apps/hospitalerpmodule/hospitalerpmodule/workspace'

print(f'Total doctypes in system: {len(all_dt)}')

files = sorted([f for f in os.listdir(ws_dir) if f.endswith('.json')])
print(f'Workspace files found: {len(files)}')

for fname in files:
    fpath = os.path.join(ws_dir, fname)
    with open(fpath) as f:
        ws = json.load(f)
    
    changes = False
    
    # Fix links
    if 'links' in ws and ws['links']:
        original_links = len(ws['links'])
        valid_links = []
        for link in ws['links']:
            dt = link.get('link_to', '')
            if dt in all_dt:
                valid_links.append(link)
            else:
                print(f'{fname}: Removing link "{link.get("label","?")}" -> {dt} (not found)')
                changes = True
        ws['links'] = valid_links
    
    # Fix shortcuts
    if 'shortcuts' in ws and ws['shortcuts']:
        original_shortcuts = len(ws['shortcuts'])
        valid_shortcuts = []
        for sc in ws['shortcuts']:
            url = sc.get('url', '')
            if url.startswith('/app/'):
                # Extract doctype from URL if it's a doctype URL
                dt_ref = url.replace('/app/', '').split('/')[0].replace('-', ' ').title()
                # Remove spaces from camelcase-like names
                dt_ref_maybe = ''.join(w.capitalize() for w in dt_ref.split())
                if dt_ref in all_dt or dt_ref_maybe in all_dt or dt_ref.replace(' ','') in all_dt:
                    valid_shortcuts.append(sc)
                else:
                    print(f'{fname}: Removing shortcut "{sc.get("label","?")}" -> {url} (doctype not found)')
                    changes = True
            else:
                valid_shortcuts.append(sc)  # Keep non-doctype URLs
        ws['shortcuts'] = valid_shortcuts
    
    # Fix charts - check report_name
    if 'charts' in ws and ws['charts']:
        for chart in ws['charts']:
            report = chart.get('report_name', '')
            if report and report not in ['']:
                if not frappe.db.exists('Report', report):
                    print(f'{fname}: Report not found: {report}')
                    # Remove the custom_options or mark it
            # Check chart doctype
            # number cards reference document_type
            chart_dt = chart.get('document_type', '')
            base_on = chart.get('based_on', '')
            if base_on and base_on not in all_dt and base_on not in ['', 'owner', 'creation', 'modified']:
                # based_on might be a field, not always a doctype
                pass
    
    if changes:
        with open(fpath, 'w') as f:
            json.dump(ws, f, indent=2)
        print(f'{fname}: Updated and saved')

print('\nDone fixing workspace links!')
frappe.db.close()
