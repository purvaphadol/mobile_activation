# pyrefly: ignore [missing-import]
# pyrefly: ignore-errors
import frappe
import json
import re
from werkzeug.exceptions import HTTPException

from werkzeug.wrappers import Response

VERIFY_TOKEN    = "glmmify_secret_token"
WHATSAPP_TOKEN  = "YOUR_ACCESS_TOKEN_HERE"       # ← paste here
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID_HERE"    # ← paste here

class PlainTextResponseException(HTTPException):
    def __init__(self, description, code=200):
        super().__init__()
        self.code = code
        self.description = description

    def get_response(self, environ=None):
        return Response(self.description, status=self.code, mimetype="text/plain")


def whatsapp_before_request():
    """
    Intercepts requests to /whatsapp_webhook before Frappe processes them.
    Returns a raw Werkzeug Response by raising a PlainTextResponseException,
    bypassing Frappe's response system entirely.
    """
    path = frappe.request.path.rstrip('/')
    if path != "/whatsapp_webhook":
        return   # not our request, let Frappe handle normally

    if frappe.request.method == "GET":
        mode      = frappe.request.args.get("hub.mode")
        token     = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
            raise PlainTextResponseException(challenge, 200)

        raise PlainTextResponseException("Forbidden", 403)

    elif frappe.request.method == "POST":
        try:
            data = json.loads(frappe.request.data)
        except Exception:
            raise PlainTextResponseException("Bad Request", 400)

        try:
            entries = data.get("entry", [])
            if entries:
                changes = entries[0].get("changes", [])
                if changes:
                    value = changes[0].get("value", {})
                    if "messages" in value:
                        messages = value.get("messages", [])
                        contacts = value.get("contacts", [])
                        if messages:
                            message = messages[0]
                            mobile = message.get("from", "")
                            wa_msg_id = message.get("id", "")
                            msg_type = message.get("type", "text")

                            sender_name = ""
                            if contacts:
                                profile = contacts[0].get("profile", {})
                                sender_name = profile.get("name", "")

                            if msg_type == "text":
                                msg_body = message.get("text", {}).get("body", "")
                            else:
                                msg_body = f"[{msg_type} message received]"

                            email_match = re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", msg_body)
                            email = email_match.group(0) if email_match else ""

                            doc = frappe.get_doc({
                                "doctype": "WhatsApp Message",
                                "mobile": mobile,
                                "sender_name": sender_name,
                                "message": msg_body,
                                "email": email,
                                "message_type": msg_type,
                                "wa_message_id": wa_msg_id,
                                "received_at": frappe.utils.now()
                            })
                            doc.insert(ignore_permissions=True)
                            frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(), "WhatsApp Webhook Error")

        raise PlainTextResponseException("ok", 200)

