"""
Analysis of Adamatzky 2021 data. These results primarily contribute to Figure 2.

"""

# imports
import os
import numpy as np
import pandas as pd
from neurodsp.spectral import compute_spectrum

import sys
sys.path.append("code")
from analysis import compute_exponent, compute_complexity, compute_timescale

# settings
DIR_INPUT = r"C:\Users\micha\datasets\adamatzky_2021\txt"

# dataset details
FS = 1 # Sampling frequency in Hz
N_CHANNELS = 7 # Number of recording channels
N_SPECIES = 4 # Number of species in the dataset


def main():
    # identify/create directories
    path_out = "./data/adamatzky_2021"
    for folder in ['psd', 'results']:
        if not os.path.exists(f"{path_out}/{folder}"): 
            os.makedirs(f"{path_out}/{folder}")

    # init
    exponent = np.zeros([N_SPECIES, N_CHANNELS])
    complexity = np.zeros([N_SPECIES, N_CHANNELS])
    timescale = np.zeros([N_SPECIES, N_CHANNELS])

    # loop through each species
    for ii, fname in enumerate(os.listdir(DIR_INPUT)):
        # load data
        data_in = pd.read_csv(os.path.join(DIR_INPUT, fname), sep='\t')
        signals = epoch_data(data_in, N_CHANNELS)

        # compute spectra
        freqs, spectra = compute_spectrum(signals, FS, nperseg=2**12)
        fname_out = fname.replace('.txt', '.npz')
        np.savez(f"{path_out}/psd/{fname_out}", spectra=spectra, freqs=freqs)

        # compute spectral exponent and complexity
        exponent[ii] = compute_exponent(spectra, freqs)
        complexity[ii] = compute_complexity(signals)

        # compute timescale
        timescale[ii] = compute_timescale(signals, FS)

    # save results
    np.save("data/adamatzky_2021/results/exponent.npy", exponent)
    np.save("data/adamatzky_2021/results/complexity.npy", complexity)
    np.save("data/adamatzky_2021/results/timescale.npy", timescale)


def epoch_data(data, n_channels):
    """
    Custom funtion for Adamatzky 2021. 
    """
    # determine number of samples to use for analysis
    shortest_signal = 263959
    potential_artifact = 50000
    n_samples = shortest_signal - potential_artifact

    # epoch data (trim to desired number of samples)
    data = data[-n_samples:]

    # interpolate NaN values
    data = data.interpolate(method='linear', axis=0)

    # grab desired channels
    data = data.values[:, :n_channels].T

    return data


if __name__ == "__main__":
    main()
