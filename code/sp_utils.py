"""Utility functions for silicon probe recordings."""

# imports
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import os
import pandas as pd


def downsample(trace, original_fs, target_fs, apply_filter=True):
    """Downsample a trace from original_fs to target_fs using decimation.
    Optionally apply an anti-aliasing filter before downsampling.
    """

    # Check if the target_fs is less than the original_fs
    if apply_filter:
        # Apply Nyquist criterion
        nyq = target_fs / 2
        
        # Design anti-aliasing filter
        b, a = signal.butter(4, nyq, fs=original_fs, btype='low')
        
        # Apply anti-aliasing filter
        trace = signal.filtfilt(b, a, trace)
    
    # Calculate downsample factor
    down = int(original_fs / target_fs)
    
    # Downsample using decimation
    downsampled = signal.decimate(trace, down, ftype='fir')
    
    return downsampled


def process_channel(filename, fs=20000, target_fs=250, apply_filter=True):
    """Process a single channel file"""
    # Memory map the file
    data = np.memmap(filename, dtype=np.int16, mode='r', offset=0)
    
    # Downsample using the provided function
    downsampled_data = downsample(data, fs, target_fs, apply_filter)
    
    return downsampled_data


def process_all_channels(folder_path, fs=20000, target_fs=250, 
                         apply_filter=True):
    """Process all continuous files in the folder"""
    # Get all .continuous files in correct order
    continuous_files = sorted([f for f in os.listdir(folder_path) 
                             if f.startswith('100_CH') and f.endswith('.continuous')],
                            key=lambda x: int(x.split('CH')[1].split('.')[0]))
    
    print(f"  Found {len(continuous_files)} continuous files")
    
    # Initialize dictionary to store processed data
    processed_data = {}
    
    # Process each channel
    for file in continuous_files:
        try:
            # Extract channel name (e.g., 'CH1', 'CH2', etc.)
            channel_name = f"CH{file.split('CH')[1].split('.')[0]}"
            print(f"    Processing {channel_name}")
            
            full_path = os.path.join(folder_path, file)
            downsampled_data = process_channel(full_path, fs, target_fs, 
                                               apply_filter)
            
            # Store in dictionary
            processed_data[channel_name] = downsampled_data
            
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    # Create timestamps
    timestamps = np.arange(len(next(iter(processed_data.values())))) / target_fs
    processed_data['time'] = timestamps
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_data)
    
    return df
