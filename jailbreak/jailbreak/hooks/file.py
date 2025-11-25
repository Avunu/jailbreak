# Copyright (c) 2025, Avunu LLC and contributors
# For license information, please see license.txt

import os

import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def merge_files(source_file: str, target_file: str) -> dict:
	"""
	Merge source_file into target_file by using bulk_rename to update all references,
	then delete the filesystem file.

	:param source_file: Name of the file to merge (will be deleted)
	:param target_file: Name of the file to merge into (will be kept)
	:return: Dictionary with success status and message
	"""
	# Check if file merge capability is enabled
	assert_capability("file_merge")

	# Validate that both files exist
	if not frappe.db.exists("File", source_file):
		frappe.throw(_("Source file {0} does not exist").format(source_file))

	if not frappe.db.exists("File", target_file):
		frappe.throw(_("Target file {0} does not exist").format(target_file))

	# Prevent merging a file into itself
	if source_file == target_file:
		frappe.throw(_("Cannot merge a file into itself"))

	# Get the source file document to access filesystem path
	source_file_doc = frappe.get_doc("File", source_file)
	file_path = source_file_doc.get_full_path()

	# Use bulk_rename to merge the files (updates all references automatically)
	# The third parameter "true" indicates merge=True (will merge instead of just renaming)
	from frappe.model.rename_doc import bulk_rename

	bulk_rename("File", [[source_file, target_file, "true"]])

	# Delete the physical file from filesystem if it exists
	# Note: This happens after the database merge, so if it fails, the DB merge has succeeded
	# but the physical file remains. This is logged but does not fail the merge operation.
	if file_path and os.path.exists(file_path):
		try:
			os.remove(file_path)
		except OSError as e:
			frappe.log_error(
				f"Failed to delete file {file_path}: {str(e)}. Database merge succeeded but physical file was not removed.",
				"File Merge - Filesystem Cleanup",
			)

	return {
		"success": True,
		"message": _("File {0} merged into {1} successfully.").format(source_file, target_file),
	}
