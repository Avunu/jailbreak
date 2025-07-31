import frappe
import json
from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import assert_capability
from frappe import _


@frappe.whitelist()
def bulk_merge(doctype, rows):
    # Check if global bulk merge capability is enabled
    assert_capability("global_bulk_merge")
    
    from frappe.model.rename_doc import bulk_rename

    rows = json.loads(rows)

    return bulk_rename(doctype, rows)
