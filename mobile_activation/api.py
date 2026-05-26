# pyrefly: ignore [missing-import]
# pyrefly: ignore-errors
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

import json
import re

VERIFY_TOKEN = "glmmify_secret_token"  # must match Meta Console

@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
    if frappe.request.method == "GET":
        mode      = frappe.request.args.get("hub.mode")
        token     = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            frappe.response["http_status_code"] = 200
            frappe.response["type"] = "text"
            frappe.response["message"] = challenge
            return

        frappe.throw("Forbidden", frappe.AuthenticationError)

    elif frappe.request.method == "POST":
        try:
            data = json.loads(frappe.request.data)
        except Exception:
            frappe.response["http_status_code"] = 400
            return

        try:
            entry       = data["entry"][0]["changes"][0]["value"]
            contact     = entry["contacts"][0]
            message     = entry["messages"][0]

            mobile      = message.get("from", "")
            sender_name = contact["profile"].get("name", "")
            msg_body    = message.get("text", {}).get("body", "")
            msg_type    = message.get("type", "text")
            wa_msg_id   = message.get("id", "")

            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", msg_body)
            email       = email_match.group(0) if email_match else ""

            doc = frappe.get_doc({
                "doctype": "WhatsApp Message",
                "mobile": mobile,
                "sender_name": sender_name,
                "message": msg_body,
                "email": email,
                "msg_type": msg_type,
                "wa_msg_id": wa_msg_id,
                "received_at": frappe.utils.now()
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception:
            frappe.log_error(frappe.get_traceback(), "WhatsApp Webhook Error")

        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "ok"