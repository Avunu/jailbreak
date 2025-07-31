/* global jailbreak */

// add a button "Calculate Outstanding Amount" to the "Sales Invoice" form
// the button will calculate the outstanding amount based on the total and the payments
frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		// Check if sales invoice calculate outstanding capability is enabled
		jailbreak.check_capability("sales_invoice_calculate_outstanding").then((enabled) => {
			if (enabled) {
				frm.add_custom_button(__('Calculate Outstanding Amount'), function() {
					frm.calculate_outstanding_amount();
				});
			}
		});
	}
});