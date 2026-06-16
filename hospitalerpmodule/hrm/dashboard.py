from frappe.model.document import Document
import frappe
from datetime import datetime
import json

class ModuleDashboard(Document):
    def before_insert(self):
        self.validate_dashboard_name()
        self.generate_dashboard_code()

    def validate_dashboard_name(self):
        if self.dashboard_name:
            existing = frappe.db.exists("Module Dashboard", {"dashboard_name": self.dashboard_name, "name": ["!=", self.name] if self.name else None})
            if existing:
                frappe.throw("Dashboard name must be unique")

    def generate_dashboard_code(self):
        if not self.dashboard_code and self.dashboard_name:
            name_parts = self.dashboard_name.split()
            code = "".join([part[0].upper() for part in name_parts if part])
            count = frappe.db.count("Module Dashboard") + 1
            self.dashboard_code = f"{code}{count:04d}"

    def validate(self):
        self.validate_dashboard_name()
        if self.dashboard_name and len(self.dashboard_name) < 3:
            frappe.throw("Dashboard name must be at least 3 characters long")

    def get_comprehensive_metrics(self):
        """Get comprehensive metrics across all modules"""
        metrics = {}

        # Patient metrics
        metrics["total_patients"] = frappe.db.count("Patient", {"status": "Active"})
        metrics["new_patients_this_month"] = frappe.db.count("Patient", {
            "status": "Active",
            "creation": ["<=", frappe.utils.add_months(frappe.utils.today(), -1)]
        })
        metrics["home_patients"] = frappe.db.count("Patient", {"status": "Home Care"})
        metrics["discharged_patients"] = frappe.db.count("Patient", {"status": "Discharged"})

        # Staff metrics
        metrics["total_employees"] = frappe.db.count("Employee", {"status": "Active"})
        metrics["doctors"] = frappe.db.count("Employee", {"designation": "Doctor"})
        metrics["nurses"] = frappe.db.count("Employee", {"designation": "Nurse"})
        metrics["clerks"] = frappe.db.count("Employee", {"designation": "HR Clerk"})

        # Appointment metrics
        metrics["total_appointments"] = frappe.db.count("Appointment", {"status": "Scheduled"})
        metrics["appointments_today"] = frappe.db.count("Appointment", {
            "status": "Scheduled",
            "appointment_date": frappe.utils.today()
        })
        metrics["appointments_this_week"] = frappe.db.count("Appointment", {
            "status": "Scheduled",
            "appointment_date": ["<=", frappe.utils.add_days(frappe.utils.today(), 7)]
        })

        # Financial metrics
        metrics["total_revenue"] = frappe.db.sum("Sales Invoice", {"docstatus": 1})
        metrics["monthly_revenue"] = frappe.db.sum("Sales Invoice", {
            "docstatus": 1,
            "posting_date": ["<=", frappe.utils.get_last_day(frappe.utils.month_start(frappe.utils.today()))]
        })
        metrics["home_care_revenue"] = frappe.db.sum("Sales Invoice", {
            "docstatus": 1,
            "is_home_care": 1
        })

        # Department metrics
        departments = frappe.db.get_all("Department", fields=["name", "department_head"])
        metrics["total_departments"] = len(departments)
        metrics["departments_with_heads"] = len([d for d in departments if d.department_head])

        # Home care metrics
        home_patients = frappe.db.get_all("Patient", {
            "status": "Home Care"
        }, fields=["name", "patient_name"])
        metrics["home_patients_count"] = len(home_patients)
        metrics["home_visits_today"] = frappe.db.count("Home Visit", {
            "visit_date": frappe.utils.today(),
            "status": "Completed"
        })

        return metrics

    def get_module_distribution_chart(self):
        """Get chart data for module distribution"""
        modules = frappe.db.get_all("Module", fields=["name", "module_name"])
        return {
            "labels": [m.module_name for m in modules],
            "values": [len(frappe.db.get_all("Employee", filters={"department": m.name})) for m in modules],
            "colors": ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"]
        }

    def get_revenue_trends(self):
        """Get revenue trends for the last 12 months"""
        today = frappe.utils.today()
        months = []
        values = []

        for i in range(12, 0, -1):
            month_date = frappe.utils.add_months(frappe.utils.month_start(today), -i)
            month_name = frappe.utils.format_date(month_date, "mmm")
            revenue = frappe.db.sum("Sales Invoice", {
                "docstatus": 1,
                "posting_date": ["<=", frappe.utils.get_last_day(month_date)]
            }) or 0

            months.append(month_name)
            values.append(revenue)

        return {
            "labels": months,
            "values": values,
            "color": "#3498db"
        }

    def get_patient_distribution_chart(self):
        """Get chart data for patient distribution"""
        patients = frappe.db.get_all("Patient", fields=["status"])
        status_counts = {}
        for patient in patients:
            status_counts[patient.status] = status_counts.get(patient.status, 0) + 1

        return {
            "labels": list(status_counts.keys()),
            "values": list(status_counts.values()),
            "colors": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
        }

    def get_color_scheme(self):
        """Get color scheme for the dashboard"""
        return {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "info": "#3498db",
            "success": "#2ecc71",
            "dark": "#2c3e50",
            "light": "#ecf0f1"
        }

    def get_dashboard_summary(self):
        """Get dashboard summary information"""
        metrics = self.get_comprehensive_metrics()

        summary = {
            "total_patients": metrics["total_patients"],
            "active_staff": metrics["total_employees"],
            "appointments_today": metrics["appointments_today"],
            "revenue_today": metrics["total_revenue"],
            "home_care_patients": metrics["home_patients"],
            "home_visits_today": metrics["home_visits_today"],
            "departments": metrics["total_departments"],
            "growth_indicators": {
                "patient_growth": (metrics["new_patients_this_month"] / max(metrics["total_patients"], 1)) * 100,
                "appointment_growth": (metrics["appointments_this_week"] / max(metrics["appointments_today"], 1)) * 100,
                "revenue_growth": ((metrics["monthly_revenue"] - metrics["total_revenue"]) / max(metrics["total_revenue"], 1)) * 100
            }
        }

        return summary

    def after_insert(self):
        self.create_default_widgets()

    def create_default_widgets(self):
        """Create default widgets for the module dashboard"""
        default_widgets = [
            {
                "widget_name": "Total Patients",
                "widget_type": "metric",
                "field": "total_patients",
                "color": "#3498db"
            },
            {
                "widget_name": "Active Staff",
                "widget_type": "metric",
                "field": "total_employees",
                "color": "#2ecc71"
            },
            {
                "widget_name": "Appointments Today",
                "widget_type": "metric",
                "field": "appointments_today",
                "color": "#f39c12"
            },
            {
                "widget_name": "Total Revenue",
                "widget_type": "metric",
                "field": "total_revenue",
                "color": "#e74c3c"
            },
            {
                "widget_name": "Home Care Patients",
                "widget_type": "metric",
                "field": "home_patients",
                "color": "#9b59b6"
            },
            {
                "widget_name": "Department Distribution",
                "widget_type": "chart",
                "chart_type": "pie",
                "metric_type": "department"
            },
            {
                "widget_name": "Revenue Trends",
                "widget_type": "chart",
                "chart_type": "line",
                "metric_type": "revenue"
            },
            {
                "widget_name": "Patient Distribution",
                "widget_type": "chart",
                "chart_type": "pie",
                "metric_type": "patient"
            }
        ]

        for widget_data in default_widgets:
            widget = frappe.new_doc("Dashboard Widget")
            widget.dashboard = self.name
            widget.widget_name = widget_data["widget_name"]
            widget.widget_type = widget_data["widget_type"]
            widget.field = widget_data.get("field", "")
            widget.color = widget_data.get("color", "")
            widget.chart_type = widget_data.get("chart_type", "")
            widget.metric_type = widget_data.get("metric_type", "")
            widget.insert(ignore_permissions=True)