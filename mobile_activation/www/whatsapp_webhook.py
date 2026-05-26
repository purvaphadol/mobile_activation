import frappe
import json
import re

VERIFY_TOKEN    = "glmmify_secret_token"
WHATSAPP_TOKEN  = "YOUR_ACCESS_TOKEN_HERE"       # ← paste here
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID_HERE"    # ← paste here

no_cache = 1

def get_context(context):
    frappe.flags.disable_website_cache = True

    if frappe.request.method == "GET":
        mode      = frappe.request.args.get("hub.mode")
        token     = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
            frappe.response["http_status_code"] = 200
            frappe.response["content_type"] = "text/plain"
            frappe.response["body"] = challenge
            raise frappe.Redirect   # stops template rendering

        frappe.response["http_status_code"] = 403
        raise frappe.Redirect

    elif frappe.request.method == "POST":
        try:
            data = json.loads(frappe.request.data)
        except Exception:
            frappe.response["http_status_code"] = 400
            raise frappe.Redirect

        try:
            entry = data["entry"][0]["changes"][0]["value"]

            if "messages" not in entry:
                frappe.response["http_status_code"] = 200
                raise frappe.Redirect

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

        except frappe.Redirect:
            raise
        except Exception:
            frappe.log_error(frappe.get_traceback(), "WhatsApp Webhook Error")

        frappe.response["http_status_code"] = 200
        raise frappe.Redirect
