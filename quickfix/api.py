import frappe

@frappe.whitelist()
def get_job_summary():
    return {
        "message": "API is working",
        "status": "success"
    }

@frappe.whitelist()
def test_error():
    1 / 0   # This will cause a Python exception