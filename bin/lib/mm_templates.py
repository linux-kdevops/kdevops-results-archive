#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

def create_html_template():
    """
    Generate the HTML dashboard template for memory management tests.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Management Test Results</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <style>
        :root {
            --primary-color: #673ab7;
            --success-color: #4caf50;
            --warning-color: #ff9800;
            --danger-color: #f44336;
            --info-color: #2196f3;
            --light-color: #f5f5f5;
            --dark-color: #333;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-color);
            color: var(--dark-color);
            line-height: 1.6;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://github.com/linux-kdevops/kdevops/raw/main/images/kdevops-trans-bg-edited-individual-with-logo-gausian-blur-1600x1600.png');
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
            opacity: 0.1;
            z-index: -1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        header h1 {
            margin: 0;
            padding: 0 20px;
        }
        
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            transition: transform 0.2s ease-in-out;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card-header {
            margin-bottom: 15px;
            font-size: 1.2em;
            color: var(--primary-color);
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        .success { color: var(--success-color); }
        .warning { color: var(--warning-color); }
        .danger { color: var(--danger-color); }
        .info { color: var(--info-color); }
        
        .chart-container {
            height: 300px;
            margin-bottom: 20px;
        }
        
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .test-card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .test-header {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--primary-color);
        }
        
        .test-stat {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-weight: bold;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
        }
        
        .tab.active {
            border-bottom: 3px solid var(--primary-color);
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .test-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Memory Management Test Results</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="card">
            <div class="card-header">Test Run Information</div>
            <div id="commit-details"></div>
        </div>
        
        <div class="tabs">
            <div class="tab active" data-tab="overview">Overview</div>
            <div class="tab" data-tab="kernel">Kernel Tests</div>
            <div class="tab" data-tab="userspace">Userspace Tests</div>
        </div>
        
        <div id="overview-tab" class="tab-content active">
            <div class="card">
                <div class="card-header">Test Results Summary</div>
                <div class="chart-container">
                    <canvas id="summary-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div id="kernel-tab" class="tab-content">
            <div class="card">
                <div class="card-header">Kernel Space Tests</div>
                <div id="kernel-tests" class="test-grid"></div>
            </div>
        </div>
        
        <div id="userspace-tab" class="tab-content">
            <div class="card">
                <div class="card-header">User Space Tests</div>
                <div id="userspace-tests" class="test-grid"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Test data will be injected here
        const testData = DATA_PLACEHOLDER;
        
        // Format date string
        function formatDate(dateString) {
            return moment(dateString).format('YYYY-MM-DD HH:mm:ss');
        }
        
        // Initialize the dashboard
        function initDashboard(data) {
            // Set commit info
            const commitDetailsHtml = `
                <p><strong>Commit:</strong> ${data.commit}</p>
                <p><strong>Date:</strong> ${formatDate(data.date)}</p>
                <p><strong>Subject:</strong> ${data.subject}</p>
                <p><strong>Kernel:</strong> ${data.kernel}</p>
                <p><strong>CPUs:</strong> ${data.cpus}</p>
            `;
            document.getElementById('commit-details').innerHTML = commitDetailsHtml;
            
            // Create summary chart
            createSummaryChart(data);
            
            // Create kernel tests display
            createTestDisplay('kernel', data.tests.kernel);
            
            // Create userspace tests display
            createTestDisplay('userspace', data.tests.userspace);
            
            // Setup tabs
            setupTabs();
        }
        
        function createSummaryChart(data) {
            const ctx = document.getElementById('summary-chart').getContext('2d');
            
            // Collect test data
            const labels = [];
            const kernelPassed = [];
            const kernelTotal = [];
            const userspacePassed = [];
            const userspaceTotal = [];
            
            // Process kernel tests
            for (const [name, test] of Object.entries(data.tests.kernel)) {
                labels.push(`${name} (Kernel)`);
                kernelPassed.push(test.passed);
                kernelTotal.push(test.total);
            }
            
            // Process userspace tests
            for (const [name, test] of Object.entries(data.tests.userspace)) {
                labels.push(`${name} (Userspace)`);
                userspacePassed.push(test.passed);
                userspaceTotal.push(test.total);
            }
            
            // Create chart
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Passed Tests',
                            data: [...kernelPassed, ...userspacePassed],
                            backgroundColor: 'rgba(76, 175, 80, 0.7)',
                            borderColor: 'rgba(76, 175, 80, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Total Tests',
                            data: [...kernelTotal, ...userspaceTotal],
                            backgroundColor: 'rgba(33, 150, 243, 0.4)',
                            borderColor: 'rgba(33, 150, 243, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Tests'
                            }
                        }
                    }
                }
            });
        }
        
        function createTestDisplay(type, tests) {
            const container = document.getElementById(`${type}-tests`);
            container.innerHTML = '';
            
            if (Object.keys(tests).length === 0) {
                container.innerHTML = `<p>No ${type} tests found.</p>`;
                return;
            }
            
            for (const [name, test] of Object.entries(tests)) {
                const passRate = (test.passed / test.total * 100).toFixed(2);
                const failCount = test.total - test.passed;
                
                const testCard = document.createElement('div');
                testCard.className = 'test-card';
                
                testCard.innerHTML = `
                    <div class="test-header">${name.charAt(0).toUpperCase() + name.slice(1)}</div>
                    <div class="test-stat">
                        <span class="stat-label">Total Tests:</span>
                        <span>${test.total.toLocaleString()}</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Tests Passed:</span>
                        <span class="success">${test.passed.toLocaleString()}</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Tests Failed:</span>
                        <span class="${failCount > 0 ? 'danger' : ''}">${failCount.toLocaleString()}</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Pass Rate:</span>
                        <span class="${passRate == 100 ? 'success' : (passRate > 90 ? 'warning' : 'danger')}">${passRate}%</span>
                    </div>
                `;
                
                container.appendChild(testCard);
            }
        }
        
        function setupTabs() {
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    // Remove active class from all tabs
                    tabs.forEach(t => t.classList.remove('active'));
                    // Add active class to clicked tab
                    this.classList.add('active');
                    
                    // Hide all tab content
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    
                    // Show the corresponding tab content
                    const tabId = this.getAttribute('data-tab');
                    document.getElementById(`${tabId}-tab`).classList.add('active');
                });
            });
        }
        
        // Initialize dashboard with data
        document.addEventListener('DOMContentLoaded', function() {
            initDashboard(testData);
        });
    </script>
</body>
</html>
"""


def create_index_template():
    """
    Generate an HTML template for the memory management index page.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Management Test Results</title>
    <style>
        :root {
            --primary-color: #673ab7;
            --success-color: #4caf50;
            --warning-color: #ff9800;
            --danger-color: #f44336;
            --info-color: #2196f3;
            --light-color: #f5f5f5;
            --dark-color: #333;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-color);
            color: var(--dark-color);
            line-height: 1.6;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://github.com/linux-kdevops/kdevops/raw/main/images/kdevops-trans-bg-edited-individual-with-logo-gausian-blur-1600x1600.png');
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
            opacity: 0.1;
            z-index: -1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        header h1 {
            margin: 0;
            padding: 0 20px;
        }
        
        .panel-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .panel {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .panel-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
        }
        
        .result-link {
            display: block;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 5px;
            background-color: var(--info-color);
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        
        .result-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .result-link.has-failures {
            background-color: var(--warning-color);
        }
        
        .result-date {
            font-size: 0.8em;
            opacity: 0.8;
            display: block;
            margin-top: 5px;
        }
        
        .result-failures {
            display: inline-block;
            background-color: white;
            color: var(--danger-color);
            padding: 2px 8px;
            border-radius: 12px;
            margin-left: 10px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            font-size: 1em;
        }
        
        .no-results {
            color: #777;
            font-style: italic;
            padding: 10px;
        }
        
        @media (max-width: 768px) {
            .panel-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Memory Management Test Results</h1>
        </div>
    </header>
    
    <div class="container">
        <input type="text" id="search-input" class="search-box" placeholder="Search by kernel version or date...">
        
        <div class="panel-container">
            <!-- Vanilla Releases Panel -->
            <div class="panel">
                <div class="panel-title">Vanilla Releases</div>
                <div id="vanilla-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No vanilla release results available</div>
                </div>
            </div>
            
            <!-- Release Candidates Panel -->
            <div class="panel">
                <div class="panel-title">Release Candidates</div>
                <div id="rc-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No RC release results available</div>
                </div>
            </div>
            
            <!-- Development Branches Panel -->
            <div class="panel">
                <div class="panel-title">Development Branches</div>
                <div id="dev-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No development branch results available</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Test results data will be injected here
        const testResults = RESULTS_PLACEHOLDER;
        
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
        
        function initIndex(results) {
            const searchInput = document.getElementById('search-input');
            
            // Group results by type
            const vanillaResults = results.filter(r => r.type === 'vanilla' || r.type === 'stable');
            const rcResults = results.filter(r => r.type === 'rc');
            const devResults = results.filter(r => r.type === 'development' || r.type === 'next');
            
            // Sort results by date (newest first)
            const sortByDate = (a, b) => new Date(b.date) - new Date(a.date);
            
            vanillaResults.sort(sortByDate);
            rcResults.sort(sortByDate);
            devResults.sort(sortByDate);
            
            // Function to create links for a panel
            function createLinks(panelId, results) {
                const panel = document.getElementById(panelId);
                
                if (results.length > 0) {
                    panel.innerHTML = '';
                    
                    results.forEach(result => {
                        const link = document.createElement('a');
                        link.href = result.url;
                        link.className = `result-link ${result.failure_count > 0 ? 'has-failures' : ''}`;
                        
                        let linkContent = `
                            ${result.display_name}
                            <span class="result-date">${formatDate(result.date)}</span>
                        `;
                        
                        if (result.failure_count > 0) {
                            linkContent += `<span class="result-failures">${result.failure_count} failures</span>`;
                        }
                        
                        link.innerHTML = linkContent;
                        panel.appendChild(link);
                    });
                }
            }
            
            // Create links for each panel
            createLinks('vanilla-releases', vanillaResults);
            createLinks('rc-releases', rcResults);
            createLinks('dev-releases', devResults);
            
            // Search functionality
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                
                // Function to filter and update a panel
                function filterPanel(panelId, panelResults) {
                    const filteredResults = panelResults.filter(result => 
                        result.display_name.toLowerCase().includes(searchTerm) || 
                        formatDate(result.date).toLowerCase().includes(searchTerm)
                    );
                    
                    const panel = document.getElementById(panelId);
                    
                    if (filteredResults.length > 0) {
                        panel.innerHTML = '';
                        filteredResults.forEach(result => {
                            const link = document.createElement('a');
                            link.href = result.url;
                            link.className = `result-link ${result.failure_count > 0 ? 'has-failures' : ''}`;
                            
                            let linkContent = `
                                ${result.display_name}
                                <span class="result-date">${formatDate(result.date)}</span>
                            `;
                            
                            if (result.failure_count > 0) {
                                linkContent += `<span class="result-failures">${result.failure_count} failures</span>`;
                            }
                            
                            link.innerHTML = linkContent;
                            panel.appendChild(link);
                        });
                    } else {
                        panel.innerHTML = '<div class="no-results">No matching results</div>';
                    }
                }
                
                // Filter and update each panel
                filterPanel('vanilla-releases', vanillaResults);
                filterPanel('rc-releases', rcResults);
                filterPanel('dev-releases', devResults);
            });
        }
        
        // Initialize the index page
        document.addEventListener('DOMContentLoaded', function() {
            initIndex(testResults);
        });
    </script>
</body>
</html>
"""
