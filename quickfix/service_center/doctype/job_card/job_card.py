import frappe
from frappe.model.document import Document


class JobCard(Document):
	def validate(self):
		self.phone_number_validate()
		self.validate_technician_required()
		self.calculate_parts_total()
		self.set_default_labour_charge()
		self.calculate_final_amount()

	def validate_technician_required(self):
		if self.status in ["In Repair", "Ready for Delivery", "Delivered"]:
			if not self.assigned_technician:
				frappe.throw("Assigned Technician is required")

	def calculate_parts_total(self):
		parts_total = 0

		for row in self.parts_used:
			row.total_price = (row.quantity or 0) * (row.unit_price or 0)
			parts_total += row.total_price

		self.parts_total = parts_total

	def set_default_labour_charge(self):
		if not self.labour_charge:
			settings = frappe.get_single("QuickFix Settings")
			self.labour_charge = settings.default_labour_charge or 0

	def calculate_final_amount(self):
		self.final_amount = self.parts_total + self.labour_charge

	def before_submit(self):
		self.validate_ready_status()
		self.check_stock_availability()

	def validate_ready_status(self):
		if self.status != "Ready for Delivery":
			frappe.throw("Job Card must be Ready for Delivery to submit")

	def check_stock_availability(self):
		for row in self.parts_used:
			stock = frappe.db.get_value("Spare Part", row.part, "stock_qty") or 0

			if stock < row.quantity:
				frappe.throw(f"Not enough stock for part {row.part}. Available: {stock}")

	def on_submit(self):
		self.deduct_stock()
		self.create_service_invoice()
		self.send_realtime_notification()
		self.enqueue_email_job()

	def deduct_stock(self):
		for row in self.parts_used:
			stock = frappe.db.get_value("Spare Part", row.part, "stock_qty") or 0
			new_stock = stock - row.quantity

			frappe.db.set_value("Spare Part", row.part, "stock_qty", new_stock, update_modified=False)

	def create_service_invoice(self):
		invoice = frappe.get_doc(
			{
				"doctype": "Service Invoice",
				"job_card": self.name,
				"labour_charge": self.labour_charge,
				"parts_total": self.parts_total,
				"total_amount": self.final_amount,
				"payment_status": "Unpaid",
			}
		)

		invoice.insert(ignore_permissions=True)

	def send_realtime_notification(self):
		frappe.publish_realtime("job_ready", {"job_card": self.name}, user=self.owner)

	def enqueue_email_job(self):
		frappe.enqueue("quickfix.api.send_job_ready_email", job_card=self.name, queue="short")

	def on_cancel(self):
		self.set_cancelled_status()
		self.restore_stock()
		self.cancel_linked_invoice()

	def set_cancelled_status(self):
		frappe.db.set_value("Job Card", self.name, "status", "Cancelled")

	def restore_stock(self):
		for row in self.parts_used:
			stock = frappe.db.get_value("Spare Part", row.part, "stock_qty") or 0
			frappe.db.set_value("Spare Part", row.part, "stock_qty", stock + row.quantity)

	def cancel_linked_invoice(self):
		invoices = frappe.get_all(
			"Service Invoice", filters={"job_card": self.name}, fields=["name", "docstatus"]
		)

		for inv in invoices:
			invoice = frappe.get_doc("Service Invoice", inv.name)
			if invoice.docstatus == 1:
				invoice.cancel()

	def on_trash(self):
		if self.status not in ["Draft", "Cancelled"]:
			frappe.throw("Only Draft or Cancelled Job Cards can be deleted")

	def phone_number_validate(self):
		if self.customer_phone and len(self.customer_phone) != 10:
			frappe.throw("Customer phone must be exactly 10 digits")

	def before_print(self, print_settings=None):
		self.print_summary = f"{self.customer_name} - {self.device_brand} {self.device_model}"


@frappe.whitelist()
def mark_as_delivered(job_card_name):
	doc = frappe.get_doc("Job Card", job_card_name)

	if doc.status != "Ready for Delivery":
		frappe.throw("Job must be Ready for Delivery before marking Delivered")

	doc.status = "Delivered"
	doc.save()


@frappe.whitelist()
def transfer_technician(job_card_name, technician):
	doc = frappe.get_doc("Job Card", job_card_name)

	tech_device_type = frappe.db.get_value("Technician", technician, "specialization")

	if tech_device_type != doc.device_type:
		frappe.throw(f"This technician handles {tech_device_type} devices only.")

	doc.assigned_technician = technician
	doc.save()

	frappe.msgprint("Technician transferred successfully")
