from datetime import datetime, timedelta

import frappe
from frappe.query_builder import DocType


@frappe.whitelist()
def get_job_summary():
	return {"message": "API is working", "status": "success"}


@frappe.whitelist()
def test_error():
	1 / 0


@frappe.whitelist()
def get_job(name):
	return frappe.get_doc("Job Card", name)


@frappe.whitelist()
def get_overdue_jobs():
	JC = DocType("Job Card")

	seven_days_ago = datetime.now() - timedelta(days=7)

	result = (
		frappe.qb.from_(JC)
		.select(JC.name, JC.status, JC.creation)
		.where((JC.status.isin(["Draft", "Submitted"])) & (JC.creation < seven_days_ago))
		.orderby(JC.creation)
		.run(as_dict=True)
	)

	return result


@frappe.whitelist()
def transfer_job(from_tech, to_tech):
	try:
		frappe.db.sql(
			"""
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
            AND status IN ('Pending Diagnosis', 'In Repair')
        """,
			(to_tech, from_tech),
		)

		frappe.db.commit()

		return {"message": "Jobs transferred successfully"}

	except frappe.ValidationError:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Job Transfer Failed")
		raise


@frappe.whitelist()
def share_job_card(job_card_name, user_email):
	frappe.share.add(
		doctype="Job Card", name=job_card_name, user=user_email, read=1, write=0, share=0, everyone=0
	)
	return "Job Card shared successfully"


@frappe.whitelist()
def manager_only_action():
	frappe.only_for("QF Manager")
	return "You are authorized as Manager"


@frappe.whitelist()
def get_job_cards_safe():
	records = frappe.get_list("Job Card", fields=["name", "customer_name", "device_type", "status"])

	# Remove sensitive data for non-managers
	if "QF Manager" not in frappe.get_roles():
		for r in records:
			r.pop("customer_phone", None)
			r.pop("customer_email", None)

	return records


@frappe.whitelist()
def rename_technician(old_name, new_name):
	frappe.rename_doc("Technician", old_name, new_name, merge=False)

	return "Technician renamed successfully"


@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
	log = frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doctype,
			"action": "count_queried",
			"user": frappe.session.user,
		}
	)
	log.insert(ignore_permissions=True)
	frappe.db.commit()

	from frappe.client import get_count

	return get_count(doctype, filters, debug, cache)
