import frappe
from frappe.model.document import Document


class ServiceInvoice(Document):
	def on_update(self):
		self.update_job_card_payment()

	def update_job_card_payment(self):
		if self.payment_status == "Paid" and self.job_card:
			frappe.db.set_value("Job Card", self.job_card, {"payment_status": "Paid", "status": "Delivered"})
