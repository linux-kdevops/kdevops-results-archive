#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

import os
import re
import json
import shutil
from lib.fs_templates import create_html_template, create_index_template

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


def parse_test_profiles(log):
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


def extract_totals(log, profiles):
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


def update_index_page(fs_dir, results):
    """
    Update the index page for a filesystem directory with provided results.
    """
    # Get the index template
    template_html = create_index_template()
    
    # Get filesystem name from directory name
    fs_name = os.path.basename(fs_dir)
    
    # Replace filesystem placeholder
    template_html = template_html.replace("FILESYSTEM", fs_name)
    
    # Replace placeholder with actual data
    index_html = template_html.replace(
        "const testResults = RESULTS_PLACEHOLDER;", 
        f"const testResults = {json.dumps(results, indent=4)};"
    )
    
    # Write the index.html
    index_path = os.path.join(fs_dir, 'index.html')
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
    Process filesystem test data and generate dashboard files.
    This is the main entry point for the fs_handler module.
    """
    # Get log content
    log = data.get('log', '')
    
    # Extract filesystem type
    fs_type = determine_filesystem_type(data['subject'], log)
    if not fs_type:
        print(f"Warning: Could not determine filesystem type for commit {data['commit']}")
        fs_type = "unknown"
    
    # Parse test profiles
    profiles = parse_test_profiles(log)
    
    # Extract totals
    totals = extract_totals(log, profiles)
    
    # Add filesystem-specific data to the common data structure
    data['filesystem'] = fs_type
    data['totals'] = totals
    data['profiles'] = profiles
    
    # Remove the full log from data before saving to JSON (to reduce file size)
    if 'log' in data:
        del data['log']
    
    # Create filesystem-specific directory within output directory
    fs_dir = os.path.join(output_dir, fs_type)
    os.makedirs(fs_dir, exist_ok=True)
    
    # Generate the HTML filename
    base_html_filename = get_html_filename(data)
    base_file_path = os.path.join(fs_dir, base_html_filename)
    
    # Get current commit's short ID
    current_commit_id = data['commit'][:8]
    
    # Create a filename with the current commit ID included
    base_name = base_html_filename.replace('.html', '')
    commit_html_filename = f"{base_name}-{current_commit_id}.html"
    commit_file_path = os.path.join(fs_dir, commit_html_filename)
    
    # Check if the base file already exists
    if os.path.exists(base_file_path):
        # Use the commit ID version for the current (newer) file
        html_path = commit_file_path
        json_path = os.path.join(fs_dir, commit_html_filename.replace('.html', '.json'))
        
        print(f"Base file exists - using {commit_html_filename} for current commit")
    else:
        # Use the base filename for the current file (first one to use this kernel version)
        html_path = base_file_path
        json_path = os.path.join(fs_dir, base_html_filename.replace('.html', '.json'))
        
        print(f"Base file does not exist - using {base_html_filename} for current commit")
    
    # Write the JSON data
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"JSON data written to {json_path}")
    
    # Create HTML file
    template_html = create_html_template()
    template_html = template_html.replace("FILESYSTEM_TYPE", fs_type)
    dashboard_html = template_html.replace(
        "const testData = DATA_PLACEHOLDER;",
        f"const testData = {json.dumps(data, indent=4)};"
    )
    
    with open(html_path, 'w') as f:
        f.write(dashboard_html)
    
    print(f"Dashboard HTML written to {html_path}")
    
    # Add the current file data for the index
    current_result = {
        'url': os.path.basename(html_path),
        'display_name': os.path.basename(html_path).replace('.html', ''),
        'type': data.get('kernel_type', 'development'),
        'date': data.get('date', ''),
        'failure_count': data.get('totals', {}).get('failure_count', 0)
    }
    
    # Collect all HTML files for the index (except index.html itself)
    html_files = [f for f in os.listdir(fs_dir) 
                 if f.endswith('.html') and f != 'index.html' 
                 and f != os.path.basename(html_path)]
    
    all_results = [current_result]  # Start with current result
    
    # Add all other HTML files
    for html_file in html_files:
        # Find the corresponding JSON file
        json_file = html_file.replace('.html', '.json')
        file_json_path = os.path.join(fs_dir, json_file)
        
        if os.path.exists(file_json_path):
            try:
                with open(file_json_path, 'r') as f:
                    file_data = json.load(f)
                
                # Add to results
                all_results.append({
                    'url': html_file,
                    'display_name': html_file.replace('.html', ''),
                    'type': file_data.get('kernel_type', 'development'),
                    'date': file_data.get('date', ''),
                    'failure_count': file_data.get('totals', {}).get('failure_count', 0)
                })
            except Exception as e:
                print(f"Error processing {file_json_path}: {e}")
    
    # Update the index page
    update_index_page(fs_dir, all_results)
    
    return html_path
