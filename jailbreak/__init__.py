__version__ = "0.0.1"

import frappe
from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import capability_name, assert_capability

@frappe.whitelist()
def assert_capability(capability: capability_name) -> None:
    return assert_capability(capability)