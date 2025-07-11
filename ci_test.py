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
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
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

def main():
    """Run all CI/CD tests"""
    print("BENFORD-MIDI CI/CD TEST SUITE")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # List of tests to run
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
        ("python -c 'import benford_midi; print(f\"Package version: {benford_midi.__version__}\")'", "Test package import"),
        
        # Test 7: Test core functionality
        ("python -c 'from benford_midi import BenfordTests, generate_benford_sample; data = generate_benford_sample(100); test = BenfordTests(data); print(\"Core functionality works\")'", "Test core functionality"),
    ]
    
    # Run all tests
    passed = 0
    failed = 0
    
    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"CI/CD TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Package is ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
