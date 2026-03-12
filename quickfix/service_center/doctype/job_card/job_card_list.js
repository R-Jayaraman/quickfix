frappe.listview_settings["Job Card"] = {
	add_fields: ["status", "final_amount", "priority"],

	has_indicator_for_draft: true,
	get_indicator: function (doc) {
		let indicator_map = {
			Draft: ["Draft", "gray"],
			"Pending Diagnosis": ["Pending Diagnosis", "orange"],
			"Awaiting Customer Approval": ["Awaiting Customer Approval", "yellow"],
			"In Repair": ["In Repair", "blue"],
			"Ready for Delivery": ["Ready for Delivery", "green"],
			Delivered: ["Delivered", "darkgrey"],
			Cancelled: ["Cancelled", "red"],
		};

		return indicator_map[doc.status];
	},
	formatters: {
		final_amount: function (value, df, doc) {
			if (!value) return "-";
			return format_currency(value, "INR");
		},

		priority: function (value, df, doc) {
			let color_map = {
				Normal: "green",
				High: "orange",
				Urgent: "red",
			};
			let color = color_map[value] || "gray";
			return `<span style="color:${color}; font-weight:bold;">
                        ${value || ""}
                    </span>`;
		},
	},

	button: {
		show: function (doc) {
			return doc.status === "In Repair";
		},
		get_label: function () {
			return "Mark Ready";
		},
		get_description: function (doc) {
			return "Mark " + doc.name + " as Ready for Delivery";
		},
		action: function (doc) {
			frappe.call({
				method: "quickfix.api.mark_ready_for_delivery",
				args: { job_card: doc.name },
				callback: function (r) {
					if (!r.exc) {
						frappe.show_alert({
							message: doc.name + " marked as Ready for Delivery",
							indicator: "green",
						});
						cur_list.refresh();
					}
				},
			});
		},
	},
};
