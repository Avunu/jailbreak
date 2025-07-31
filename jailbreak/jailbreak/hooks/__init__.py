import frappe
import json


@frappe.whitelist()
def bulk_merge(doctype, rows):
    from frappe.model.rename_doc import bulk_rename

    rows = json.loads(rows)

    return bulk_rename(doctype, rows)
