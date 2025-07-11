#!/usr/bin/env python3
"""
Command-line interface for Benford MIDI Analysis package.
"""

import argparse
import sys
import traceback
from pathlib import Path

from .analysis import analyze_single_directory, compare_directories


def main():
    parser = argparse.ArgumentParser(
        description="Benford's Law Analysis for MIDI Files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./midi_files/classical
  %(prog)s compare ./midi_files/classical ./midi_files/jazz --output_dir ./results
  %(prog)s analyze ./midi_files/pop --no_plots --output_dir ./output
        """,
    )

    parser.add_argument(
        "action",
        choices=["analyze", "compare"],
        help="Action to perform: 'analyze' a single directory or 'compare' two directories",
    )

    parser.add_argument("directory", type=str, help="Path to the first MIDI directory")

    parser.add_argument(
        "--compare_with",
        type=str,
        help="Path to the second MIDI directory (required for 'compare' action)",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        help="Directory to save output files (CSV and plots). Default: same as input directory",
    )

    parser.add_argument(
        "--no_plots", action="store_true", help="Disable plot generation"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Set up verbose output
    if args.verbose:
        print(f"Benford MIDI Analysis CLI v1.0.0")
        print(f"Action: {args.action}")
        print(f"Directory: {args.directory}")
        if args.compare_with:
            print(f"Compare with: {args.compare_with}")
        if args.output_dir:
            print(f"Output directory: {args.output_dir}")
        print(f"Generate plots: {not args.no_plots}")
        print("-" * 50)

    try:
        if args.action == "analyze":
            # Single directory analysis
            midi_dir = Path(args.directory)
            if not midi_dir.exists():
                print(f"Error: Directory not found: {midi_dir}", file=sys.stderr)
                sys.exit(1)
            if not midi_dir.is_dir():
                print(f"Error: Path is not a directory: {midi_dir}", file=sys.stderr)
                sys.exit(1)

            print(f"Analyzing MIDI files in directory: {midi_dir}")

            # Check if directory has MIDI files
            midi_files = list(midi_dir.glob("*.mid")) + list(midi_dir.glob("*.midi"))
            if not midi_files:
                print(f"Warning: No MIDI files found in {midi_dir}")
                sys.exit(0)

            print(f"Found {len(midi_files)} MIDI files")

            # Run analysis
            results_df = analyze_single_directory(
                dir_path=midi_dir,
                output_dir=args.output_dir,
                create_plots=not args.no_plots,
            )

            if len(results_df) > 0:
                print(
                    f"\n✓ Analysis complete! Processed {len(results_df)} files successfully."
                )

                # Summary statistics
                avg_score = results_df["Benford_Score"].mean()
                compliant_count = len(
                    results_df[
                        results_df["Benford_Category"].isin(
                            ["Strong", "Moderate", "Weak"]
                        )
                    ]
                )
                compliance_rate = compliant_count / len(results_df) * 100

                print(f"  Average Benford Score: {avg_score:.3f}")
                print(
                    f"  Overall Compliance Rate: {compliance_rate:.1f}% ({compliant_count}/{len(results_df)} files)"
                )

                # Category breakdown
                category_counts = results_df["Benford_Category"].value_counts()
                print(f"  Category Breakdown:")
                for category in ["Strong", "Moderate", "Weak", "Non-Benford"]:
                    count = category_counts.get(category, 0)
                    percentage = count / len(results_df) * 100
                    print(f"    {category}: {count} ({percentage:.1f}%)")
            else:
                print("No files were successfully processed.")
                sys.exit(1)

        elif args.action == "compare":
            # Directory comparison
            if not args.compare_with:
                print(
                    "Error: The --compare_with argument is required for comparison.",
                    file=sys.stderr,
                )
                sys.exit(1)

            midi_dir1 = Path(args.directory)
            midi_dir2 = Path(args.compare_with)

            # Validate directories
            for i, dir_path in enumerate([midi_dir1, midi_dir2], 1):
                if not dir_path.exists():
                    print(
                        f"Error: Directory {i} not found: {dir_path}", file=sys.stderr
                    )
                    sys.exit(1)
                if not dir_path.is_dir():
                    print(
                        f"Error: Path {i} is not a directory: {dir_path}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

            # Check for MIDI files in both directories
            midi_files1 = list(midi_dir1.glob("*.mid")) + list(midi_dir1.glob("*.midi"))
            midi_files2 = list(midi_dir2.glob("*.mid")) + list(midi_dir2.glob("*.midi"))

            if not midi_files1:
                print(f"Warning: No MIDI files found in {midi_dir1}")
            if not midi_files2:
                print(f"Warning: No MIDI files found in {midi_dir2}")

            if not midi_files1 and not midi_files2:
                print("Error: No MIDI files found in either directory.")
                sys.exit(1)

            print(f"Comparing MIDI files:")
            print(f"  Directory 1: {midi_dir1} ({len(midi_files1)} files)")
            print(f"  Directory 2: {midi_dir2} ({len(midi_files2)} files)")

            # Run comparison
            results_dir1, results_dir2, combined_df = compare_directories(
                dir1=midi_dir1,
                dir2=midi_dir2,
                output_dir=args.output_dir,
                create_plots=not args.no_plots,
            )

            print(f"\n✓ Comparison complete!")
            print(f"  {midi_dir1.name}: {len(results_dir1)} files processed")
            print(f"  {midi_dir2.name}: {len(results_dir2)} files processed")

            if len(combined_df) > 0:
                # Quick comparison summary
                df1 = combined_df[combined_df["Directory"] == midi_dir1.name]
                df2 = combined_df[combined_df["Directory"] == midi_dir2.name]

                if len(df1) > 0 and len(df2) > 0:
                    avg1 = df1["Benford_Score"].mean()
                    avg2 = df2["Benford_Score"].mean()

                    print(f"\nQuick Summary:")
                    print(f"  {midi_dir1.name} average score: {avg1:.3f}")
                    print(f"  {midi_dir2.name} average score: {avg2:.3f}")

                    if abs(avg1 - avg2) < 0.01:
                        print(f"  → Very similar Benford compliance")
                    elif avg1 > avg2:
                        print(f"  → {midi_dir1.name} shows stronger Benford compliance")
                    else:
                        print(f"  → {midi_dir2.name} shows stronger Benford compliance")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
