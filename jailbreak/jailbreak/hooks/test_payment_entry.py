# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.payment_entry.set_clearance_date`."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.hooks.payment_entry import set_clearance_date
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_payment_entry, set_capability


class TestSetClearanceDate(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		pe = make_payment_entry()
		set_capability("payment_entry_set_clearance_date", 0)

		with self.assertRaises(frappe.PermissionError):
			set_clearance_date(pe.name, "2021-06-15")

	def test_sets_the_clearance_date(self):
		pe = make_payment_entry()

		with self.capability_enabled("payment_entry_set_clearance_date"):
			result = set_clearance_date(pe.name, "2021-06-15")

		self.assertEqual(result, f"Payment Entry {pe.name} clearance date set to 2021-06-15.")
		self.assertEqual(str(frappe.db.get_value("Payment Entry", pe.name, "clearance_date")), "2021-06-15")
