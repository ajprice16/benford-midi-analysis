"""
Benford MIDI Analysis Package

A Python package for analyzing MIDI files using Benford's Law.
"""

# Import main analysis functions
from .analysis import (
    analyze_single_directory,
    compare_directories,
    BenfordTests,
    classify_benford_compliance,
    parse_midi,
    parse_midi_extended,
    analyze_midi_features,
    process_midi_file,
    print_analysis_summary,
    analyze_comparison_results,
    create_single_directory_plots,
    create_comparison_plots,
    perform_statistical_comparison,
)

# Import utility functions
from .utils import (
    format_p,
    get_first_digit,
    get_significand,
    benford_first_digit_prob,
    generate_benford_sample,
    z_transform,
    get_props,
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Alex Price"
__email__ = "ajprice@mail.wlu.edu"

# Define what gets imported with "from benford_midi import *"
__all__ = [
    "analyze_single_directory",
    "compare_directories",
    "BenfordTests",
    "classify_benford_compliance",
    "parse_midi",
    "parse_midi_extended",
    "analyze_midi_features",
    "process_midi_file",
    "print_analysis_summary",
    "analyze_comparison_results",
    "create_single_directory_plots",
    "create_comparison_plots",
    "perform_statistical_comparison",
    "format_p",
    "get_first_digit",
    "get_significand",
    "benford_first_digit_prob",
    "generate_benford_sample",
    "z_transform",
    "get_props",
]
