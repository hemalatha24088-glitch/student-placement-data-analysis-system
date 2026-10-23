/**
 * Main Application JavaScript
 * Handles notifications dismissal, sidebar toggle, modal confirmations, and table interactions.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss alert notifications after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = "0";
            alert.style.transition = "opacity 0.4s ease";
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000);
    });

    // Mobile sidebar toggle if trigger exists
    const toggleBtn = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".app-sidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }

    // Confirmation for delete actions
    const deleteForms = document.querySelectorAll("form.delete-confirm");
    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const itemName = form.getAttribute("data-item") || "this record";
            if (!confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
});
