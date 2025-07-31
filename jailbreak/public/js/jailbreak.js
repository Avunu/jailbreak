// Global jailbreak object for capability checking
window.jailbreak = {
	/**
	 * Check if a jailbreak capability is enabled before using it
	 * @param {string} capability - The capability to check
	 * @returns {Promise<boolean>} - Promise that resolves to true if enabled
	 * @throws {Error} - Throws error if capability is not enabled
	 */
	assert_capability: function (capability) {
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "jailbreak.assert_capability",
				args: {
					capability: capability,
				},
				callback: function (r) {
					if (!r.exc) {
						resolve(true);
					}
				},
				error: function (r) {
					// The error is already handled by assert_capability throwing frappe.throw
					reject(new Error(`Capability ${capability} not enabled`));
				},
			});
		});
	},

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
};
