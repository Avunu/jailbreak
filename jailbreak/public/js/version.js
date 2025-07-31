// Copyright (c) 2016, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Version", {
	refresh: function (frm) {
		// Check if version restore capability is enabled
		jailbreak.assert_capability('version_restore')
			.then(() => {
				if (frm.doc.restored) {
					frm.add_custom_button(__("Open"), function () {
						frappe.set_route("Form", frm.doc.deleted_doctype, frm.doc.new_name);
					});
				} else {
					frm.add_custom_button(__("Restore"), function () {
						frm.call({
							method: "restore",
							doc: frm.doc,
							callback: function (r) {
								frm.reload_doc();
							},
						});
					});
				}
			})
			.catch(() => {
				// Capability not enabled, don't show buttons
			});
	},
});
