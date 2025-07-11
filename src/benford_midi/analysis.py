# File: /benford-midi-analysis/benford-midi-analysis/src/benford_midi/analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mido
import os
import warnings
from pathlib import Path
from scipy.stats import chi2, ttest_ind
from scipy import stats
from tqdm import tqdm
import multiprocessing as mp
from functools import partial

from .utils import (
    format_p,
    get_first_digit,
    get_significand,
    benford_first_digit_prob,
    generate_benford_sample,
    z_transform,
    get_props,
)

# Constants
C = np.log10(np.e)  # Sum invariance constant (log10(e))
DIGITS = np.arange(1, 10)  # First digits 1-9


def parse_midi(file):
    """Parse MIDI file and convert notes to frequencies"""

    def note_to_freq(note):
        freq = 440 * (2 ** ((note - 69) / 12))
        return freq

    notes = []
    for i, track in enumerate(file.tracks):
        for msg in track:
            if msg.is_meta == False and msg.type == "note_on":
                notes.append(msg.note)

    if len(notes) == 0:
        raise Exception(f"Failed: File {str(file)} is empty")

    # Convert notes to frequencies
    frequencies = [round(note_to_freq(note)) for note in notes]
    return frequencies


def parse_midi_extended(file):
    """Parse MIDI file and extract multiple numerical features"""

    def note_to_freq(note):
        freq = 440 * (2 ** ((note - 69) / 12))
        return freq

    # Collections for different features
    notes = []
    velocities = []
    frequencies = []
    durations = []
    inter_onset_intervals = []
    control_values = []
    delta_times = []

    # Track note_on events to calculate durations
    active_notes = {}
    current_time = 0
    last_note_time = 0

    for id, track in enumerate(file.tracks):
        track_time = 0
        for msg in track:
            track_time += msg.time
            delta_times.append(msg.time) if msg.time > 0 else None

            if not msg.is_meta:
                if msg.type == "note_on" and msg.velocity > 0:
                    notes.append(msg.note)
                    velocities.append(msg.velocity)
                    frequencies.append(round(note_to_freq(msg.note)))

                    # Calculate inter-onset interval
                    if last_note_time > 0:
                        interval = track_time - last_note_time
                        if interval > 0:
                            inter_onset_intervals.append(interval)
                    last_note_time = track_time

                    # Store note_on time for duration calculation
                    note_key = (msg.channel, msg.note)
                    active_notes[note_key] = track_time

                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    # Calculate note duration
                    note_key = (msg.channel, msg.note)
                    if note_key in active_notes:
                        duration = track_time - active_notes[note_key]
                        if duration > 0:
                            durations.append(duration)
                        del active_notes[note_key]

                elif msg.type == "control_change":
                    if msg.value > 0:  # Exclude zero values
                        control_values.append(msg.value)

    # Filter out zero values and convert to appropriate units
    features = {
        "frequencies": [f for f in frequencies if f > 0],
        "velocities": [v for v in velocities if v > 0],
        "notes": [n for n in notes if n > 0],
        "durations": [d for d in durations if d > 0],
        "inter_onset_intervals": [i for i in inter_onset_intervals if i > 0],
        "control_values": [c for c in control_values if c > 0],
        "delta_times": [d for d in delta_times if d > 0],
    }

    return features


def analyze_midi_features(midi_file):
    """Analyze multiple MIDI features for Benford's law compliance"""
    features = parse_midi_extended(mido.MidiFile(str(midi_file)))

    results = {}
    for feature_name, data in features.items():
        if len(data) >= 10:  # Minimum data requirement
            try:
                test = BenfordTests(data)
                chi2_stat, chi2_p = test.pearson_chi2()
                results[feature_name] = {
                    "n": len(data),
                    "chi2_p": chi2_p,
                    "follows_benford": chi2_p > 0.05,
                }
            except Exception as e:
                results[feature_name] = {"error": str(e)}
        else:
            results[feature_name] = {"insufficient_data": len(data)}

    return results


def classify_benford_compliance(test_results):
    """
    Classify Benford compliance

    Returns:
    - benford_score: Float between 0-1 indicating strength of Benford compliance
    - benford_category: String category ('Strong', 'Moderate', 'Weak', 'Non-Benford')
    - primary_evidence: String describing main evidence for classification
    """
    chi2_p, ks_p, q_p, m_p, g_p, combined_p, pearson_p, mad, ned, z_stat = test_results

    # Use descriptive stats to adjust weights, not include them directly
    if np.isnan(q_p):
        # For small samples, give more weight to robust tests
        if mad < 0.006:  # Very good MAD
            test_weights = {"chi2_p": 0.4, "ks_p": 0.35, "mad": 0.25}
        elif mad > 0.020:  # Poor MAD
            test_weights = {"chi2_p": 0.3, "ks_p": 0.2, "mad": 0.5}  # Penalize heavily
        else:
            test_weights = {"chi2_p": 0.35, "ks_p": 0.25, "mad": 0.15}
    else:
        # For larger samples, use all formal tests
        test_weights = {
            "chi2_p": 0.25,
            "combined_p": 0.30,
            "ks_p": 0.20,
            "q_p": 0.15,
            "mad": 0.10,
        }

    # Use descriptive stats as secondary criteria
    descriptive_penalty = 0
    if ned > 0.15:  # High NED indicates poor fit
        descriptive_penalty += 0.1
    if z_stat > 3:  # High Z-stat indicates outlier digits
        descriptive_penalty += 0.05

    # Calculate score and apply penalty
    p_score = sum(
        p_val * weight
        for p_val, weight in zip(
            [chi2_p, ks_p, q_p],
            [test_weights.get(k, 0.0) for k in ["chi2_p", "ks_p", "q_p"]],
        )
    )
    mad_component = max(0.0, min(1.0, (0.02 - mad) / 0.014)) * test_weights["mad"]

    benford_score = max(0.0, min(1.0, p_score + mad_component - descriptive_penalty))

    # Count significant tests (p > 0.05), excluding NaN values
    p_values = [chi2_p, ks_p, m_p, g_p, combined_p]
    if not np.isnan(q_p):
        p_values.append(q_p)

    valid_p_values = [p for p in p_values if not np.isnan(p)]
    significant_tests = sum([p > 0.05 for p in valid_p_values])
    total_tests = len(valid_p_values)

    # Adjusted classification thresholds for smaller samples
    if total_tests < 5:  # Small sample adjustments
        if (
            benford_score >= 0.6
            and significant_tests >= max(2, total_tests * 0.6)
            and mad < 0.015
        ):
            category = "Strong"
            primary_evidence = f"High p-values ({significant_tests}/{total_tests} tests), low MAD ({mad:.4f}) [Small sample]"
        elif (
            benford_score >= 0.3
            and significant_tests >= max(1, total_tests * 0.4)
            and mad < 0.025
        ):
            category = "Moderate"
            primary_evidence = f"Mixed evidence ({significant_tests}/{total_tests} tests), moderate MAD ({mad:.4f}) [Small sample]"
        elif benford_score >= 0.15 and (significant_tests >= 1 or mad < 0.020):
            category = "Weak"
            primary_evidence = f"Weak evidence ({significant_tests}/{total_tests} tests), MAD ({mad:.4f}) [Small sample]"
        else:
            category = "Non-Benford"
            primary_evidence = f"Strong rejection ({significant_tests}/{total_tests} tests), high MAD ({mad:.4f}) [Small sample]"
    else:
        # Original thresholds for larger samples
        if benford_score >= 0.7 and significant_tests >= 4 and mad < 0.010:
            category = "Strong"
            primary_evidence = f"High p-values ({significant_tests}/{total_tests} tests), low MAD ({mad:.4f})"
        elif benford_score >= 0.4 and significant_tests >= 3 and mad < 0.020:
            category = "Moderate"
            primary_evidence = f"Mixed evidence ({significant_tests}/{total_tests} tests), moderate MAD ({mad:.4f})"
        elif benford_score >= 0.2 and (significant_tests >= 2 or mad < 0.015):
            category = "Weak"
            primary_evidence = f"Weak evidence ({significant_tests}/{total_tests} tests), MAD ({mad:.4f})"
        else:
            category = "Non-Benford"
            primary_evidence = f"Strong rejection ({significant_tests}/{total_tests} tests), high MAD ({mad:.4f})"

    return benford_score, category, primary_evidence


def process_midi_file(midi_file_path, midi_dir):
    """Process a single MIDI file and return results"""
    try:
        # Change to MIDI directory for relative paths
        original_dir = os.getcwd()
        os.chdir(midi_dir)

        # Parse MIDI file to get frequencies
        frequencies = parse_midi(mido.MidiFile(str(midi_file_path)))

        if len(frequencies) < 10:  # Skip files with too few notes
            return (
                None,
                f"Skipping {midi_file_path.name}: too few notes ({len(frequencies)})",
            )

        # Run Benford analysis with reduced B for faster processing
        tests = BenfordTests(frequencies)

        # Run all tests
        chi2_stat, chi2_p = tests.pearson_chi2()
        ks_stat, ks_p = tests.kolmogorov_smirnov()
        q_stat, q_p = tests.hotelling_q(B=200)  # Reduced B for multiprocessing
        m_stat, m_p = tests.sup_norm_m(B=200)
        g_stat, g_p = tests.min_p_value_g(B=200)
        combined_stat, combined_p = tests.combined_test(B=200)
        pearson_stat, pearson_p = tests.pearson()
        mad_stat = tests.MAD()
        ned_stat = tests.NED()
        z_stat = tests.zStat()
        observed_props = tests.return_observed_props()

        # Get improved Benford classification
        test_results = (
            chi2_p,
            ks_p,
            q_p,
            m_p,
            g_p,
            combined_p,
            pearson_p,
            mad_stat,
            ned_stat,
            z_stat,
        )
        benford_score, benford_category, primary_evidence = classify_benford_compliance(
            test_results
        )

        # Store results with new classification system
        file_results = [
            midi_file_path.name,
            chi2_p,
            ks_p,
            q_p,
            m_p,
            g_p,
            combined_p,
            pearson_p,
            mad_stat,
            ned_stat,
            z_stat,
            benford_score,
            benford_category,
            primary_evidence,
            observed_props,
        ]

        # Restore original directory
        os.chdir(original_dir)

        return file_results, None

    except Exception as e:
        # Restore original directory
        os.chdir(original_dir)
        return None, f"Error processing {midi_file_path.name}: {e}"


def analyze_single_directory(dir_path, output_dir=None, create_plots=True):
    """
    Analyze a single directory of MIDI files

    Args:
        dir_path: Path to directory containing MIDI files
        output_dir: Directory to save results (default: same as dir_path)
        create_plots: Whether to create visualization plots

    Returns:
        pandas.DataFrame: Results dataframe
    """
    dir_path = Path(dir_path)
    if output_dir is None:
        output_dir = dir_path.parent
    else:
        output_dir = Path(output_dir)

    # Find MIDI files
    midi_files = [
        f for f in dir_path.iterdir() if f.suffix.lower() in (".mid", ".midi")
    ]
    print(f"Found {len(midi_files)} MIDI files in {dir_path.name}")

    if len(midi_files) == 0:
        print("No MIDI files found in directory")
        return pd.DataFrame()

    # Process files with multiprocessing
    results = []
    num_processes = min(mp.cpu_count(), len(midi_files))
    print(f"Using {num_processes} processes")

    process_func = partial(process_midi_file, midi_dir=dir_path)

    with mp.Pool(processes=num_processes) as pool:
        results_iter = pool.imap(process_func, midi_files)

        for result, error in tqdm(
            results_iter, total=len(midi_files), desc="Processing MIDI files"
        ):
            if result is not None:
                results.append(result)
            elif error is not None:
                print(error)

    # Create DataFrame
    names = [
        "Name",
        "Chi2_P",
        "K-S_P",
        "H_Q_P",
        "S_M_P",
        "G_P",
        "Combined_P",
        "Pearson_P",
        "MAD",
        "NED",
        "ZStat",
        "Benford_Score",
        "Benford_Category",
        "Primary_Evidence",
        "Observed_Props",
    ]

    results_df = pd.DataFrame(results, columns=names)

    # Print summary
    print_analysis_summary(results_df, dir_path.name)

    # Save results
    output_filename = f"benford_analysis_{dir_path.name}.csv"
    results_df.to_csv(output_dir / output_filename, index=False)
    print(f"\nDetailed results saved to: {output_dir / output_filename}")

    # Create visualization
    if create_plots and len(results_df) > 0:
        try:
            create_single_directory_plots(results_df, dir_path.name, output_dir)
        except Exception as e:
            print(f"Error creating visualization: {e}")

    return results_df


def compare_directories(dir1, dir2, output_dir=None, create_plots=True):
    """
    Compare Benford's law compliance between two directories of MIDI files

    Args:
        dir1: Path to first directory
        dir2: Path to second directory
        output_dir: Directory to save results
        create_plots: Whether to create visualization plots

    Returns:
        tuple: (results_dir1, results_dir2, combined_df)
    """
    dir1 = Path(dir1)
    dir2 = Path(dir2)

    if output_dir is None:
        output_dir = dir1.parent
    else:
        output_dir = Path(output_dir)

    results_dir1 = []
    results_dir2 = []

    # Process first directory
    print(f"\nProcessing directory 1: {dir1.name}")
    midi_files_1 = [f for f in dir1.iterdir() if f.suffix.lower() in (".mid", ".midi")]
    print(f"Found {len(midi_files_1)} MIDI files in {dir1.name}")

    if len(midi_files_1) > 0:
        num_processes = min(mp.cpu_count(), len(midi_files_1))
        process_func = partial(process_midi_file, midi_dir=dir1)

        with mp.Pool(processes=num_processes) as pool:
            results_iter = pool.imap(process_func, midi_files_1)
            for result, error in tqdm(
                results_iter, total=len(midi_files_1), desc=f"Processing {dir1.name}"
            ):
                if result is not None:
                    results_dir1.append(result)
                elif error is not None:
                    print(error)

    # Process second directory
    print(f"\nProcessing directory 2: {dir2.name}")
    midi_files_2 = [f for f in dir2.iterdir() if f.suffix.lower() in (".mid", ".midi")]
    print(f"Found {len(midi_files_2)} MIDI files in {dir2.name}")

    if len(midi_files_2) > 0:
        num_processes = min(mp.cpu_count(), len(midi_files_2))
        process_func = partial(process_midi_file, midi_dir=dir2)

        with mp.Pool(processes=num_processes) as pool:
            results_iter = pool.imap(process_func, midi_files_2)
            for result, error in tqdm(
                results_iter, total=len(midi_files_2), desc=f"Processing {dir2.name}"
            ):
                if result is not None:
                    results_dir2.append(result)
                elif error is not None:
                    print(error)

    # Analyze and display results
    combined_df = analyze_comparison_results(
        results_dir1, results_dir2, dir1.name, dir2.name
    )

    # Save combined results
    output_filename = f"benford_comparison_{dir1.name}_vs_{dir2.name}.csv"
    combined_df.to_csv(output_dir / output_filename, index=False)
    print(f"\nDetailed results saved to: {output_dir / output_filename}")

    # Create visualization
    if create_plots and len(combined_df) > 0:
        try:
            create_comparison_plots(combined_df, dir1.name, dir2.name, output_dir)
        except Exception as e:
            print(f"Error creating visualization: {e}")

    return results_dir1, results_dir2, combined_df


def print_analysis_summary(results_df, dir_name):
    """Print summary statistics for single directory analysis"""
    print(f"\nAnalysis Results for {dir_name}:")
    print(f"=" * 50)

    total = len(results_df)
    if total > 0:
        # Count by category
        category_counts = results_df["Benford_Category"].value_counts()
        strong_count = category_counts.get("Strong", 0)
        moderate_count = category_counts.get("Moderate", 0)
        weak_count = category_counts.get("Weak", 0)
        non_benford_count = category_counts.get("Non-Benford", 0)

        # Calculate average score
        avg_score = results_df["Benford_Score"].mean()

        print(f"Total files processed: {total}")
        print(f"Average Benford Score: {avg_score:.3f}")
        print(f"Classification breakdown:")
        print(f"  Strong Benford:    {strong_count:3d} ({strong_count/total*100:.1f}%)")
        print(
            f"  Moderate Benford:  {moderate_count:3d} ({moderate_count/total*100:.1f}%)"
        )
        print(f"  Weak Benford:      {weak_count:3d} ({weak_count/total*100:.1f}%)")
        print(
            f"  Non-Benford:       {non_benford_count:3d} ({non_benford_count/total*100:.1f}%)"
        )

        # Overall compliance (Strong + Moderate + Weak)
        compliant_count = strong_count + moderate_count + weak_count
        print(
            f"Overall compliance: {compliant_count} ({compliant_count/total*100:.1f}%)"
        )

        # Statistical summaries
        print(f"Average statistics:")
        print(f"  MAD: {results_df['MAD'].mean():.4f}")
        print(f"  Combined p-value: {format_p(results_df['Combined_P'].mean())}")


def analyze_comparison_results(results_dir1, results_dir2, dir1_name, dir2_name):
    """Analyze and compare the results from two directories"""
    names = [
        "Name",
        "Chi2_P",
        "K-S_P",
        "H_Q_P",
        "S_M_P",
        "G_P",
        "Combined_P",
        "Pearson_P",
        "MAD",
        "NED",
        "ZStat",
        "Benford_Score",
        "Benford_Category",
        "Primary_Evidence",
        "Observed_Props",
    ]

    # Create DataFrames
    df1 = (
        pd.DataFrame(results_dir1, columns=names)
        if results_dir1
        else pd.DataFrame(columns=names)
    )
    df2 = (
        pd.DataFrame(results_dir2, columns=names)
        if results_dir2
        else pd.DataFrame(columns=names)
    )

    # Add directory labels
    df1["Directory"] = dir1_name
    df2["Directory"] = dir2_name

    # Combine DataFrames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    print(f"\n{'='*60}")
    print(f"COMPARISON RESULTS: {dir1_name} vs {dir2_name}")
    print(f"{'='*60}")

    def analyze_directory(df, dir_name):
        if len(df) > 0:
            total = len(df)

            # Count by category
            category_counts = df["Benford_Category"].value_counts()
            strong_count = category_counts.get("Strong", 0)
            moderate_count = category_counts.get("Moderate", 0)
            weak_count = category_counts.get("Weak", 0)
            non_benford_count = category_counts.get("Non-Benford", 0)

            # Calculate average score
            avg_score = df["Benford_Score"].mean()

            print(f"\n{dir_name}:")
            print(f"  Total files processed: {total}")
            print(f"  Average Benford Score: {avg_score:.3f}")
            print(f"  Classification breakdown:")
            print(
                f"    Strong Benford:    {strong_count:3d} ({strong_count/total*100:.1f}%)"
            )
            print(
                f"    Moderate Benford:  {moderate_count:3d} ({moderate_count/total*100:.1f}%)"
            )
            print(
                f"    Weak Benford:      {weak_count:3d} ({weak_count/total*100:.1f}%)"
            )
            print(
                f"    Non-Benford:       {non_benford_count:3d} ({non_benford_count/total*100:.1f}%)"
            )

            # Overall compliance (Strong + Moderate + Weak)
            compliant_count = strong_count + moderate_count + weak_count
            print(
                f"  Overall compliance: {compliant_count} ({compliant_count/total*100:.1f}%)"
            )

            # Statistical summaries
            print(f"  Average statistics:")
            print(f"    MAD: {df['MAD'].mean():.4f}")
            print(f"    Combined p-value: {format_p(df['Combined_P'].mean())}")

            return {
                "total": total,
                "avg_score": avg_score,
                "strong": strong_count,
                "moderate": moderate_count,
                "weak": weak_count,
                "non_benford": non_benford_count,
                "compliant": compliant_count,
            }
        else:
            print(f"\n{dir_name}: No files processed")
            return None

    # Analyze both directories
    stats1 = analyze_directory(df1, dir1_name)
    stats2 = analyze_directory(df2, dir2_name)

    # Statistical comparison if both directories have data
    if stats1 and stats2:
        perform_statistical_comparison(df1, df2, dir1_name, dir2_name, stats1, stats2)

    return combined_df


def perform_statistical_comparison(df1, df2, dir1_name, dir2_name, stats1, stats2):
    """Perform statistical comparison between two directories"""
    print(f"\n{'='*40}")
    print(f"STATISTICAL COMPARISON")
    print(f"{'='*40}")

    # Compare average Benford scores using t-test with precision check
    try:
        # Check if data are nearly identical (variance close to zero)
        var1 = df1["Benford_Score"].var()
        var2 = df2["Benford_Score"].var()
        mean_diff = abs(df1["Benford_Score"].mean() - df2["Benford_Score"].mean())

        if var1 < 1e-10 and var2 < 1e-10 and mean_diff < 1e-6:
            print(f"T-test for Benford Score difference:")
            print(f"  Mean score {dir1_name}: {stats1['avg_score']:.3f}")
            print(f"  Mean score {dir2_name}: {stats2['avg_score']:.3f}")
            print(f"  Result: Data are nearly identical - no meaningful difference")
        else:
            # Suppress the precision and division warnings for this specific calculation
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="Precision loss occurred in moment calculation"
                )
                warnings.filterwarnings(
                    "ignore", message="invalid value encountered in scalar divide"
                )
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                t_stat, t_p = ttest_ind(df1["Benford_Score"], df2["Benford_Score"])

            print(f"T-test for Benford Score difference:")
            print(f"  Mean score {dir1_name}: {stats1['avg_score']:.3f}")
            print(f"  Mean score {dir2_name}: {stats2['avg_score']:.3f}")

            # Handle NaN values from t-test
            if np.isnan(t_stat) or np.isnan(t_p):
                print(f"  T-statistic: nan, p-value: nan")
                print(f"  Result: No significant difference in Benford scores")
            else:
                print(f"  T-statistic: {t_stat:.3f}, p-value: {format_p(t_p)}")

                if t_p < 0.05:
                    better_dir = (
                        dir1_name
                        if stats1["avg_score"] > stats2["avg_score"]
                        else dir2_name
                    )
                    print(
                        f"  Result: {better_dir} has significantly higher Benford scores"
                    )
                else:
                    print(f"  Result: No significant difference in Benford scores")
    except Exception as e:
        print(f"T-test error: {e}")

    # Add descriptive comparison
    print(f"\nDescriptive Comparison:")
    score_diff = abs(stats1["avg_score"] - stats2["avg_score"])
    if score_diff < 0.01:
        print(f"  Benford scores are very similar (difference: {score_diff:.4f})")
    elif score_diff < 0.05:
        print(f"  Benford scores are somewhat different (difference: {score_diff:.4f})")
    else:
        print(f"  Benford scores are notably different (difference: {score_diff:.4f})")

    # Compare compliance rates
    compliance1 = stats1["compliant"] / stats1["total"] * 100
    compliance2 = stats2["compliant"] / stats2["total"] * 100
    compliance_diff = abs(compliance1 - compliance2)

    print(f"  Compliance rate difference: {compliance_diff:.1f}%")


def create_single_directory_plots(results_df, dir_name, output_dir):
    """Create visualization plots for single directory analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f"Benford's Law Analysis: {dir_name}", fontsize=16)

    # Category distribution pie chart
    category_counts = results_df["Benford_Category"].value_counts()
    axes[0, 0].pie(
        category_counts.values, labels=category_counts.index, autopct="%1.1f%%"
    )
    axes[0, 0].set_title("Benford Category Distribution")

    # Benford score histogram
    axes[0, 1].hist(results_df["Benford_Score"], bins=20, alpha=0.7, color="skyblue")
    axes[0, 1].set_title("Benford Score Distribution")
    axes[0, 1].set_xlabel("Benford Score")
    axes[0, 1].set_ylabel("Frequency")

    # MAD distribution
    axes[1, 0].hist(results_df["MAD"], bins=20, alpha=0.7, color="lightgreen")
    axes[1, 0].set_title("MAD Distribution")
    axes[1, 0].set_xlabel("MAD Value")
    axes[1, 0].set_ylabel("Frequency")

    # Combined p-value distribution
    axes[1, 1].hist(results_df["Combined_P"], bins=20, alpha=0.7, color="orange")
    axes[1, 1].set_title("Combined P-value Distribution")
    axes[1, 1].set_xlabel("P-value")
    axes[1, 1].set_ylabel("Frequency")

    plt.tight_layout()
    plot_filename = f"benford_analysis_{dir_name}.png"
    plt.savefig(output_dir / plot_filename, dpi=300, bbox_inches="tight")
    print(f"Visualization saved to: {output_dir / plot_filename}")
    plt.show()


def create_comparison_plots(combined_df, dir1_name, dir2_name, output_dir):
    """Create visualization plots for directory comparison"""
    # Split data by directory
    df1 = combined_df[combined_df["Directory"] == dir1_name]
    df2 = combined_df[combined_df["Directory"] == dir2_name]

    if len(df1) == 0 or len(df2) == 0:
        print("Insufficient data for comparison plots")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f"Benford's Law Comparison: {dir1_name} vs {dir2_name}", fontsize=16)

    # Benford compliance rates
    compliance_rates = [
        df1[df1["Benford_Category"].isin(["Strong", "Moderate", "Weak"])].shape[0]
        / len(df1)
        * 100,
        df2[df2["Benford_Category"].isin(["Strong", "Moderate", "Weak"])].shape[0]
        / len(df2)
        * 100,
    ]

    axes[0, 0].bar(
        [dir1_name, dir2_name], compliance_rates, color=["skyblue", "lightcoral"]
    )
    axes[0, 0].set_title("Benford Compliance Rate (%)")
    axes[0, 0].set_ylabel("Percentage")

    # Benford score distributions
    axes[0, 1].hist(
        df1["Benford_Score"], alpha=0.7, label=dir1_name, bins=20, color="skyblue"
    )
    axes[0, 1].hist(
        df2["Benford_Score"], alpha=0.7, label=dir2_name, bins=20, color="lightcoral"
    )
    axes[0, 1].set_title("Benford Score Distribution")
    axes[0, 1].set_xlabel("Benford Score")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].legend()

    # MAD comparison
    mad_values = [df1["MAD"].mean(), df2["MAD"].mean()]
    axes[1, 0].bar([dir1_name, dir2_name], mad_values, color=["lightgreen", "orange"])
    axes[1, 0].set_title("Average MAD (Mean Absolute Deviation)")
    axes[1, 0].set_ylabel("MAD Value")

    # File count comparison
    file_counts = [len(df1), len(df2)]
    axes[1, 1].bar([dir1_name, dir2_name], file_counts, color=["purple", "gold"])
    axes[1, 1].set_title("Number of Files Processed")
    axes[1, 1].set_ylabel("File Count")

    plt.tight_layout()
    plot_filename = f"benford_comparison_{dir1_name}_vs_{dir2_name}.png"
    plt.savefig(output_dir / plot_filename, dpi=300, bbox_inches="tight")
    print(f"Comparison visualization saved to: {output_dir / plot_filename}")
    plt.show()


class BenfordTests:
    def __init__(self, data):
        self.data = np.asarray(data)
        self.n = len(self.data)
        self.first_digits = get_first_digit(self.data)
        self.significands = get_significand(self.data)

        # Expected counts under Benford's law
        self.expected_counts = np.array(
            [benford_first_digit_prob(d) * self.n for d in DIGITS]
        )

        # Observed counts
        self.observed_counts = np.array(
            [np.sum(self.first_digits == d) for d in DIGITS]
        )

        # Z_d statistics
        self.z_bars = np.array([np.mean(z_transform(self.data, d)) for d in DIGITS])

        # Theoretical moments under Benford's law
        self.var_z = np.array([C * (d + 0.5 - C) for d in DIGITS])
        self.cov_z = -(C**2)  # Covariance between different Z_d's

    def pearson_chi2(self):
        """Pearson's chi-square test for first-digit Benford's law"""
        chi2_stat = np.sum(
            (self.observed_counts - self.expected_counts) ** 2 / self.expected_counts
        )
        p_value = 1 - chi2.cdf(chi2_stat, df=8)  # 9 digits - 1 = 8 df
        return chi2_stat, p_value

    def pearson(self):
        return stats.pearsonr(self.observed_counts, self.expected_counts)

    def kolmogorov_smirnov(self):
        """Kolmogorov-Smirnov test for significand distribution"""
        sorted_s = np.sort(self.significands)
        ecdf = np.arange(1, len(sorted_s) + 1) / len(sorted_s)
        benford_cdf = np.log10(sorted_s)
        ks_stat = np.max(np.abs(ecdf - benford_cdf))

        # More accurate p-value calculation with proper bounds
        n = len(sorted_s)
        p_value = 2 * np.exp(-2 * (ks_stat * np.sqrt(n) + 0.12) ** 2)

        # Ensure p-value is within valid bounds [0, 1]
        p_value = np.clip(p_value, 0.0, 1.0)
        return ks_stat, p_value

    def hotelling_q(self, B=1000):
        """Hotelling-type test based on sum-invariance property"""
        # Check if we have enough data for reliable Hotelling test
        if self.n < 100:
            # Return a neutral result for small samples instead of warning
            return np.nan, 0.5  # Neutral p-value that doesn't favor either hypothesis

        # Covariance matrix under H0
        sigma = np.diag(self.var_z) + self.cov_z * (1 - np.eye(9))

        # Test statistic
        diff = self.z_bars - C
        q_stat = self.n * diff @ np.linalg.inv(sigma) @ diff

        # Monte Carlo p-value with continuity correction
        q_samples = []
        for _ in range(B):  # Removed tqdm for multiprocessing
            benford_sample = generate_benford_sample(self.n)
            test = BenfordTests(benford_sample)
            q_samples.append(
                self.n * (test.z_bars - C) @ np.linalg.inv(sigma) @ (test.z_bars - C)
            )

        # Calculate p-value with continuity correction
        extreme_count = np.sum(np.array(q_samples) >= q_stat)
        p_value = (extreme_count + 1) / (B + 1)  # Add-1 correction
        return q_stat, p_value

    def sup_norm_m(self, B=1000):
        """Sup-norm test based on standardized Z_d statistics"""
        # Standardized statistics
        t_stats = (self.z_bars - C) / np.sqrt(self.var_z / self.n)
        m_stat = np.max(np.abs(t_stats))

        # Monte Carlo p-value with continuity correction
        m_samples = []
        for _ in range(B):  # Removed tqdm for multiprocessing
            benford_sample = generate_benford_sample(self.n)
            test = BenfordTests(benford_sample)
            t_stats_b = (test.z_bars - C) / np.sqrt(self.var_z / self.n)
            m_samples.append(np.max(np.abs(t_stats_b)))

        # Calculate p-value with continuity correction
        extreme_count = np.sum(np.array(m_samples) >= m_stat)
        p_value = (extreme_count + 1) / (B + 1)  # Add-1 correction
        return m_stat, p_value

    def min_p_value_g(self, B=1000):
        """Min p-value test combining standardized Z_d statistics"""
        # Standardized statistics and their p-values
        t_stats = (self.z_bars - C) / np.sqrt(self.var_z / self.n)
        abs_t = np.abs(t_stats)

        # Get null distribution of |T_d| via Monte Carlo
        abs_t_samples = np.zeros((B, 9))
        for i in range(B):  # Removed tqdm for multiprocessing
            benford_sample = generate_benford_sample(self.n)
            test = BenfordTests(benford_sample)
            abs_t_samples[i] = np.abs((test.z_bars - C) / np.sqrt(self.var_z / self.n))

        # Compute p-values for each T_d with continuity correction
        p_values = np.array(
            [(np.sum(abs_t_samples[:, d] >= abs_t[d]) + 1) / (B + 1) for d in range(9)]
        )

        # Test statistic is the minimum p-value
        g_stat = np.min(p_values)

        # Monte Carlo p-value for G with continuity correction
        g_samples = []
        for i in range(B):
            g_samples.append(
                np.min(
                    [
                        (np.sum(abs_t_samples[:, d] >= abs_t_samples[i, d]) + 1)
                        / (B + 1)
                        for d in range(9)
                    ]
                )
            )

        p_value = (np.sum(np.array(g_samples) <= g_stat) + 1) / (B + 1)
        return g_stat, p_value

    def combined_test(self, B=1000):
        """Combined test of chi-square and Hotelling Q statistics"""
        chi2_stat, chi2_p = self.pearson_chi2()

        # For small samples, skip Hotelling and just return chi-square result
        if self.n < 100:
            return chi2_stat, chi2_p

        q_stat, q_p = self.hotelling_q(B)

        # Handle zero p-values to avoid log(0) issues
        chi2_p_safe = max(chi2_p, 1e-16)  # Use very small value instead of 0
        q_p_safe = max(q_p, 1e-16)

        # Fisher's method for combining p-values
        fisher_stat = -2 * (np.log(chi2_p_safe) + np.log(q_p_safe))
        p_value = 1 - chi2.cdf(fisher_stat, df=4)  # 2*2 df

        return fisher_stat, p_value

    def zStat(self):
        diff_array = []
        observed_props, expected_props = get_props(
            self.observed_counts, self.expected_counts
        )
        for i in range(9):
            val = abs(observed_props[i] - expected_props[i]) / np.std(expected_props)
            diff_array.append(val)
        return max(diff_array)

    def MAD(self):
        observed_props, expected_props = get_props(
            self.observed_counts, self.expected_counts
        )

        abs_sum = np.sum(np.abs(observed_props - expected_props))
        return np.mean(abs_sum)

    def NED(self):
        observed_props, expected_props = get_props(
            self.observed_counts, self.expected_counts
        )
        # Avoid division by zero in expected_props
        return np.sqrt(
            np.sum(np.square(observed_props - expected_props) / expected_props)
        )

    def return_observed_props(self):
        """Return observed proportions for external use"""
        observed_props, _ = get_props(self.observed_counts, self.expected_counts)
        return str(observed_props)

    def plot_digit_distribution(self):
        """Plot observed vs expected first digit frequencies"""
        plt.figure(figsize=(10, 5))
        plt.bar(
            DIGITS - 0.2, self.observed_counts / self.n, width=0.4, label="Observed"
        )
        plt.bar(
            DIGITS + 0.2,
            self.expected_counts / self.n,
            width=0.4,
            label="Expected (Benford)",
        )
        plt.xlabel("First Digit")
        plt.ylabel("Proportion")
        plt.title("First Digit Distribution (n={})".format(self.n))
        plt.xticks(DIGITS)
        plt.legend()
        plt.show()
