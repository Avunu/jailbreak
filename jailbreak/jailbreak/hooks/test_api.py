# Copyright (c) 2025, Avunu LLC and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAccountingJailbreaks(FrappeTestCase):
	def test_api_methods_exist(self):
		"""Test that all API methods are properly exposed"""
		from jailbreak.jailbreak.hooks import api

		# Check that all required methods exist
		self.assertTrue(hasattr(api, 'manually_clear_journal_entry'))
		self.assertTrue(hasattr(api, 'remove_clearance_date_journal_entry'))
		self.assertTrue(hasattr(api, 'change_bank_transaction_date'))
		self.assertTrue(hasattr(api, 'mark_payment_request_as_paid'))
		self.assertTrue(hasattr(api, 'reinitiate_payment_request_charge'))
		self.assertTrue(hasattr(api, 'set_clearance_date'))

	def test_api_methods_are_whitelisted(self):
		"""Test that all API methods are properly whitelisted"""
		# These should not raise exceptions when called via frappe.call
		methods = [
			'jailbreak.jailbreak.hooks.api.manually_clear_journal_entry',
			'jailbreak.jailbreak.hooks.api.remove_clearance_date_journal_entry',
			'jailbreak.jailbreak.hooks.api.change_bank_transaction_date',
			'jailbreak.jailbreak.hooks.api.mark_payment_request_as_paid',
			'jailbreak.jailbreak.hooks.api.reinitiate_payment_request_charge',
			'jailbreak.jailbreak.hooks.api.set_clearance_date',
		]

		for method in methods:
			# Check if method is whitelisted (should not raise PermissionError)
			self.assertTrue(frappe.is_whitelisted(method))
