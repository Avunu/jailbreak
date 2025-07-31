import json

import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def bulk_merge(doctype, rows):
	# Check if global bulk merge capability is enabled
	assert_capability("global_bulk_merge")

	from frappe.model.rename_doc import bulk_rename

	rows = json.loads(rows)

	return bulk_rename(doctype, rows)


@frappe.whitelist()
def unsubmit_document(doctype, name):
	"""
	Unsubmit a document by changing its docstatus from 1 to 0.
	
	:param doctype: The doctype of the document to unsubmit
	:param name: The name of the document to unsubmit
	:return: Success message or raises exception
	"""
	# Check if user has unsubmit permission for this specific doctype
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import assert_unsubmit_permission
	assert_unsubmit_permission(doctype)
	
	# Get the document
	doc = frappe.get_doc(doctype, name)
	
	# Check if document is submitted
	if doc.docstatus != 1:
		frappe.throw(_("Document {0} is not in submitted state").format(name))
	
	# Check if user has permission to submit/unsubmit this document
	if not frappe.has_permission(doctype, "submit", doc):
		frappe.throw(_("Insufficient permissions to unsubmit {0} {1}").format(doctype, name))
	
	# Additional check: ensure the doctype supports submission
	meta = frappe.get_meta(doctype)
	if not meta.is_submittable:
		frappe.throw(_("DocType {0} does not support submission").format(doctype))
	
	# Unsubmit the document
	doc.docstatus = 0
	doc.add_comment("Workflow", _("Document unsubmitted via Jailbreak"))
	
	# Save without ignore_permissions to respect normal save validations
	doc.save()
	
	return {
		"success": True,
		"message": _("Document {0} has been unsubmitted successfully").format(name)
	}
