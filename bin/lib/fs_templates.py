#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

def create_html_template():
    """
    Generate the HTML dashboard template for filesystem tests.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>fstests results dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <style>
        :root {
            --primary-color: #2c3e50;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --info-color: #3498db;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f9f9f9;
            color: #333;
            line-height: 1.6;
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
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
        
        .card-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .success { color: var(--success-color); }
        .warning { color: var(--warning-color); }
        .danger { color: var(--danger-color); }
        .info { color: var(--info-color); }
        
        .card-subtitle {
            color: #777;
            font-size: 0.9em;
        }
        
        .chart-container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .chart-header {
            margin-bottom: 15px;
            font-size: 1.2em;
            color: var(--primary-color);
        }
        
        .profile-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .progress {
            height: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 5px;
        }
        
        .success-bar { background-color: var(--success-color); }
        .warning-bar { background-color: var(--warning-color); }
        .danger-bar { background-color: var(--danger-color); }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        table th, table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        table th {
            background-color: var(--primary-color);
            color: white;
            position: sticky;
            top: 0;
        }
        
        table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        table tr:hover {
            background-color: #f1f1f1;
        }
        
        .failure-tag {
            display: inline-block;
            background-color: var(--danger-color);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        
        .failures-container {
            max-height: 200px;
            overflow-y: auto;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #eee;
        }
        
        .search-box {
            padding: 10px;
            width: 100%;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
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
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .profile-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>fstests results dashboard - FILESYSTEM_TYPE</h1>
        </div>
    </header>
    
    <div class="container">
        <div id="commit-info" class="card">
            <div class="card-header">Test Run Information</div>
            <div id="commit-details"></div>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-header">Total Tests</div>
                <div id="total-tests" class="card-value info">0</div>
                <div class="card-subtitle">Executed across all profiles</div>
            </div>
            
            <div class="card">
                <div class="card-header">Pass Rate</div>
                <div id="pass-rate" class="card-value success">0%</div>
                <div class="card-subtitle">Tests passed successfully</div>
            </div>
            
            <div class="card">
                <div class="card-header">Failed Tests</div>
                <div id="failed-tests" class="card-value danger">0</div>
                <div class="card-subtitle">Tests with failures</div>
            </div>
            
            <div class="card">
                <div class="card-header">Skipped Tests</div>
                <div id="skipped-tests" class="card-value warning">0</div>
                <div class="card-subtitle">Tests skipped</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" data-tab="summary">Summary</div>
            <div class="tab" data-tab="profiles">Profiles</div>
            <div class="tab" data-tab="failures">Failures</div>
        </div>
        
        <div id="summary-tab" class="tab-content active">
            <div class="chart-container">
                <div class="chart-header">Results Overview</div>
                <canvas id="results-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-header">Test Duration by Profile</div>
                <canvas id="duration-chart"></canvas>
            </div>
        </div>
        
        <div id="profiles-tab" class="tab-content">
            <input type="text" id="profile-search" class="search-box" placeholder="Search profiles...">
            <div id="profile-list" class="profile-grid"></div>
        </div>
        
        <div id="failures-tab" class="tab-content">
            <input type="text" id="failure-search" class="search-box" placeholder="Search failures...">
            <table id="failures-table">
                <thead>
                    <tr>
                        <th>Test</th>
                        <th>Profiles</th>
                    </tr>
                </thead>
                <tbody id="failures-body"></tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Test data will be injected here
        const testData = DATA_PLACEHOLDER;
        
        // Format seconds to readable duration
        function formatDuration(seconds) {
            return moment.duration(seconds, 'seconds').humanize();
        }
        
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
                <p><strong>Filesystem:</strong> ${data.filesystem}</p>
                <p><strong>CPUs:</strong> ${data.cpus}</p>
                <p><strong>Total Duration:</strong> ${formatDuration(data.totals.duration)}</p>
            `;
            document.getElementById('commit-details').innerHTML = commitDetailsHtml;
            
            // Set summary cards
            document.getElementById('total-tests').textContent = data.totals.test_count.toLocaleString();
            
            const passRate = ((data.totals.test_count - data.totals.failure_count - data.totals.skipped_count) / data.totals.test_count * 100).toFixed(1);
            document.getElementById('pass-rate').textContent = passRate + '%';
            
            document.getElementById('failed-tests').textContent = data.totals.failure_count.toLocaleString();
            document.getElementById('skipped-tests').textContent = data.totals.skipped_count.toLocaleString();
            
            // Create results chart
            const resultsCtx = document.getElementById('results-chart').getContext('2d');
            const resultsChart = new Chart(resultsCtx, {
                type: 'pie',
                data: {
                    labels: ['Passed', 'Failed', 'Skipped'],
                    datasets: [{
                        data: [
                            data.totals.test_count - data.totals.failure_count - data.totals.skipped_count,
                            data.totals.failure_count,
                            data.totals.skipped_count
                        ],
                        backgroundColor: [
                            'rgba(39, 174, 96, 0.8)',
                            'rgba(231, 76, 60, 0.8)',
                            'rgba(243, 156, 18, 0.8)'
                        ],
                        borderColor: [
                            'rgba(39, 174, 96, 1)',
                            'rgba(231, 76, 60, 1)',
                            'rgba(243, 156, 18, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${context.label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Create duration chart
            const durationCtx = document.getElementById('duration-chart').getContext('2d');
            const profileNames = Object.keys(data.profiles);
            const profileDurations = profileNames.map(name => data.profiles[name].duration / 60); // Convert to minutes
            
            const durationChart = new Chart(durationCtx, {
                type: 'bar',
                data: {
                    labels: profileNames,
                    datasets: [{
                        label: 'Duration (minutes)',
                        data: profileDurations,
                        backgroundColor: 'rgba(52, 152, 219, 0.5)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Minutes'
                            }
                        }
                    }
                }
            });
            
            // Create profile cards
            const profileList = document.getElementById('profile-list');
            profileList.innerHTML = '';
            
            Object.keys(data.profiles).forEach(profileName => {
                const profile = data.profiles[profileName];
                const passCount = profile.test_count - profile.failure_count - profile.skipped_count;
                const passPercent = (passCount / profile.test_count * 100).toFixed(1);
                const failPercent = (profile.failure_count / profile.test_count * 100).toFixed(1);
                const skipPercent = (profile.skipped_count / profile.test_count * 100).toFixed(1);
                
                const profileCard = document.createElement('div');
                profileCard.className = 'card';
                profileCard.innerHTML = `
                    <div class="card-header">${profileName}</div>
                    <div>Total: <strong>${profile.test_count}</strong> tests</div>
                    <div>Duration: <strong>${formatDuration(profile.duration)}</strong></div>
                    <div class="progress-container">
                        <label>Passed: ${passCount} (${passPercent}%)</label>
                        <div class="progress">
                            <div class="progress-bar success-bar" style="width: ${passPercent}%"></div>
                        </div>
                    </div>
                    <div class="progress-container">
                        <label>Failed: ${profile.failure_count} (${failPercent}%)</label>
                        <div class="progress">
                            <div class="progress-bar danger-bar" style="width: ${failPercent}%"></div>
                        </div>
                    </div>
                    <div class="progress-container">
                        <label>Skipped: ${profile.skipped_count} (${skipPercent}%)</label>
                        <div class="progress">
                            <div class="progress-bar warning-bar" style="width: ${skipPercent}%"></div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong>Failures:</strong>
                        <div class="failures-container">
                            ${profile.failures.map(f => `<span class="failure-tag">${f}</span>`).join('')}
                        </div>
                    </div>
                `;
                
                profileList.appendChild(profileCard);
            });
            
            // Create failures table
            const failuresTable = document.getElementById('failures-body');
            failuresTable.innerHTML = '';
            
            // Collect all unique failures and the profiles they appear in
            const failureMap = {};
            
            Object.keys(data.profiles).forEach(profileName => {
                const profile = data.profiles[profileName];
                
                profile.failures.forEach(failure => {
                    if (!failureMap[failure]) {
                        failureMap[failure] = [];
                    }
                    failureMap[failure].push(profileName);
                });
            });
            
            // Sort failures by number of profiles they appear in (descending)
            const sortedFailures = Object.keys(failureMap).sort((a, b) => 
                failureMap[b].length - failureMap[a].length
            );
            
            sortedFailures.forEach(failure => {
                const row = document.createElement('tr');
                
                const testCell = document.createElement('td');
                testCell.textContent = failure;
                
                const profilesCell = document.createElement('td');
                profilesCell.innerHTML = failureMap[failure].map(p => 
                    `<span class="failure-tag">${p}</span>`
                ).join('');
                
                row.appendChild(testCell);
                row.appendChild(profilesCell);
                
                failuresTable.appendChild(row);
            });
            
            // Setup search functionality
            document.getElementById('profile-search').addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                const profileCards = profileList.querySelectorAll('.card');
                
                profileCards.forEach(card => {
                    const profileName = card.querySelector('.card-header').textContent.toLowerCase();
                    if (profileName.includes(searchTerm)) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
            
            document.getElementById('failure-search').addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                const rows = failuresTable.querySelectorAll('tr');
                
                rows.forEach(row => {
                    const testName = row.cells[0].textContent.toLowerCase();
                    if (testName.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
        
        // Setup tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Hide all tab content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Show the corresponding tab content
                const tabId = this.getAttribute('data-tab');
                document.getElementById(tabId + '-tab').classList.add('active');
            });
        });
        
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
    Generate an HTML template for the filesystem index page.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FILESYSTEM fstests results</title>
    <style>
        :root {
            --primary-color: #2c3e50;
            --stable-color: #3498db;
            --vanilla-color: #27ae60;
            --next-color: #f39c12;
            --dev-color: #e74c3c;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f9f9f9;
            color: #333;
            line-height: 1.6;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
            border-bottom: 2px solid;
            padding-bottom: 10px;
        }
        
        .stable-panel .panel-title {
            border-color: var(--stable-color);
        }
        
        .vanilla-panel .panel-title {
            border-color: var(--vanilla-color);
        }
        
        .next-panel .panel-title {
            border-color: var(--next-color);
        }
        
        .dev-panel .panel-title {
            border-color: var(--dev-color);
        }
        
        .result-link {
            display: block;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        
        .result-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stable-link {
            background-color: var(--stable-color);
        }
        
        .vanilla-link {
            background-color: var(--vanilla-color);
        }
        
        .next-link {
            background-color: var(--next-color);
        }
        
        .dev-link {
            background-color: var(--dev-color);
        }
        
        .result-date {
            font-size: 0.8em;
            opacity: 0.8;
            display: block;
            margin-top: 5px;
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
            <h1>FILESYSTEM fstests results</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="panel-container">
            <!-- Stable Releases Panel -->
            <div class="panel stable-panel">
                <div class="panel-title">Stable Releases</div>
                <div id="stable-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No stable release results available</div>
                </div>
            </div>
            
            <!-- Vanilla Releases Panel -->
            <div class="panel vanilla-panel">
                <div class="panel-title">Vanilla Releases</div>
                <div id="vanilla-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No vanilla release results available</div>
                </div>
            </div>
            
            <!-- Next Releases Panel -->
            <div class="panel next-panel">
                <div class="panel-title">Linux Next</div>
                <div id="next-releases">
                    <!-- Will be filled dynamically -->
                    <div class="no-results">No linux-next results available</div>
                </div>
            </div>
            
            <!-- Development Releases Panel -->
            <div class="panel dev-panel">
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
            // Group results by type
            const stableResults = results.filter(r => r.type === 'stable');
            const vanillaResults = results.filter(r => r.type === 'vanilla' || r.type === 'rc');
            const nextResults = results.filter(r => r.type === 'next');
            const devResults = results.filter(r => r.type === 'development');
            
            // Sort results by date (newest first)
            const sortByDate = (a, b) => new Date(b.date) - new Date(a.date);
            
            stableResults.sort(sortByDate);
            vanillaResults.sort(sortByDate);
            nextResults.sort(sortByDate);
            devResults.sort(sortByDate);
            
            // Function to create links for a panel
            function createLinks(panelId, results, linkClass) {
                const panel = document.getElementById(panelId);
                
                if (results.length > 0) {
                    panel.innerHTML = '';
                    
                    results.forEach(result => {
                        const link = document.createElement('a');
                        link.href = result.url;
                        link.className = `result-link ${linkClass}`;
                        
                        let displayName = result.display_name;
                        if (result.failure_count > 0) {
                            displayName += ` (${result.failure_count} failures)`;
                        }
                        
                        link.innerHTML = `
                            ${displayName}
                            <span class="result-date">${formatDate(result.date)}</span>
                        `;
                        
                        panel.appendChild(link);
                    });
                }
            }
            
            // Create links for each panel
            createLinks('stable-releases', stableResults, 'stable-link');
            createLinks('vanilla-releases', vanillaResults, 'vanilla-link');
            createLinks('next-releases', nextResults, 'next-link');
            createLinks('dev-releases', devResults, 'dev-link');
        }
        
        // Initialize the index page
        document.addEventListener('DOMContentLoaded', function() {
            initIndex(testResults);
        });
    </script>
</body>
</html>
"""
