# Copyright (c) 2025, Avunu LLC and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from jailbreak import assert_capability


@frappe.whitelist()
def merge_files(source_file: str, target_file: str) -> dict:
	"""
	Merge source_file into target_file by replacing all references
	to source_file with target_file, then delete source_file.

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

	# Get file URLs before making any changes
	source_file_doc = frappe.get_doc("File", source_file)
	source_file_url = source_file_doc.file_url

	target_file_doc = frappe.get_doc("File", target_file)
	target_file_url = target_file_doc.file_url

	# Get all documents that reference the source file
	references = get_file_references(source_file)

	# Replace all references to source_file with target_file
	for ref in references:
		update_file_reference(
			ref["doctype"], ref["docname"], ref["fieldname"], source_file, source_file_url, target_file, target_file_url
		)

	# Delete the source file
	frappe.delete_doc("File", source_file, force=True)

	return {
		"success": True,
		"message": _("File {0} merged into {1} successfully. {2} references updated.").format(
			source_file, target_file, len(references)
		),
		"references_updated": len(references),
	}


def get_file_references(file_name: str) -> list[dict]:
	"""
	Get all documents that reference a file.

	:param file_name: Name of the file
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
	file_url = file_doc.file_url

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
				doc.save(ignore_permissions=True)
				return

		# Update field if specified
		if fieldname:
			current_value = doc.get(fieldname)
			if current_value in [old_file_url, old_file]:
				doc.set(fieldname, new_file_url)
				doc.save(ignore_permissions=True)

	except (frappe.DoesNotExistError, frappe.ValidationError) as e:
		# Log expected errors (document doesn't exist, validation failed)
		frappe.log_error(
			f"Failed to update file reference in {doctype} {docname}: {str(e)}", "File Merge Error"
		)
	except Exception as e:
		# Log and re-raise unexpected errors
		frappe.log_error(
			f"Unexpected error updating file reference in {doctype} {docname}: {str(e)}", "File Merge Error"
		)
		raise
