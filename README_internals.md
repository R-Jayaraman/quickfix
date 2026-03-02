### /api/method/quickfix.api.get_job_summary

When this URL is called, Frappe treats it as a request to a Python function marked with @frappe.whitelist().

The request goes through Nginx → Gunicorn → WSGI → Frappe.
Frappe imports quickfix/api.py, runs get_job_summary(), and sends the returned data as JSON.

DocType REST API

### /api/resource/Job Card/JC-2024-0001

This uses Frappe’s built-in REST system.

Instead of custom code, Frappe directly fetches the “Job Card” document from the database.
Before sending data, it checks user permissions. If access is not allowed, it returns an error.

Website Route

### /track-job

This is not an API — it is a web page route.

Frappe looks inside the www folder of installed apps.
If track-job.py or track-job.html exists, it renders that page.
If nothing matches, a 404 error is shown.

### Security & Session
CSRF Token

X-Frappe-CSRF-Token protects POST requests from forgery attacks.
It is tied to the logged-in user session.
Missing or invalid token → request rejected (403).

### Session Data

frappe.session contains info like user ID and session ID.

In bench console, frappe.session.data may be empty because it is not a real browser session.

### Production Mode
developer_mode = 0

In production, detailed errors are hidden.
Users only see generic messages like “500: Uncaught Exception”.

Full errors are stored in log files:

- logs/web.error.log

- logs/worker.error.log

Admins can check these for debugging.

### Permission Checks

When frappe.get_doc() is called normally, Frappe verifies whether the current user can access that document.

If not allowed → PermissionError → request stops.

Permission checks happen at the ORM level, protecting database records.

### Database & ORM Basics

Each DocType becomes a table named:

tab<DocType Name>

Example:
Job Card → tabJob Card

### DocStatus Values

0 → Draft (editable)

1 → Submitted (locked)

2 → Cancelled (invalid)

Frappe also prevents overwriting changes if another user modified the document meanwhile.

### Document Validation Example

Inside validate() you can compute values:

``` self.total = sum(r.amount for r in self.items)```

Updating another document inside validate must be done carefully, since save operations are already in progress.

### Child Table Behavior

When adding a child row, Frappe auto-fills:

parent — parent document name

parenttype — parent DocType

parentfield — field name in parent

idx — row order

If a row is deleted, idx values are automatically rearranged without gaps.

### Rename & Tracking
Renaming Linked Documents

If a document is renamed using Frappe’s rename feature, all linked fields across the system update automatically.

Track Changes

Enabling Track Changes stores edit history:

changed fields

old vs new values

who changed

when

Saved in Version records and shown in timeline.

### Unique Constraints
Unique Field Property

Setting a field as Unique enforces uniqueness at the database level.
No duplicates allowed — safest method.

Manual Check in validate()

Using frappe.db.exists() checks duplicates in Python code.
It is slower and can be bypassed in some cases, but useful for conditional rules.

Roles, Permissions & Sharing

Permissions can be exported as fixtures for deployment using:

fixtures = ["Role", "Custom DocPerm"]
Sharing a Document via Code

Example: share a Job Card with another user (read access only):

```python
frappe.share.add(
    doctype="Job Card",
    name=job_card_name,
    user=user_email,
    read=1
)
```
### Advanced Permission Control
permission_query_conditions

Custom filters can restrict what records a role can see.
Example: technicians can view only job cards assigned to them.

has_permission

Used for document-level access logic.
Example: block invoice access if payment is not completed (except managers).

### Safe vs Unsafe Data Retrieval
Unsafe — frappe.get_all

Returns records without permission checks.
If exposed in APIs, it can leak sensitive data.

### Safe — frappe.get_list

Respects:

role permissions

custom filters

sharing rules

Recommended for public or whitelisted methods.

### Why merge=True Is Risky
When merge=True is used, the old document is combined into another one and then removed.

Problems this can cause:

Original record is permanently lost

All links now point to a different document

Conflicting data may overwrite existing info

Past records may become inaccurate

Because of this, merging should only be done when both records actually refer to the same real person or item.