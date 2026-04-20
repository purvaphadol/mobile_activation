import frappe

def get_context(context):
    code = frappe.form_dict.get("code")

    if not code:
        context.message = "Activation code missing"
        return

    result = frappe.call("mobile_activation.api.activate_user", code=code)

    # If your API returns {"status": "success"}
    if isinstance(result, dict):
        context.message = result.get("status")
    else:
        context.message = result
