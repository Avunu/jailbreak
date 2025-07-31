import frappe
from frappe import _

from jailbreak import assert_jailbreak_capability


@frappe.whitelist()
def set_clearance_date(payment_entry_name, clearance_date):
	"""Set clearance date for a payment entry."""
	# Check if the payment entry set clearance date capability is enabled
	assert_jailbreak_capability("payment_entry_set_clearance_date")
	
	try:
		frappe.db.set_value('Payment Entry', payment_entry_name, 'clearance_date', clearance_date)
		frappe.db.commit()
		return f'Payment Entry {payment_entry_name} clearance date set to {clearance_date}.'
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Payment Entry Set Clearance Date Error"))
		frappe.throw(_("Error setting payment entry clearance date: {0}").format(str(e)))