"""
Figure 3: Shared spectral signiture across kingdoms

A. Cartoon to represent kingdoms
B. Example time-series for each kingdom
C. Power spectra for each kingdom
D. Violin plot of exponent across kingdoms 
E. Violin plot of complexity across kingdoms 

"""

# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

import sys
sys.path.append("code")
# from pico_utils import import_data
from analysis import compute_exponent, compute_complexity
from utils import shift_signals
from plots import plot_spectra, beautify_ax

# settings
SHIFT = [8, 5, 5] # Shift signals for plotting (STDs)


def main():
    # LOAD DATA ################################################################
    print("Importing data...")

    # init
    signals, time, spectra, freqs = {}, {}, {}, {}
    
    # loop through kingdoms
    for ii, kingdom in enumerate(['fungal', 'plant', 'human']):
        # TEMP
        if kingdom == 'plant': continue

        # load signals
        data_in = np.load(f"data/manuscript/signals_{kingdom}.npz")
        signals[kingdom] = data_in['signals']
        time[kingdom] = data_in['time']

        # load example spectra
        data_in = np.load(f"data/manuscript/spectra_{kingdom}.npz")
        spectra[kingdom] = data_in['spectra']
        freqs[kingdom] = data_in['freqs']

    # ANALYSIS #################################################################
    print("Running analysis...")

    # measure and correlate exponent and complexity
    exponent, complexity = {}, {}
    df = pd.DataFrame()
    for ii, kingdom in enumerate(['fungal', 'human']):
        complexity[kingdom] = compute_complexity(signals[kingdom])
        exponent[kingdom] = compute_exponent(spectra[kingdom], freqs[kingdom])
        df = pd.concat([df, pd.DataFrame({'kingdom': kingdom, 
                                          'exponent': exponent[kingdom], 
                                          'complexity': complexity[kingdom]})])

    # PLOT #####################################################################
    print("Plotting...")
    
    # create figure and nested gridspec
    fig = plt.figure(figsize=[12, 8], constrained_layout=True)
    spec = gridspec.GridSpec(figure=fig, ncols=4, nrows=3, 
                             width_ratios=[1, 1, 1, 1], height_ratios=[1, 1, 1])
    gs_a = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=spec[:, 0])
    gs_de = gridspec.GridSpecFromSubplotSpec(4, 1, 
                                             height_ratios=[0.3, 1, 1, 0.3],
                                             subplot_spec=spec[:, 3])

    # plot subplot a
    ax_a = fig.add_subplot(gs_a[0])
    ax_a.imshow(plt.imread("data/manuscript/figure_3_cartoon.png"))
    ax_a.axis('off')
    fig.text(0.01, 0.85, 'Fungal', va='center', rotation='vertical', fontsize=12)
    fig.text(0.01, 0.52, 'Plant', va='center', rotation='vertical', fontsize=12)
    fig.text(0.01, 0.20, 'Human', va='center', rotation='vertical', fontsize=12)

    # loop through kingdoms
    for ii, kingdom in enumerate(['fungal', 'plant', 'human']):
        # TEMP
        if kingdom == 'plant': continue

        # plot subplot b
        ax_b = fig.add_subplot(spec[ii, 1])
        signals_i = shift_signals(signals[kingdom], std=SHIFT[ii])
        ax_b.plot(time[kingdom], signals_i.T, color='k', alpha=0.5)
        ax_b.set(xlabel='Time (s)', ylabel='Voltage (uV)')
        beautify_ax(ax_b)

        # plot subplot c
        ax_c = fig.add_subplot(spec[ii, 2])
        plot_spectra(spectra[kingdom], freqs[kingdom], ax=ax_c, color='k')
        beautify_ax(ax_c)

        # labels
        if ii == 0:
            ax_b.set_title('Voltage time-series')
            ax_c.set_title('Power spectra')

    # plot subplot d
    ax_d = fig.add_subplot(gs_de[1])
    sns.violinplot(data=df, x='kingdom', y='exponent', ax=ax_d)
    ax_d.set_xticklabels(ax_d.get_xticklabels(), rotation=15)
    ax_d.set(xlabel="Kingdom", ylabel="Exponent")
    ax_d.set_title('Exponent')

    # plot subplot e
    ax_e = fig.add_subplot(gs_de[2])
    sns.violinplot(data=df, x='kingdom', y='complexity', ax=ax_e)
    ax_e.set_xticklabels(ax_e.get_xticklabels(), rotation=15)
    ax_e.set(xlabel="Kingdom", ylabel="Complexity")
    ax_e.set_title('Complexity')

    # beautify
    for ax in [ax_d, ax_e]:
        beautify_ax(ax)

    # save figure
    fig.savefig("figures/manuscript/figure_3.png")


if __name__ == "__main__":
    main()
