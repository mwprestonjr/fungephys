"""
Figure 2: 1/f-like power spectra

A. Power spectra (with exponential fit)
B. Histogram of exponent
C. Violin of exponent compared to Adamatzky 2021
D. Autocorrelation function (with exponential fit)
E. Histogram of timescale
F. Violin of timescale compared to Adamatzky 2021
"""

# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from specparam import SpectralGroupModel
from timescales.fit import ACF

import sys
sys.path.append("code")
from analysis import compute_exponent, compute_timescale
from info import N_CHANNELS
from plots import beautify_ax

# settings
EXAMPLE_IDX = 0 # Index of spectra to plot
FS = 1/0.06 # Sampling frequency (Hz)


def main():
    # LOAD DATA ################################################################
    print("Importing data...")

    # load signals
    data_in = np.load(f"data/manuscript/signals_fungal.npz")
    signals = data_in['signals']

    # load example spectra
    data_in = np.load("data/manuscript/spectra_fungal.npz")
    spectra = data_in['spectra']
    freqs = data_in['freqs']

    # load Adamatsky 2021 complexity measures
    aa2021_exponent = np.load("data/adamatzky_2021/results/exponent.npy")
    aa2021_timescale = np.load("data/adamatzky_2021/results/timescale.npy")
    genera = ['cordyceps', 'flammulina', 'omphalotus','schizophyllum']
    df = pd.DataFrame({'species': np.repeat(genera, N_CHANNELS),
                    'exponent': aa2021_exponent.flatten(),
                    'timescale': aa2021_timescale.flatten()})
    
    # ANALYSIS #################################################################
    print("Running analysis...")

    # fit power spectra
    sgm = SpectralGroupModel(aperiodic_mode='knee')
    sgm.fit(freqs, spectra)
    sm = sgm.get_model(EXAMPLE_IDX)
    exponent = sgm.get_params('aperiodic', 'exponent')

    # measure and correlate exponent and complexity
    exponent = compute_exponent(spectra, freqs)
    # timescale = compute_timescale(signals, FS)

    # fit autocorrelation function
    nlags = int(0.5 * signals.shape[1])
    acf = ACF()
    acf.compute_acf(signals[EXAMPLE_IDX], FS, nlags=nlags)
    acf.fit()
    timescales = acf.params[0]

    #  TEMP
    exponent_distr = np.random.normal(np.mean(exponent), np.std(exponent), 100)
    # timescale_distr = np.random.normal(np.mean(timescale), np.std(timescale), 100)
    timescale_distr = np.random.normal(timescales, timescales, 100)

    # PLOT #####################################################################
    print("Plotting...")
    
    # create figure and gridspec
    fig = plt.figure(figsize=[12, 6], constrained_layout=True)
    spec = gridspec.GridSpec(figure=fig, ncols=3, nrows=2, 
                             width_ratios=[1,1,1])
    ax_a = fig.add_subplot(spec[0,0])
    ax_b = fig.add_subplot(spec[0,1])
    ax_c = fig.add_subplot(spec[0,2])
    ax_d = fig.add_subplot(spec[1,0])
    ax_e = fig.add_subplot(spec[1,1])
    ax_f = fig.add_subplot(spec[1,2])

    # plot subplot a
    ax_a.plot(sm.freqs, sm.power_spectrum, linewidth=2, color='k', label="PSD")
    ax_a.plot(sm.freqs, sm._ap_fit, linestyle="--", color='r', label="model")
    ax_a.legend()
    ax_a.set_xscale('log')
    ax_a.set(xlabel="frequency (Hz)", ylabel="power (\u03BCV\u00b2/Hz)")
    ax_a.set_title('PSD model')

    # loop through features
    for ax_1, ax_2, feature, data in zip([ax_b, ax_e], 
                                         [ax_c, ax_f], 
                                         ['exponent', 'timescale'],
                                         [exponent_distr, timescale_distr]):

        # plot subplot b/e
        ax_1.hist(data, bins=20, color='gray', edgecolor='k')
        ax_1.set(xlabel=feature, ylabel="count")
        ax_1.set_title(f'{feature[0].upper()}{feature[1:]} distribution')
        # string = f"mean: {np.mean(data):.2f}\nstd: {np.std(data):.2f}"
        # ax_1.text(0.05, 0.95, string, transform=ax_b.transAxes, ha='left', 
        #           va='top')

        # plot subplot c/f
        # sns.violinplot(data=df, x='species', y=feature, ax=ax_2)
        sns.boxplot(data=df, x='species', y=feature, ax=ax_2, color='gray')
        ax_2.set_xticklabels(ax_c.get_xticklabels(), rotation=15)
        ax_2.set(xlabel="fungal species", ylabel=feature)
        ax_2.set_title(f'{feature[0].upper()}{feature[1:]} across species')

    # plot subplot d
    lags = acf.lags / FS
    ax_d.plot(lags, acf.corrs, color='k', label="ACF")
    ax_d.plot(lags, acf.corrs_fit, linestyle="--", color='r', label="model")
    ax_d.legend()
    ax_d.set(xlabel="lag (s)", ylabel="correlation")
    ax_d.set_title('ACF model')

    # beautify
    for ax in [ax_a, ax_b, ax_c, ax_d, ax_e, ax_f]:
        beautify_ax(ax)

    # save figure
    fig.savefig("figures/manuscript/figure_2.png")


if __name__ == "__main__":
    main()
