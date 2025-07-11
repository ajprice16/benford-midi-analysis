import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from benford_midi.analysis import (
    analyze_midi_features,
    classify_benford_compliance,
    BenfordTests,
)
from benford_midi.utils import generate_benford_sample


def test_benford_tests_basic():
    """Test basic BenfordTests functionality"""
    # Generate test data that should follow Benford's law
    test_data = generate_benford_sample(100)
    tests = BenfordTests(test_data)

    # Test that basic statistics work
    chi2_stat, chi2_p = tests.pearson_chi2()
    assert isinstance(chi2_stat, (int, float))
    assert isinstance(chi2_p, (int, float))
    assert 0 <= chi2_p <= 1

    # Test MAD calculation
    mad = tests.MAD()
    assert isinstance(mad, (int, float))
    assert mad >= 0


def test_analyze_midi_features():
    # Test the function with a mock MIDI file
    with patch("benford_midi.analysis.mido.MidiFile") as mock_midi:
        with patch("benford_midi.analysis.parse_midi_extended") as mock_parse:
            # Mock the parsed features
            mock_parse.return_value = {
                "frequencies": [
                    220,
                    440,
                    880,
                    1760,
                    3520,
                    7040,
                    14080,
                    28160,
                    56320,
                    112640,
                ],
                "velocities": [64, 80, 96, 112, 127, 64, 80, 96, 112, 127],
            }

            results = analyze_midi_features("fake_file.mid")

            assert "frequencies" in results
            assert results["frequencies"]["n"] == 10
            assert "chi2_p" in results["frequencies"]
            assert "follows_benford" in results["frequencies"]


def test_classify_benford_compliance():
    # Test with sample p-values and statistics
    test_results = (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.005, 0.10, 2.0)
    benford_score, category, evidence = classify_benford_compliance(test_results)

    assert isinstance(benford_score, float)
    assert benford_score >= 0.0 and benford_score <= 1.0
    assert category in ["Strong", "Moderate", "Weak", "Non-Benford"]
    assert isinstance(evidence, str)


if __name__ == "__main__":
    print("Running benford_midi tests...")

    try:
        test_benford_tests_basic()
        print("✓ test_benford_tests_basic passed")
    except Exception as e:
        print(f"✗ test_benford_tests_basic failed: {e}")

    try:
        test_analyze_midi_features()
        print("✓ test_analyze_midi_features passed")
    except Exception as e:
        print(f"✗ test_analyze_midi_features failed: {e}")

    try:
        test_classify_benford_compliance()
        print("✓ test_classify_benford_compliance passed")
    except Exception as e:
        print(f"✗ test_classify_benford_compliance failed: {e}")

    print("Test run completed.")
