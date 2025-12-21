
// Initialize Tooltips
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});

function confirmDelete(event) {
    if (!confirm(confirmDeleteText)) {
        event.preventDefault();
        return false;
    }
    return true;
}
