// add a button 'Mark as Paid' to the 'Payment Request' form
// the button will set the Status field to 'Paid'
frappe.ui.form.on('Payment Request', {
	refresh: function (frm) {
		frm.add_custom_button(__('Mark as Paid'), function () {
			frappe.call({
				method: 'jailbreak.jailbreak.hooks.api.mark_payment_request_as_paid',
				args: {
					payment_request_name: frm.doc.name
				},
				callback: function (response) {
					if (response.message) {
						frappe.msgprint(response.message);
					}
				}
			});
		});
		if (
			frm.doc.payment_request_type == 'Inward' &&
			frm.doc.payment_channel !== 'Phone' &&
			!['Initiated', 'Paid'].includes(frm.doc.status) &&
			!frm.doc.__islocal &&
			frm.doc.docstatus == 1
		) {
			frm.add_custom_button(__('Re-Initiate Charge'), function () {
				frappe.call({
					method: 'jailbreak.jailbreak.hooks.api.reinitiate_payment_request_charge',
					args: {
						payment_request_name: frm.doc.name
					},
					freeze: true,
					freeze_message: __('Re-initiating charge...'),
					callback: function (response) {
						if (response.message) {
							frappe.show_alert({
								message: "Charge re-initiated successfully",
								indicator: 'green'
							});
							// refresh the form
							frm.reload_doc();
						}
					}
				});
			});
		}
	}
});