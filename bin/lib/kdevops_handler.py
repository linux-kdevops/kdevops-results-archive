#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

import os
import re
import json
import shutil

# Import templates
from lib.kdevops_templates import create_html_template, create_index_template

def determine_filesystem_type(subject, log):
    """
    Determine the filesystem type from the commit subject or log content.
    """
    # Common filesystem identifiers
    fs_patterns = {
        'ext4': [r'ext4', r'linux-ext4'],
        'btrfs': [r'btrfs', r'linux-btrfs'],
        'xfs': [r'xfs', r'linux-xfs'],
        # Add more filesystems as needed
    }
    
    # Check in subject first (more reliable)
    for fs, patterns in fs_patterns.items():
        for pattern in patterns:
            if re.search(pattern, subject, re.IGNORECASE):
                return fs
    
    # Try to find in log content if not found in subject
    for fs, patterns in fs_patterns.items():
        for pattern in patterns:
            if re.search(pattern, log, re.IGNORECASE):
                return fs
    
    # Try to determine from profile names (last resort)
    profile_match = re.search(r"^((?:\w+_)+\w+): \d+ tests", log, re.MULTILINE)
    if profile_match:
        profile_name = profile_match.group(1).lower()
        for fs in fs_patterns.keys():
            if fs in profile_name:
                return fs
    
    return None


def parse_fs_test_profiles(log):
    """
    Parse filesystem test profiles from the log.
    """
    profiles = {}

    # Find all profile sections
    profile_pattern = r"^((?:\w+_)+\w+): (\d+) tests, (\d+) failures, (\d+) skipped, (\d+) seconds\n(?:.*?\n)*?  Failures:(.*?)(?=\n(?:\w+_)+\w+: |\nTotals: |\n\n|\Z)"
    profile_sections = re.finditer(profile_pattern, log, re.MULTILINE | re.DOTALL)

    for match in profile_sections:
        profile = match.group(1)
        test_count = int(match.group(2))
        failure_count = int(match.group(3))
        skipped_count = int(match.group(4))
        duration = int(match.group(5))
        
        # Extract all failures, handling multi-line lists
        failures_text = match.group(6).strip()
        # Split by whitespace and filter out empty strings
        failures = [f for f in re.split(r'\s+', failures_text) if f]
        
        profiles[profile] = {
            'test_count': test_count,
            'failure_count': failure_count,
            'skipped_count': skipped_count,
            'duration': duration,
            'failures': failures
        }
        
    return profiles


def extract_fs_totals(log, profiles):
    """
    Extract or calculate filesystem test totals from the log.
    """
    # Extract totals if available
    totals_match = re.search(r"Totals: (\d+) tests, (\d+) skipped, (\d+) failures, (\d+) errors, (\d+)s", log)
    if totals_match:
        return {
            'test_count': int(totals_match.group(1)),
            'skipped_count': int(totals_match.group(2)),
            'failure_count': int(totals_match.group(3)),
            'error_count': int(totals_match.group(4)),
            'duration': int(totals_match.group(5))
        }
    else:
        # Calculate totals from profiles if not explicitly provided
        return {
            'test_count': sum(p['test_count'] for p in profiles.values()),
            'skipped_count': sum(p['skipped_count'] for p in profiles.values()),
            'failure_count': sum(p['failure_count'] for p in profiles.values()),
            'error_count': 0,
            'duration': sum(p['duration'] for p in profiles.values())
        }


def update_index_page(kdevops_dir, results):
    """
    Update the index page for the kdevops directory with provided results.
    """
    # Get the index template
    template_html = create_index_template()
    
    # Replace placeholder with actual data
    index_html = template_html.replace(
        "const testResults = RESULTS_PLACEHOLDER;", 
        f"const testResults = {json.dumps(results, indent=4)};"
    )
    
    # Write the index.html
    index_path = os.path.join(kdevops_dir, 'index.html')
    with open(index_path, 'w') as f:
        f.write(index_html)
    
    print(f"Index HTML updated at {index_path}")


def get_html_filename(data):
    """
    Generate the HTML filename based on the kernel data.
    """
    # For kdevops tests, use a format that includes test number if available
    if 'test_number' in data:
        date_str = data.get('date', '').split()[0]  # Get just the date part
        if date_str:
            return f"{date_str}_test{data['test_number']}.html"
    
    # Fallback to kernel version based naming
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
    Process kdevops test data and generate dashboard files.
    This is the main entry point for the kdevops_handler module.
    """
    # Get log content
    log = data.get('log', '')
    
    # Extract filesystem type if any
    fs_type = determine_filesystem_type(data['subject'], log)
    
    # Parse test profiles
    profiles = parse_fs_test_profiles(log)
    
    # Extract totals
    totals = extract_fs_totals(log, profiles)
    
    # Extract tree and ref
    tree_match = re.search(r"tree:\s+(.*?)\n", log)
    tree = tree_match.group(1).strip() if tree_match else "unknown"
    
    ref_match = re.search(r"ref:\s+(.*?)\n", log)
    ref = ref_match.group(1).strip() if ref_match else "unknown"
    
    # Extract test result
    result_match = re.search(r"test result:\s+(.*?)\n", log)
    test_result = result_match.group(1).strip() if result_match else "unknown"
    
    # Add kdevops-specific data to the common data structure
    data['filesystem'] = fs_type
    data['totals'] = totals
    data['profiles'] = profiles
    data['tree'] = tree
    data['ref'] = ref
    data['test_result'] = test_result
    
    # Remove the full log from data before saving to JSON (to reduce file size)
    if 'log' in data:
        del data['log']
    
    # Create directory for kdevops tests
    kdevops_dir = os.path.join(output_dir, 'kdevops')
    os.makedirs(kdevops_dir, exist_ok=True)
    
    # Determine the HTML filename
    html_filename = get_html_filename(data)
    
    # Write the JSON data file
    json_path = os.path.join(kdevops_dir, html_filename.replace('.html', '.json'))
    
    # Remove existing file if it exists
    if os.path.exists(json_path):
        os.remove(json_path)
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"JSON data written to {json_path}")
    
    # Create HTML file path
    html_path = os.path.join(kdevops_dir, html_filename)
    
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
        'test_result': data.get('test_result', 'unknown'),
        'test_number': data.get('test_number', '0'),
        'failure_count': data.get('totals', {}).get('failure_count', 0)
    }
    
    # Find all existing HTML files (except index.html) to compile index
    all_results = [index_result]  # Start with the current result
    html_files = [f for f in os.listdir(kdevops_dir) if f.endswith('.html') and f != 'index.html' and f != html_filename]
    
    for html_file in html_files:
        # Find the corresponding JSON file
        json_file = html_file.replace('.html', '.json')
        json_path = os.path.join(kdevops_dir, json_file)
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    file_data = json.load(f)
                
                # Extract relevant information
                result = {
                    'url': html_file,
                    'display_name': html_file.replace('.html', ''),
                    'type': file_data.get('kernel_type', 'development'),
                    'date': file_data.get('date', ''),
                    'test_result': file_data.get('test_result', 'unknown'),
                    'test_number': file_data.get('test_number', '0'),
                    'failure_count': file_data.get('totals', {}).get('failure_count', 0)
                }
                
                all_results.append(result)
            except Exception as e:
                print(f"Error processing {json_path}: {e}")
    
    # Update the index page
    update_index_page(kdevops_dir, all_results)
    
    return html_path
