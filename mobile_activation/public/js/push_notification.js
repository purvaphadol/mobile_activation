// // Lead Follow-up Push Notification Listener
// // Loaded on every Frappe Desk page via app_include_js in hooks.py

// frappe.ready(function () {
//     console.log("Lead Follow-up Reminder: listener registered");

//     // Request browser notification permission on page load.
//     // This is a no-op if the user has already granted or permanently denied permissions.
//     // Note: Modern browsers require a user gesture for the very first permission dialog.
//     // If this request is silently ignored, the user must manually enable notifications
//     // from the browser address bar padlock icon.
//     if (Notification && Notification.permission === "default") {
//         Notification.requestPermission();
//     }

//     frappe.realtime.on("lead_followup_reminder", function (data) {
//         console.log("Lead Follow-up Reminder received:", data);

//         if (Notification && Notification.permission === "granted") {
//             // Show native OS browser notification
//             var n = new Notification("Lead Follow-up Reminder", {
//                 body: data.message,
//                 icon: "/assets/frappe/images/frappe-framework-logo.png",
//             });

//             n.onclick = function () {
//                 window.focus();
//                 window.open("/app/lead/" + data.lead, "_blank");
//             };
//         } else {
//             // Fallback: Frappe desk toast alert (visible even if notifications are blocked)
//             frappe.show_alert(
//                 {
//                     message: data.message,
//                     indicator: "orange",
//                 },
//                 10
//             );
//         }
//     });
// });
