# import frappe
# from frappe.utils import now_datetime, add_to_date


# def send_lead_followup_reminders():
#     """Send browser push reminders 30 min before Lead follow-up time.

#     Designed to run every 5 minutes via the scheduler cron job.
#     Uses a small back-buffer on the window start to avoid gaps between runs.
#     """
#     now = now_datetime()
#     window_start = add_to_date(now, minutes=-5)   # 5-min back-buffer for gap safety
#     window_end   = add_to_date(now, minutes=30)

#     leads = frappe.get_all(
#         "Lead",
#         filters={
#             "custom_follow_up_date_time": ["between", [window_start, window_end]],
#             "custom_reminder_sent": 0,
#             "status": ["!=", "Converted"],
#         },
#         fields=["name", "lead_name", "custom_follow_up_date_time", "owner"],
#     )

#     for lead in leads:
#         if not lead.owner:
#             continue

#         frappe.publish_realtime(
#             "lead_followup_reminder",
#             {
#                 "message": "Follow-up for Lead {} in 30 minutes".format(
#                     lead.lead_name or lead.name
#                 ),
#                 "lead": lead.name,
#             },
#             user=lead.owner,
#         )

#         frappe.db.set_value("Lead", lead.name, "custom_reminder_sent", 1)

#     if leads:
#         frappe.db.commit()



