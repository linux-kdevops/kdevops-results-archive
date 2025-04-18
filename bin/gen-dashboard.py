#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0 OR copyleft-next-0.3.1

import sys
import os
import re
import subprocess
import argparse
import json
import shutil
from collections import defaultdict
from datetime import datetime
import importlib.util

# Add the current directory to the Python path to find the lib modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now imports should work correctly
from lib.fs_handler import process_data as process_fs_data
from lib.mm_handler import process_data as process_mm_data
from lib.kdevops_handler import process_data as process_kdevops_data

# Common utility functions
def get_commit_subject(commit_id):
    """
    Gets the commit subject line for a given commit ID.
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s", commit_id], capture_output=True, text=True
    )

    if result.returncode != 0:
        return "Unknown"

    return result.stdout.strip()


def get_commit_date(commit_id):
    """
    Gets the commit date for a given commit ID.
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ai", commit_id], capture_output=True, text=True
    )

    if result.returncode != 0:
        return "Unknown"

    return result.stdout.strip()


def parse_kernel_version(kernel_version):
    """
    Parse kernel version string to extract base version and commit hash.
    Examples:
    - 6.15.0-rc2-g57265e6ac675 -> (6.15.0-rc2, 57265e6ac675)
    - 6.15.0-g57265e6ac675 -> (6.15.0, 57265e6ac675)
    - next-20250321-g1234abcd -> (next-20250321, 1234abcd)
    """
    # Pattern for standard kernel versions with git hash
    standard_pattern = re.compile(r'^(\d+\.\d+(?:\.\d+)?(?:-\w+\d+)?(?:-\w+\d+)?)-g([a-f0-9]+)$')
    # Pattern for linux-next tags
    next_pattern = re.compile(r'^(next-\d+)-g([a-f0-9]+)$')
    
    match = standard_pattern.match(kernel_version)
    if match:
        return match.group(1), match.group(2)
    
    match = next_pattern.match(kernel_version)
    if match:
        return match.group(1), match.group(2)
    
    # If no pattern matches, return the original and empty hash
    return kernel_version, ""


def is_vanilla_release(subject, base_version):
    """
    Determine if this is an official vanilla kernel release.
    """
    # Check if subject contains "Linux version" and the base version
    if "Linux" in subject and base_version in subject:
        return True
    
    # Look for patterns indicating an official release tag
    if re.search(r'Linux \d+\.\d+(?:\.\d+)?(?:-rc\d+)?', subject):
        return True
    
    return False


def get_kernel_type(base_version):
    """
    Determine the kernel type based on the base version.
    Returns one of: 'stable', 'vanilla', 'rc', 'next', 'development'
    """
    if base_version.startswith("next-"):
        return "next"
    
    if "-rc" in base_version:
        return "rc"
    
    # Check if it's a stable version (has three version components)
    version_parts = re.findall(r'\d+', base_version)
    if len(version_parts) >= 3 and int(version_parts[2]) > 0:
        return "stable"
    
    # If it has just major.minor or major.minor.0, it's a vanilla release
    if len(version_parts) >= 2:
        if len(version_parts) == 2 or int(version_parts[2]) == 0:
            return "vanilla"
    
    # Default to development
    return "development"


def parse_commit(commit_id):
    """
    Extracts information from a git commit and determines the test type.
    Returns the parsed data or None if not a relevant test commit.
    """
    # Get the commit log
    result = subprocess.run(
        ["git", "show", "--no-patch", "--format=%B", commit_id],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: Failed to retrieve commit {commit_id}")
        sys.exit(1)

    log = result.stdout

    # Get subject from the commit
    subject = get_commit_subject(commit_id)
    
    # Skip CI verification commits with "kdevops:" subject prefix 
    # but containing "CI:" in the subject (these are CI verification commits)
    if subject.startswith("kdevops:") and "CI:" in subject:
        print(f"Skipping CI verification commit: {commit_id} ('{subject}')")
        return None

    # Determine test type
    test_type = None
    
    # Check for kdevops bringup/test commits we want to include
    if subject.startswith("kdevops:") and "CI:" not in subject:
        # This is a kdevops test we want to track
        workflow_match = re.search(r"workflow:\s+(.*?)\n", log)
        if workflow_match and "fstests" in workflow_match.group(1).lower():
            test_type = "kdevops"
        else:
            return None  # Not a kdevops test workflow we're tracking
    elif "linux-mm-kpd:" in subject:
        test_type = "mm"
        workflow_match = re.search(r"workflow:\s+(.*?)\n", log)
        if not workflow_match or "selftests" not in workflow_match.group(1).lower():
            return None  # Not a memory management selftest workflow
    else:
        # Check if this is an fstests workflow commit
        workflow_match = re.search(r"workflow:\s+(.*?)\n", log)
        if not workflow_match or "fstests" not in workflow_match.group(1).lower():
            return None  # Not an fstests workflow commit
        test_type = "fs"

    # Extract kernel version
    kernel_match = re.search(r"KERNEL:\s+(.*?)\n", log)
    if kernel_match:
        kernel_version = kernel_match.group(1).strip()
    else:
        # For MM tests, try to find kernel version in other formats
        kernel_match = re.search(r"workflows/selftests/results/last-run/([\d\.\w-]+[\+]?)/", log)
        if kernel_match:
            kernel_version = kernel_match.group(1).strip()
        else:
            kernel_version = "Unknown"

    # Extract test number if available (useful for kdevops tests)
    test_number_match = re.search(r"test number:\s+(\d+)", log)
    test_number = test_number_match.group(1) if test_number_match else None

    # Extract CPU count if available
    cpu_match = re.search(r"CPUS:\s+(\d+)", log)
    cpu_count = cpu_match.group(1) if cpu_match else "Unknown"
    
    # Parse kernel version to extract base version and commit
    base_version, commit_hash = parse_kernel_version(kernel_version)
    
    # Determine if this is an official tag release
    is_vanilla = is_vanilla_release(subject, base_version)
    kernel_type = get_kernel_type(base_version)

    # Build base data structure with common properties
    data = {
        'commit': commit_id,
        'subject': subject,
        'kernel': kernel_version,
        'base_version': base_version,
        'commit_hash': commit_hash,
        'is_vanilla': is_vanilla,
        'kernel_type': kernel_type,
        'cpus': cpu_count,
        'date': get_commit_date(commit_id),
        'test_type': test_type,
        'log': log  # Include the full log for module processing
    }
    
    # Add test number if available (for kdevops tests)
    if test_number:
        data['test_number'] = test_number

    return data

def should_process_with_fs_handler(tree, subject):
    """
    Determines if a commit should be processed with fs_handler.py.
    """

    # Valid trees to process.
    valid_trees = ["linux", "linux-next", "linux-stable"]

    # Valid subjects
    valid_subjects = ["linux-xfs-kpd", "linux-ext4-kpd", "linux-btrfs-kpd", "linux-tmpfs-kpd"]

    # kdevops will *always* test fstests, but we don't want those tests
    # to be counted as valid fstests, those test are simply done to ensure
    # we can build linux, build fstests, and run at least one test.
    if subject.startswith("kdevops:") or subject.startswith("kdevops-kpd:"):
        return False

    # Check if the tree matches one of the valid trees we support
    if tree not in valid_trees:
        return True

    # Check if the tree matches one of the valid trees we support
    if subject not in valid_subjects:
        return True

    return False

def generate_dashboard(commit_id, output_dir='.'):
    """
    Generate a dashboard HTML file and associated JSON data for the given commit.
    """
    print(f"Parsing commit {commit_id}...")
    data = parse_commit(commit_id)

    if not data:
        print(f"Commit {commit_id} is not a relevant test commit. Skipping.")
        return None

    # Determine the tree from the commit log
    tree_match = re.search(r"tree:\s+(.*?)\n", data['log'])
    tree = tree_match.group(1).strip() if tree_match else "unknown"

    # Process data based on test type
    if data['test_type'] == 'fs' and should_process_with_fs_handler(tree, data['subject']):
        result = process_fs_data(data, output_dir)
    elif data['test_type'] == 'mm':
        result = process_mm_data(data, output_dir)
    elif data['test_type'] == 'kdevops':
        result = process_kdevops_data(data, output_dir)
    else:
        print(f"Unknown or unsupported test type for commit {commit_id}: {data['test_type']}")
        return None

    # Update the main index
    create_master_index(output_dir)
    return result

def create_master_index(output_dir):
    """
    Create a master index.html page that links to each filesystem directory.
    """
    # Find all subdirectories (filesystem types)
    subdirs = [d for d in os.listdir(output_dir)
               if os.path.isdir(os.path.join(output_dir, d)) and not d.startswith('.')]

    if not subdirs:
        print("No test directories found, skipping master index creation")
        return

    # Group directories by type
    fs_dirs = []
    special_dirs = []

    for d in subdirs:
        if d in ['mm', 'kdevops']:
            special_dirs.append(d)
        else:
            fs_dirs.append(d)  # Filesystem directories

    # Sort directories
    fs_dirs.sort()
    special_dirs.sort()

    # Create simple HTML for master index
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kdevops: Linux Kernel Test Results Dashboard</title>
    <style>
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
            padding: 20px;
            position: relative;
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
            position: relative;
            z-index: 1;
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        h2 {
            color: #3498db;
            margin: 30px 0 20px;
            text-align: center;
            text-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }

        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto 40px;
        }

        .card {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.2s ease-in-out;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .fs-card .header {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
        }

        .mm-card .header {
            background-color: #673ab7;
            color: white;
            padding: 15px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
        }

        .kdevops-card .header {
            background-color: #34495e;
            color: white;
            padding: 15px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
        }

        .content {
            padding: 20px;
            text-align: center;
        }

        .link {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 15px;
            transition: background-color 0.2s ease-in-out;
        }

        .fs-link {
            background-color: #3498db;
            color: white;
        }

        .fs-link:hover {
            background-color: #2980b9;
        }

        .mm-link {
            background-color: #673ab7;
            color: white;
        }

        .mm-link:hover {
            background-color: #5e35b1;
        }

        .kdevops-link {
            background-color: #34495e;
            color: white;
        }

        .kdevops-link:hover {
            background-color: #2c3e50;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .logo-small {
            display: block;
            width: 100px;
            margin: 10px auto;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>kdevops: Linux Kernel Test Results Dashboard</h1>
"""

    # Add special directories section if any exist
    if special_dirs:
        html += """
        <h2>Specialized Test Results</h2>
        <div class="grid-container">
"""

        for d in special_dirs:
            if d == 'mm':
                html += f"""
            <div class="card mm-card">
                <div class="header">Memory Management</div>
                <div class="content">
                    <p>Memory Management test results including xarray, maple tree and more</p>
                    <a href="{d}/index.html" class="link mm-link">View Results</a>
                </div>
            </div>
"""
            elif d == 'kdevops':
                html += f"""
            <div class="card kdevops-card">
                <div class="header">kdevops</div>
                <div class="content">
                    <p>kdevops integration test results</p>
                    <a href="{d}/index.html" class="link kdevops-link">View Results</a>
                </div>
            </div>
"""

        html += """
        </div>
"""

    # Add filesystem section if any exist
    if fs_dirs:
        html += """
        <h2>Filesystem Test Results</h2>
        <div class="grid-container">
"""

        for d in fs_dirs:
            html += f"""
            <div class="card fs-card">
                <div class="header">{d}</div>
                <div class="content">
                    <p>Test results for {d} filesystem</p>
                    <a href="{d}/index.html" class="link fs-link">View Results</a>
                </div>
            </div>
"""

        html += """
        </div>
"""

    # Add footer with small logo
    html += """
        <div class="footer">
            <img src="https://github.com/linux-kdevops/kdevops/raw/main/images/kdevops-trans-bg-edited-individual-with-logo-gausian-blur-1600x1600.png" alt="kdevops logo" class="logo-small">
            <p>kdevops: Linux Kernel Test Automation</p>
        </div>
    </div>
</body>
</html>
"""

    # Write the master index.html
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w') as f:
        f.write(html)

    print(f"Master index created at {index_path}")

def process_commits_in_range(start_commit=None, end_commit="HEAD", output_dir="dashboard"):
    """
    Process a range of commits from start_commit to end_commit.
    If start_commit is None, process only the end_commit.
    """
    if start_commit:
        # Get list of commits in range
        result = subprocess.run(
            ["git", "log", "--pretty=format:%H", f"{start_commit}..{end_commit}"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"Error: Failed to retrieve commit range {start_commit}..{end_commit}")
            sys.exit(1)
            
        commits = result.stdout.strip().split('\n')
        if not commits[0]:  # Handle empty result
            commits = []
    else:
        # Just process the end commit
        commits = [end_commit]
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each commit
    processed_commits = 0
    for commit in commits:
        if generate_dashboard(commit, output_dir):
            processed_commits += 1
    
    print(f"Processed {processed_commits} test workflow commits")
    
    # Create a master index page
    create_master_index(output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML dashboard from test results in commits"
    )
    parser.add_argument("commit", nargs='?', default="HEAD",
                        help="Commit ID containing test results (default: HEAD)")
    parser.add_argument("-s", "--start-commit", 
                        help="Start commit for processing a range (if omitted, only the specified commit is processed)")
    parser.add_argument("-o", "--output-dir", default="dashboard", 
                       help="Output directory (default: dashboard)")
    
    args = parser.parse_args()
    
    process_commits_in_range(args.start_commit, args.commit, args.output_dir)


if __name__ == "__main__":
    main()
