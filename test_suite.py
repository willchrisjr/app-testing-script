#!/usr/bin/env python3

"""
MacOS Application Testing Script

This script automates testing of macOS applications by launching them,
monitoring for crashes, and scanning log files for errors.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Test a macOS application for stability and errors.')
    parser.add_argument('app_path', help='Path to the macOS application (.app bundle)')
    parser.add_argument('--log', default='~/Library/Logs/DiagnosticReports/*.crash',
                        help='Path to log files to scan (default: ~/Library/Logs/DiagnosticReports/*.crash)')
    parser.add_argument('--continuous', action='store_true',
                        help='Run in continuous mode, launching the app every 10 seconds')
    return parser.parse_args()


def launch_app(app_path):
    """
    Launch the application and monitor for crashes.
    
    Returns:
        tuple: (success, error_message)
    """
    try:
        # Use 'open' command to launch macOS applications
        process = subprocess.Popen(['open', app_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # Wait for the process to complete or timeout after 30 seconds
        try:
            stdout, stderr = process.communicate(timeout=30)
            if process.returncode != 0:
                return False, f"Application exited with code {process.returncode}: {stderr.decode('utf-8')}"
            return True, None
        except subprocess.TimeoutExpired:
            # The process is still running after 30 seconds, which is expected for GUI apps
            # Kill the process to clean up
            process.kill()
            return True, None
    except Exception as e:
        return False, f"Failed to launch application: {str(e)}"


def scan_logs(log_path, keywords=None):
    """
    Scan log files for keywords indicating errors or crashes.
    
    Args:
        log_path: Path to log files (can include wildcards)
        keywords: List of keywords to search for (default: ['error', 'crash', 'fail'])
        
    Returns:
        list: List of found issues with line numbers
    """
    if keywords is None:
        keywords = ['error', 'crash', 'fail']
    
    issues = []
    
    # Expand the log path (handle ~ for home directory)
    expanded_log_path = os.path.expanduser(log_path)
    
    # If the path contains wildcards, we need to use glob
    if '*' in expanded_log_path:
        import glob
        log_files = glob.glob(expanded_log_path)
    else:
        log_files = [expanded_log_path] if os.path.exists(expanded_log_path) else []
    
    # Create regex pattern for keywords
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        issues.append(f"[{log_file}:{i}] {line.strip()}")
        except Exception as e:
            issues.append(f"Error reading log file {log_file}: {str(e)}")
    
    return issues


def generate_report(app_path, launch_success, error_message, issues):
    """
    Generate a test report with findings.
    
    Args:
        app_path: Path to the tested application
        launch_success: Whether the app launched successfully
        error_message: Error message if launch failed
        issues: List of issues found in logs
        
    Returns:
        str: Formatted report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app_name = os.path.basename(app_path)
    
    report = [f"=== Test Report for {app_name} ===\n"]
    report.append(f"Timestamp: {timestamp}")
    
    # App status
    if launch_success:
        report.append("App Status: Launched successfully")
    else:
        report.append(f"App Status: Failed: {error_message}")
    
    # Issues found
    report.append(f"\nIssues Found: {len(issues)}")
    if issues:
        report.append("\nDetailed Issues:")
        for issue in issues:
            report.append(f"  {issue}")
    else:
        report.append("No issues detected")
    
    report.append("\n=== End of Report ===\n")
    
    return "\n".join(report)


def write_report_to_file(report, append=False):
    """
    Write the report to the log file.
    
    Args:
        report: The formatted report string
        append: Whether to append to existing file
    """
    mode = 'a' if append else 'w'
    with open('test_report.log', mode) as f:
        f.write(report)


def test_mode(app_path, log_path):
    """
    Run a single test of the application.
    
    Args:
        app_path: Path to the application
        log_path: Path to log files
        
    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"Testing application: {app_path}")
    
    # Launch the app
    launch_success, error_message = launch_app(app_path)
    
    # Give some time for potential crashes to be logged
    time.sleep(2)
    
    # Scan logs for issues
    issues = scan_logs(log_path)
    
    # Generate and write report
    report = generate_report(app_path, launch_success, error_message, issues)
    print(report)
    write_report_to_file(report)
    
    # Check if report file exists and has content
    if os.path.exists('test_report.log') and os.path.getsize('test_report.log') > 0:
        if launch_success and not issues:
            print("Test passed")
            return True
        else:
            print("Test failed: issues detected")
            return False
    else:
        print("Test failed: log issue")
        return False


def continuous_mode(app_path, log_path):
    """
    Run continuous testing of the application.
    
    Args:
        app_path: Path to the application
        log_path: Path to log files
    """
    print(f"Starting continuous testing of {app_path}")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Launch the app
            launch_success, error_message = launch_app(app_path)
            
            # Give some time for potential crashes to be logged
            time.sleep(2)
            
            # Scan logs for issues
            issues = scan_logs(log_path)
            
            # Generate and write report
            report = generate_report(app_path, launch_success, error_message, issues)
            print(report)
            write_report_to_file(report, append=True)
            
            # Wait before next launch
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nContinuous testing stopped by user")


def main():
    """
    Main function to run the test suite.
    """
    args = parse_arguments()
    
    # Validate app path
    if not os.path.exists(args.app_path):
        print(f"Error: Application not found at {args.app_path}")
        return 1
    
    if not args.app_path.endswith('.app'):
        print(f"Warning: {args.app_path} does not appear to be a macOS application bundle (.app)")
    
    # Run in appropriate mode
    if args.continuous:
        continuous_mode(args.app_path, args.log)
    else:
        test_passed = test_mode(args.app_path, args.log)
        return 0 if test_passed else 1


if __name__ == "__main__":
    sys.exit(main())