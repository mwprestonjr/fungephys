"""
This script processes a silicon probe recording and saves the processed data in 
Parquet format.

Inputs:
- path_in: Path to the input data directory containing silicon probe recordings.
- path_out: Path to the output directory where processed data will be saved.
    Default output directory is 'data/silicon_probe/processed_data'.
- fs: Original sampling frequency of the data (default: 20000 Hz).
- target_fs: Desired sampling frequency after downsampling (default: 100 Hz).

Outputs:
- Processed data saved in Parquet format in the specified output directory.

Usage:
# required arguments only
python process_silicon_probe_recording.py --path_in <input_directory>

# with optional arguments
python process_silicon_probe_recording.py --path_in <input_directory> 
--path_out <output_directory> --fs <original_fs> --target_fs <target_fs>

"""

# imports
import os
import argparse

import sys
sys.path.append("code")
from sp_utils import process_all_channels


def main(path_in, path_out, fs, target_fs, apply_filter):
    # check for pyarrow or fastparquet dependency
    try:
        import pyarrow
    except ImportError:
        try:
            import fastparquet
        except ImportError:
            raise ImportError("Please install either 'pyarrow' or 'fastparquet' to save data in Parquet format.")

    # Create output directory
    os.makedirs(path_out, exist_ok=True)
    
    # Process data
    print("Processing all channels...")
    df = process_all_channels(path_in, fs, target_fs, apply_filter)

    # Save results
    output_filename = f"{path_out}/{os.path.basename(path_in)}.parquet"
    print(f"\nSaving data to {output_filename}...")
    df.to_parquet(output_filename)
    print("Done!")

    # Print some information about the saved data
    print("\nDataset information:")
    print(f"  Number of channels: {len(df.columns) - 1}")  # -1 for time column
    print(f"  Duration: {df['time'].max():.2f} seconds")
    print(f"  Original sampling rate: {fs} Hz")
    print(f"  Sampling rate after downsampling: {target_fs} Hz")

    print("\nTo load this data later, use:")
    print("import pandas as pd")
    print(f"df = pd.read_parquet('{output_filename}')")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process electrophysiological data and save as Parquet.")
    parser.add_argument("--path_in", type=str, 
                        help="Path to the input data directory.")
    parser.add_argument("--path_out", type=str, 
                        default="data/silicon_probe/processed_data",
                        help="Path to the output directory (default: data/silicon_probe/processed_data).")
    parser.add_argument("--fs", type=int, default=20000,
                        help="Original sampling frequency (default: 20000 Hz).")
    parser.add_argument("--target_fs", type=int, default=100,
                        help="Desired sampling frequency after downsampling (default: 100 Hz).")
    parser.add_argument("--apply_filter", type=bool, default=True,
                        help="Whether to apply an anti-aliasing filter during downsampling (default: True).")
    
    args = parser.parse_args()
    
    main(args.path_in, args.path_out, args.fs, args.target_fs, args.apply_filter)
