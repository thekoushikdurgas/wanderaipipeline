// Modern Data Table JavaScript
class DataTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            pageSize: 10,
            currentPage: 1,
            sortColumn: 'place_id',
            sortOrder: 'ASC',
            searchTerm: '',
            ...options
        };
        
        this.data = [];
        this.filteredData = [];
        this.totalPages = 0;
        this.totalRecords = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.render();
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = this.container.querySelector('.search-control input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.options.searchTerm = e.target.value;
                this.options.currentPage = 1;
                this.filterData();
                this.render();
            });
        }
        
        // Entries per page
        const entriesSelect = this.container.querySelector('.entries-control select');
        if (entriesSelect) {
            entriesSelect.addEventListener('change', (e) => {
                this.options.pageSize = parseInt(e.target.value);
                this.options.currentPage = 1;
                this.calculatePagination();
                this.render();
            });
        }
        
        // Sort functionality
        this.container.addEventListener('click', (e) => {
            if (e.target.tagName === 'TH' && e.target.classList.contains('sortable')) {
                this.handleSort(e.target);
            }
        });
        
        // Pagination
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('pagination-btn')) {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.options.currentPage) {
                    this.options.currentPage = page;
                    this.render();
                }
            }
        });
        
        // Action buttons
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit')) {
                this.handleEdit(e.target.dataset.id);
            } else if (e.target.classList.contains('btn-delete')) {
                this.handleDelete(e.target.dataset.id);
            } else if (e.target.classList.contains('btn-view')) {
                this.handleView(e.target.dataset.id);
            }
        });
    }
    
    setData(data) {
        this.data = data;
        this.filterData();
        this.calculatePagination();
        this.render();
    }
    
    filterData() {
        if (!this.options.searchTerm) {
            this.filteredData = [...this.data];
        } else {
            const searchTerm = this.options.searchTerm.toLowerCase();
            this.filteredData = this.data.filter(item => 
                item.name.toLowerCase().includes(searchTerm) ||
                item.types.toLowerCase().includes(searchTerm) ||
                item.address.toLowerCase().includes(searchTerm)
            );
        }
        
        this.totalRecords = this.filteredData.length;
    }
    
    calculatePagination() {
        this.totalPages = Math.ceil(this.totalRecords / this.options.pageSize);
    }
    
    handleSort(headerElement) {
        const column = headerElement.dataset.column;
        
        if (this.options.sortColumn === column) {
            this.options.sortOrder = this.options.sortOrder === 'ASC' ? 'DESC' : 'ASC';
        } else {
            this.options.sortColumn = column;
            this.options.sortOrder = 'ASC';
        }
        
        this.sortData();
        this.render();
    }
    
    sortData() {
        this.filteredData.sort((a, b) => {
            let aVal = a[this.options.sortColumn];
            let bVal = b[this.options.sortColumn];
            
            // Handle numeric values
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return this.options.sortOrder === 'ASC' ? aVal - bVal : bVal - aVal;
            }
            
            // Handle string values
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
            
            if (aVal < bVal) {
                return this.options.sortOrder === 'ASC' ? -1 : 1;
            }
            if (aVal > bVal) {
                return this.options.sortOrder === 'ASC' ? 1 : -1;
            }
            return 0;
        });
    }
    
    getCurrentPageData() {
        const startIndex = (this.options.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        return this.filteredData.slice(startIndex, endIndex);
    }
    
    render() {
        const currentData = this.getCurrentPageData();
        
        // Update table body
        const tbody = this.container.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = this.renderTableBody(currentData);
        }
        
        // Update pagination
        const pagination = this.container.querySelector('.pagination');
        if (pagination) {
            pagination.innerHTML = this.renderPagination();
        }
        
        // Update entries info
        const entriesInfo = this.container.querySelector('.entries-info');
        if (entriesInfo) {
            const start = (this.options.currentPage - 1) * this.options.pageSize + 1;
            const end = Math.min(this.options.currentPage * this.options.pageSize, this.totalRecords);
            entriesInfo.textContent = `Showing ${start} to ${end} of ${this.totalRecords} entries`;
        }
        
        // Update sort indicators
        this.updateSortIndicators();
    }
    
    renderTableBody(data) {
        if (data.length === 0) {
            return `
                <tr>
                    <td colspan="6" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div class="empty-state-title">No data found</div>
                        <div class="empty-state-description">
                            ${this.options.searchTerm ? 'No records match your search criteria.' : 'No records available.'}
                        </div>
                    </td>
                </tr>
            `;
        }
        
        return data.map(item => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #6c757d; font-size: 12px;">▶</span>
                        <strong>${this.escapeHtml(item.name)}</strong>
                    </div>
                </td>
                <td>${this.escapeHtml(item.types)}</td>
                <td>${this.escapeHtml(item.address)}</td>
                <td>${item.latitude}, ${item.longitude}</td>
                <td>${this.escapeHtml(item.pincode)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-view" data-id="${item.place_id}" title="View Details">
                            👁️ View
                        </button>
                        <button class="btn btn-edit" data-id="${item.place_id}" title="Edit">
                            ✏️ Edit
                        </button>
                        <button class="btn btn-delete" data-id="${item.place_id}" title="Delete">
                            🗑️ Delete
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    renderPagination() {
        if (this.totalPages <= 1) {
            return '';
        }
        
        const currentPage = this.options.currentPage;
        const totalPages = this.totalPages;
        
        let paginationHTML = '';
        
        // First page
        paginationHTML += `
            <button class="pagination-btn" data-page="1" ${currentPage === 1 ? 'disabled' : ''}>
                «
            </button>
        `;
        
        // Previous page
        paginationHTML += `
            <button class="pagination-btn" data-page="${currentPage - 1}" ${currentPage === 1 ? 'disabled' : ''}>
                ‹
            </button>
        `;
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="pagination-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">
                    ${i}
                </button>
            `;
        }
        
        // Next page
        paginationHTML += `
            <button class="pagination-btn" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'disabled' : ''}>
                ›
            </button>
        `;
        
        // Last page
        paginationHTML += `
            <button class="pagination-btn" data-page="${totalPages}" ${currentPage === totalPages ? 'disabled' : ''}>
                »
            </button>
        `;
        
        return paginationHTML;
    }
    
    updateSortIndicators() {
        const headers = this.container.querySelectorAll('th.sortable');
        headers.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (header.dataset.column === this.options.sortColumn) {
                header.classList.add(this.options.sortOrder === 'ASC' ? 'sort-asc' : 'sort-desc');
            }
        });
    }
    
    handleEdit(id) {
        // Trigger custom event for edit
        const event = new CustomEvent('tableEdit', { detail: { id: parseInt(id) } });
        this.container.dispatchEvent(event);
    }
    
    handleDelete(id) {
        if (confirm('Are you sure you want to delete this record?')) {
            // Trigger custom event for delete
            const event = new CustomEvent('tableDelete', { detail: { id: parseInt(id) } });
            this.container.dispatchEvent(event);
        }
    }
    
    handleView(id) {
        // Trigger custom event for view
        const event = new CustomEvent('tableView', { detail: { id: parseInt(id) } });
        this.container.dispatchEvent(event);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Public methods for external control
    setPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.options.currentPage = page;
            this.render();
        }
    }
    
    setSearchTerm(term) {
        this.options.searchTerm = term;
        this.options.currentPage = 1;
        this.filterData();
        this.render();
    }
    
    setPageSize(size) {
        this.options.pageSize = size;
        this.options.currentPage = 1;
        this.calculatePagination();
        this.render();
    }
    
    refresh() {
        this.filterData();
        this.calculatePagination();
        this.render();
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB');
}

function formatCoordinates(lat, lon) {
    return `${parseFloat(lat).toFixed(6)}, ${parseFloat(lon).toFixed(6)}`;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DataTable, formatDate, formatCoordinates };
}
