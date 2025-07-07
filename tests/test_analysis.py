from src.benford_midi.analysis import analyze_midi_features, classify_benford_compliance

def test_analyze_midi_features():
    # Test with a sample MIDI feature set
    sample_data = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76]  # Example MIDI note numbers
    results = analyze_midi_features(sample_data)
    
    assert 'frequencies' in results
    assert results['frequencies']['n'] == len(sample_data)
    assert 'chi2_p' in results['frequencies']
    assert 'follows_benford' in results['frequencies']

def test_classify_benford_compliance():
    # Test with sample p-values and statistics
    test_results = (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.005, 0.10, 2.0)
    benford_score, category, evidence = classify_benford_compliance(test_results)
    
    assert isinstance(benford_score, float)
    assert benford_score >= 0.0 and benford_score <= 1.0
    assert category in ['Strong', 'Moderate', 'Weak', 'Non-Benford']
    assert isinstance(evidence, str)