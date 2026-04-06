// ==================== Global State ====================
let trendChart, categoryChart, categoryChartFull, trendChartFull;

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', function() {
    setupNavigation();
    loadDashboard();
    
    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();
});

// ==================== Navigation ====================
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.dataset.tab;
            switchTab(tabName);
            
            // Update active state
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
        
        // Load tab-specific data
        if (tabName === 'expenses') {
            loadExpenses();
        } else if (tabName === 'analytics') {
            loadAnalytics();
        } else if (tabName === 'budget') {
            loadBudget();
        }
    }
}

// ==================== Dashboard ====================
function loadDashboard() {
    loadStats();
    loadCharts();
    loadInsights();
}

function loadStats() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => {
            document.getElementById('stat-total').textContent = `₹${data.total_spent.toFixed(2)}`;
            document.getElementById('stat-count').textContent = data.transaction_count;
            document.getElementById('stat-avg').textContent = `₹${data.average_transaction.toFixed(2)}`;
            document.getElementById('stat-month').textContent = `₹${data.this_month.toFixed(2)}`;
        })
        .catch(err => console.error('Error loading stats:', err));
}

function loadCharts() {
    // Load trending data
    fetch('/api/expenses/timeline')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('trendChart').getContext('2d');
            if (trendChart) trendChart.destroy();
            trendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Daily Spending',
                        data: data.amounts,
                        borderColor: '#2563EB',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#2563EB',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + value;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Error loading trend chart:', err));
    
    // Load category breakdown
    fetch('/api/expenses/category')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('categoryChart').getContext('2d');
            if (categoryChart) categoryChart.destroy();
            categoryChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: [
                            '#2563EB', '#10B981', '#F59E0B', '#EF4444',
                            '#8B5CF6', '#EC4899', '#14B8A6', '#3B82F6'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Error loading category chart:', err));
}

function loadInsights() {
    fetch('/api/insights')
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('insights-container');
            container.innerHTML = '';
            data.forEach(insight => {
                const div = document.createElement('div');
                div.className = 'insight-item';
                div.innerHTML = insight;
                container.appendChild(div);
            });
        })
        .catch(err => console.error('Error loading insights:', err));
}

// ==================== Expenses ====================
function loadExpenses() {
    fetch('/api/expenses')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('expenses-tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No expenses found</td></tr>';
                return;
            }
            
            data.reverse().forEach(expense => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(expense.date).toLocaleDateString()}</td>
                    <td><span style="background: var(--bg-light); padding: 0.25rem 0.75rem; border-radius: 0.25rem;">${expense.category}</span></td>
                    <td>${expense.description}</td>
                    <td><strong>₹${expense.amount.toFixed(2)}</strong></td>
                    <td><button class="btn-delete" onclick="deleteExpense(${expense.id})">Delete</button></td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => console.error('Error loading expenses:', err));
}

function deleteExpense(id) {
    if (confirm('Are you sure you want to delete this expense?')) {
        fetch(`/api/delete-expense/${id}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    loadExpenses();
                    loadStats();
                    loadCharts();
                }
            })
            .catch(err => console.error('Error deleting expense:', err));
    }
}

// ==================== Add Expense ====================
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-expense-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;
            const description = document.getElementById('description').value;
            const dateValue = document.getElementById('date').value;
            
            fetch('/api/add-expense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount, category, description, date: dateValue })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message + (data.warning ? '\n\n' + data.warning : ''));
                    form.reset();
                    const dateInput = document.getElementById('date');
                    dateInput.value = new Date().toISOString().slice(0, 16);
                    loadStats();
                    loadCharts();
                    loadBudget();
                } else {
                    alert('❌ ' + data.error);
                }
            })
            .catch(err => console.error('Error adding expense:', err));
        });
    }
});

// ==================== Budget ====================
function loadBudget() {
    fetch('/api/budget')
        .then(r => r.json())
        .then(data => {
            document.getElementById('budget-amount').textContent = `₹${data.budget}`;
            document.getElementById('budget-spent').textContent = `₹${data.spent.toFixed(2)}`;
            document.getElementById('budget-remaining').textContent = `₹${data.remaining.toFixed(2)}`;
            document.getElementById('budget-percentage').textContent = `${data.percentage}%`;
            
            const progressBar = document.getElementById('budget-progress-bar');
            progressBar.style.width = `${Math.min(data.percentage, 100)}%`;
            
            if (data.over_budget) {
                progressBar.style.background = 'linear-gradient(90deg, #EF4444, #DC2626)';
                document.getElementById('budget-warning').textContent = `⚠️ You have exceeded your monthly budget by ₹${data.over_amount}. Spend cautiously or increase next month's budget.`;
                document.getElementById('budget-warning').classList.add('budget-warning-active');
            } else {
                if (data.percentage > 80) {
                    progressBar.style.background = 'linear-gradient(90deg, #F59E0B, #FBBF24)';
                } else {
                    progressBar.style.background = 'linear-gradient(90deg, #2563EB, #10B981)';
                }
                document.getElementById('budget-warning').textContent = '';
                document.getElementById('budget-warning').classList.remove('budget-warning-active');
            }
            
            document.getElementById('budget-input').value = data.budget;
        })
        .catch(err => console.error('Error loading budget:', err));
}

function setBudget() {
    const budget = document.getElementById('budget-input').value;
    if (!budget || budget <= 0) {
        alert('Please enter a valid budget amount');
        return;
    }
    
    fetch('/api/budget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ budget: parseFloat(budget) })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('✅ Budget updated!');
            loadBudget();
        }
    })
    .catch(err => console.error('Error setting budget:', err));
}

// ==================== Analytics ====================
function loadAnalytics() {
    // Category breakdown
    fetch('/api/expenses/category')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('categoryChartFull').getContext('2d');
            if (categoryChartFull) categoryChartFull.destroy();
            categoryChartFull = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Spending by Category',
                        data: Object.values(data),
                        backgroundColor: [
                            '#2563EB', '#10B981', '#F59E0B', '#EF4444',
                            '#8B5CF6', '#EC4899', '#14B8A6', '#3B82F6'
                        ],
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    indexAxis: 'x',
                    responsive: true,
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + value;
                                }
                            }
                        }
                    }
                }
            });
        });
    
    // Trend chart
    fetch('/api/expenses/timeline')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('trendChartFull').getContext('2d');
            if (trendChartFull) trendChartFull.destroy();
            trendChartFull = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Daily Spending Trend',
                        data: data.amounts,
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: '#10B981'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + value;
                                }
                            }
                        }
                    }
                }
            });
        });
}

// ==================== Chat ====================
function sendMessage(event) {
    event.preventDefault();
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;
    
    const chatMessages = document.getElementById('chat-messages');
    
    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user';
    userDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    chatMessages.appendChild(userDiv);
    
    // Clear input
    input.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Send to API
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
    .then(r => r.json())
    .then(data => {
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-message bot';
        botDiv.innerHTML = `<div class="message-content">${formatMessage(data.response)}</div>`;
        chatMessages.appendChild(botDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Refresh data
        loadStats();
        loadCharts();
    })
    .catch(err => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message bot';
        errorDiv.innerHTML = `<div class="message-content">❌ Error: ${err.message}</div>`;
        chatMessages.appendChild(errorDiv);
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatMessage(text) {
    // Convert markdown-style formatting
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

// ==================== Export ====================
function exportData() {
    window.location.href = '/api/export';
}
