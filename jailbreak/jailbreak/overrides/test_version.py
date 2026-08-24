# Copyright (c) 2026, Avunu LLC and contributors
# For license information, please see license.txt

"""S2 coverage for the `Version` controller override - the app's namesake
"restore" feature.

**Real bug found and pinned, not fixed** - needs a product decision, same
category as the other tiers' pinned findings (`Design.reindex()`,
`merge_legacy_designs()`, the artist reports' missing `docstatus` filter).

`Version.restore()` is adapted from Frappe's own `DeletedDocument.restore()`
(same shape: check-already-restored, `doc.update(version_data)`, catch
`DocstatusTransitionError`, `add_comment`, mark restored). But
`DeletedDocument.data` is a **full document snapshot** - `frappe.get_doc()`
on it builds a whole new document. `Version.data` (built by
`Version.set_diff()`, the framework's own automatic version tracking) is a
**diff**: `{"changed": [[field, old, new], ...], "added": [...], "removed":
[...], "row_changed": [...], ...}`. Nothing in this app ever writes a
Version with a flat field->value `data` shape (grepped: only Frappe's own
tracking ever creates a Version row here) - so `doc.update(version_data)`
is always handed a diff dict, tries to set `changed`/`added`/`removed`/
`row_changed`/`data_import`/`updater_reference` as if they were fields on
the target document, and none of them are. `doc.save()` then succeeds as a
near no-op: the field the user actually wants back never changes, `restored`
is still set to `1`, and the success alert fires - **restore silently does
nothing but look like it worked.** Pinned as
`test_restore_does_not_actually_revert_the_changed_field` below, the same
way `Design.reindex()`'s bug was pinned rather than patched: the real fix
(replay `changed`/`added`/`removed` onto the live document, or capture full
snapshots instead of diffs) is a design decision about what "restore" means
here, not something to decide inside a testing pass.

**A second real bug found and fixed, not pinned** - `bulk_restore()`'s loop
checked `if version.restored: invalid.append(d)` but fell through into
`version.restore(alert=False)` anyway instead of `continue`-ing. That call
immediately raises `DocumentAlreadyRestored` (the same check `restore()`
itself does), caught by the surrounding `except frappe.DocumentAlreadyRestored:`,
which appends `d` to `invalid` *again* - so a bulk-restore that includes one
already-restored Version reports it twice in `invalid` and once in neither
list is worse: nothing here made it wrong for the *other* rows, but the
caller (the "Restore" list-view action) shows the same docname flagged
invalid twice. Fixed with the missing `continue`; pinned as
`test_mixes_restored_invalid_and_failed` below, now asserting each row
appears exactly once.
"""

from __future__ import annotations

import frappe

from jailbreak.jailbreak.overrides.version import Version, bulk_restore
from jailbreak.tests import JailbreakIntegrationTestCase
from jailbreak.tests.factories import make_note_with_version, set_capability


class TestRestore(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		version = make_note_with_version()
		set_capability("version_restore", 0)

		with self.assertRaises(frappe.PermissionError):
			Version("Version", version.name).restore(alert=False)

	def test_nonexistent_document_throws(self):
		version = make_note_with_version()
		frappe.delete_doc("Note", version.docname, force=True, ignore_permissions=True)

		with self.capability_enabled("version_restore"):
			with self.assertRaises(frappe.ValidationError):
				Version("Version", version.name).restore(alert=False)

	def test_already_restored_raises_document_already_restored(self):
		version = make_note_with_version()
		version.db_set("restored", 1)

		with self.capability_enabled("version_restore"):
			with self.assertRaises(frappe.DocumentAlreadyRestored):
				Version("Version", version.name).restore(alert=False)

	def test_restore_marks_the_version_restored_and_returns_the_docname(self):
		version = make_note_with_version()

		with self.capability_enabled("version_restore"):
			new_name = Version("Version", version.name).restore(alert=False)

		self.assertEqual(new_name, version.docname)
		self.assertEqual(frappe.db.get_value("Version", version.name, "restored"), 1)

	def test_restore_does_not_actually_revert_the_changed_field(self):
		"""Pinned bug - see the module docstring. A real user clicking
		"Restore" on this Version gets told it worked and sees `content`
		still at the *new* value, not the one being "restored"."""
		version = make_note_with_version(original="<p>original</p>", changed="<p>changed</p>")

		with self.capability_enabled("version_restore"):
			Version("Version", version.name).restore(alert=False)

		note = frappe.get_doc("Note", version.docname)
		self.assertEqual(note.content, "<p>changed</p>")  # not "<p>original</p>"


class TestBulkRestore(JailbreakIntegrationTestCase):
	def test_disabled_capability_raises_permission_error(self):
		version = make_note_with_version()
		set_capability("version_restore", 0)

		result = bulk_restore(frappe.as_json([version.name]))

		self.assertEqual(result["failed"], [version.name])
		self.assertEqual(result["restored"], [])

	def test_mixes_restored_invalid_and_failed(self):
		restorable = make_note_with_version()
		already_restored = make_note_with_version()
		already_restored.db_set("restored", 1)

		with self.capability_enabled("version_restore"):
			result = bulk_restore(frappe.as_json([restorable.name, already_restored.name, "not-a-version"]))

		self.assertEqual(len(result["restored"]), 1)
		self.assertEqual(result["restored"][0]["version"], restorable.name)
		self.assertEqual(result["restored"][0]["new_name"], restorable.docname)
		self.assertEqual(result["invalid"], [already_restored.name])
		self.assertEqual(result["failed"], ["not-a-version"])
