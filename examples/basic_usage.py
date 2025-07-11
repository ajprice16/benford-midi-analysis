# Example usage of the Benford MIDI Analysis package

from benford_midi.analysis import analyze_midi_features
from pathlib import Path


def main():
    # Specify the path to the MIDI file
    midi_file_path = Path("path/to/your/midi/file.mid")

    # Analyze the MIDI features for Benford's Law compliance
    results = analyze_midi_features(midi_file_path)

    # Print the analysis results
    print(f"Analysis results for {midi_file_path.name}:")
    for feature, result in results.items():
        print(f"  Feature: {feature}")
        print(f"    Number of data points: {result['n']}")
        print(f"    Chi-square p-value: {result['chi2_p']:.4f}")
        print(
            f"    Follows Benford's Law: {'Yes' if result['follows_benford'] else 'No'}"
        )


if __name__ == "__main__":
    main()
