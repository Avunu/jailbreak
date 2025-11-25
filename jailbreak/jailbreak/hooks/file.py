# Copyright (c) 2025, Avunu LLC and contributors
# For license information, please see license.txt

import os

import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def merge_files(source_file: str, target_file: str) -> dict:
	"""
	Merge source_file into target_file by replacing all references
	to source_file with target_file, then delete source_file and its filesystem file.

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

	# Get file documents and paths before making changes
	source_file_doc = frappe.get_doc("File", source_file)
	target_file_doc = frappe.get_doc("File", target_file)

	source_file_url = source_file_doc.file_url
	target_file_url = target_file_doc.file_url
	file_path = source_file_doc.get_full_path()

	# Get all documents that reference the source file
	references = get_file_references(source_file, source_file_url)

	# Replace all references to source_file with target_file
	for ref in references:
		update_file_reference(
			ref["doctype"],
			ref["docname"],
			ref["fieldname"],
			source_file,
			source_file_url,
			target_file,
			target_file_url,
		)

	# Delete the source file document
	frappe.delete_doc("File", source_file, force=True)

	# Delete the physical file from filesystem if it exists
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
		"message": _("File {0} merged into {1} successfully. {2} references updated.").format(
			source_file, target_file, len(references)
		),
		"references_updated": len(references),
	}


@frappe.whitelist()
def batch_merge_files(files_to_merge: str | list, target_file: str) -> dict:
	"""
	Merge multiple files into a target file.

	:param files_to_merge: List of file names to merge (will be deleted)
	:param target_file: Name of the file to merge into (will be kept)
	:return: Dictionary with success status and message
	"""
	import json

	# Check if file merge capability is enabled
	assert_capability("file_merge")

	# Parse files_to_merge if it's a JSON string
	if isinstance(files_to_merge, str):
		files_to_merge = json.loads(files_to_merge)

	if not files_to_merge:
		frappe.throw(_("No files selected to merge"))

	total_references = 0
	merged_count = 0
	failed_files = []

	for source_file in files_to_merge:
		try:
			result = merge_files(source_file, target_file)
			if result.get("success"):
				merged_count += 1
				total_references += result.get("references_updated", 0)
		except Exception as e:
			failed_files.append({"file": source_file, "error": str(e)})
			frappe.log_error(f"Failed to merge {source_file} into {target_file}: {str(e)}", "Batch File Merge Error")

	message = _("{0} file(s) merged into {1} successfully. {2} references updated.").format(
		merged_count, target_file, total_references
	)

	if failed_files:
		message += " " + _("{0} file(s) failed to merge.").format(len(failed_files))

	return {
		"success": True,
		"message": message,
		"merged_count": merged_count,
		"total_references": total_references,
		"failed_files": failed_files,
	}


def get_file_references(file_name: str, file_url: str) -> list[dict]:
	"""
	Get all documents that reference a file.

	:param file_name: Name of the file
	:param file_url: URL of the file
	:return: List of dictionaries with doctype, docname, and fieldname
	"""
	references = []

	# Get file document
	file_doc = frappe.get_doc("File", file_name)

	# Check attached_to_doctype and attached_to_name
	if file_doc.attached_to_doctype and file_doc.attached_to_name:
		references.append(
			{
				"doctype": file_doc.attached_to_doctype,
				"docname": file_doc.attached_to_name,
				"fieldname": file_doc.attached_to_field or None,
			}
		)

	# Search for any other references in the database
	# Note: This is a broad search across all doctypes that might have file fields.
	# For large databases, this could be slow. The search is limited to DocTypes with
	# Attach or Attach Image fields, and errors are caught to avoid breaking the merge.

	# Get all DocTypes with attach or attach_image fields
	doctypes_with_file_fields = frappe.get_all(
		"DocField",
		filters={"fieldtype": ["in", ["Attach", "Attach Image"]]},
		fields=["parent", "fieldname"],
	)

	for dt in doctypes_with_file_fields:
		try:
			# Search for documents with this file in the field
			docs = frappe.get_all(
				dt["parent"],
				filters={dt["fieldname"]: ["in", [file_url, file_name]]},
				fields=["name"],
			)

			for doc in docs:
				# Avoid duplicates
				ref = {
					"doctype": dt["parent"],
					"docname": doc["name"],
					"fieldname": dt["fieldname"],
				}
				if ref not in references:
					references.append(ref)
		except (frappe.DoesNotExistError, frappe.ValidationError, frappe.PermissionError):
			# Skip if doctype doesn't exist or has issues
			continue
		except Exception as e:
			# Log unexpected errors but continue processing other doctypes
			frappe.log_error(f"Error searching {dt['parent']}: {str(e)}", "File Reference Search")
			continue

	return references


def update_file_reference(
	doctype: str,
	docname: str,
	fieldname: str | None,
	old_file: str,
	old_file_url: str,
	new_file: str,
	new_file_url: str,
):
	"""
	Update a file reference in a document.

	:param doctype: DocType of the document
	:param docname: Name of the document
	:param fieldname: Field name containing the file reference (can be None)
	:param old_file: Old file name
	:param old_file_url: Old file URL
	:param new_file: New file name
	:param new_file_url: New file URL
	"""
	try:
		doc = frappe.get_doc(doctype, docname)

		# Update attached_to references if this is a File doctype attachment
		if hasattr(doc, "attached_to_doctype") and doc.attached_to_doctype == "File":
			if doc.attached_to_name == old_file:
				doc.attached_to_name = new_file
				doc.save()
				return

		# Update field if specified
		if fieldname:
			current_value = doc.get(fieldname)
			if current_value in [old_file_url, old_file]:
				doc.set(fieldname, new_file_url)
				doc.save()

	except (frappe.DoesNotExistError, frappe.ValidationError) as e:
		# Log expected errors (document doesn't exist, validation failed)
		frappe.log_error(
			f"Failed to update file reference in {doctype} {docname}: {str(e)}", "File Merge Error"
		)
	except Exception as e:
		# Log unexpected errors but don't break the merge operation
		# Most references may still be updated successfully
		frappe.log_error(
			f"Unexpected error updating file reference in {doctype} {docname}: {str(e)}",
			"File Merge Critical Error",
		)
