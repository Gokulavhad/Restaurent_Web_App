document.addEventListener('DOMContentLoaded', function() {
    // Get variables from template
    const weeklyRevenue = JSON.parse(document.getElementById('weeklyRevenue').value || '[]');
    const popularItems = JSON.parse(document.getElementById('popularItems').value || '[]');

    // Navigation
    const navLinks = document.querySelectorAll('.sidebar a');
    const sections = document.querySelectorAll('.dashboard-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            
            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection) {
                    section.classList.add('active');
                }
            });
        });
    });

    // Charts
    const revenueCtx = document.getElementById('revenueChart');
    const itemsCtx = document.getElementById('itemsChart');

    // Weekly Revenue Chart
    if (revenueCtx) {
        new Chart(revenueCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Revenue',
                    data: weeklyRevenue,
                    borderColor: '#4CAF50',
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    // Popular Items Chart
    if (itemsCtx) {
        new Chart(itemsCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: popularItems.map(item => item.name),
                datasets: [{
                    data: popularItems.map(item => item.count),
                    backgroundColor: [
                        '#4CAF50',
                        '#45a049',
                        '#357a38',
                        '#2e6830',
                        '#255628'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Order Status Updates
    const updateButtons = document.querySelectorAll('.btn-update');
    updateButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const orderId = button.getAttribute('data-order-id');
            try {
                const response = await fetch(`/api/orders/${orderId}/status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        status: 'Completed'  // You can make this dynamic with a dropdown
                    })
                });
                
                if (response.ok) {
                    // Refresh the page or update the UI
                    location.reload();
                }
            } catch (error) {
                console.error('Error updating order:', error);
            }
        });
    });

    // Status Filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            const selectedStatus = statusFilter.value.toLowerCase();
            const orderRows = document.querySelectorAll('#orders tbody tr');
            
            orderRows.forEach(row => {
                const statusCell = row.querySelector('.status-badge');
                const rowStatus = statusCell.textContent.trim().toLowerCase();
                
                if (!selectedStatus || rowStatus === selectedStatus) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
