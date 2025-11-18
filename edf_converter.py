"""
EDF Reader and Converter
Provides functionality to read EDF (European Data Format) files and convert them
to various formats including CSV, JSON, and NumPy arrays.
"""

import mne
import numpy as np
import json
import csv
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union


class EDFConverter:
    """
    A class for reading and converting EDF files to various formats.

    Attributes:
        filepath (str): Path to the EDF file
        raw (mne.io.Raw): MNE Raw object containing the loaded data
    """

    def __init__(self, filepath: str):
        """
        Initialize the EDFConverter with an EDF file.

        Args:
            filepath (str): Path to the EDF file to read

        Raises:
            FileNotFoundError: If the EDF file doesn't exist
            ValueError: If the file cannot be read as EDF
        """
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"EDF file not found: {filepath}")

        try:
            self.raw = mne.io.read_raw_edf(str(self.filepath), preload=True, verbose=False)
        except Exception as e:
            raise ValueError(f"Failed to read EDF file: {e}")

    def get_info(self) -> Dict:
        """
        Get metadata and information about the EDF file.

        Returns:
            Dict: Dictionary containing channel names, sampling rates, duration, etc.
        """
        info = {
            'filename': self.filepath.name,
            'n_channels': len(self.raw.ch_names),
            'channel_names': self.raw.ch_names,
            'sampling_rate': self.raw.info['sfreq'],
            'duration_seconds': self.raw.times[-1],
            'n_samples': len(self.raw.times),
            'measurement_date': str(self.raw.info['meas_date']) if self.raw.info['meas_date'] else None,
        }
        return info

    def get_data(self, channels: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the raw signal data and time points.

        Args:
            channels (Optional[List[str]]): List of channel names to extract.
                                           If None, returns all channels.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (data, times) where data is shape (n_channels, n_samples)
        """
        if channels:
            picks = mne.pick_channels(self.raw.ch_names, channels)
            data = self.raw.get_data(picks=picks)
        else:
            data = self.raw.get_data()

        times = self.raw.times
        return data, times

    def to_csv(self, output_path: str, channels: Optional[List[str]] = None,
               include_time: bool = True) -> None:
        """
        Export EDF data to CSV format.

        Args:
            output_path (str): Path for the output CSV file
            channels (Optional[List[str]]): Specific channels to export (None = all)
            include_time (bool): Whether to include a time column
        """
        data, times = self.get_data(channels)

        # Get channel names
        if channels:
            ch_names = channels
        else:
            ch_names = self.raw.ch_names

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            header = ['Time'] if include_time else []
            header.extend(ch_names)
            writer.writerow(header)

            # Write data
            for i in range(len(times)):
                row = [times[i]] if include_time else []
                row.extend(data[:, i])
                writer.writerow(row)

        print(f"CSV file saved to: {output_path}")

    def to_json(self, output_path: str, channels: Optional[List[str]] = None,
                include_metadata: bool = True) -> None:
        """
        Export EDF data to JSON format.

        Args:
            output_path (str): Path for the output JSON file
            channels (Optional[List[str]]): Specific channels to export (None = all)
            include_metadata (bool): Whether to include metadata in the output
        """
        data, times = self.get_data(channels)

        # Get channel names
        if channels:
            ch_names = channels
        else:
            ch_names = self.raw.ch_names

        # Build JSON structure
        output = {}

        if include_metadata:
            output['metadata'] = self.get_info()

        # Convert data to list format for JSON serialization
        output['data'] = {
            'times': times.tolist(),
            'channels': {}
        }

        for i, ch_name in enumerate(ch_names):
            output['data']['channels'][ch_name] = data[i, :].tolist()

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"JSON file saved to: {output_path}")

    def to_numpy(self, output_path: str, channels: Optional[List[str]] = None) -> None:
        """
        Export EDF data to NumPy .npz format.

        Args:
            output_path (str): Path for the output .npz file
            channels (Optional[List[str]]): Specific channels to export (None = all)
        """
        data, times = self.get_data(channels)

        # Get channel names
        if channels:
            ch_names = channels
        else:
            ch_names = self.raw.ch_names

        # Save as compressed numpy archive
        np.savez_compressed(
            output_path,
            data=data,
            times=times,
            channel_names=ch_names,
            sampling_rate=self.raw.info['sfreq']
        )

        print(f"NumPy file saved to: {output_path}")

    def plot(self, duration: float = 10.0, n_channels: int = 20,
             start: float = 0.0) -> None:
        """
        Plot the EDF signals using MNE's interactive viewer.

        Args:
            duration (float): Duration of data to display in seconds
            n_channels (int): Number of channels to display at once
            start (float): Start time in seconds
        """
        self.raw.plot(duration=duration, n_channels=n_channels, start=start)

    def get_channel_data(self, channel_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get data for a specific channel.

        Args:
            channel_name (str): Name of the channel to extract

        Returns:
            Tuple[np.ndarray, np.ndarray]: (channel_data, times)

        Raises:
            ValueError: If channel name is not found
        """
        if channel_name not in self.raw.ch_names:
            raise ValueError(f"Channel '{channel_name}' not found. Available channels: {self.raw.ch_names}")

        data, times = self.get_data(channels=[channel_name])
        return data[0], times


def main():
    """Example usage of the EDFConverter class."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python edf_converter.py <input_edf_file> [output_format]")
        print("Formats: csv, json, numpy, info")
        print("Example: python edf_converter.py example.edf csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_format = sys.argv[2].lower() if len(sys.argv) > 2 else 'info'

    try:
        converter = EDFConverter(input_file)

        if output_format == 'info':
            print("\nEDF File Information:")
            print("-" * 50)
            info = converter.get_info()
            for key, value in info.items():
                print(f"{key}: {value}")

        elif output_format == 'csv':
            output_file = Path(input_file).stem + '.csv'
            converter.to_csv(output_file)

        elif output_format == 'json':
            output_file = Path(input_file).stem + '.json'
            converter.to_json(output_file)

        elif output_format == 'numpy' or output_format == 'npz':
            output_file = Path(input_file).stem + '.npz'
            converter.to_numpy(output_file)

        else:
            print(f"Unknown format: {output_format}")
            print("Available formats: csv, json, numpy, info")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
