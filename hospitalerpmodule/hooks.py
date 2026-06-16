from . import __version__ as app_version

app_name = "hospitalerpmodule"
app_title = "Hospital ERP"
app_publisher = "Hospital ERP"
app_description = "Comprehensive Hospital ERP System with Healthcare, HRM, Inventory, Finance, and Queue Management"
app_email = "support@hospitalerp.com"
app_license = "MIT"

app_dashboard_url = "/app/hospital-dashboard"

fixtures = ["Custom Field", "Property Setter"]

before_install = "hospitalerpmodule.install.before_install"
after_install = "hospitalerpmodule.install.after_install"

doc_events = {}

doctype_js = {}

doctype_list_js = {}

scheduler_events = {}

doctype_list = []

standard_entries = []

docs_url = ""
app_website_url = ""
