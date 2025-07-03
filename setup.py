from setuptools import setup, find_packages

setup(
    name='benford-midi',
    version='0.1.0',
    author='Alex Price',
    author_email='ajprice@mail.wlu.edu',
    description='A package for analyzing MIDI files for compliance with Benford\'s Law',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ajprice16/benford-midi-analysis',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'mido',
        'tqdm',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'console_scripts': [
            'benford-midi=benford_midi.cli:main',
        ],
    },
)