import frappe
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def activate_user(code):

    token = frappe.get_doc(
        "Mobile Activation Token",
        {"code": code}
    )

    if not token:
        return {"status": "invalid"}

    if token.used:
        return {"status": "already_used"}

    if token.expiry < now_datetime():
        return {"status": "expired"}

    user = frappe.get_doc("User", token.user)
    user.enabled = 1
    user.save(ignore_permissions=True)

    token.used = 1
    token.save(ignore_permissions=True)

    frappe.db.commit()

    return {"status": "success"}
