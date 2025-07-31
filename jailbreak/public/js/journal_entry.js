// add a button "Manually Clear" to the "Journal Entry" form
// the button will find a matching bank transaction and set the corresponding "clearance_date" field
frappe.ui.form.on('Journal Entry', {
	refresh: function (frm) {
		frm.add_custom_button(
			__('Manually Clear'),
			function () {
				// find a matching bank transaction
				frappe.call({
					method: 'jailbreak.jailbreak.hooks.api.manually_clear_journal_entry',
					args: {
						journal_entry_name: frm.doc.name
					},
					callback: function (response) {
						if (response.message) {
							frappe.msgprint(response.message);
						}
					}
				});
			},
			__("Actions")
		);
		frm.add_custom_button(
			__('Remove Clearance'),
			function () {
				// find a matching bank transaction
				frappe.call({
					method: 'jailbreak.jailbreak.hooks.api.remove_clearance_date_journal_entry',
					args: {
						journal_entry_name: frm.doc.name
					},
					callback: function (response) {
						if (response.message) {
							frappe.msgprint(response.message);
						}
					}
				});
			},
			__("Actions")
		);
	}
});