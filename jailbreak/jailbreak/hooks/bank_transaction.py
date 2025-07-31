import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def change_bank_transaction_date(bank_transaction_name, date):
	"""Change the date of a bank transaction."""
	# Check if the bank transaction change date capability is enabled
	assert_capability("bank_transaction_change_date")
	
	try:
		frappe.db.set_value('Bank Transaction', bank_transaction_name, 'date', date)
		frappe.db.commit()
		return f'Bank Transaction {bank_transaction_name} date changed to {date}.'
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Bank Transaction Change Date Error"))
		frappe.throw(_("Error changing bank transaction date: {0}").format(str(e)))