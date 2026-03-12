import frappe
from frappe.utils import date_diff


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns(filters):
	columns = [
		{
			"label": "Technician",
			"fieldname": "technician",
			"fieldtype": "Link",
			"options": "Technician",
			"width": 150,
		},
		{"label": "Total Jobs", "fieldname": "total_jobs", "fieldtype": "Int", "width": 120},
		{"label": "Completed", "fieldname": "completed", "fieldtype": "Int", "width": 120},
		{"label": "Avg Turnaround Days", "fieldname": "avg_days", "fieldtype": "Float", "width": 150},
		{"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": "Completion Rate %", "fieldname": "completion_rate", "fieldtype": "Percent", "width": 150},
	]

	# Dynamic Device Type Columns
	device_types = frappe.get_all("Device Type", fields=["name"])

	for dt in device_types:
		field = dt.name.lower().replace(" ", "_")
		columns.append({"label": dt.name, "fieldname": field, "fieldtype": "Int", "width": 100})

	return columns


def get_data(filters):
	conditions = {}

	if filters.get("technician"):
		conditions["assigned_technician"] = filters.get("technician")

	if filters.get("from_date") and filters.get("to_date"):
		conditions["creation"] = ["between", [filters.get("from_date"), filters.get("to_date")]]

	jobs = frappe.get_list(
		"Job Card",
		fields=["assigned_technician", "device_type", "status", "final_amount", "delivery_date", "creation"],
		filters=conditions,
		limit_page_length=0,
	)

	device_types = frappe.get_all("Device Type", fields=["name"])

	tech_map = {}

	for j in jobs:
		tech = j.assigned_technician

		if not tech:
			continue

		if tech not in tech_map:
			row = {
				"technician": tech,
				"total_jobs": 0,
				"completed": 0,
				"avg_days": 0,
				"revenue": 0,
				"completion_rate": 0,
			}

			# Initialize dynamic device columns
			for dt in device_types:
				field = dt.name.lower().replace(" ", "_")
				row[field] = 0

			tech_map[tech] = row

		tech_map[tech]["total_jobs"] += 1

		# Count device types safely
		if j.device_type:
			device_field = j.device_type.lower().replace(" ", "_")
			if device_field in tech_map[tech]:
				tech_map[tech][device_field] += 1

		# Completed job
		if j.status == "Delivered":
			tech_map[tech]["completed"] += 1
			tech_map[tech]["revenue"] += j.final_amount or 0

			if j.delivery_date:
				days = date_diff(j.delivery_date, j.creation)
				tech_map[tech]["avg_days"] += days

	# Calculate averages
	for tech in tech_map.values():
		if tech["completed"] > 0:
			tech["avg_days"] = tech["avg_days"] / tech["completed"]

		if tech["total_jobs"] > 0:
			tech["completion_rate"] = (tech["completed"] / tech["total_jobs"]) * 100

	return list(tech_map.values())


def get_chart(data):
	labels = []
	total_jobs = []
	completed_jobs = []

	for d in data:
		labels.append(d["technician"])
		total_jobs.append(d["total_jobs"])
		completed_jobs.append(d["completed"])

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Total Jobs", "values": total_jobs},
				{"name": "Completed Jobs", "values": completed_jobs},
			],
		},
		"type": "bar",
	}


def get_summary(data):
	total_jobs = 0
	total_revenue = 0

	for d in data:
		total_jobs += d["total_jobs"]
		total_revenue += d["revenue"]

	best = None

	if data:
		best = max(data, key=lambda x: x["completion_rate"])

	return [
		{"label": "Total Jobs", "value": total_jobs, "indicator": "Blue"},
		{"label": "Total Revenue", "value": total_revenue, "indicator": "Green"},
		{"label": "Best Technician", "value": best["technician"] if best else "", "indicator": "Orange"},
	]


def prepare_report(filters=None):
	frappe.enqueue(
		"quickfix.service_center.report.technician_performance_report.technician_performance_report.execute",
		queue="long",
		timeout=600,
		filters=filters,
	)
