
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

document.addEventListener('change', function (e) {
    if (e.target && e.target.classList.contains('status-dropdown')) {
        const caseId = e.target.getAttribute('data-case-id');
        const newStatus = e.target.value;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch(`/cases/update-status/${caseId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ status: newStatus })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Optional: Show success toast
                    // location.reload(); // Or just let it stay
                    // Maybe update the color of the dropdown?
                    e.target.style.borderColor = "#198754"; // Green border for success
                    setTimeout(() => e.target.style.borderColor = "", 2000);
                } else {
                    alert('Error updating status: ' + data.message);
                    // Revert selection?
                }
            })
            .catch(err => console.error('Error:', err));
    }
});
