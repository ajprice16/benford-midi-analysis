# Benford MIDI Analysis

This project provides a Python package for analyzing MIDI files in accordance with Benford's Law. It includes functionalities for statistical analysis, compliance testing, and command-line interface usage.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install the package, clone the repository and install the required dependencies:

```bash
git clone https://github.com/ajprice16/benford-midi-analysis.git
cd benford-midi-analysis
pip install -r requirements.txt
```

Alternatively, you can install the package directly using pip:

```bash
pip install .
```

## Usage

You can use the package from the command line or import it into your Python scripts. The main functionalities include:

- Analyzing MIDI files for Benford's Law compliance.
- Comparing compliance between two sets of MIDI files.

For command-line usage, you can run:

```bash
python -m benford_midi.cli
```

## Examples

Check the `examples` directory for usage examples:

- `basic_usage.py`: A simple example demonstrating basic functionality.
- `comparison_example.py`: An example showcasing how to compare two sets of MIDI files.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.