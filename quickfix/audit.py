import frappe


def audit_log(doc, method):
	if doc.doctype == "Audit Log":
		return
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doc.doctype,
			"document_name": doc.name,
			"action": method,
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}
	).insert(ignore_permissions=True)
