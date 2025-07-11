#!/usr/bin/env python3
"""
CI/CD test script for benford-midi package
This script runs all tests and validates the package installation
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success/failure"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        print("✓ SUCCESS")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("✗ FAILED")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_github_actions_locally():
    """Check if we can run GitHub Actions locally"""
    print("\n" + "="*60)
    print("GITHUB ACTIONS LOCAL TESTING OPTIONS")
    print("="*60)
    
    # Check for act
    try:
        result = subprocess.run(
            "act --version", shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ 'act' is available! You can run GitHub Actions locally with:")
            print("  act push                    # Run push event")
            print("  act workflow_dispatch      # Run manual trigger")
            print("  act pull_request           # Run PR event")
            return True
    except:
        pass
    
    print("ℹ️  'act' not found. You can install it with:")
    print("  brew install act           # macOS")
    print("  # Requires Docker to be installed")
    print()
    print("🔧 Alternative: Use workflow_dispatch in GitHub Actions")
    print("  1. Push this workflow file")
    print("  2. Go to Actions tab on GitHub")
    print("  3. Click 'Run workflow' button")
    return False


def run_linting_tests():
    """Run the same linting tests as GitHub Actions"""
    print("\n" + "="*60)
    print("RUNNING LINTING TESTS (like GitHub Actions)")
    print("="*60)
    
    linting_tests = [
        # Install linting tools
        ("pip install flake8 black", "Install linting dependencies"),
        # Run flake8 - critical errors only
        ("flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics", "Run flake8 critical checks"),
        # Run flake8 - all checks (non-blocking)
        ("flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics", "Run flake8 full checks"),
        # Check black formatting
        ("black --check --diff src/ tests/", "Check code formatting with black"),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, description in linting_tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1
    
    return passed, failed


def main():
    """Run all CI/CD tests"""
    print("BENFORD-MIDI CI/CD TEST SUITE")
    print("=" * 60)

    # Get the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Check GitHub Actions options
    check_github_actions_locally()

    # List of tests to run (matching GitHub Actions)
    tests = [
        # Test 1: Install package in development mode
        ("pip install -e .", "Install package in development mode"),
        # Test 2: Run main test suite
        ("python test_package.py", "Run main test package"),
        # Test 3: Run unit tests
        ("python tests/test_analysis.py", "Run unit tests"),
        # Test 4: Run comprehensive tests
        ("python -m unittest tests.tests -v", "Run comprehensive test suite"),
        # Test 5: Test CLI functionality
        ("python -m benford_midi.cli --help", "Test CLI help"),
        # Test 6: Test package import
        (
            "python -c 'import benford_midi; print(f\"Package version: {benford_midi.__version__}\")'",
            "Test package import",
        ),
        # Test 7: Test core functionality
        (
            "python -c 'from benford_midi import BenfordTests, generate_benford_sample; data = generate_benford_sample(100); test = BenfordTests(data); print(\"Core functionality works\")'",
            "Test core functionality",
        ),
    ]

    # Run main tests
    passed = 0
    failed = 0

    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1

    # Run linting tests
    print("\n" + "="*60)
    print("RUNNING ADDITIONAL LINTING TESTS")
    print("="*60)
    
    lint_passed, lint_failed = run_linting_tests()
    passed += lint_passed
    failed += lint_failed

    # Summary
    print(f"\n{'='*60}")
    print(f"CI/CD TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("🎉 ALL TESTS PASSED! Package is ready for deployment.")
        print("\n📝 Next steps:")
        print("  1. Commit your changes")
        print("  2. Push to GitHub (or use workflow_dispatch)")
        print("  3. GitHub Actions will run automatically")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
