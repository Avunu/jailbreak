// Set full-width default if not already set
if (!localStorage.hasOwnProperty('container_fullwidth')) {
	localStorage.container_fullwidth = "true";
	frappe.ui.toolbar.set_fullwidth_if_enabled();
}