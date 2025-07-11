# Example of comparing two sets of MIDI files using the benford-midi package

from pathlib import Path
import pandas as pd
from benford_midi.analysis import compare_directories


def main():
    # Define the base directory for MIDI files
    base_dir = Path("path/to/your/midi/files")  # Update this path

    # Specify the two directories to compare
    dir1 = base_dir / "directory1"  # Update with your first directory
    dir2 = base_dir / "directory2"  # Update with your second directory

    # Ensure the directories exist
    if not dir1.exists() or not dir2.exists():
        print(f"One or both directories do not exist: {dir1}, {dir2}")
        return

    # Compare the directories and get results
    results_dir1, results_dir2 = compare_directories(dir1, dir2, base_dir)

    # Create DataFrames for analysis
    df1 = pd.DataFrame(results_dir1)
    df2 = pd.DataFrame(results_dir2)

    # Print summary of results
    print(f"Results for {dir1.name}:")
    print(df1)
    print(f"\nResults for {dir2.name}:")
    print(df2)


if __name__ == "__main__":
    main()
