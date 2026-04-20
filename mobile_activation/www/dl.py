import frappe
from frappe import _

no_cache = 1

def get_context(context):
    # Initialize all variables to prevent "None" errors in HTML
    context.error = None
    context.doctype = None
    context.name = None
    context.browser_url = "/app" # Default fallback

    doctype = frappe.form_dict.get("doctype")
    name = frappe.form_dict.get("name")

    # 1. Missing Params
    if not doctype or not name:
        context.error = "Missing parameters"
        return

    # 2. Check if DocType exists
    if not frappe.db.exists("DocType", doctype):
        context.error = f"Invalid document type: {doctype}"
        return

    # 3. Check if Document Name exists
    if not frappe.db.exists(doctype, name):
        context.error = f"Document not found: {name}"
        return

    # 4. Success - Set variables
    context.doctype = doctype
    context.name = name
    
    # Generate the correct web URL
    # We use frappe.utils.get_url() to ensure it works on local and hosted
    safe_doctype = doctype.lower().replace(" ", "-")
    context.browser_url = f"/app/{safe_doctype}/{name}"