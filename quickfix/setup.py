import frappe


def install():
	device_types = ["Mobile", "Laptop", "Tablet"]

	for dt in device_types:
		if not frappe.db.exists("Device Type", dt):
			frappe.get_doc({"doctype": "Device Type", "device_type": dt}).insert()

	frappe.make_property_setter("Job Card", "remarks", "bold", 1, "Check")
	print("Device Types created and Property Setter applied successfully.")


def create_settings():
	if not frappe.db.exists("QuickFix Settings"):
		frappe.get_doc(
			{
				"doctype": "QuickFix Settings",
				"shop_name": "QuickFix Repair Center",
				"manager_email": "manager@quickfix.com",
			}
		).insert()
	print("QuickFix Settings created successfully.")


def uninstall_check():
	if frappe.db.exists("Job Card", {"docstatus": 1}):
		raise frappe.ValidationError("Cannot uninstall QuickFix. Submitted Job Cards exist.")
	print("QuickFix Settings created successfully.")


def extend_bootinfo(bootinfo):
	settings = frappe.get_single("QuickFix Settings")

	bootinfo.quickfix_shop_name = settings.shop_name
	bootinfo.quickfix_manager_email = settings.manager_email
	print("Bootinfo extended with QuickFix Settings.")
