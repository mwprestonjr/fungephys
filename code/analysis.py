"""
Analysis functions:
- compute_timescale: compute the timescale of a set of signals
- compute_exponent: compute the exponent of a set of power spectra
- compute_complexity: compute the Lempel-Ziv complexity of a set of signals
- lempel_ziv_complexity: calculate the Lempel-Ziv complexity of a binary array
"""

import numpy as np
from specparam import SpectralGroupModel
from timescales.fit import ACF

import sys
sys.path.append("code")
from settings import SPECPARAM_SETTINGS, N_JOBS


def compute_timescale(signals, fs, nlags=None):
    """Compute the timescale of a set of signals"""

    if nlags is None:
        nlags = int(0.5 * signals.shape[1])
        
    acf = ACF()
    acf.compute_acf(signals, fs, nlags=nlags)
    acf.fit()
    timescale = acf.params[:, 0]

    return timescale


def compute_exponent(spectra, freqs, ap_mode='knee', freq_range=None):

    # fit power spectra
    sgm = SpectralGroupModel(**SPECPARAM_SETTINGS, aperiodic_mode=ap_mode, 
                             verbose=False)
    sgm.fit(freqs, spectra, n_jobs=N_JOBS, freq_range=freq_range)
    exponent = sgm.get_params('aperiodic', 'exponent')

    return exponent


def compute_complexity(signals):
    """Binaraize signals and compute the Lempel-Ziv complexity"""

    complexity = np.zeros(len(signals))
    for ii in range(len(signals)):
        # remove mean
        signal = signals[ii] - np.mean(signals[ii])

        # binarize signals
        signal = np.array(signal > 0, dtype=int)

        # compute complexity
        complexity[ii] = lempel_ziv_complexity(signal)

    return complexity


def lempel_ziv_complexity(binary_array):
    """
    Calculate the Lempel-Ziv complexity of a binary array of integers.

    Parameters:
        binary_array (list or array-like): A list of binary integers (0s and 1s).

    Returns:
        int: The Lempel-Ziv complexity of the binary array.
    """

    sub_strings = set()
    w = []
    for c in binary_array:
        wc = w + [c]
        if tuple(wc) not in sub_strings:  # Use tuple for immutability
            sub_strings.add(tuple(wc))
            w = []
        else:
            w = wc
    return len(sub_strings)
