"""
This script records data from a PicoLog ADC24 data logger using the PicoHRDL
library. The script is written to record data in the differential set-up.

Adaptred from: Mishra et al. 2024, doi: 10.5281/zenodo.12810869
Originally adapted from: PicoTech, https://github.com/picotech/picosdk-python-wrappers/blob/master/picohrdlExamples/picohrdlSingleModeExample.py

"""

# SETTINGS #####################################################################
FNAME = "data/recordings/20250220_lightdark.txt" # Output filename
CHANNEL = 5 # channel to record - script written for differential recording; this is the odd-numbered channel
DT = 100 # in milliseconds (1/FS)
DURATION = 60 * 100 + 30 # duration of recording in seconds
VOLTAGE_RANGE = 39 # voltage range in millivolts (see function voltage_key below for options)
N_DROP = 300 # number of samples to drop from the beginning of the recording

# Compute sampling frequency and number of samples
fs = 1000 / DT
n_samples = int(DURATION * fs + N_DROP)

# Print settings
print("\nRecording settings:")
print(f"  Recording channels: \t{CHANNEL} and {CHANNEL+1} (differential mode)")
print(f"  Output filename: \t'{FNAME}'")
print(f"  Voltage range: \t{VOLTAGE_RANGE} mV")
print(f"  Sampling frequency: \t{fs:0.1f} Hz ({DT} ms intervals)")
print(f"  Recording duration: \t{DURATION} seconds")

# SET-UP #######################################################################
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
print("\nSetting up data logger...")

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
status["enableDifferentialChannel"] = \
    hrdl.HRDLSetAnalogInChannel(chandle, CHANNEL, 1, 
                                voltage_key(VOLTAGE_RANGE), 0)

# Compute voltage scaling ######################################################
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

# RECORD DATA ##################################################################
print("\nRecording data...")

# Initialize data saving parameters
reading = []
start_time = time.time()

# Collect data
for i in range(n_samples):
    hrdl.HRDLGetSingleValue(chandle, CHANNEL, range_, conversionTime, 0, 
                            ctypes.byref(overflow), ctypes.byref(value))
    reading.append(value.value)

# Print the elapsed time
print(f"  Complete in {time.time() - start_time:0.2f} seconds")

# Save the data
voltage = np.array(reading) * (VOLTAGE_RANGE * 1000 / max_value.value)
np.savetxt(FNAME, voltage[N_DROP:], delimiter=',')
print(f"  Saved data to '{FNAME}'")

# Close unit
status["closeUnit"] = hrdl.HRDLCloseUnit(chandle)
assert_pico2000_ok(status["closeUnit"])

# Print final status
print("\nStatus:", status)
print("\n--------- END ---------")
