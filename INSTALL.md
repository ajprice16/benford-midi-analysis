# Installation and Troubleshooting Guide

## Installation

### Standard Installation

The easiest way to install the benford-midi package:

```bash
pip install benford-midi
```

### Development Installation

To install from source for development:

```bash
git clone https://github.com/ajprice16/benford-midi-analysis.git
cd benford-midi-analysis
pip install -e .
```

### Virtual Environment (Recommended)

To avoid conflicts with other packages:

```bash
python -m venv benford_env
source benford_env/bin/activate  # On Windows: benford_env\Scripts\activate
pip install benford-midi
```

## Verification

After installation, verify everything works:

```bash
# Test basic import
python -c "import benford_midi; print('Success! Version:', benford_midi.__version__)"

# Test CLI
benford-midi --help

# Run comprehensive tests (if installed from source)
python test_package.py
```

## Requirements

- Python 3.7 or higher
- numpy>=1.20.0
- pandas>=1.3.0
- matplotlib>=3.5.0
- scipy>=1.7.0
- mido>=1.2.0
- tqdm>=4.60.0

## Troubleshooting Common Installation Issues

### 1. ModuleNotFoundError: No module named 'benford_midi'

**Cause**: Package not installed in current Python environment

**Solution**:
```bash
# Check if package is installed
pip list | grep benford

# If not installed, install it
pip install benford-midi

# If using virtual environment, make sure it's activated
source your_venv/bin/activate  # Linux/Mac
your_venv\Scripts\activate     # Windows
```

### 2. Permission Denied or externally-managed-environment

**Cause**: System Python protection (common on newer systems)

**Solution**:
```bash
# Use virtual environment (recommended)
python -m venv benford_env
source benford_env/bin/activate
pip install benford-midi

# Or use --user flag (not recommended)
pip install --user benford-midi
```

### 3. Dependency Conflicts

**Cause**: Conflicting package versions

**Solution**:
```bash
# Create fresh environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install benford-midi

# Or update existing packages
pip install --upgrade numpy pandas matplotlib scipy mido tqdm
```

### 4. CLI Command Not Found

**Cause**: Entry point not in PATH or virtual environment not activated

**Solution**:
```bash
# Make sure virtual environment is activated
source your_venv/bin/activate

# Or use module execution
python -m benford_midi.cli --help

# Check if entry point is installed
pip show benford-midi
```

### 5. ImportError: Failed to import required modules

**Cause**: Missing system dependencies or corrupted installation

**Solution**:
```bash
# Reinstall package
pip uninstall benford-midi
pip install benford-midi

# Check system dependencies (especially for matplotlib)
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On macOS with Homebrew:
brew install python-tk
```

### 6. matplotlib or plotting issues

**Cause**: Missing GUI backend for matplotlib

**Solution**:
```bash
# Install GUI backend
pip install PyQt5

# Or use non-interactive backend in scripts
import matplotlib
matplotlib.use('Agg')  # Add before importing pyplot
```

## Platform-Specific Notes

### Windows
- Use `py` instead of `python` if you have multiple Python versions
- Activate virtual environment with `Scripts\activate.bat`

### macOS
- May need to install Command Line Tools: `xcode-select --install`
- Use `python3` explicitly if needed

### Linux
- May need to install `python3-venv` and `python3-dev` packages
- Some distributions require separate `python3-pip` package

## Testing Your Installation

Run the built-in test suite to verify everything works:

```bash
# Download test script if installed via pip
curl -O https://raw.githubusercontent.com/ajprice16/benford-midi-analysis/main/test_package.py

# Run tests
python test_package.py
```

Expected output:
```
BENFORD MIDI PACKAGE TEST SUITE
==================================================
✓ All basic functionality tests passed!
✓ Package structure verified
✓ CLI working correctly
==================================================
RESULTS: 3/3 tests passed
🎉 ALL TESTS PASSED!
```

## Getting Help

If you're still having issues:

1. Check the [GitHub Issues](https://github.com/ajprice16/benford-midi-analysis/issues)
2. Create a new issue with:
   - Your operating system and Python version
   - Full error message
   - Installation method used
   - Output of `pip list | grep -E "(benford|numpy|pandas|matplotlib|scipy|mido|tqdm)"`
