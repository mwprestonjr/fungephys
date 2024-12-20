"""
Analysis functions.
"""

import numpy as np
from specparam import SpectralGroupModel

import sys
sys.path.append("code")
from settings import SPECPARAM_SETTINGS, N_JOBS


def compute_exponent(spectra, freqs, ap_mode='knee', freq_range=None):

    # fit power spectra
    sgm = SpectralGroupModel(**SPECPARAM_SETTINGS, aperiodic_mode=ap_mode, 
                             verbose=False)
    sgm.fit(freqs, spectra, n_jobs=N_JOBS, freq_range=freq_range)
    exponent = sgm.get_params('aperiodic', 'exponent')

    return exponent


def compute_complexity(signals):
    """Compute the Lempel-Ziv complexity of a set of binary signals"""

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

