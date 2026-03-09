import frappe
from frappe.utils import now


def log_login(login_manager):
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"document_name": frappe.session.user,
			"action": "login",
			"user": frappe.session.user,
			"timestamp": now(),
		}
	).insert(ignore_permissions=True)


def log_logout(login_manager):
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"document_name": frappe.session.user,
			"action": "logout",
			"user": frappe.session.user,
			"timestamp": now(),
		}
	).insert(ignore_permissions=True)
