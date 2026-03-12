import frappe


def execute(filters=None):
	columns = [
		{"label": "Part Name", "fieldname": "part_name", "fieldtype": "Data", "width": 150},
		{"label": "Part Code", "fieldname": "part_code", "fieldtype": "Data", "width": 120},
		{"label": "Device Type", "fieldname": "device_type", "fieldtype": "Data", "width": 120},
		{"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
		{"label": "Reorder Level", "fieldname": "reorder_level", "fieldtype": "Float", "width": 120},
		{"label": "Unit Cost", "fieldname": "unit_cost", "fieldtype": "Currency", "width": 120},
		{"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 120},
		{"label": "Margin %", "fieldname": "margin", "fieldtype": "Percent", "width": 100},
		{"label": "Total Value", "fieldname": "total_value", "fieldtype": "Currency", "width": 120},
	]

	data = frappe.db.sql(
		"""
        SELECT
            part_name,
            part_code,
            Compatible_device_type,
            stock_qty,
            reorder_level,
            unit_cost,
            selling_price
        FROM `tabSpare Part`
    """,
		as_dict=1,
	)

	total_qty = 0
	total_value = 0

	for d in data:
		d.margin = ((d.selling_price - d.unit_cost) / d.unit_cost) * 100 if d.unit_cost else 0
		d.total_value = d.stock_qty * d.unit_cost

		total_qty += d.stock_qty
		total_value += d.total_value

	data.append({"part_name": "TOTAL", "stock_qty": total_qty, "total_value": total_value})

	summary = [
		{"label": "Total Parts", "value": len(data) - 1, "indicator": "Blue"},
		{
			"label": "Below Reorder",
			"value": sum(1 for d in data if d.get("stock_qty", 0) <= d.get("reorder_level", 0)),
			"indicator": "Red",
		},
		{"label": "Total Inventory Value", "value": total_value, "indicator": "Green"},
	]

	return columns, data, None, None, summary
