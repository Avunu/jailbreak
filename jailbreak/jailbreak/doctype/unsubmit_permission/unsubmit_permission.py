# Copyright (c) 2025, Avunu LLC and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UnsubmitPermission(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		doctype_name: DF.Link
		role: DF.Link
	# end: auto-generated types

	pass