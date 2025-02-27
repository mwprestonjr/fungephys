"""
Spectral analysis functions.
"""

# imports
import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt


def compute_spectra(data, fs, nperseg=2**12):
    """Compute power spectra using Welch's method.

    Parameters
    ----------
    data : np.array
        2D array of shape (n_channels, n_samples)
    fs : float
        Sampling frequency in Hz
    nperseg : int
        Length of each segment for Welch's method

    Returns
    -------
    spectra : list of np.array
        List of power spectra for each channel
    freq : np.array
        Frequencies corresponding to the power spectra
    """
    if data.ndim == 1:
        freqs, spectra = welch(data, fs=fs, nperseg=nperseg)

    elif data.ndim == 2:
        # init
        freqs, _ = welch(data[0], fs=fs, nperseg=nperseg)
        spectra = np.zeros((data.shape[0], len(freqs)))

        # compute spectra
        for i_chan in range(data.shape[0]):
            _, spectra[i_chan] = welch(data[i_chan], fs=fs, nperseg=nperseg)

    return freqs, spectra


def plot_spectra(freqs, spectra, shade_sem=True, ax=None, color='k',
                 title=None, fname=None):

    # create figure
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 6))
    ax.set(ylabel='power (mV^2/Hz)', xlabel='frequency (Hz)')

    # plot spectra
    if shade_sem:
        spectra_mean = np.mean(spectra, axis=0)
        spectra_sem = np.std(spectra, axis=0) / np.sqrt(spectra.shape[0])
        ax.fill_between(freqs, spectra_mean-spectra_sem, 
                        spectra_mean+spectra_sem, color=color, alpha=0.5)
        ax.loglog(freqs, spectra_mean, color=color, lw=2)

    else:
        ax.loglog(freqs, spectra.T, color=color, alpha=0.5)

    # add title
    if not title is None:
        ax.set_title(title)
    
    # save figure
    if not fname is None:
        plt.savefig(fname)
