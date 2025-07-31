__version__ = "0.0.1"

import frappe

from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import (
	assert_capability,
	check_capability,
	capability_name,
	check_capability,
)


@frappe.whitelist()
def assert_jailbreak_capability(capability: capability_name) -> None:
	return assert_capability(capability)


@frappe.whitelist()
def check_capability(capability: capability_name) -> bool:
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import check_capability as _check_capability
	return _check_capability(capability)
