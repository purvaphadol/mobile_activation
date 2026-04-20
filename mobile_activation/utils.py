import frappe
import secrets
from datetime import timedelta
from frappe.utils import now_datetime

def generate_activation_token(user_email):

    # delete old unused tokens
    frappe.db.delete(
        "Mobile Activation Token",
        {
            "user": user_email,
            "used": 0
        }
    )

    token = secrets.token_urlsafe(32)

    doc = frappe.get_doc({
        "doctype": "Mobile Activation Token",
        "code": token,
        "user": user_email,
        "expiry": now_datetime() + timedelta(hours=24),
        "used": 0
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return token
