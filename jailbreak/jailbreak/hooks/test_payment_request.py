# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S1 coverage for `hooks.payment_request`'s two functions.

**Real bug found and fixed here, not pinned** - `mark_payment_request_as_paid`
called `assert_capability("payment_request_mark_as_paid")`, but the
capability is registered (in `jailbreak_settings.py`'s `capabilities` dict
and `capability_name` Literal, and in `public/js/payment_request.js`'s own
`check_capability` call) as `payment_request_mark_paid` - no "as". Every
call raised `ValidationError: Invalid capability: ...` before it ever
reached the enabled/disabled check, so no user could ever mark a payment
request paid through this button even with the capability turned on in
Jailbreak Settings. Fixed by matching the registered name; no product
decision involved, same class as `hooks.item`'s `NameError`."""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.hooks.payment_request import (
	mark_payment_request_as_paid,
	reinitiate_payment_request_charge,
)
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_payment_request, set_capability


class TestMarkPaymentRequestAsPaid(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		pr = make_payment_request()
		set_capability("payment_request_mark_paid", 0)

		with self.assertRaises(frappe.PermissionError):
			mark_payment_request_as_paid(pr.name)

	def test_marks_the_payment_request_paid(self):
		pr = make_payment_request()
		self.assertEqual(pr.status, "Draft")

		with self.capability_enabled("payment_request_mark_paid"):
			result = mark_payment_request_as_paid(pr.name)

		self.assertEqual(result, f"Payment Request {pr.name} marked as paid.")
		self.assertEqual(frappe.db.get_value("Payment Request", pr.name, "status"), "Paid")


class TestReinitiatePaymentRequestCharge(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		pr = make_payment_request()
		set_capability("payment_request_reinitiate_charge", 0)

		with self.assertRaises(frappe.PermissionError):
			reinitiate_payment_request_charge(pr.name)

	def test_no_payment_gateway_configured_returns_false(self):
		"""`payment_gateway_validation()` (vendored, `payments`/`erpnext`) swallows
		its own lookup failure and returns False when the Payment Request has
		no `payment_gateway` set - no outbound call happens, so nothing needs
		mocking here."""
		pr = make_payment_request()
		self.assertFalse(pr.payment_gateway)

		with self.capability_enabled("payment_request_reinitiate_charge"):
			result = reinitiate_payment_request_charge(pr.name)

		self.assertFalse(result)
