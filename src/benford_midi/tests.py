# Test cases for the analysis functions in the benford_midi package

import unittest
from benford_midi.analysis import analyze_midi_features, classify_benford_compliance

class TestBenfordMidiAnalysis(unittest.TestCase):

    def test_analyze_midi_features_valid(self):
        # Test with a valid MIDI feature set
        test_data = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76]  # Example MIDI note numbers
        results = analyze_midi_features(test_data)
        self.assertIn('frequencies', results)
        self.assertGreater(results['frequencies']['chi2_p'], 0)

    def test_analyze_midi_features_insufficient_data(self):
        # Test with insufficient data
        test_data = [60]  # Only one note
        results = analyze_midi_features(test_data)
        self.assertEqual(results['frequencies'], {'insufficient_data': 1})

    def test_classify_benford_compliance_strong(self):
        # Test classification for strong compliance
        test_results = (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.01, 0.02, 2.0)
        score, category, evidence = classify_benford_compliance(test_results)
        self.assertGreater(score, 0.7)
        self.assertEqual(category, 'Strong')

    def test_classify_benford_compliance_non_benford(self):
        # Test classification for non-compliance
        test_results = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.1, 0.2, 5.0)
        score, category, evidence = classify_benford_compliance(test_results)
        self.assertLess(score, 0.15)
        self.assertEqual(category, 'Non-Benford')

if __name__ == '__main__':
    unittest.main()