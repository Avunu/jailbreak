# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.bank_transaction.change_bank_transaction_date`."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.hooks.bank_transaction import change_bank_transaction_date
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_bank_transaction, set_capability


class TestChangeBankTransactionDate(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		bt = make_bank_transaction()
		set_capability("bank_transaction_change_date", 0)

		with self.assertRaises(frappe.PermissionError):
			change_bank_transaction_date(bt.name, "2021-06-15")

	def test_changes_the_date_and_returns_a_confirmation(self):
		bt = make_bank_transaction(date="2020-01-01")

		with self.capability_enabled("bank_transaction_change_date"):
			result = change_bank_transaction_date(bt.name, "2021-06-15")

		self.assertEqual(result, f"Bank Transaction {bt.name} date changed to 2021-06-15.")
		self.assertEqual(str(frappe.db.get_value("Bank Transaction", bt.name, "date")), "2021-06-15")
