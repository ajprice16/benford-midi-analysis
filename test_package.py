#!/usr/bin/env python3
"""
Quick test script to verify the benford_midi package is working correctly.
"""

import sys
import subprocess
import numpy as np
from pathlib import Path

def test_basic_functionality():
    """Test basic package functionality"""
    print("Testing basic package functionality...")
    
    try:
        # Test imports
        from benford_midi import (
            BenfordTests, generate_benford_sample, classify_benford_compliance,
            format_p, get_first_digit
        )
        print("✓ All imports successful")
        
        # Test utility functions
        test_data = [123, 456, 789, 234, 567]
        first_digits = get_first_digit(test_data)
        print(f"✓ First digits extracted: {first_digits}")
        
        # Test p-value formatting
        p_formatted = format_p(0.0001)
        print(f"✓ P-value formatting: {p_formatted}")
        
        # Generate Benford sample
        benford_data = generate_benford_sample(100)
        print(f"✓ Generated {len(benford_data)} Benford-distributed numbers")
        
        # Test BenfordTests class
        tests = BenfordTests(benford_data)
        chi2_stat, chi2_p = tests.pearson_chi2()
        ks_stat, ks_p = tests.kolmogorov_smirnov()
        mad = tests.MAD()
        print(f"✓ BenfordTests working: χ² p={format_p(chi2_p)}, KS p={format_p(ks_p)}, MAD={mad:.4f}")
        
        # Test classification
        test_results = (chi2_p, ks_p, 0.5, 0.4, 0.3, 0.55, 0.45, mad, 0.09, 2.2)
        score, category, evidence = classify_benford_compliance(test_results)
        print(f"✓ Classification: Score={score:.3f}, Category={category}")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

def test_cli():
    """Test that CLI is accessible"""
    print("\nTesting CLI accessibility...")
    
    try:
        import subprocess
        import sys
        
        # Test CLI help
        result = subprocess.run([
            sys.executable, "-m", "benford_midi.cli", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Benford's Law Analysis" in result.stdout:
            print("✓ CLI help works correctly")
            return True
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def test_package_structure():
    """Test package structure"""
    print("\nTesting package structure...")
    
    try:
        import benford_midi
        
        # Check version
        version = getattr(benford_midi, '__version__', 'Unknown')
        print(f"✓ Package version: {version}")
        
        # Check key attributes
        expected_attrs = [
            'analyze_single_directory', 'compare_directories', 'BenfordTests',
            'classify_benford_compliance', 'format_p', 'get_first_digit'
        ]
        
        missing_attrs = []
        for attr in expected_attrs:
            if not hasattr(benford_midi, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"❌ Missing attributes: {missing_attrs}")
            return False
        else:
            print(f"✓ All {len(expected_attrs)} expected attributes present")
            return True
            
    except Exception as e:
        print(f"❌ Package structure test error: {e}")
        return False

def main():
    """Run all tests"""
    print("BENFORD MIDI PACKAGE TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_package_structure,
        test_cli
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your package is working correctly.")
        print("\nYou can now use the package with:")
        print("  python -m benford_midi.cli analyze /path/to/midi/files")
        print("  python -c 'import benford_midi; print(benford_midi.__version__)'")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
