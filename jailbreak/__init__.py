__version__ = "0.0.1"

import frappe

from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import (
	capability_name,
)


@frappe.whitelist()
def assert_capability(capability: capability_name) -> None:
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import assert_capability as _assert_capability
	return _assert_capability(capability)


@frappe.whitelist()
def check_capability(capability: capability_name) -> bool:
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import check_capability as _check_capability
	return _check_capability(capability)


@frappe.whitelist()
def check_unsubmit_permission(doctype: str) -> bool:
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import check_unsubmit_permission as _check_unsubmit_permission
	return _check_unsubmit_permission(doctype)


@frappe.whitelist()
def assert_unsubmit_permission(doctype: str) -> None:
	from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import assert_unsubmit_permission as _assert_unsubmit_permission
	return _assert_unsubmit_permission(doctype)
