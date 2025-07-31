__version__ = "0.0.1"

import frappe

from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import (
	assert_capability,
	capability_name,
)


@frappe.whitelist()
def assert_jailbreak_capability(capability: capability_name) -> None:
	return assert_capability(capability)
