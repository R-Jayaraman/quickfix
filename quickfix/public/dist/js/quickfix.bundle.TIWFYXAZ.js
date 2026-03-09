(() => {
  // ../quickfix/quickfix/public/js/quickfix.bundle.js
  frappe.ui.form.on("*", {
    refresh(frm) {
      if (frappe.boot.quickfix_shop_name && frm.doc) {
        frm.page.set_title(frappe.boot.quickfix_shop_name);
      }
    }
  });
})();
//# sourceMappingURL=quickfix.bundle.TIWFYXAZ.js.map
