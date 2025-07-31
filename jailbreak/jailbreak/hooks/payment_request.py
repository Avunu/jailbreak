import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def mark_payment_request_as_paid(payment_request_name):
	"""Mark a payment request as paid."""
	# Check if the payment request mark as paid capability is enabled
	assert_capability("payment_request_mark_as_paid")
	
	try:
		frappe.db.set_value('Payment Request', payment_request_name, 'status', 'Paid')
		frappe.db.commit()
		return f'Payment Request {payment_request_name} marked as paid.'
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Payment Request Mark as Paid Error"))
		frappe.throw(_("Error marking payment request as paid: {0}").format(str(e)))


@frappe.whitelist()
def reinitiate_payment_request_charge(payment_request_name):
	"""Re-initiate charge for a payment request."""
	# Check if the payment request reinitiate charge capability is enabled
	assert_capability("payment_request_reinitiate_charge")
	
	try:
		pr = frappe.get_doc('Payment Request', payment_request_name)
		return pr.payment_gateway_validation()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Payment Request Reinitiate Charge Error"))
		frappe.throw(_("Error reinitiating payment request charge: {0}").format(str(e)))