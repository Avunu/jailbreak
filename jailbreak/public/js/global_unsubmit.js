/* global jailbreak */

/**
 * Granular unsubmit functionality for submitted documents
 * Adds an "Unsubmit" button to submitted documents when user has permission for that specific DocType
 */

// Store original setup methods to extend them
const original_setup_methods = {};

// Override frappe.ui.form.Form to add unsubmit button to all forms
frappe.ui.form.Form = class extends frappe.ui.form.Form {
	constructor(doctype, parent, in_modal, doctype_layout) {
		super(doctype, parent, in_modal, doctype_layout);
		this.unsubmit_button_added = false;
	}

	refresh() {
		super.refresh();
		this.add_unsubmit_button();
	}

	add_unsubmit_button() {
		// Reset button state on each refresh
		this.unsubmit_button_added = false;
		
		// Only add button for submitted documents
		if (!this.doc || this.doc.docstatus !== 1) {
			return;
		}

		// Check if user has unsubmit permission for this specific DocType
		jailbreak.check_unsubmit_permission(this.doc.doctype).then((hasPermission) => {
			if (hasPermission && this.doc && this.doc.docstatus === 1 && !this.unsubmit_button_added) {
				this.add_custom_button(__("Unsubmit"), () => {
					this.unsubmit_document();
				});
				this.unsubmit_button_added = true;
			}
		});
	}

	unsubmit_document() {
		// Confirm action with user
		frappe.confirm(
			__("Are you sure you want to unsubmit this document? This action will change the document status from Submitted to Draft."),
			() => {
				frappe.call({
					method: "jailbreak.jailbreak.hooks.unsubmit_document",
					args: {
						doctype: this.doc.doctype,
						name: this.doc.name,
					},
					callback: (r) => {
						if (r.message && r.message.success) {
							frappe.show_alert({
								message: r.message.message,
								indicator: "green",
							});
							this.reload_doc();
						}
					},
					error: (r) => {
						frappe.msgprint({
							title: __("Error"),
							message: r.message || __("An error occurred while unsubmitting the document"),
							indicator: "red",
						});
					},
				});
			}
		);
	}
};