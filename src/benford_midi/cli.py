import argparse
from pathlib import Path
from benford_midi.analysis import analyze_midi_features, compare_directories

def main():
    parser = argparse.ArgumentParser(description="Benford's Law Analysis for MIDI Files")
    parser.add_argument('action', choices=['analyze', 'compare'], help="Action to perform: analyze a single directory or compare two directories.")
    parser.add_argument('directory', type=str, help="Path to the MIDI directory for analysis.")
    parser.add_argument('--compare_with', type=str, help="Path to the second MIDI directory for comparison (required if action is 'compare').")

    args = parser.parse_args()

    if args.action == 'analyze':
        midi_dir = Path(args.directory)
        if not midi_dir.exists() or not midi_dir.is_dir():
            raise FileNotFoundError(f"Directory not found: {midi_dir}")
        
        print(f"Analyzing MIDI files in directory: {midi_dir}")
        results = analyze_midi_features(midi_dir)
        print("Analysis results:", results)

    elif args.action == 'compare':
        if not args.compare_with:
            raise ValueError("The --compare_with argument is required for comparison.")
        
        midi_dir1 = Path(args.directory)
        midi_dir2 = Path(args.compare_with)

        if not midi_dir1.exists() or not midi_dir1.is_dir():
            raise FileNotFoundError(f"Directory not found: {midi_dir1}")
        if not midi_dir2.exists() or not midi_dir2.is_dir():
            raise FileNotFoundError(f"Directory not found: {midi_dir2}")

        print(f"Comparing MIDI files between {midi_dir1} and {midi_dir2}")
        results_dir1, results_dir2 = compare_directories(midi_dir1, midi_dir2)
        print("Comparison results:", results_dir1, results_dir2)

if __name__ == "__main__":
    main()