# Copyright (c) 2025, Avunu LLC and contributors
# For license information, please see license.txt

from typing import Literal

import frappe
from frappe import _
from frappe.model.document import Document

capability_name = Literal[
	"global_bulk_merge", "global_unsubmit", "item_convert_to_variant", "version_restore"
]

capabilities = {
	"global_bulk_merge": "Bulk Merge",
	"global_unsubmit": "Unsubmit",
	"item_convert_to_variant": "Convert to Variant",
	"version_restore": "Version Restore",
}


class JailbreakSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		global_bulk_merge: DF.Check
		global_unsubmit: DF.Check
		item_convert_to_variant: DF.Check
		version_restore: DF.Check
	# end: auto-generated types
	pass


@frappe.whitelist()
def check_capability(capability: capability_name) -> bool:
	"""
	Check if a jailbreak capability is enabled (for frontend use).

	:param capability: The capability to check.
	:type capability: capability_name
	:return: True if the capability is enabled, False otherwise.
	:rtype: bool
	"""
	try:
		settings: JailbreakSettings = frappe.get_cached_doc("Jailbreak Settings")  # type: ignore
	except frappe.DoesNotExistError:
		return False

	if capability not in capabilities:
		return False

	return bool(getattr(settings, capability, False))


@frappe.whitelist()
def assert_capability(capability: capability_name) -> None:
	"""
	Check if a jailbreak capability is enabled prior to exposing or using it.

	:param capability: The capability to check.
	:type capability: capability_names
	:raises frappe.PermissionError: If the capability is not enabled.
	:raises frappe.DoesNotExistError: If the Jailbreak Settings document does not exist.
	:raises frappe.ValidationError: If the capability is not recognized.
	"""
	settings: JailbreakSettings
	try:
		settings = frappe.get_cached_doc("Jailbreak Settings")  # type: ignore
	except frappe.DoesNotExistError:
		frappe.throw(
			_("Jailbreak Settings document does not exist."),
			exc=frappe.DoesNotExistError,
		)

	if capability not in capabilities:
		frappe.throw(_("Invalid capability: {0}").format(capability), exc=frappe.ValidationError)

	# Check if the capability is enabled
	if not getattr(settings, capability, False):
		capability_label = capabilities.get(capability, capability)
		frappe.throw(
			_("The {0} capability is not enabled.").format(capability_label),
			exc=frappe.PermissionError,
		)
