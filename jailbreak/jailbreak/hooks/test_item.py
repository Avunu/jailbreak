# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.item.convert_to_variant`.

**Real bug found and fixed here, not pinned** - unlike the other tiers'
findings, this one needed no product decision. `item_doc`/`template_doc`
were built with `Item("Item", item)`, but `Item` was only imported under
`if TYPE_CHECKING:` - at runtime that name does not exist, so *every* call
to `convert_to_variant` raised `NameError: name 'Item' is not defined`,
caught by the function's own `except Exception`, logged, and re-thrown as
"Error converting item to variant: name 'Item' is not defined". This
function has never worked. Fixed by loading through `frappe.get_doc` (cast
to `Item` for typing, per Class-Based Architecture.md), which is what
`test_convert_to_variant_actually_converts_the_item` below now proves
against a real document read back from the database."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.hooks.item import convert_to_variant
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_item, make_item_template, set_capability


class TestConvertToVariant(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		item = make_item("_JB Test Convert Guard")
		template = make_item_template()
		set_capability("item_convert_to_variant", 0)

		with self.assertRaises(frappe.PermissionError):
			convert_to_variant(item.name, template.name, {"Colour": "Red"})

	def test_convert_to_variant_actually_converts_the_item(self):
		item = make_item("_JB Test Convert Real", stock_uom="Box")
		template = make_item_template()

		with self.capability_enabled("item_convert_to_variant"):
			self.assertTrue(convert_to_variant(item.name, template.name, {"Colour": "Red"}))

		converted = frappe.get_doc("Item", item.name)
		self.assertEqual(converted.variant_of, template.name)
		# UOM is swapped from the template, and the item's original stock_uom
		# becomes its sales_uom - see convert_to_variant's UOM-conversion step.
		self.assertEqual(converted.stock_uom, template.stock_uom)
		self.assertEqual(converted.sales_uom, "Box")
		self.assertEqual(
			[(a.attribute, a.attribute_value) for a in converted.attributes], [("Colour", "Red")]
		)

	def test_missing_attribute_value_is_skipped_not_errored(self):
		"""A template attribute absent from `attribute_values` is a no-op on
		that row rather than a crash - `attribute_values.get(...)` returning
		falsy just skips the `append`. Two attributes so the item still ends
		up with a non-empty attribute table (`Item.validate()` requires one
		for a variant), and only the provided one shows up."""
		item = make_item("_JB Test Convert Partial")
		template = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "_JB Test Two-Attribute Template",
				"item_name": "_JB Test Two-Attribute Template",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"has_variants": 1,
				"attributes": [{"attribute": "Colour"}, {"attribute": "Size"}],
			}
		)
		if not frappe.db.exists("Item", template.item_code):
			template.insert(ignore_permissions=True)
		else:
			template = frappe.get_doc("Item", template.item_code)

		with self.capability_enabled("item_convert_to_variant"):
			self.assertTrue(convert_to_variant(item.name, template.name, {"Colour": "Red"}))

		converted = frappe.get_doc("Item", item.name)
		self.assertEqual(converted.variant_of, template.name)
		self.assertEqual(
			[(a.attribute, a.attribute_value) for a in converted.attributes], [("Colour", "Red")]
		)
