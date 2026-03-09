import frappe


def get_shop_name():
	settings = frappe.get_single("QuickFix Settings")
	return settings.shop_name
