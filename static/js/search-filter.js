// Search and Filter Functionality for Dashboard
(function () {
    'use strict';

    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const ongFilter = document.getElementById('ongFilter');
    const domainFilter = document.getElementById('domainFilter');
    const clearBtn = document.getElementById('clearFilters');
    const resultsCount = document.getElementById('resultsCount');
    const casesContainer = document.getElementById('casesContainer');
    const noResults = document.getElementById('noResults');
    const caseCards = document.querySelectorAll('.case-card-wrapper');

    // Debounce function for search input
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Pagination constraints
    const itemsPerPage = 10;
    let currentPage = 1;
    let filteredCards = []; // Store currently matching cards

    // Filter function
    function filterCases() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedStatus = statusFilter.value;
        const selectedOng = ongFilter.value;
        const selectedDomain = domainFilter.value;

        // Reset matching list
        filteredCards = [];

        caseCards.forEach(card => {
            const title = card.dataset.title || '';
            const description = card.dataset.description || '';
            const status = card.dataset.status || '';
            const ongId = card.dataset.ongId || '';
            const domain = card.dataset.domain || '';

            // Check all filter conditions
            const matchesSearch = !searchTerm ||
                title.includes(searchTerm) ||
                description.includes(searchTerm);

            const matchesStatus = !selectedStatus || status === selectedStatus;
            const matchesOng = !selectedOng || ongId === selectedOng;
            const matchesDomain = !selectedDomain || domain.includes(selectedDomain);

            if (matchesSearch && matchesStatus && matchesOng && matchesDomain) {
                filteredCards.push(card);
            } else {
                card.style.display = 'none';
                card.classList.remove('fade-in');
            }
        });

        // Reset to page 1 on filter change
        currentPage = 1;
        updateDisplay();
    }

    // Update Display (Pagination & Counts)
    function updateDisplay() {
        const totalItems = filteredCards.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage);

        // Hide all first
        caseCards.forEach(card => card.style.display = 'none');

        // Show items for current page
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageItems = filteredCards.slice(start, end);

        pageItems.forEach(card => {
            card.style.display = '';
            card.classList.add('fade-in');
        });

        // Update UI elements
        updateResultsCount(totalItems);
        renderPagination(totalPages);

        // Show/Hide container/no results
        if (totalItems === 0) {
            casesContainer.style.display = 'none';
            noResults.style.display = 'block';
            document.getElementById('paginationControls').style.display = 'none';
        } else {
            casesContainer.style.display = '';
            noResults.style.display = 'none';
            document.getElementById('paginationControls').style.display = totalPages > 1 ? 'block' : 'none';
        }
    }

    // Render Pagination Controls
    function renderPagination(totalPages) {
        const paginationContainer = document.getElementById('paginationControls');
        if (!paginationContainer) return;

        let html = '<ul class="pagination justify-content-center">';

        // Previous Button
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${currentPage - 1}">
                        <i class="bi bi-chevron-left"></i>
                    </a>
                 </li>`;

        // Page Numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                            <a class="page-link" href="#" data-page="${i}">${i}</a>
                         </li>`;
            } else if (i === currentPage - 2 || i === currentPage + 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        // Next Button
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${currentPage + 1}">
                        <i class="bi bi-chevron-right"></i>
                    </a>
                 </li>`;

        html += '</ul>';
        paginationContainer.innerHTML = html;

        // Add click listeners
        paginationContainer.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.currentTarget.dataset.page);
                if (page && page > 0 && page <= totalPages && page !== currentPage) {
                    currentPage = page;
                    updateDisplay();
                    window.scrollTo({ top: document.getElementById('casesContainer').offsetTop - 100, behavior: 'smooth' });
                }
            });
        });
    }

    // Update results count message
    function updateResultsCount(count) {
        const lang = document.documentElement.lang || 'fr';
        let message;
        if (lang === 'ar') {
            message = `عرض ${count} حالة`;
        } else {
            message = `Affichage de ${count} cas`;
        }
        resultsCount.textContent = message;
    }

    // Clear all filters
    function clearFilters() {
        searchInput.value = '';
        statusFilter.value = '';
        ongFilter.value = '';
        domainFilter.value = '';
        filterCases(); // This resets page to 1 automatically

        // Add visual feedback
        clearBtn.classList.add('btn-success');
        setTimeout(() => {
            clearBtn.classList.remove('btn-success');
        }, 500);
    }

    // Event Listeners
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterCases, 300));
    }

    if (statusFilter) {
        statusFilter.addEventListener('change', filterCases);
    }

    if (ongFilter) {
        ongFilter.addEventListener('change', filterCases);
    }

    if (domainFilter) {
        domainFilter.addEventListener('change', filterCases);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', clearFilters);
    }

    // Initialize on page load
    filterCases();

    // Keyboard shortcut: "/" to focus search
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    });
})();
