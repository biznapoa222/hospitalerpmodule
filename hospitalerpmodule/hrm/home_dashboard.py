from frappe.model.document import Document
import frappe
from datetime import datetime
import json

class HomeDashboard(Document):
    def before_insert(self):
        self.validate_dashboard_name()
        self.generate_dashboard_code()

    def validate_dashboard_name(self):
        if self.dashboard_name:
            existing = frappe.db.exists("Home Dashboard", {"dashboard_name": self.dashboard_name, "name": ["!=", self.name] if self.name else None})
            if existing:
                frappe.throw("Dashboard name must be unique")

    def generate_dashboard_code(self):
        if not self.dashboard_code and self.dashboard_name:
            name_parts = self.dashboard_name.split()
            code = "".join([part[0].upper() for part in name_parts if part])
            count = frappe.db.count("Home Dashboard") + 1
            self.dashboard_code = f"{code}{count:04d}"

    def validate(self):
        self.validate_dashboard_name()
        if self.dashboard_name and len(self.dashboard_name) < 3:
            frappe.throw("Dashboard name must be at least 3 characters long")

    def get_home_dashboard_metrics(self):
        """Get all metrics for home healthcare dashboard"""
        metrics = {}

        # Patient metrics
        metrics["total_home_patients"] = frappe.db.count("Patient", {"status": "Home Care"})
        metrics["active_home_patients"] = frappe.db.count("Patient", {
            "status": "Home Care",
            "home_care_start_date": ["<=", frappe.utils.today()]
        })
        metrics["home_patients_discharged"] = frappe.db.count("Patient", {
            "status": "Discharged",
            "home_care_end_date": ["<=", frappe.utils.today()]
        })

        # Visit metrics
        metrics["total_home_visits"] = frappe.db.count("Home Visit", {"status": "Completed"})
        metrics["visits_today"] = frappe.db.count("Home Visit", {
            "status": "Scheduled",
            "visit_date": frappe.utils.today()
        })
        metrics["visits_this_week"] = frappe.db.count("Home Visit", {
            "status": "Completed",
            "visit_date": ["<=", frappe.utils.add_days(frappe.utils.today(), 7)]
        })

        # Staff metrics
        metrics["total_nurses"] = frappe.db.count("Employee", {"designation": "Nurse"})
        metrics["available_nurses"] = frappe.db.count("Employee", {
            "designation": "Nurse",
            "status": "Active"
        })

        # Medication metrics
        metrics["total_medications_dispensed"] = frappe.db.count("Stock Entry", {
            "purpose": "Home Care",
            "docstatus": 1
        })

        # Financial metrics
        metrics["total_home_care_revenue"] = frappe.db.sum("Sales Invoice", {
            "docstatus": 1,
            "is_home_care": 1
        })

        # Home metrics
        homes = frappe.db.get_all("Home", {"is_active": 1}, fields=["name", "home_name", "current_occupancy", "max_capacity"])
        metrics["total_homes"] = len(homes)
        metrics["total_home_capacity"] = sum([h.max_capacity for h in homes])
        metrics["total_home_occupancy"] = sum([h.current_occupancy for h in homes])

        return metrics

    def get_home_visit_trends(self):
        """Get home visit trends for the last 30 days"""
        today = frappe.utils.today()
        dates = [frappe.utils.add_days(today, -i) for i in range(30, 0, -1)]
        values = []
        for date in dates:
            count = frappe.db.count("Home Visit", {
                "visit_date": date,
                "status": "Completed"
            })
            values.append(count)
        return {
            "labels": [frappe.utils.format_date(d) for d in dates],
            "values": values,
            "color": "#2ecc71"
        }

    def get_nurse_utilization(self):
        """Get nurse utilization data"""
        nurses = frappe.db.get_all("Employee", {
            "designation": "Nurse",
            "status": "Active"
        }, fields=["name", "first_name", "last_name"])

        nurse_data = []
        for nurse in nurses:
            visits = frappe.db.count("Home Visit", {
                "assigned_nurse": nurse.name,
                "visit_date": ["<=", frappe.utils.today()]
            })
            nurse_data.append({
                "name": nurse.name,
                "label": f"{nurse.first_name} {nurse.last_name}",
                "visits": visits,
                "color": "#3498db"
            })
        return nurse_data

    def get_medication_summary(self):
        """Get medication summary for home care"""
        medications = frappe.db.get_all("Stock", {
            "purpose": "Home Care"
        }, fields=["item_code", "item_name", "quantity"])

        return {
            "labels": [m.item_name for m in medications],
            "values": [m.quantity for m in medications],
            "colors": ["#e74c3c", "#f39c12", "#3498db", "#2ecc71", "#9b59b6"]
        }

    def get_home_capacity_chart(self):
        """Get home capacity chart data"""
        homes = frappe.db.get_all("Home", {
            "is_active": 1
        }, fields=["home_name", "current_occupancy", "max_capacity"])

        return {
            "labels": [h.home_name for h in homes],
            "values": [h.current_occupancy for h in homes],
            "max_values": [h.max_capacity for h in homes],
            "colors": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6"]
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

    def get_home_dashboard_summary(self):
        """Get home dashboard summary information"""
        metrics = self.get_home_dashboard_metrics()

        summary = {
            "total_home_patients": metrics["total_home_patients"],
            "available_nurses": metrics["available_nurses"],
            "visits_today": metrics["visits_today"],
            "home_care_revenue": metrics["total_home_care_revenue"],
            "total_homes": metrics["total_homes"],
            "current_occupancy": metrics["total_home_occupancy"],
            "max_capacity": metrics["total_home_capacity"],
            "occupancy_rate": (metrics["total_home_occupancy"] / max(metrics["total_home_capacity"], 1)) * 100,
            "growth_indicators": {
                "visit_growth": (metrics["visits_this_week"] / max(metrics["visits_today"], 1)) * 100,
                "patient_growth": (metrics["active_home_patients"] / max(metrics["total_home_patients"], 1)) * 100,
                "utilization_growth": ((metrics["available_nurses"] - metrics["total_nurses"]) / max(metrics["total_nurses"], 1)) * 100
            }
        }

        return summary

    def after_insert(self):
        self.create_default_widgets()

    def create_default_widgets(self):
        """Create default widgets for the home dashboard"""
        default_widgets = [
            {
                "widget_name": "Active Home Patients",
                "widget_type": "metric",
                "field": "active_home_patients",
                "color": "#2ecc71"
            },
            {
                "widget_name": "Home Visits Today",
                "widget_type": "metric",
                "field": "visits_today",
                "color": "#3498db"
            },
            {
                "widget_name": "Available Nurses",
                "widget_type": "metric",
                "field": "available_nurses",
                "color": "#f39c12"
            },
            {
                "widget_name": "Home Care Revenue",
                "widget_type": "metric",
                "field": "total_home_care_revenue",
                "color": "#e74c3c"
            },
            {
                "widget_name": "Home Capacity",
                "widget_type": "chart",
                "chart_type": "bar",
                "metric_type": "capacity"
            },
            {
                "widget_name": "Home Visit Trends",
                "widget_type": "chart",
                "chart_type": "line",
                "metric_type": "trends"
            },
            {
                "widget_name": "Nurse Utilization",
                "widget_type": "chart",
                "chart_type": "bar",
                "metric_type": "nurse"
            },
            {
                "widget_name": "Medication Summary",
                "widget_type": "chart",
                "chart_type": "pie",
                "metric_type": "medication"
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