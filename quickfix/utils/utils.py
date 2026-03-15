import base64
from datetime import date
from io import BytesIO

import frappe
import qrcode
from frappe.utils import now


def get_shop_name():
	settings = frappe.get_single("QuickFix Settings")
	return settings.shop_name


def generate_qr(data):
	img = qrcode.make(data)
	buffer = BytesIO()
	img.save(buffer, format="PNG")
	return base64.b64encode(buffer.getvalue()).decode()


def bulk_insert_logs():
	records = []

	for i in range(500):
		records.append(
			(frappe.generate_hash(), "Job Card", f"JOB-{i}", "bulk_test", frappe.session.user, now())
		)

	frappe.db.bulk_insert(
		"Audit Log",
		fields=["name", "doctype_name", "document_name", "action", "user", "timestamp"],
		values=records,
	)

	frappe.db.commit()


@frappe.whitelist()
def get_job_summary():
	job_card_name = frappe.form_dict.get("job_card_name")
	if not frappe.db.exists("Job Card", job_card_name):
		frappe.local.response["http_status_code"] = 404
		return {"error": "Not found"}

	job = frappe.get_doc("Job Card", job_card_name)
	today = date.today()
	return {
		"job_card": job.name,
		"customer_name": job.customer_name,
		"status": job.status,
		"final_amount": job.final_amount,
		"today": today,
	}
