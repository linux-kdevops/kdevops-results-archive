#!/usr/bin/python3

import sys
import re
import subprocess
import argparse
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

    # Find all profile sections - modified to work with any filesystem test profile
    # and to properly capture multi-line failure lists
    profile_pattern = r"^((?:\w+_)+\w+): (\d+) tests,.*?\n(?:.*?\n)*?  Failures:(.*?)(?=\n(?:\w+_)+\w+: |\nTotals: |\n\n|\Z)"
    profile_sections = re.finditer(profile_pattern, log, re.MULTILINE | re.DOTALL)

    for match in profile_sections:
        profile = match.group(1)
        # Extract all failures, handling multi-line lists
        failures_text = match.group(3).strip()
        # Split by whitespace and filter out empty strings
        failures = [f for f in re.split(r'\s+', failures_text) if f]
        profiles[profile] = failures

    return kernel_version, profiles


def is_failure_present_in_any_profile(failure, profiles):
    """
    Check if a failure appears in any of the profile's failure lists.
    """
    return any(failure in failures for failures in profiles.values())


def compare_results(baseline_id, test_id, verbose=False):
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

    if verbose:
        print("Verbose Test Results Comparison:")
    else:
        print("Test Results Comparison:")
    print("=" * 80)

    found_changes = False
    total_regressions = 0
    total_fixes = 0
    total_unchanged = 0

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

        if verbose:
            # Create a set of all tests from both baseline and test
            all_tests = baseline_failures.union(test_failures)
            
            if all_tests:  # Only display profiles with tests
                print(f"\nProfile: {profile}")
                print(f"{'':19} | {'BASELINE':<12} | {'TEST':<12}")
                print(f"{'-'*19}|{'-'*14}|{'-'*14}")
                
                for test in sorted(all_tests):
                    baseline_status = "[fail]" if test in baseline_failures else "[pass]"
                    test_status = "[fail]" if test in test_failures else "[pass]"
                    
                    # Determine if this is a regression or fix
                    status_indicator = ""
                    if test in new_failures:
                        status_indicator = "--> regression"
                        total_regressions += 1
                    elif test in resolved_failures:
                        status_indicator = "--> fixed"
                        total_fixes += 1
                    else:
                        total_unchanged += 1
                        
                    print(f"{test:19} | {baseline_status:<12} | {test_status:<12} {status_indicator}")
            
        elif new_failures or resolved_failures:
            found_changes = True
            print(f"\nProfile: {profile}")

            if new_failures:
                print("  New Failures:")
                for failure in sorted(new_failures):
                    print(f"    + {failure}")
                total_regressions += len(new_failures)

            if resolved_failures:
                print("  Resolved Failures:")
                for failure in sorted(resolved_failures):
                    print(f"    - {failure}")
                total_fixes += len(resolved_failures)

    if verbose:
        print("\nSummary:")
        print(f"  - Total regressions: {total_regressions}")
        print(f"  - Total fixes: {total_fixes}")
        print(f"  - Unchanged failures: {total_unchanged}")
    elif not found_changes:
        print("\nNo changes in test results between the commits")


def main():
    parser = argparse.ArgumentParser(
        description="Compare fstests results between two commits"
    )
    parser.add_argument("baseline", help="Baseline commit ID")
    parser.add_argument("test", help="Test commit ID")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Show verbose output with detailed comparison tables")
    
    args = parser.parse_args()
    compare_results(args.baseline, args.test, args.verbose)


if __name__ == "__main__":
    main()
