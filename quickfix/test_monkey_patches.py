import unittest

import frappe
import frappe.utils as fu

from quickfix.monkey_patches import apply_all


class TestGetUrl(unittest.TestCase):
	def test_url_with_prefix(self):
		frappe.conf.custom_url_prefix = "https://cdn.example.com"

		apply_all()

		url = fu.get_url("/files/test.png")

		self.assertTrue(url.startswith("https://cdn.example.com"))

	def test_url_without_prefix(self):
		if hasattr(frappe.conf, "custom_url_prefix"):
			del frappe.conf.custom_url_prefix

		apply_all()

		url = fu.get_url("/files/test.png")

		self.assertIn("/files/test.png", url)
