// add a button "Set Clearance Date" to the "Payment Entry" form
// the button will set the corresponding "clearance_date" field
frappe.ui.form.on('Payment Entry', {
	refresh: function (frm) {
		frm.add_custom_button(__('Set Clearance Date'), function () {
			// open a dialog to change the date
			frappe.prompt([
				{
					fieldname: 'clearance_date',
					fieldtype: 'Date',
					label: __('Clearance Date'),
					reqd: 1,
					default: frm.doc.clearance_date
				}
			], function (values) {
				// change the date
				frappe.call({
					method: 'jailbreak.jailbreak.hooks.api.set_clearance_date',
					args: {
						payment_entry_name: frm.doc.name,
						clearance_date: values.clearance_date
					},
					callback: function (response) {
						if (response.message) {
							frappe.msgprint(response.message);
						}
					}
				});
			}
			, __('Set Clearance Date'), __('Set'));
		});
	}
});