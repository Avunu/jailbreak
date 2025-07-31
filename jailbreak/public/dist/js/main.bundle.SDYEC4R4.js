(() => {
  // ../jailbreak/jailbreak/public/js/merge_records.js
  frappe.provide("frappe.ui.merge_records");
  frappe.ui.merge_records = {
    merge_selected_records: function(listview) {
      if (listview.get_checked_items().length < 2) {
        frappe.throw(__("Please select at least two records to merge."));
        return;
      }
      let selected_docs = listview.get_checked_items().map((doc) => doc.name);
      let d = new frappe.ui.Dialog({
        title: __("Merge Records"),
        fields: [
          {
            label: __("Merge into"),
            fieldname: "merge_into",
            fieldtype: "Select",
            options: selected_docs,
            reqd: 1
          }
        ],
        primary_action_label: __("Merge"),
        primary_action: function() {
          let merge_into = d.get_value("merge_into");
          let docs_to_merge = selected_docs.filter((doc) => doc !== merge_into);
          frappe.call({
            method: "jailbreak.jailbreak.hooks.bulk_merge",
            args: {
              doctype: listview.doctype,
              rows: docs_to_merge.map((doc) => [doc, merge_into, "true"])
            },
            callback: function(r) {
              if (r.message) {
                listview.clear_checked_items();
                listview.refresh();
              }
            }
          });
          d.hide();
        }
      });
      d.show();
    }
  };
  frappe.views.ListView = class extends frappe.views.ListView {
    constructor(opts) {
      super(opts);
      this.merge_button_added = false;
    }
    setup_page() {
      super.setup_page();
      this.add_merge_button();
    }
    add_merge_button() {
      if (!this.merge_button_added) {
        jailbreak.assert_capability("global_bulk_merge").then(() => {
          this.page.add_action_item(__("Merge Selected"), () => {
            frappe.ui.merge_records.merge_selected_records(this);
          });
        }).catch(() => {
        });
        this.merge_button_added = true;
      }
    }
  };

  // ../jailbreak/jailbreak/public/js/full_width.js
  if (!localStorage.hasOwnProperty("container_fullwidth")) {
    localStorage.container_fullwidth = "true";
    frappe.ui.toolbar.set_fullwidth_if_enabled();
  }

  // ../jailbreak/jailbreak/public/js/jailbreak.js
  window.jailbreak = {
    assert_capability: function(capability) {
      return new Promise((resolve, reject) => {
        frappe.call({
          method: "jailbreak.assert_capability",
          args: {
            capability
          },
          callback: function(r) {
            if (!r.exc) {
              resolve(true);
            }
          },
          error: function(r) {
            reject(new Error(`Capability ${capability} not enabled`));
          }
        });
      });
    }
  };
})();
//# sourceMappingURL=main.bundle.SDYEC4R4.js.map
