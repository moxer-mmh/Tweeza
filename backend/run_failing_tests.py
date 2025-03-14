#!/usr/bin/env python
import pytest
import os
import sys


def main():
    """Run failing tests for the Tweeza backend."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change to the project root directory
    os.chdir(script_dir)

    # Build the pytest command with arguments focusing on API tests where most failures happen
    args = [
        "-xvs",  # x: exit on first error, v: verbose, s: no capture
        "tests/test_api",  # API test directory
        "--no-cov",  # Disable coverage to focus on test success first
    ]

    # Add any command-line arguments passed to this script
    args.extend(sys.argv[1:])

    # Run pytest with the arguments
    result = pytest.main(args)

    # Return the exit code
    return result


if __name__ == "__main__":
    sys.exit(main())
