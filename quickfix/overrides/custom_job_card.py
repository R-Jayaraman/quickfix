import frappe

from quickfix.service_center.doctype.job_card.job_card import JobCard


class CustomJobCard(JobCard):
	"""
	About MRO (Method Resolution Order)

	Python follows a specific order when looking for methods in inherited classes.
	For this controller the order is roughly:

	CustomJobCard - JobCard - Document -  Base classes

	When validate() runs, it first executes the method in this class.
	Calling super().validate() makes sure the original JobCard validation
	still runs before our custom logic.

	If we skip super(), the validations written in JobCard (like phone checks,
	price calculations, etc.) would not run, which could allow bad data
	to be saved.
	"""

	"""
    override_doctype_class vs doc_events

    override_doctype_class replaces the original controller with our custom one.
    This is useful when we need to extend or modify the internal logic
    of the DocType.

    doc_events is usually safer because it only attaches extra logic
    through hooks and does not replace the controller itself.

    In most cases doc_events is preferred, but override_doctype_class
    is useful when deeper customization is required.
    """

	def validate(self):
		super().validate()

		self._check_urgent_unassigned()

	def _check_urgent_unassigned(self):
		if self.priority == "Urgent" and not self.assigned_technician:
			settings = frappe.get_single("QuickFix Settings")

			frappe.enqueue(
				"quickfix.utils.send_urgent_alert", job_card=self.name, manager=settings.manager_email
			)
