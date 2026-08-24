# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.bulk_merge` (`hooks/__init__.py`) - a thin
capability-gated wrapper around Frappe's own `bulk_rename`. Not one of the
5 hook modules the plan names by file, but it lives in the same package and
is whitelisted, destructive, and untested."""

from __future__ import annotations

import json

import frappe

from jailbreak.jailbreak.hooks import bulk_merge
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_item, set_capability


class TestBulkMerge(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		item = make_item("_JB Test Bulk Guard")
		set_capability("global_bulk_merge", 0)

		with self.assertRaises(frappe.PermissionError):
			bulk_merge("Item", json.dumps([[item.name, "_JB Test Bulk Guard Renamed"]]))

	def test_renames_the_document(self):
		item = make_item("_JB Test Bulk Old")

		with self.capability_enabled("global_bulk_merge"):
			result = bulk_merge("Item", json.dumps([[item.name, "_JB Test Bulk New"]]))

		self.assertEqual(result, [f"Successful: {item.name} to _JB Test Bulk New"])
		self.assertTrue(frappe.db.exists("Item", "_JB Test Bulk New"))
		self.assertFalse(frappe.db.exists("Item", item.name))
