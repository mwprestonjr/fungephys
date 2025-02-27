"""
This script records data from a PicoLog ADC24 data logger using the PicoHRDL
library. The script is written to record data from a single channel in chunks of
300 samples, saving each chunk to a text file. The script is written to
record data in the differential set-up.

Adaptred from: Mishra et al. 2024, doi: 10.5281/zenodo.12810869
Originally adapted from: PicoTech, https://github.com/picotech/picosdk-python-wrappers/blob/master/picohrdlExamples/picohrdlSingleModeExample.py

"""

# SETTINGS #####################################################################
DIR_OUT = "20250127_control" # Output folder within data/recordings
DT = 100 # Sampling frequency in milliseconds
CHANNEL = 3 # Channel to record from - script written for differential recording so this is the odd-numbered channel
DURATION = 60 * 10 # Duration of recording in seconds
N_SAMPLES_CHUNK = 300 # Number of samples to record before saving to file
VMAX = 39000  # Maximum voltage in microvolts (Mishra et al. 2024 used 39000)
VOLTAGE_RANGE = 39 # Voltage range in millivolts (see function voltage_key below for options)

fs = int(1000 / DT)
n_samples = int(DURATION *fs)
n_chunks = int(n_samples / N_SAMPLES_CHUNK)

# Print settings
print("\nRecording settings:")
print(f"  Recording from channel {CHANNEL} in differential mode")
print(f"  Voltage range: {VOLTAGE_RANGE} mV")
print(f"  Sampling frequency: {fs} Hz ({DT} ms intervals)")
print(f"  Total recording time: {DURATION} seconds")
print(f"  Saving to data/recordings/{DIR_OUT}")
print(f"  Saving {N_SAMPLES_CHUNK} samples per file ({n_chunks} files total)")

# SET-UP #######################################################################
print("\nSetting up data logger...")

# imports
import ctypes
import numpy as np
from picosdk.picohrdl import picohrdl as hrdl
from picosdk.functions import assert_pico2000_ok
import time

# create function that maps these valtages to the corresponding values
def voltage_key(s):
    return {
        39: 6,
        78: 5,
        156: 4,
        313: 3,
        625: 2,
        1250: 1,
        2500: 0
    }[s]

# SET-UP DATA LOGGER ###########################################################
# print("\nSetting up data logger...")

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open unit
status["openUnit"] = hrdl.HRDLOpenUnit()
assert_pico2000_ok(status["openUnit"])
chandle = status["openUnit"]

# Set mains noise rejection to reject 50 Hz mains noise
status["mainsRejection"] = hrdl.HRDLSetMains(chandle, 0)
assert_pico2000_ok(status["mainsRejection"])

# Disable corresponding even-numbered channel to enable differential recording
status["disableDifferentialChannel"] = \
    hrdl.HRDLSetAnalogInChannel(chandle, CHANNEL+1, 0, 
                                voltage_key(VOLTAGE_RANGE), 0)
status["disableDifferentialChannel"] = \
    hrdl.HRDLSetAnalogInChannel(chandle, CHANNEL, 1, 
                                voltage_key(VOLTAGE_RANGE), 0)

# Compute voltage scaling ######################################################
# print("\nComputing voltage scaling...")

# Set single reading parameters
range_ = hrdl.HRDL_VOLTAGERANGE[f"HRDL_{VOLTAGE_RANGE}_MV"]
conversionTime = hrdl.HRDL_CONVERSIONTIME[f"HRDL_{DT}MS"]
overflow = ctypes.c_int16(0)
value = ctypes.c_int32()

# Get the minimum and maximum ADC values for scaling
max_value = ctypes.c_int32()
min_value = ctypes.c_int32()
hrdl.HRDLGetMinMaxAdcCounts(chandle, ctypes.byref(min_value), 
                            ctypes.byref(max_value), CHANNEL)
print("  Max ADC Value:", max_value.value)
print("  Min ADC Value:", min_value.value)

# Calculate voltage from ADC value
raw_ADC_value = value.value
max_ADC_Value = max_value.value
V = (raw_ADC_value / max_ADC_Value) * VMAX
print("  Voltage:", V)

# RECORD DATA ##################################################################
# Initialize data saving parameters
save_data = []
start_time = time.time()
count = 0

# Collect and save data in chunks of 300 samples
print("\nRecording data...")
for i in range(n_samples):
    status["getSingleValue"] = hrdl.HRDLGetSingleValue(
        chandle, CHANNEL, range_, conversionTime, 0, ctypes.byref(overflow), 
        ctypes.byref(value)
    )
    value_data = value.value
    V = (float(value_data) / float(max_ADC_Value)) * float(VMAX)
    save_data.append(V)
    
    if len(save_data) == N_SAMPLES_CHUNK:
        np.savetxt(f"data/recordings/{DIR_OUT}/{count}.txt", save_data, 
                   delimiter=',')
        print(f"  Saved chunk {count+1}/{n_chunks}")
        count += 1
        save_data = []

# Print the elapsed time
print(f"--- {time.time() - start_time} seconds ---")
print("\nRecording complete")

# Close unit
status["closeUnit"] = hrdl.HRDLCloseUnit(chandle)
assert_pico2000_ok(status["closeUnit"])

# Print final status
print("\nStatus:", status)
