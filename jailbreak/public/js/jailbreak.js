// Global jailbreak object for capability checking
window.jailbreak = {
	/**
	 * Check if a jailbreak capability is enabled without throwing errors
	 * @param {string} capability - The capability to check
	 * @returns {Promise<boolean>} - Promise that resolves to true if enabled, false otherwise
	 */
	check_capability: function (capability) {
		return new Promise((resolve) => {
			frappe.call({
				method: "jailbreak.check_capability",
				args: {
					capability: capability,
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						resolve(r.message === true);
					} else {
						resolve(false);
					}
				},
				error: function (r) {
					// If there's an error, capability is not enabled
					resolve(false);
				},
			});
		});
	},

	/**
	 * Check if user has permission to unsubmit documents of a specific DocType
	 * @param {string} doctype - The DocType to check
	 * @returns {Promise<boolean>} - Promise that resolves to true if permission exists, false otherwise
	 */
	check_unsubmit_permission: function (doctype) {
		return new Promise((resolve) => {
			frappe.call({
				method: "jailbreak.check_unsubmit_permission",
				args: {
					doctype: doctype,
				},
				callback: function (r) {
					if (!r.exc && r.message !== undefined) {
						resolve(r.message === true);
					} else {
						resolve(false);
					}
				},
				error: function (r) {
					// If there's an error, permission is not granted
					resolve(false);
				},
			});
		});
	},
};
