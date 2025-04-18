#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

def create_html_template():
    """
    Generate the HTML dashboard template for kdevops tests.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kdevops Test Results</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <style>
        :root {
            --primary-color: #34495e;
            --success-color: #2ecc71;
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
        
        .chip {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .chip-ok {
            background-color: var(--success-color);
        }
        
        .chip-failed {
            background-color: var(--danger-color);
        }
        
        .chip-unknown {
            background-color: var(--warning-color);
        }
        
        .test-details {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .test-section {
            margin-bottom: 20px;
        }
        
        .test-section-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--primary-color);
        }
        
        .test-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        
        .test-item:last-child {
            border-bottom: none;
        }
        
        .test-name {
            font-weight: bold;
        }
        
        .test-result {
            float: right;
            font-weight: bold;
        }
        
        .test-result.pass {
            color: var(--success-color);
        }
        
        .test-result.fail {
            color: var(--danger-color);
        }

        .header-content {
            display: flex; /* Use flexbox to align children */
            justify-content: space-between; /* Space between text and the image */
            align-items: center; /* Vertically align text and image */
            gap: 10px; /* Space between the text and the image */
        }

        .header-text {
            flex: 1; /* Text takes available space */
            margin: 0; /* Remove extra margin around the heading */
        }

        .header-logo {
            width: 40px; /* Adjust logo size */
            height: auto; /* Maintain aspect ratio */
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .summary-cards {
                grid-template-columns: 1fr;
            }

            .header-text {
                flex: 1; /* Text takes available space */
                margin: 0; /* Remove extra margin around the heading */
            }

            .header-content {
                flex-direction: column; /* Stack text and image */
                text-align: center;
            }

            .header-logo {
                width: 20px; /* Slightly smaller on small screens */
                height: auto; /* Maintain aspect ratio */
            }

        }
    </style>
</head>
<body>
    <header>
        <div class="container">
             <div class="header-content">
                <div class="header-text">
                    <h1>kdevops Test Results</h1>
                </div>
                <a href="https://github.com/linux-kdevops/kdevops-results-archive" alt="kdevops-results-archive git tree">
                <img src="https://github.com/linux-kdevops/kdevops-results-archive/raw/main/images/kdevops-archive.png" alt="kdevops-results-archive logo" class="header-logo">
                </a>
             </div>
        </div>
    </header>
    
    <div class="container">
        <div class="card">
            <div class="card-header">Test Run Information</div>
            <div id="commit-details"></div>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-header">Test Result</div>
                <div id="test-result-chip"></div>
                <div id="test-number" class="card-subtitle"></div>
            </div>
            
            <div class="card">
                <div class="card-header">Test Stats</div>
                <div id="test-stats"></div>
            </div>
            
            <div class="card">
                <div class="card-header">Environment</div>
                <div id="environment-details"></div>
            </div>
        </div>
        
        <div class="test-details">
            <div class="test-section-title">Test Profiles</div>
            <div id="test-profiles"></div>
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
                ${data.filesystem ? `<p><strong>Filesystem:</strong> ${data.filesystem}</p>` : ''}
                <p><strong>Tree:</strong> ${data.tree}</p>
                <p><strong>Ref:</strong> ${data.ref}</p>
            `;
            document.getElementById('commit-details').innerHTML = commitDetailsHtml;
            
            // Set test result chip
            const resultClass = data.test_result === 'ok' ? 'chip-ok' : 
                              (data.test_result === 'failed' ? 'chip-failed' : 'chip-unknown');
            const resultText = data.test_result.toUpperCase();
            
            document.getElementById('test-result-chip').innerHTML = 
                `<div class="chip ${resultClass}">${resultText}</div>`;
                
            // Set test number
            if (data.test_number) {
                document.getElementById('test-number').textContent = 
                    `Test run #${data.test_number} of the day`;
            }
            
            // Set test stats
            const totalTests = data.totals.test_count;
            const passedTests = totalTests - data.totals.failure_count - data.totals.skipped_count;
            const statsHtml = `
                <p><strong>Total Tests:</strong> ${totalTests}</p>
                <p><strong>Passed Tests:</strong> <span class="success">${passedTests}</span></p>
                <p><strong>Failed Tests:</strong> <span class="danger">${data.totals.failure_count}</span></p>
                <p><strong>Skipped Tests:</strong> <span class="warning">${data.totals.skipped_count}</span></p>
                <p><strong>Duration:</strong> ${formatDuration(data.totals.duration)}</p>
            `;
            document.getElementById('test-stats').innerHTML = statsHtml;
            
            // Set environment details
            const envHtml = `
                <p><strong>CPUs:</strong> ${data.cpus}</p>
                ${data.filesystem ? `<p><strong>Filesystem:</strong> ${data.filesystem.toUpperCase()}</p>` : ''}
            `;
            document.getElementById('environment-details').innerHTML = envHtml;
            
            // Set test profiles
            const testProfilesEl = document.getElementById('test-profiles');
            testProfilesEl.innerHTML = '';
            
            Object.keys(data.profiles).forEach(profileName => {
                const profile = data.profiles[profileName];
                
                const profileEl = document.createElement('div');
                profileEl.className = 'test-section';
                
                const headerEl = document.createElement('div');
                headerEl.className = 'test-section-title';
                headerEl.textContent = `${profileName}: ${profile.test_count} tests, ${profile.failure_count} failures, ${profile.skipped_count} skipped, ${profile.duration} seconds`;
                
                profileEl.appendChild(headerEl);
                
                // Add test results if any
                if (profile.failures && profile.failures.length > 0) {
                    const failuresEl = document.createElement('div');
                    failuresEl.innerHTML = `<strong>Failures:</strong> ${profile.failures.join(', ')}`;
                    profileEl.appendChild(failuresEl);
                }
                
                testProfilesEl.appendChild(profileEl);
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
    Generate an HTML template for the kdevops index page.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kdevops Test Results</title>
    <style>
        :root {
            --primary-color: #34495e;
            --success-color: #2ecc71;
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
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
        
        .result-ok {
            background-color: var(--success-color);
        }
        
        .result-failed {
            background-color: var(--danger-color);
        }
        
        .result-unknown {
            background-color: var(--warning-color);
        }
        
        .result-test-number {
            background-color: white;
            color: #333;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .result-date {
            font-size: 0.8em;
            opacity: 0.8;
            display: block;
            margin-top: 5px;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            font-size: 1em;
        }
        
        .filters {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .filter-button {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            background-color: #eee;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .filter-button.active {
            background-color: var(--primary-color);
            color: white;
        }
        
        .no-results {
            color: #777;
            font-style: italic;
            padding: 10px;
        }

        .header-content {
            display: flex;
            justify-content: space-between; /* Space between text and images */
            align-items: center; /* Vertically align text and images */
            gap: 20px; /* Space between the text and the image container */
            text-align: left;
        }

        .header-text {
            flex: 1; /* Allow text to take up as much space as needed */
        }

        .header-logos {
            display: flex;
            flex-direction: row; /* Align images side-by-side */
            align-items: center; /* Center the images vertically */
            gap: 10px; /* Space between the images */
        }

        .header-logo {
            width: 40px; /* Adjust size of logos */
            height: auto; /* Automatically adjust height to maintain aspect ratio */
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .filters {
                flex-wrap: wrap;
            }

            .header-content {
                flex-direction: column; /* Stack text and images vertically */
                text-align: center;
            }

            .header-text {
                margin-bottom: 20px;
            }

            .header-logos {
                flex-direction: row; /* Keep images side-by-side even on small screens */
                gap: 10px;
            }

            .header-logo {
                width: 20px; /* Slightly smaller logos on small screens */
                height: auto; /* Maintain aspect ratio */
            }

        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="header-text">
                    <h1>kdevops Test Results</h1>
                </div>
                <div class="header-logos">
                    <a href="https://github.com/linux-kdevops/kdevops-results-archive" alt="kdevops-results-archive git tree">
                    <img src="https://github.com/linux-kdevops/kdevops-results-archive/raw/main/images/kdevops-archive.png" alt="kdevops-results-archive logo" class="header-logo">
                    </a>
                </div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <input type="text" id="search-input" class="search-box" placeholder="Search by kernel version, date, or commit message...">
        
        <div class="filters">
            <button class="filter-button active" data-filter="all">All</button>
            <button class="filter-button" data-filter="ok">Passed</button>
            <button class="filter-button" data-filter="failed">Failed</button>
        </div>
        
        <div class="panel">
            <div class="panel-title">Test Results</div>
            <div id="test-results">
                <div class="no-results">No test results available</div>
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
            const resultsContainer = document.getElementById('test-results');
            const searchInput = document.getElementById('search-input');
            const filterButtons = document.querySelectorAll('.filter-button');
            
            // Sort results by date (newest first)
            results.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            // Current filter
            let currentFilter = 'all';
            
            // Function to render results based on filter and search
            function renderResults() {
                const searchTerm = searchInput.value.toLowerCase();
                
                // Filter results
                const filteredResults = results.filter(result => {
                    // Apply search filter
                    const matchesSearch = 
                        result.display_name.toLowerCase().includes(searchTerm) || 
                        (new Date(result.date).toLocaleDateString() + ' ' + 
                         new Date(result.date).toLocaleTimeString()).toLowerCase().includes(searchTerm);
                    
                    // Apply status filter
                    const matchesFilter = 
                        currentFilter === 'all' || 
                        (currentFilter === 'ok' && result.test_result === 'ok') ||
                        (currentFilter === 'failed' && result.test_result === 'failed');
                    
                    return matchesSearch && matchesFilter;
                });
                
                // Render results
                if (filteredResults.length > 0) {
                    resultsContainer.innerHTML = '';
                    
                    filteredResults.forEach(result => {
                        const link = document.createElement('a');
                        link.href = result.url;
                        
                        // Determine result class
                        const resultClass = result.test_result === 'ok' ? 'result-ok' : 
                                         (result.test_result === 'failed' ? 'result-failed' : 'result-unknown');
                        
                        link.className = `result-link ${resultClass}`;
                        
                        link.innerHTML = `
                            <div>
                                <div>${result.display_name}</div>
                                <span class="result-date">${formatDate(result.date)}</span>
                            </div>
                            <div class="result-test-number">${result.test_number || '?'}</div>
                        `;
                        
                        resultsContainer.appendChild(link);
                    });
                } else {
                    resultsContainer.innerHTML = '<div class="no-results">No matching test results found</div>';
                }
            }
            
            // Initial render
            renderResults();
            
            // Search input event
            searchInput.addEventListener('input', renderResults);
            
            // Filter button events
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active class from all buttons
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    
                    // Add active class to clicked button
                    this.classList.add('active');
                    
                    // Set current filter
                    currentFilter = this.dataset.filter;
                    
                    // Re-render results
                    renderResults();
                });
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
