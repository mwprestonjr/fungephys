"""
Utility functions.
"""

import numpy as np


def zscore(x):
    """
    Calculate z-scores of a 1D array
    
    Parameters
    ----------
    x : np.array
        1D or 2D array to calculate z-scores for
    
    Returns
    -------
    np.array
        z-scores of x
    """

    if x.ndim == 1:
        zscore = (x - np.mean(x)) / np.std(x)
    elif x.ndim == 2:
        zscore = (x - np.mean(x, axis=0)) / np.std(x, axis=0)
    else:
        raise ValueError("x must be a 1D or 2D array")

    return zscore


def subtract_mean(x):
    """
    Subtract the mean of a 1D array
    
    Parameters
    ----------
    x : np.array
        1D array to subtract the mean from
    
    Returns
    -------
    np.array
        x with the mean subtracted
    """

    return x - np.mean(x)


def shift_signals(signals, std=5):
    """
    Shift signals for visualization.

    Parameters
    ----------
    signals : np.array
        2D array of signals to shift
    std : float, optional
        Standard deviation of the shift, by default 5
    
    Returns
    -------
    np.array
        Shifted signals
    """

    shift = std * np.mean(np.std(signals, axis=1))
    for ii in range(1, len(signals)):
        signals[ii] = signals[ii] + (shift * ii)

    return signals
