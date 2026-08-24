# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.journal_entry`'s two functions."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.hooks.journal_entry import (
	manually_clear_journal_entry,
	remove_clearance_date_journal_entry,
)
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_cleared_journal_entry, make_journal_entry, set_capability


class TestManuallyClearJournalEntry(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		je = make_cleared_journal_entry()
		set_capability("journal_entry_manually_clear", 0)

		with self.assertRaises(frappe.PermissionError):
			manually_clear_journal_entry(je.name)

	def test_clears_against_the_matching_bank_transaction_date(self):
		je = make_cleared_journal_entry(clearance_date="2020-02-02")

		with self.capability_enabled("journal_entry_manually_clear"):
			result = manually_clear_journal_entry(je.name)

		self.assertEqual(result, f"Journal Entry {je.name} cleared to 2020-02-02.")
		self.assertEqual(str(frappe.db.get_value("Journal Entry", je.name, "clearance_date")), "2020-02-02")

	def test_no_matching_bank_transaction_reports_none_found(self):
		je = make_journal_entry()  # no Bank Transaction references it

		with self.capability_enabled("journal_entry_manually_clear"):
			result = manually_clear_journal_entry(je.name)

		self.assertEqual(result, "No matching bank transaction found.")
		self.assertIsNone(frappe.db.get_value("Journal Entry", je.name, "clearance_date"))


class TestRemoveClearanceDateJournalEntry(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		je = make_journal_entry()
		frappe.db.set_value("Journal Entry", je.name, "clearance_date", "2020-02-02")
		set_capability("journal_entry_remove_clearance", 0)

		with self.assertRaises(frappe.PermissionError):
			remove_clearance_date_journal_entry(je.name)

	def test_removes_an_existing_clearance_date(self):
		je = make_journal_entry()
		frappe.db.set_value("Journal Entry", je.name, "clearance_date", "2020-02-02")

		with self.capability_enabled("journal_entry_remove_clearance"):
			result = remove_clearance_date_journal_entry(je.name)

		self.assertEqual(result, f"Journal Entry {je.name} clearance date removed.")
		self.assertIsNone(frappe.db.get_value("Journal Entry", je.name, "clearance_date"))
