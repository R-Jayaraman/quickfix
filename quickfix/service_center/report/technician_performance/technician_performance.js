frappe.query_reports["Technician Performance"] = {
	filters: [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			reqd: 1,
		},

		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			reqd: 1,
		},

		{
			fieldname: "technician",
			label: "Technician",
			fieldtype: "Link",
			options: "Technician",
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "completion_rate") {
			if (data.completion_rate < 70) {
				value = `<span style="color:red">${value}</span>`;
			}

			if (data.completion_rate >= 90) {
				value = `<span style="color:green">${value}</span>`;
			}
		}

		return value;
	},
};
