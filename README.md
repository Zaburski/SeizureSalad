# SeizureSalad - EDF File Reader and Converter

A Python tool for reading, analyzing, and converting EEG/seizure data stored in EDF (European Data Format) files.

## Features

- Read EDF files with comprehensive metadata extraction
- Convert to multiple formats: CSV, JSON, NumPy
- Extract specific channels or all channels
- Interactive signal plotting
- Command-line interface for easy usage
- Python API for programmatic access

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install mne pyedflib numpy
```

## Quick Start

### Command-Line Interface

**Get file information:**
```bash
python edf_cli.py info your_file.edf
```

**Convert to CSV:**
```bash
python edf_cli.py convert your_file.edf --format csv
```

**Convert specific channels to JSON:**
```bash
python edf_cli.py convert your_file.edf --format json --channels EEG1 EEG2
```

**Plot signals:**
```bash
python edf_cli.py plot your_file.edf
```

### Python API

```python
from edf_converter import EDFConverter

# Load EDF file
converter = EDFConverter('your_file.edf')

# Get information
info = converter.get_info()
print(f"Duration: {info['duration_seconds']} seconds")
print(f"Channels: {info['channel_names']}")

# Extract data
data, times = converter.get_data()  # Get all channels
channel_data, times = converter.get_channel_data('EEG1')  # Get specific channel

# Convert to different formats
converter.to_csv('output.csv')
converter.to_json('output.json')
converter.to_numpy('output.npz')

# Plot signals
converter.plot()
```

## Examples

Run the example script to see all features:

```bash
python example_usage.py
```

## File Format Support

**Input:** EDF (European Data Format) files

**Output formats:**
- CSV - Comma-separated values with time column and channel data
- JSON - Structured JSON with metadata and channel data
- NumPy - Compressed .npz archive with data arrays and metadata

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed documentation on the codebase architecture and usage.

## Requirements

- Python 3.7+
- mne >= 1.0.0
- pyedflib >= 0.1.30
- numpy >= 1.20.0

## License

This project is provided as-is for educational and research purposes.
