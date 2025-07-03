"""
Benford MIDI Analysis Package

A Python package for analyzing MIDI files using Benford's Law.

This package provides comprehensive tools for:
- Parsing MIDI files and extracting numerical features
- Applying various statistical tests for Benford's Law compliance
- Classifying compliance levels with sophisticated scoring
- Comparing multiple directories of MIDI files
- Generating publication-ready visualizations
- Exporting results in CSV format

Example usage:
    >>> from benford_midi import analyze_single_directory, BenfordTests
    >>> results = analyze_single_directory("path/to/midi/files")
    >>> 
    >>> # Or for detailed analysis of specific data
    >>> tests = BenfordTests([123, 456, 789, 234, 567])
    >>> chi2_stat, p_value = tests.pearson_chi2()
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
    perform_statistical_comparison
)

# Import utility functions
from .utils import (
    format_p,
    get_first_digit,
    get_significand,
    benford_first_digit_prob,
    generate_benford_sample,
    z_transform,
    get_props
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A Python package for analyzing MIDI files using Benford's Law"
__url__ = "https://github.com/yourusername/benford-midi-analysis"
__license__ = "MIT"

# Define what gets imported with "from benford_midi import *"
__all__ = [
    # Main analysis functions
    'analyze_single_directory',
    'compare_directories',
    'BenfordTests',
    'classify_benford_compliance',
    
    # MIDI parsing functions
    'parse_midi',
    'parse_midi_extended',
    'analyze_midi_features',
    
    # Processing and visualization functions
    'process_midi_file',
    'print_analysis_summary',
    'analyze_comparison_results',
    'create_single_directory_plots',
    'create_comparison_plots',
    'perform_statistical_comparison',
    
    # Utility functions
    'format_p',
    'get_first_digit',
    'get_significand',
    'benford_first_digit_prob',
    'generate_benford_sample',
    'z_transform',
    'get_props',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    '__url__',
    '__license__'
]

# Convenience imports for common workflows
def quick_analyze(midi_directory, output_dir=None, create_plots=True):
    """
    Quick analysis wrapper for single directory analysis.
    
    Args:
        midi_directory (str or Path): Directory containing MIDI files
        output_dir (str or Path, optional): Output directory for results
        create_plots (bool): Whether to generate visualization plots
        
    Returns:
        pandas.DataFrame: Analysis results
        
    Example:
        >>> results = quick_analyze("my_midi_files/")
        >>> print(f"Analyzed {len(results)} files")
    """
    return analyze_single_directory(midi_directory, output_dir, create_plots)

def quick_compare(dir1, dir2, output_dir=None, create_plots=True):
    """
    Quick comparison wrapper for two directories.
    
    Args:
        dir1 (str or Path): First directory of MIDI files
        dir2 (str or Path): Second directory of MIDI files
        output_dir (str or Path, optional): Output directory for results
        create_plots (bool): Whether to generate visualization plots
        
    Returns:
        tuple: (results_dir1, results_dir2, combined_dataframe)
        
    Example:
        >>> r1, r2, combined = quick_compare("classical/", "jazz/")
        >>> print(f"Classical: {len(r1)} files, Jazz: {len(r2)} files")
    """
    return compare_directories(dir1, dir2, output_dir, create_plots)

# Add convenience functions to __all__
__all__.extend(['quick_analyze', 'quick_compare'])

# Version checking utilities
def check_dependencies():
    """
    Check if all required dependencies are available and their versions.
    
    Returns:
        dict: Dictionary of package names and their versions
    """
    import sys
    dependencies = {}
    
    try:
        import numpy as np
        dependencies['numpy'] = np.__version__
    except ImportError:
        dependencies['numpy'] = 'NOT INSTALLED'
    
    try:
        import pandas as pd
        dependencies['pandas'] = pd.__version__
    except ImportError:
        dependencies['pandas'] = 'NOT INSTALLED'
    
    try:
        import matplotlib
        dependencies['matplotlib'] = matplotlib.__version__
    except ImportError:
        dependencies['matplotlib'] = 'NOT INSTALLED'
    
    try:
        import scipy
        dependencies['scipy'] = scipy.__version__
    except ImportError:
        dependencies['scipy'] = 'NOT INSTALLED'
    
    try:
        import mido
        dependencies['mido'] = mido.__version__
    except ImportError:
        dependencies['mido'] = 'NOT INSTALLED'
    
    try:
        import tqdm
        dependencies['tqdm'] = tqdm.__version__
    except ImportError:
        dependencies['tqdm'] = 'NOT INSTALLED'
    
    dependencies['python'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return dependencies

def print_package_info():
    """Print package information and dependency status."""
    print(f"Benford MIDI Analysis Package v{__version__}")
    print(f"Author: {__author__}")
    print(f"Description: {__description__}")
    print("\nDependency Status:")
    print("-" * 40)
    
    deps = check_dependencies()
    for package, version in deps.items():
        status = "✓" if version != 'NOT INSTALLED' else "✗"
        print(f"{status} {package}: {version}")

# Add utility functions to __all__
__all__.extend(['check_dependencies', 'print_package_info'])

# Module-level constants that users might need
BENFORD_PROBABILITIES = [benford_first_digit_prob(d) for d in range(1, 10)]
FIRST_DIGITS = list(range(1, 10))

__all__.extend(['BENFORD_PROBABILITIES', 'FIRST_DIGITS'])

# Initialize logging (optional)
import logging

# Create a logger for the package
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # Prevent logging unless configured by user

def setup_logging(level=logging.INFO, format_string=None):
    """
    Setup logging for the package.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(level=level, format=format_string)
    logger.setLevel(level)

__all__.append('setup_logging')