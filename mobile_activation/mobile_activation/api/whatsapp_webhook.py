# pyrefly: ignore-errors
import frappe
import json
import re
from werkzeug.wrappers import Response as WerkzeugResponse


VERIFY_TOKEN    = "glmmify_secret_token"
WHATSAPP_TOKEN  = "WHATSAPP_TOKEN"
PHONE_NUMBER_ID = "PHONE_NUMBER_ID"

@frappe.whitelist(allow_guest=True)
def whatsapp_webhook(**kwargs):
    if frappe.request.method == "GET":
        mode      = frappe.request.args.get("hub.mode")
        token     = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
            # Directly set a plain-text Werkzeug response — bypasses Frappe JSON layer
            frappe.local.response = WerkzeugResponse(
                response=challenge,
                status=200,
                mimetype="text/plain"
            )
            return

        frappe.local.response = WerkzeugResponse(
            response="Forbidden",
            status=403,
            mimetype="text/plain"
        )
        return

    elif frappe.request.method == "POST":
        try:
            data = json.loads(frappe.request.data)
        except Exception:
            frappe.response["http_status_code"] = 400
            return

        try:
            entry = data["entry"][0]["changes"][0]["value"]

            if "messages" not in entry:
                frappe.response["http_status_code"] = 200
                frappe.response["message"] = "ok"
                return

            contact     = entry["contacts"][0]
            message     = entry["messages"][0]

            mobile      = message.get("from", "")
            sender_name = contact["profile"].get("name", "")
            msg_type    = message.get("type", "text")
            wa_msg_id   = message.get("id", "")

            if msg_type == "text":
                msg_body = message.get("text", {}).get("body", "")
            else:
                msg_body = f"[{msg_type} message received]"

            email_match = re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", msg_body)
            email = email_match.group(0) if email_match else ""

            doc = frappe.get_doc({
                "doctype":     "WhatsApp Message",
                "mobile":      mobile,
                "sender_name": sender_name,
                "message":     msg_body,
                "email":       email,
                "msg_type":    msg_type,
                "wa_msg_id":   wa_msg_id,
                "received_at": frappe.utils.now()
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception:
            frappe.log_error(frappe.get_traceback(), "WhatsApp Webhook Error")

        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "ok"
