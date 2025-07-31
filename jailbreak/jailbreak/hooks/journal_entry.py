import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def manually_clear_journal_entry(journal_entry_name):
	"""Manually clear a journal entry by finding matching bank transaction."""
	# Check if the journal entry manually clear capability is enabled
	assert_capability("journal_entry_manually_clear")
	
	try:
		# find a matching bank transaction
		bank_transaction_date = frappe.db.get_value('Bank Transaction',
		                                            [['Bank Transaction Payments', 'payment_entry', '=', journal_entry_name]], 'date')
		if bank_transaction_date:
			# set the clearance date on the journal entry
			frappe.db.set_value('Journal Entry', journal_entry_name,
			                    'clearance_date', bank_transaction_date)
			frappe.db.commit()
			return f'Journal Entry {journal_entry_name} cleared to {bank_transaction_date}.'
		else:
			return 'No matching bank transaction found.'
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Journal Entry Manual Clear Error"))
		frappe.throw(_("Error manually clearing journal entry: {0}").format(str(e)))


@frappe.whitelist()
def remove_clearance_date_journal_entry(journal_entry_name):
	"""Remove clearance date from a journal entry."""
	# Check if the journal entry remove clearance capability is enabled
	assert_capability("journal_entry_remove_clearance")
	
	try:
		frappe.db.set_value('Journal Entry', journal_entry_name, 'clearance_date', None)
		frappe.db.commit()
		return f'Journal Entry {journal_entry_name} clearance date removed.'
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Journal Entry Remove Clearance Error"))
		frappe.throw(_("Error removing journal entry clearance date: {0}").format(str(e)))