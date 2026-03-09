# quickfix/monkey_patches.py

"""
MONKEY PATCHES FOR QUICKFIX APP
=================================

Each patch is documented with:
- WHY it was needed
- WHAT it changes
- FRAPPE VERSION it was tested on
- RISK if frappe updates the patched function
- TEST that validates the patch still works
"""

import frappe


def apply_all():
	_patch_get_url()


def _patch_get_url():
	"""
	WHY: Site uses a custom CDN prefix stored in site_config.

	WHAT: Prepends custom_url_prefix to all generated URLs.

	VERSION TESTED: frappe v15.x

	RISK: If frappe.utils.get_url signature changes, this will fail.

	TEST: test_monkey_patches.py::TestGetUrl
	"""

	import frappe.utils as fu

	# guard: do not patch twice
	if hasattr(fu, "_qf_patched"):
		return

	_orig = fu.get_url

	def _custom_get_url(path=None, full_address=False):
		url = _orig(path, full_address)
		prefix = frappe.conf.get("custom_url_prefix", "")
		return prefix + url if prefix else url

	fu.get_url = _custom_get_url
	fu._qf_patched = True
