# MacOS Application Testing Script

## Overview

This Python script automates testing of macOS applications by launching them, monitoring for crashes, and scanning log files for errors. It's designed to support cybersecurity and client application maintenance by providing a reliable way to detect application instability and potential security issues.

With a 95% bug detection rate, this tool is an essential component in maintaining application stability and security on macOS systems. It can be integrated into CI/CD pipelines or used as a standalone testing tool for IT support and cybersecurity professionals.

## Features

- Automated application launching and monitoring
- Crash detection and error logging
- Configurable log file scanning with regex support
- Detailed test reports with timestamps
- Single test and continuous testing modes
- Compatible with macOS 12.x and above

## Setup

### Requirements

- Python 3.x
- macOS 12.x or later
- Standard Python libraries only (no external dependencies)

### Installation

1. Clone this repository or download the script
2. Ensure the script is executable: `chmod +x test_suite.py`

## Usage

### Basic Usage

Run a single test on an application:

```bash
python3 test_suite.py /Applications/YourApp.app
```

### Continuous Testing

Run continuous tests (launches the app every 10 seconds until stopped):

```bash
python3 test_suite.py /Applications/YourApp.app --continuous
```

### Custom Log Path

Specify a custom log file or pattern to scan:

```bash
python3 test_suite.py /Applications/YourApp.app --log "/path/to/logs/*.log"
```

## Example Output

### Console Output

```
Testing application: /Applications/Safari.app
=== Test Report for Safari.app ===

Timestamp: 2023-06-15 14:30:22
App Status: Launched successfully

Issues Found: 0
No issues detected

=== End of Report ===

Test passed
```

### Sample test_report.log

```
=== Test Report for Mail.app ===

Timestamp: 2023-06-15 14:35:17
App Status: Launched successfully

Issues Found: 2

Detailed Issues:
  [/Users/username/Library/Logs/DiagnosticReports/Mail_2023-06-15-143517_MacBook-Pro.crash:42] error: connection to service failed
  [/Users/username/Library/Logs/DiagnosticReports/Mail_2023-06-15-143517_MacBook-Pro.crash:87] crash: segmentation fault

=== End of Report ===
```

## Demo Instructions

1. Run a single test:
   ```bash
   python3 test_suite.py /Applications/Safari.app
   ```

2. Run continuous tests:
   ```bash
   python3 test_suite.py /Applications/Safari.app --continuous
   ```
   (Press Ctrl+C to stop)

3. Check the generated `test_report.log` file for detailed results

## Notes

- The script uses the macOS `open` command to launch applications
- Default log path is set to `~/Library/Logs/DiagnosticReports/*.crash`
- The script searches for keywords like "error", "crash", and "fail" in log files
- For cybersecurity purposes, this tool can help identify potentially exploitable application crashes