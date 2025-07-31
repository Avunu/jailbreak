import frappe


@frappe.whitelist()
def manually_clear_journal_entry(journal_entry_name):
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


@frappe.whitelist()
def remove_clearance_date_journal_entry(journal_entry_name):
	frappe.db.set_value('Journal Entry', journal_entry_name, 'clearance_date', None)
	frappe.db.commit()
	return f'Journal Entry {journal_entry_name} clearance date removed.'


@frappe.whitelist()
def change_bank_transaction_date(bank_transaction_name, date):
	frappe.db.set_value('Bank Transaction', bank_transaction_name, 'date', date)
	frappe.db.commit()
	return f'Bank Transaction {bank_transaction_name} date changed to {date}.'


@frappe.whitelist()
def mark_payment_request_as_paid(payment_request_name):
	frappe.db.set_value('Payment Request', payment_request_name, 'status', 'Paid')
	frappe.db.commit()


@frappe.whitelist()
def reinitiate_payment_request_charge(payment_request_name):
	pr = frappe.get_doc('Payment Request', payment_request_name)
	return pr.payment_gateway_validation()


@frappe.whitelist()
def set_clearance_date(payment_entry_name, clearance_date):
	frappe.db.set_value('Payment Entry', payment_entry_name, 'clearance_date', clearance_date)
	frappe.db.commit()
	return f'Payment Entry {payment_entry_name} clearance date set to {clearance_date}.'
