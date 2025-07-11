from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text()
except FileNotFoundError:
    long_description = (
        "A package for analyzing MIDI files for compliance with Benford's Law"
    )

setup(
    name="benford-midi",
    version="1.0.0",
    author="Alex Price",
    author_email="ajprice@mail.wlu.edu",
    description="A package for analyzing MIDI files for compliance with Benford's Law",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajprice16/benford-midi-analysis",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "mido>=1.2.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "benford-midi=benford_midi.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
