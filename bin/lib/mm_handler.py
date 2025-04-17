#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

import os
import re
import json
import shutil

# Import templates
from lib.mm_templates import create_html_template, create_index_template

def parse_mm_test_results(log):
    """
    Parse memory management test results from the log.
    """
    tests = {
        'kernel': {},
        'userspace': {}
    }
    
    # Parse kernel test results
    kernel_pattern = r"(\w+) kernel: (\w+): (\d+) of (\d+) tests passed"
    kernel_matches = re.finditer(kernel_pattern, log, re.MULTILINE)
    
    for match in kernel_matches:
        test_name = match.group(2).lower()
        passed = int(match.group(3))
        total = int(match.group(4))
        
        tests['kernel'][test_name] = {
            'passed': passed,
            'total': total,
            'failed': total - passed
        }
    
    # Parse userspace test results
    userspace_pattern = r"(\w+): (\d+) of (\d+) tests passed"
    userspace_matches = re.finditer(userspace_pattern, log, re.MULTILINE)
    
    for match in userspace_matches:
        test_name = match.group(1).lower()
        passed = int(match.group(2))
        total = int(match.group(3))
        
        # Skip duplicates (already found in kernel tests)
        if test_name not in tests['userspace']:
            tests['userspace'][test_name] = {
                'passed': passed,
                'total': total,
                'failed': total - passed
            }
    
    return tests


def update_index_page(mm_dir, results):
    """
    Update the index page for the memory management directory with provided results.
    """
    # Get the index template
    template_html = create_index_template()
    
    # Replace placeholder with actual data
    index_html = template_html.replace(
        "const testResults = RESULTS_PLACEHOLDER;", 
        f"const testResults = {json.dumps(results, indent=4)};"
    )
    
    # Write the index.html
    index_path = os.path.join(mm_dir, 'index.html')
    with open(index_path, 'w') as f:
        f.write(index_html)
    
    print(f"Index HTML updated at {index_path}")


def get_html_filename(data):
    """
    Generate the HTML filename based on the kernel data.
    """
    if data['is_vanilla']:
        # For vanilla releases, use version number directly
        if data['kernel_type'] == "stable":
            return f"v{data['base_version']}.html"
        elif data['kernel_type'] == "rc":
            # Transform 6.15.0-rc2 to v6.15-rc2.html
            base = data['base_version'].replace('.0-rc', '-rc')
            return f"v{base}.html"
        elif data['kernel_type'] == "vanilla":
            # Transform 6.15.0 to v6.15.html
            if data['base_version'].endswith('.0'):
                base = data['base_version'][:-2]
            else:
                base = data['base_version']
            return f"v{base}.html"
    elif data['kernel_type'] == "next":
        # For linux-next, use the tag
        return f"{data['base_version']}.html"
    
    # For development branches, use the full kernel version
    return f"{data['kernel']}.html"


def process_data(data, output_dir):
    """
    Process memory management test data and generate dashboard files.
    This is the main entry point for the mm_handler module.
    """
    # Get log content
    log = data.get('log', '')
    
    # Parse memory management test results
    tests = parse_mm_test_results(log)
    
    # Add MM-specific data to the common data structure
    data['tests'] = tests
    
    # Calculate total failures for summary
    kernel_failures = sum(test.get('failed', 0) for test in tests.get('kernel', {}).values())
    userspace_failures = sum(test.get('failed', 0) for test in tests.get('userspace', {}).values())
    total_failures = kernel_failures + userspace_failures
    
    # Remove the full log from data before saving to JSON (to reduce file size)
    if 'log' in data:
        del data['log']
    
    # Create directory for memory management tests
    mm_dir = os.path.join(output_dir, 'mm')
    os.makedirs(mm_dir, exist_ok=True)
    
    # Determine the HTML filename
    html_filename = get_html_filename(data)
    
    # Write the JSON data file
    json_path = os.path.join(mm_dir, html_filename.replace('.html', '.json'))
    
    # Remove existing file if it exists
    if os.path.exists(json_path):
        os.remove(json_path)
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"JSON data written to {json_path}")
    
    # Create HTML file path
    html_path = os.path.join(mm_dir, html_filename)
    
    # Remove existing HTML if it exists
    if os.path.exists(html_path):
        os.remove(html_path)
    
    # Get the HTML template
    template_html = create_html_template()
    
    # Replace placeholder with actual JSON data
    dashboard_html = template_html.replace(
        "const testData = DATA_PLACEHOLDER;", 
        f"const testData = {json.dumps(data, indent=4)};"
    )
    
    # Write the HTML dashboard
    with open(html_path, 'w') as f:
        f.write(dashboard_html)
    
    print(f"Dashboard HTML written to {html_path}")
    
    # Collect data for the index
    index_result = {
        'url': html_filename,
        'display_name': html_filename.replace('.html', ''),
        'type': data.get('kernel_type', 'development'),
        'date': data.get('date', ''),
        'failure_count': total_failures
    }
    
    # Find all existing HTML files (except index.html) to compile index
    all_results = [index_result]  # Start with the current result
    html_files = [f for f in os.listdir(mm_dir) if f.endswith('.html') and f != 'index.html' and f != html_filename]
    
    for html_file in html_files:
        # Find the corresponding JSON file
        json_file = html_file.replace('.html', '.json')
        json_path = os.path.join(mm_dir, json_file)
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    file_data = json.load(f)
                
                # Calculate failures
                k_fails = sum(test.get('failed', 0) for test in file_data.get('tests', {}).get('kernel', {}).values())
                u_fails = sum(test.get('failed', 0) for test in file_data.get('tests', {}).get('userspace', {}).values())
                
                # Extract relevant information
                result = {
                    'url': html_file,
                    'display_name': html_file.replace('.html', ''),
                    'type': file_data.get('kernel_type', 'development'),
                    'date': file_data.get('date', ''),
                    'failure_count': k_fails + u_fails
                }
                
                all_results.append(result)
            except Exception as e:
                print(f"Error processing {json_path}: {e}")
    
    # Update the index page
    update_index_page(mm_dir, all_results)
    
    return html_path
