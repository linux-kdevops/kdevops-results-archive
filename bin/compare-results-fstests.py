#!/usr/bin/python3

import sys
import re
import subprocess
from collections import defaultdict


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


def parse_commit(commit_id):
    """
    Extracts the kernel version, test profiles, and failures from a git commit.
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

    # Extract kernel version
    kernel_match = re.search(r"KERNEL:\s+(.*?)\n", log)
    kernel_version = kernel_match.group(1).strip() if kernel_match else "Unknown"

    # Parse test profiles and their failures
    profiles = defaultdict(list)

    # Find all profile sections - modified to work with any filesystem prefix
    # and to properly capture multi-line failure lists
    profile_pattern = r"^(\w+(?:_[a-zA-Z0-9]+)*): .*?tests.*?\n(?:.*?\n)*?  Failures:(.*?)(?=\n\w+(?:_[a-zA-Z0-9]+)*: |\nTotals: |\n\n|\Z)"
    profile_sections = re.finditer(profile_pattern, log, re.MULTILINE | re.DOTALL)

    for match in profile_sections:
        profile = match.group(1)
        # Extract all failures, handling multi-line lists
        failures_text = match.group(2).strip()
        # Split by whitespace and filter out empty strings
        failures = [f for f in re.split(r'\s+', failures_text) if f]
        profiles[profile] = failures

    return kernel_version, profiles


def is_failure_present_in_any_profile(failure, profiles):
    """
    Check if a failure appears in any of the profile's failure lists.
    """
    return any(failure in failures for failures in profiles.values())


def compare_results(baseline_id, test_id):
    """
    Compare test results between baseline and new test commit.
    """
    print("Comparing commits:")
    baseline_subject = get_commit_subject(baseline_id)
    test_subject = get_commit_subject(test_id)

    print(f"{'Baseline:':<15}{baseline_id[:12]} | {baseline_subject}")
    print(f"{'Test:':<15}{test_id[:12]} | {test_subject}")
    print()

    baseline_kernel, baseline_profiles = parse_commit(baseline_id)
    test_kernel, test_profiles = parse_commit(test_id)

    print(f"{'Baseline Kernel:':<15}{baseline_kernel}")
    print(f"{'Test Kernel:':<15}{test_kernel}")
    print()

    all_profiles = sorted(set(baseline_profiles.keys()).union(test_profiles.keys()))

    if not all_profiles:
        print("No test profiles found in the commits")
        return

    print("Test Results Comparison:")
    print("=" * 80)

    found_changes = False

    for profile in all_profiles:
        baseline_failures = set(baseline_profiles.get(profile, []))
        test_failures = set(test_profiles.get(profile, []))

        new_failures = test_failures - baseline_failures
        potential_resolved = baseline_failures - test_failures

        # Only consider a failure resolved if it's not present in any other test profile
        resolved_failures = {
            failure
            for failure in potential_resolved
            if not is_failure_present_in_any_profile(failure, test_profiles)
        }

        if new_failures or resolved_failures:
            found_changes = True
            print(f"\nProfile: {profile}")

            if new_failures:
                print("  New Failures:")
                for failure in sorted(new_failures):
                    print(f"    + {failure}")

            if resolved_failures:
                print("  Resolved Failures:")
                for failure in sorted(resolved_failures):
                    print(f"    - {failure}")

    if not found_changes:
        print("\nNo changes in test results between the commits")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <baseline-commit-id> <test-commit-id>")
        sys.exit(1)

    baseline_commit = sys.argv[1]
    test_commit = sys.argv[2]
    compare_results(baseline_commit, test_commit)


if __name__ == "__main__":
    main()
