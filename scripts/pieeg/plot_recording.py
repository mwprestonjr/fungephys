# imports
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

from scipy.signal import resample
from neurodsp.spectral import compute_spectrum
from neurodsp.plts import plot_power_spectra


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Plot ephys data.')
    parser.add_argument('--fname', type=str, help='Filename of ephys data')
    parser.add_argument('--path_in', type=str, default='data/recordings/',
                        help='Path to the data folder')
    parser.add_argument('--fs', type=int, default=100,
                        help='Sampling frequency of the data')
    parser.add_argument('--col', type=str, default='chan_1',
                        help='Column name of the signal to plot')
    args = parser.parse_args()

    # check if fname was input and exists
    if args.fname is None:
        raise ValueError("Please input a filename")
    if not os.path.exists(f"{args.path_in}/{args.fname}"):
        raise ValueError(f"File {args.path_in}/{args.fname} does not exist")

    # init figure
    fig = plt.figure(figsize=(16, 4), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1])
    data = pd.read_csv(f"{args.path_in}/{args.fname}")
    plot_data(args, fig, gs, data)

    # animate
    ani = FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False,
                        fargs=(args, fig, gs))
    plt.show()


def update_plot(frame, args, fig, gs):
    data = pd.read_csv(f"{args.path_in}/{args.fname}")
    plot_data(args, fig, gs, data)
    
    
def plot_data(args, fig, gs, data):
    # unpack args
    fname = f"{args.path_in}/{args.fname}"
    fs = args.fs
    col = args.col

    # clear figure
    fig.clear()

    # init axes
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])

    # plot signal time-series
    ax0.plot(data['time'], data[col])
    ax0.set(xlabel='time (s)', ylabel='voltage')

    # set y-limits to 3 std from mean
    std = np.std(data[col])
    mean = np.mean(data[col])
    n = 3
    ax0.set_ylim(mean-n*std, mean+n*std)

    # resmple signal for spectral analysis (data is irregularly sampled)
    duration = data['time'].iloc[-1] - data['time'].iloc[0]
    signal = resample(data[col], int(duration*fs))
    time = np.linspace(0, len(signal)/fs, len(signal))

    # compute and plot signal power spectrum
    freqs, powers = compute_spectrum(signal, fs)
    plot_power_spectra(freqs, powers, log_powers=True, ax=ax1)


if __name__ == "__main__":
    main()