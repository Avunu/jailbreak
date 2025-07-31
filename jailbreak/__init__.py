__version__ = "0.0.1"

import frappe

from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import (
	assert_capability,
	capability_name,
	check_capability,
)


@frappe.whitelist()
def assert_jailbreak_capability(capability: capability_name) -> None:
	return assert_capability(capability)


@frappe.whitelist()
def check_jailbreak_capability(capability: capability_name) -> bool:
	"""
	Check if a jailbreak capability is enabled (for frontend use).

	:param capability: The capability to check.
	:type capability: capability_name
	:return: True if the capability is enabled, False otherwise.
	:rtype: bool
	"""
	return check_capability(capability)
