"""
Figure 2: 1/f-like power spectra

A. Power spectra (with exponential fit)
B. Histogram of exponent
C. Violin of exponent compared to Adamatzky XXXX
D. Correlation between exponent and complexity

"""

# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from specparam import SpectralGroupModel
from scipy import stats
import seaborn as sns

import sys
sys.path.append("code")
# from pico_utils import import_data
from analysis import compute_exponent, compute_complexity
from info import N_CHANNELS
from plots import beautify_ax

# settings
I_SPECTRA = 0 # Index of spectra to plot


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
    aa2021_complexity = np.load("data/adamatzky_2021/results/complexity.npy")

    # ANALYSIS #################################################################
    print("Running analysis...")

    # fit power spectra
    sgm = SpectralGroupModel(aperiodic_mode='knee')
    sgm.fit(freqs, spectra)
    sm = sgm.get_model(I_SPECTRA)
    exponent = sgm.get_params('aperiodic', 'exponent')

    # measure and correlate exponent and complexity
    complexity = compute_complexity(signals)
    exponent = compute_exponent(spectra, freqs)
    linreg = stats.linregress(exponent, complexity)
    linreg_x = np.array([min(exponent), max(exponent)])
    linreg_y = linreg[0] * linreg_x + linreg[1]

    #  TEMP
    exponent_distr = np.random.normal(np.mean(exponent), np.std(exponent), 100)

    # PLOT #####################################################################
    print("Plotting...")
    
    # create figure and gridspec
    fig = plt.figure(figsize=[12, 3], constrained_layout=True)
    spec = gridspec.GridSpec(figure=fig, ncols=4, nrows=1, 
                             width_ratios=[1,1,1,1])
    ax_a = fig.add_subplot(spec[0,0])
    ax_b = fig.add_subplot(spec[0,1])
    ax_c = fig.add_subplot(spec[0,2])
    ax_d = fig.add_subplot(spec[0,3])

    # plot subplot a
    ax_a.plot(sm.freqs, sm.power_spectrum, linewidth=2, color='k', 
              label="spectrum")
    ax_a.plot(sm.freqs, sm._ap_fit, linestyle="--", color='r', label="model")
    ax_a.legend()
    ax_a.set_xscale('log')
    ax_a.set(xlabel="frequency (Hz)", ylabel="power (\u03BCV\u00b2/Hz)")
    ax_a.set_title('Spectral parameterization')

    # plot subplot b
    ax_b.hist(exponent_distr, bins=20, color='gray', edgecolor='k')
    ax_b.set(xlabel="exponent", ylabel="count")
    ax_b.set_title('Exponent distribution')
    ax_b.text(0.05, 0.95, f"mean: {np.mean(exponent):.2f}\nstd: {np.std(exponent):.2f}",
                transform=ax_b.transAxes, ha='left', va='top')

    # plot subplot c
    geni = ['cordyceps', 'flammulina', 'omphalotus','schizophyllum']
    df = pd.DataFrame({'species': np.repeat(geni, N_CHANNELS),
                       'exponent': aa2021_exponent.flatten(),
                        'complexity': aa2021_complexity.flatten()})
    sns.violinplot(data=df, x='species', y='exponent', ax=ax_c)
    ax_c.set_xticklabels(ax_c.get_xticklabels(), rotation=15)
    ax_c.set(xlabel="fungal species", ylabel="exponent")
    ax_c.set_title('Exponent across species')

    # plot subplot d
    ax_d.scatter(exponent, complexity, color='k', alpha=0.5)
    ax_d.plot(linreg_x, linreg_y, linestyle="--", color='k')
    ax_d.set(xlabel="exponent", ylabel="complexity")
    ax_d.set_title('Exponent vs complexity')
    # add stats text
    ax_d.text(0.95, 0.95, f"r = {linreg[2]:.2f}\np = {linreg[3]:.2f}",
                transform=ax_d.transAxes, ha='right', va='top')

    # beautify
    for ax in [ax_a, ax_b, ax_c, ax_d]:
        beautify_ax(ax)

    # save figure
    fig.savefig("figures/manuscript/figure_2.png")


if __name__ == "__main__":
    main()
