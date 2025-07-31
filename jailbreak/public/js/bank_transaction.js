// Add a button "Change Date" to the "Bank Transaction" form
// the button will change the "date" field of the corresponding journal entry
frappe.ui.form.on('Bank Transaction', {
	refresh: function (frm) {
		frm.add_custom_button(__('Change Date'), function () {
			// open a dialog to change the date
			frappe.prompt([
				{
					fieldname: 'date',
					fieldtype: 'Date',
					label: __('Date'),
					reqd: 1,
					default: frm.doc.date
				}
			], function (values) {
				// change the date
				frappe.call({
					method: 'jailbreak.jailbreak.hooks.api.change_bank_transaction_date',
					args: {
						bank_transaction_name: frm.doc.name,
						date: values.date
					},
					callback: function (response) {
						if (response.message) {
							frappe.msgprint(response.message);
						}
					}
				});
			}, __('Change Date'), __('Change'));
		});
	}
});