frappe.query_reports["Spare Parts Inventory"] = {
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data && data.stock_qty <= data.reorder_level) {
			value = "<span style='background-color:red'>" + value + "</span>";
		}

		return value;
	},
};
