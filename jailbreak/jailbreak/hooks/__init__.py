import json

import frappe
from frappe import _

from jailbreak import assert_jailbreak_capability


@frappe.whitelist()
def bulk_merge(doctype, rows):
	# Check if global bulk merge capability is enabled
	assert_jailbreak_capability("global_bulk_merge")

	from frappe.model.rename_doc import bulk_rename

	rows = json.loads(rows)

	return bulk_rename(doctype, rows)
