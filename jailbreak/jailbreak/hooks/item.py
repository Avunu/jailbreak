from typing import TYPE_CHECKING

import frappe
from frappe import _

from jailbreak import assert_jailbreak_capability

if TYPE_CHECKING:
	from erpnext.stock.doctype.item.item import Item


@frappe.whitelist()
def convert_to_variant(item: str, template: str, attribute_values: dict) -> bool:
	# Check if the item convert to variant capability is enabled
	assert_jailbreak_capability("item_convert_to_variant")

	try:
		# Parse attribute_values if it's a string
		if isinstance(attribute_values, str):
			import json

			attribute_values = json.loads(attribute_values)

		# Update variant fields
		frappe.db.set_value("Item", item, "variant_of", template)

		# Get the source item and template
		item_doc: Item = Item("Item", item)
		template_doc: Item = Item("Item", template)

		# Clear existing attributes
		item_doc.attributes = []

		# Add all attributes from the template with their values
		for template_attribute in template_doc.attributes:
			attribute_name = template_attribute.attribute

			# Get the attribute value from the submitted values
			# The key in attribute_values is in format "attribute_NAME"
			attribute_value = attribute_values.get(attribute_name)

			if attribute_value:
				item_doc.append(
					"attributes",
					{"attribute": attribute_name, "attribute_value": attribute_value},
				)

		# Handle UOM conversion
		if item_doc.stock_uom != template_doc.stock_uom:
			old_stock_uom = item_doc.stock_uom
			item_doc.stock_uom = template_doc.stock_uom
			item_doc.sales_uom = old_stock_uom

		item_doc.save()
		frappe.db.commit()

		return True

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Item to Variant Conversion Error"))
		frappe.throw(_("Error converting item to variant: {0}").format(str(e)))
		return False
