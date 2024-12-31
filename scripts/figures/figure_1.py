"""
Figure 1: Fungal electrophysiology 

A. Experimental set-up image
B. Voltage time-series (for all channels across all time)
C. Example data snippet
D. Example power spectra
E. Example autocorrelation function
"""

# imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from timescales.fit import ACF

import sys
sys.path.append("code")
from utils import shift_signals
from plots import plot_spectra, beautify_ax

# settings
FS = 1/0.06 # Sampling frequency (Hz)
EXAMPLE_IDX = 0 # Channel to plot in C
EPOCH = [900, 1200] # Time to plot in C
NPERSEG = 2**12 # Spectral decomposition: samples per segment


def main():
    # LOAD DATA ################################################################
    print("Importing data...")

    # load signals
    data_in = np.load(f"data/manuscript/signals_fungal.npz")
    signals = data_in['signals']
    time = data_in['time']

    # load example spectra
    data_in = np.load(f"data/manuscript/spectra_fungal.npz")
    spectra = data_in['spectra']
    freqs = data_in['freqs']

    # ANALYSIS #################################################################
    print("Running analysis...")

    # fit autocorrelation function
    nlags = int(0.5 * signals.shape[1])
    acf = ACF()
    acf.compute_acf(signals[EXAMPLE_IDX], FS, nlags=nlags)
    acf.fit()

    # PLOT #####################################################################

    # create figure and gridspec
    print("Plotting...")
    fig = plt.figure(figsize=[8, 9], constrained_layout=True)
    spec = gridspec.GridSpec(figure=fig, ncols=2, nrows=3, 
                             width_ratios=[1, 1], height_ratios=[1, 1, 1])
    ax_c = fig.add_subplot(spec[1,:])
    ax_d = fig.add_subplot(spec[2,0])
    ax_e = fig.add_subplot(spec[2,1])

    spec_ab = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=spec[0,:],
                                               width_ratios=[0.45, 1])
    ax_a = fig.add_subplot(spec_ab[0])
    ax_b = fig.add_subplot(spec_ab[1])

    # plot subplot a
    ax_a.imshow(plt.imread("data/manuscript/figure_1_cartoon.png"))
    ax_a.set_axis_off()
    ax_a.set_title('Experimantal set-up')

    # plot subplot b
    signals_shifted = shift_signals(signals, std=5)
    ax_b.plot(time, signals_shifted.T, color='k', linewidth=0.5)
    ax_b.set(xlabel='Time (s)', ylabel='Recording electrode')
    ax_b.legend().set_visible(False)
    ax_b.set_yticks([])
    ax_b.set_title('Voltage time-series')

    # plot subplot c
    t_mask = (time > EPOCH[0]) & (time < EPOCH[1])    
    ax_c.plot(time[t_mask], signals[EXAMPLE_IDX, t_mask], color='k')
    ax_c.set(xlabel='Time (s)', ylabel='Voltage (uV)')
    ax_c.set_title('Example recording')

    # plot subplot d
    plot_spectra(spectra, freqs, ax=ax_d, color='k')
    ax_d.set_title('Power spectral density')

    # plot subplot d
    lags = acf.lags / FS
    ax_e.plot(lags, acf.corrs, color='k')
    ax_e.set(xlabel='Lag (s)', ylabel='Autocorrelation')
    ax_e.set_title('Autocorrelation function')

    # beautify
    for ax in [ax_a, ax_b, ax_c, ax_d]:
        beautify_ax(ax)

    # save figure
    fig.savefig("figures/manuscript/figure_1.png")


if __name__ == "__main__":
    main()
