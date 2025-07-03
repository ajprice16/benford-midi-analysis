# File: /benford-midi-analysis/benford-midi-analysis/src/benford_midi/analysis.py

import numpy as np
import pandas as pd
import mido
from scipy import stats
from pathlib import Path

def parse_midi(file_path):
    """Parse MIDI file and extract note frequencies."""
    midi_file = mido.MidiFile(file_path)
    frequencies = []
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                frequency = 440 * (2 ** ((msg.note - 69) / 12))
                frequencies.append(frequency)
    return frequencies

def analyze_frequencies(frequencies):
    """Analyze frequencies for Benford's Law compliance."""
    if len(frequencies) < 10:
        raise ValueError("Not enough data to analyze.")
    
    first_digits = [int(str(freq)[0]) for freq in frequencies if freq > 0]
    observed_counts = np.bincount(first_digits)[1:10]  # Count digits 1-9
    total_counts = observed_counts.sum()
    
    expected_counts = [np.log10(1 + 1/d) * total_counts for d in range(1, 10)]
    
    chi2_stat, p_value = stats.chisquare(observed_counts, expected_counts)
    
    return {
        'observed_counts': observed_counts,
        'expected_counts': expected_counts,
        'chi2_stat': chi2_stat,
        'p_value': p_value
    }

def run_analysis(directory):
    """Run analysis on all MIDI files in a directory."""
    results = []
    midi_files = Path(directory).glob('*.mid')
    
    for midi_file in midi_files:
        frequencies = parse_midi(midi_file)
        analysis_result = analyze_frequencies(frequencies)
        results.append({
            'file': midi_file.name,
            'chi2_stat': analysis_result['chi2_stat'],
            'p_value': analysis_result['p_value']
        })
    
    return pd.DataFrame(results)