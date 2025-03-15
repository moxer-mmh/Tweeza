#!/usr/bin/env python
import pytest
import os
import sys
import argparse


def main():
    """Run all tests for the Tweeza backend."""
    # Create argument parser
    parser = argparse.ArgumentParser(description="Run Tweeza backend tests")
    parser.add_argument(
        "--path", default="tests", help="Test path to run (e.g., tests/test_services)"
    )
    parser.add_argument(
        "--no-cov", action="store_true", help="Disable coverage reporting"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )

    # Parse arguments and get any additional pytest args
    args, pytest_args = parser.parse_known_args()

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change to the project root directory
    os.chdir(script_dir)

    # Build the pytest command with arguments
    pytest_args_list = [
        "-xvs",  # x: exit on first error, v: verbose, s: no capture
        args.path,  # Test directory/path
    ]

    if not args.no_cov:
        pytest_args_list.extend(
            [
                "--cov=app",  # Coverage for app directory
                "--cov-report=term",  # Coverage report format
            ]
        )

        if args.html:
            pytest_args_list.append("--cov-report=html")

    # Add any additional pytest arguments
    pytest_args_list.extend(pytest_args)

    # Run pytest with the arguments
    result = pytest.main(pytest_args_list)

    # Return the exit code
    return result


if __name__ == "__main__":
    sys.exit(main())
