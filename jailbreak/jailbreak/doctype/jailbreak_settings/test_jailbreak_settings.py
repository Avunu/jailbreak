# Copyright (c) 2025, Avunu LLC and Contributors
# See license.txt

"""S1 coverage for the two functions every other whitelisted function in this
app calls first: `assert_capability`/`check_capability`. Also covers the
identical top-level wrappers in `jailbreak/__init__.py`, since that is the
path every JS caller actually goes through (`jailbreak.check_capability`,
`jailbreak.assert_capability`)."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.doctype.jailbreak_settings.jailbreak_settings import (
	assert_capability,
	check_capability,
)
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import set_capability


class TestCheckCapability(JailbreakIntegrationTestCase):
	def test_disabled_capability_is_false(self):
		set_capability("version_restore", 0)
		self.assertFalse(check_capability("version_restore"))

	def test_enabled_capability_is_true(self):
		with self.capability_enabled("version_restore"):
			self.assertTrue(check_capability("version_restore"))

	def test_unknown_capability_is_false_not_an_error(self):
		self.assertFalse(check_capability("not_a_real_capability"))


class TestAssertCapability(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		set_capability("bank_transaction_change_date", 0)
		with self.assertRaises(frappe.PermissionError):
			assert_capability("bank_transaction_change_date")

	def test_enabled_capability_does_not_raise(self):
		with self.capability_enabled("bank_transaction_change_date"):
			self.assertIsNone(assert_capability("bank_transaction_change_date"))

	def test_unknown_capability_raises_validation_error(self):
		with self.assertRaises(frappe.ValidationError):
			assert_capability("not_a_real_capability")


class TestTopLevelWrappers(JailbreakIntegrationTestCase):
	"""`jailbreak/__init__.py`'s `assert_capability`/`check_capability` are
	the actual whitelisted entry points every JS caller reaches
	(`jailbreak.check_capability` in `frappe.call`) - they just delegate to
	the module above, but that delegation is worth pinning on its own."""

	def test_wrapper_check_capability_delegates(self):
		import jailbreak

		with self.capability_enabled("bank_transaction_change_date"):
			self.assertTrue(jailbreak.check_capability("bank_transaction_change_date"))

	def test_wrapper_assert_capability_delegates(self):
		import jailbreak

		set_capability("bank_transaction_change_date", 0)
		with self.assertRaises(frappe.PermissionError):
			jailbreak.assert_capability("bank_transaction_change_date")
